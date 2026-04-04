"""Top bar: battery indicator (left) + hamburger menu (right)."""
import lvgl as lv
from ..stubs import Battery
from .ui_consts import (
    TOP_BAR_HEIGHT, SCREEN_WIDTH, PAD_SM, PAD_MD,
    BG_BLACK_HEX, WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from .symbol_lib import BTC_ICONS


class TopBar(lv.obj):
    """Minimal top bar with battery on left, hamburger on right."""

    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui

        self.set_size(SCREEN_WIDTH, TOP_BAR_HEIGHT)
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(0, 0)
        self.set_style_pad_bottom(0, 0)
        self.align(lv.ALIGN.TOP_LEFT, 0, 0)

        # Battery indicator (left)
        self.batt_icon = Battery(self)
        self.batt_icon.VALUE = gui.specter_state.battery_pct
        self.batt_icon.update()
        self.batt_icon.align(lv.ALIGN.LEFT_MID, 0, 0)

        # Hamburger menu button (right)
        self.hamburger_btn = lv.button(self)
        self.hamburger_btn.set_size(44, 36)
        self.hamburger_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.hamburger_btn.set_style_border_width(0, 0)
        self.hamburger_btn.set_style_shadow_width(0, 0)
        self.hamburger_btn.align(lv.ALIGN.RIGHT_MID, 0, 0)

        # Hamburger icon (three lines using MENU icon)
        self.hamburger_ico = lv.image(self.hamburger_btn)
        BTC_ICONS.MENU(WHITE_HEX).add_to_parent(self.hamburger_ico, zoom=180)
        self.hamburger_ico.center()

        self.hamburger_btn.add_event_cb(self._hamburger_cb, lv.EVENT.CLICKED, None)

    def _hamburger_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("settings")

    def refresh(self, state):
        """Update battery from state."""
        self.batt_icon.CHARGING = state.is_charging
        if state.has_battery:
            self.batt_icon.VALUE = state.battery_pct
            self.batt_icon.update()
        else:
            self.batt_icon.VALUE = 100
            self.batt_icon.update()
