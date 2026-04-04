"""Settings menu (hamburger): completely independent page.
Interface icons at top, unique settings below. No wallets/seeds shown."""
import lvgl as lv
from ..basic.ui_consts import (
    SCREEN_WIDTH, PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX, GREY_HEX,
    RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SettingsMenu(lv.obj):
    """Full independent settings page with interface status at top."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        state = gui.specter_state

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        # Title
        title = lv.label(self)
        title.set_text("Settings")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        # === Interface Status Bar (moved from old top bar) ===
        iface_card = lv.obj(self)
        iface_card.set_size(lv.pct(100), 60)
        iface_card.set_style_bg_color(BG_CARD_HEX, 0)
        iface_card.set_style_bg_opa(lv.OPA.COVER, 0)
        iface_card.set_style_radius(10, 0)
        iface_card.set_style_border_width(0, 0)
        iface_card.set_style_pad_all(PAD_SM, 0)
        iface_card.set_layout(lv.LAYOUT.FLEX)
        iface_card.set_flex_flow(lv.FLEX_FLOW.ROW)
        iface_card.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        # QR Scanner
        if state.hasQR():
            self._add_iface_icon(iface_card, BTC_ICONS.QR_CODE, "QR",
                                 state.QR_enabled(), "interfaces")
        # USB
        if state.hasUSB():
            self._add_iface_icon(iface_card, BTC_ICONS.USB, "USB",
                                 state.USB_enabled(), "interfaces")
        # SD Card
        if state.hasSD():
            color = GREEN_HEX if state.SD_detected() else (WHITE_HEX if state.SD_enabled() else GREY_HEX)
            self._add_iface_icon_colored(iface_card, BTC_ICONS.SD_CARD, "SD", color, "interfaces")
        # SmartCard
        if state.hasSmartCard():
            color = GREEN_HEX if state.SmartCard_detected() else (WHITE_HEX if state.SmartCard_enabled() else GREY_HEX)
            self._add_iface_icon_colored(iface_card, BTC_ICONS.SMARTCARD, "SC", color, "interfaces")

        # === Settings Menu Items (unique to this menu) ===

        # Device section
        section_lbl = lv.label(self)
        section_lbl.set_text("Device")
        section_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        section_lbl.set_style_text_color(GREY_LIGHT_HEX, 0)

        self._add_toggle_row("Power", state.battery_pct is not None, self._power_cb)
        self._add_toggle_row("Lock Device", state.is_locked, self._lock_cb)
        self._add_nav_item("Manage Interfaces", BTC_ICONS.USB, "interfaces")
        self._add_nav_item("Language", BTC_ICONS.GLOBE, "language_settings")

        # Security section
        sec_lbl = lv.label(self)
        sec_lbl.set_text("Security")
        sec_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        sec_lbl.set_style_text_color(GREY_LIGHT_HEX, 0)

        self._add_nav_item("Backup / Restore", BTC_ICONS.SAFE, "backup")
        self._add_nav_item("Firmware Info", BTC_ICONS.INFO, "firmware_info")

        # Danger zone
        danger_lbl = lv.label(self)
        danger_lbl.set_text("Danger Zone")
        danger_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        danger_lbl.set_style_text_color(RED_HEX, 0)

        self._add_nav_item("Wipe Device", BTC_ICONS.TRASH, "wipe_device", color=RED_HEX)

    def _add_iface_icon(self, parent, icon, label, enabled, target):
        color = GREEN_HEX if enabled else GREY_HEX
        self._add_iface_icon_colored(parent, icon, label, color, target)

    def _add_iface_icon_colored(self, parent, icon, label, color, target):
        btn = lv.button(parent)
        btn.set_size(lv.SIZE_CONTENT, 48)
        btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_pad_all(4, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        btn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        ico = lv.image(btn)
        icon(color).add_to_parent(ico, zoom=150)

        lbl = lv.label(btn)
        lbl.set_text(label)
        lbl.set_style_text_font(lv.font_montserrat_12, 0)
        lbl.set_style_text_color(color, 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _add_toggle_row(self, text, initial_state, callback):
        row = lv.obj(self)
        row.set_size(lv.pct(100), 48)
        row.set_style_bg_color(BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        lbl = lv.label(row)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(WHITE_HEX, 0)
        lbl.align(lv.ALIGN.LEFT_MID, 0, 0)

        sw = lv.switch(row)
        sw.set_size(50, 26)
        sw.align(lv.ALIGN.RIGHT_MID, 0, 0)
        if initial_state:
            sw.add_state(lv.STATE.CHECKED)
        sw.set_style_bg_color(CYAN_HEX, lv.PART.INDICATOR | lv.STATE.CHECKED)
        sw.add_event_cb(callback, lv.EVENT.VALUE_CHANGED, None)

    def _add_nav_item(self, text, icon, target, color=None):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), 48)
        btn.set_style_bg_color(BG_CARD_HEX, 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(8, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        ico = lv.image(btn)
        txt_color = color if color else WHITE_HEX
        icon(txt_color).add_to_parent(ico, zoom=130)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(txt_color, 0)
        lbl.set_flex_grow(1)

        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _power_cb(self, e):
        if e.get_code() == lv.EVENT.VALUE_CHANGED:
            sw = e.get_target_obj()
            if sw.has_state(lv.STATE.CHECKED):
                self.gui.specter_state.battery_pct = 100
            else:
                self.gui.specter_state.battery_pct = None
            self.gui.refresh_ui()

    def _lock_cb(self, e):
        if e.get_code() == lv.EVENT.VALUE_CHANGED:
            sw = e.get_target_obj()
            if sw.has_state(lv.STATE.CHECKED):
                self.gui.specter_state.lock()
                self.gui.show_menu(None)
