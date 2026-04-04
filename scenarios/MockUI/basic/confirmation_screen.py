import lvgl as lv
from .menu import GenericMenu
from .ui_consts import BTN_HEIGHT, BTN_WIDTH, CRITICAL_RED_HEX


class ConfirmationScreen(GenericMenu):
    """Reusable confirmation dialog for destructive actions.

    Shows a warning message with Cancel and Confirm buttons.
    Confirm button is styled in red to indicate destructive action.
    """

    def __init__(self, parent, title, warning_message, on_confirm, *args, **kwargs):
        """
        Args:
            parent: NavigationController parent
            title: Title text for the screen
            warning_message: Description of the action to be confirmed
            on_confirm: Callback function to execute when user confirms
        """
        # Get translation function
        t = parent.i18n.t
        self.t = t
        self._on_confirm_callback = on_confirm

        # Initialize with empty menu items - we'll add custom content
        super().__init__("confirmation", title, [], parent, *args, **kwargs)

        # Center content in container
        self.container.set_flex_align(
            lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )

        # Warning message
        self.warning_lbl = lv.label(self.container)
        self.warning_lbl.set_text(warning_message)
        self.warning_lbl.set_width(lv.pct(90))
        self.warning_lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

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

        # Cancel button (left, neutral styling)
        self.cancel_btn = lv.button(btn_container)
        self.cancel_btn.set_width(lv.pct(40))
        self.cancel_btn.set_height(BTN_HEIGHT)
        cancel_lbl = lv.label(self.cancel_btn)
        cancel_lbl.set_text(t("CONFIRMATION_CANCEL"))
        cancel_lbl.center()
        self.cancel_btn.add_event_cb(self._on_cancel, lv.EVENT.CLICKED, None)

        # Confirm button (right, RED for destructive action)
        self.confirm_btn = lv.button(btn_container)
        self.confirm_btn.set_width(lv.pct(40))
        self.confirm_btn.set_height(BTN_HEIGHT)
        self.confirm_btn.set_style_bg_color(CRITICAL_RED_HEX, lv.PART.MAIN)
        confirm_lbl = lv.label(self.confirm_btn)
        confirm_lbl.set_text(t("CONFIRMATION_CONFIRM"))
        confirm_lbl.center()
        self.confirm_btn.add_event_cb(self._on_confirm, lv.EVENT.CLICKED, None)

    def _on_cancel(self, e):
        """Handle cancel button - navigate back to previous screen."""
        if e.get_code() == lv.EVENT.CLICKED:
            self.on_navigate(None)

    def _on_confirm(self, e):
        """Handle confirm button - execute callback then navigate back."""
        if e.get_code() == lv.EVENT.CLICKED:
            if self._on_confirm_callback:
                self._on_confirm_callback()
            self.on_navigate(None)
