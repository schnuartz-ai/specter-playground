import lvgl as lv
from .menu import GenericMenu
from .symbol_lib import BTC_ICONS
from .ui_consts import BTN_HEIGHT, RED_HEX


class ErrorScreen(GenericMenu):
    """Reusable error dialog screen.

    Displays an error icon, error message, and action buttons.
    Shows Back button (always) and Retry button (if on_retry provided).
    """

    def __init__(self, parent, title, error_message, on_retry=None, on_back=None, *args, **kwargs):
        """
        Args:
            parent: NavigationController parent
            title: Title text for the screen
            error_message: Description of the error that occurred
            on_retry: Optional callback function for retry action
            on_back: Optional callback function for back action (defaults to navigation back)
        """
        # Get translation function
        t = parent.i18n.t
        self.t = t
        self._on_retry_callback = on_retry
        self._on_back_callback = on_back

        # Initialize with empty menu items - we'll add custom content
        super().__init__("error", title, [], parent, *args, **kwargs)

        # Center content in container
        self.container.set_flex_align(
            lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )

        # Error icon
        icon_container = lv.obj(self.container)
        icon_container.set_size(60, 60)
        icon_container.set_style_border_width(0, 0)
        icon_container.set_style_pad_all(0, 0)
        error_icon = lv.image(icon_container)
        BTC_ICONS.ALERT_CIRCLE.add_to_parent(error_icon)
        error_icon.center()

        # Error message in RED
        self.error_lbl = lv.label(self.container)
        self.error_lbl.set_text(error_message)
        self.error_lbl.set_width(lv.pct(90))
        self.error_lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.error_lbl.set_style_text_color(RED_HEX, 0)

        # Button container for horizontal layout
        btn_container = lv.obj(self.container)
        btn_container.set_layout(lv.LAYOUT.FLEX)
        btn_container.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn_container.set_width(lv.pct(100))
        btn_container.set_height(BTN_HEIGHT + 20)
        btn_container.set_flex_align(
            lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )
        btn_container.set_style_border_width(0, 0)
        btn_container.set_style_pad_all(0, 0)

        # Back button (always shown)
        self.back_btn = lv.button(btn_container)
        # Adjust width based on whether retry button is shown
        if on_retry:
            self.back_btn.set_width(lv.pct(40))
        else:
            self.back_btn.set_width(lv.pct(60))
        self.back_btn.set_height(BTN_HEIGHT)
        back_lbl = lv.label(self.back_btn)
        back_lbl.set_text(t("ERROR_SCREEN_BACK"))
        back_lbl.center()
        self.back_btn.add_event_cb(self._on_back_pressed, lv.EVENT.CLICKED, None)

        # Retry button (only if callback provided)
        if on_retry:
            self.retry_btn = lv.button(btn_container)
            self.retry_btn.set_width(lv.pct(40))
            self.retry_btn.set_height(BTN_HEIGHT)
            retry_lbl = lv.label(self.retry_btn)
            retry_lbl.set_text(t("ERROR_SCREEN_RETRY"))
            retry_lbl.center()
            self.retry_btn.add_event_cb(self._on_retry_pressed, lv.EVENT.CLICKED, None)

    def _on_back_pressed(self, e):
        """Handle back button press."""
        if e.get_code() == lv.EVENT.CLICKED:
            if self._on_back_callback:
                self._on_back_callback()
            else:
                # Default: navigate back
                self.on_navigate(None)

    def _on_retry_pressed(self, e):
        """Handle retry button press."""
        if e.get_code() == lv.EVENT.CLICKED:
            if self._on_retry_callback:
                self._on_retry_callback()
