"""Interfaces screen: enable/disable hardware interfaces."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class InterfacesScreen(lv.obj):
    """Enable/disable hardware interfaces (QR, USB, SD, SmartCard)."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text("Interfaces")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        state = gui.specter_state
        rows = []
        if state.hasQR():
            rows.append((BTC_ICONS.QR_CODE, "QR Scanner", "_enabledQR"))
        if state.hasUSB():
            rows.append((BTC_ICONS.USB, "USB", "_enabledUSB"))
        if state.hasSD():
            rows.append((BTC_ICONS.SD_CARD, "SD Card", "_enabledSD"))
        if state.hasSmartCard():
            rows.append((BTC_ICONS.SMARTCARD, "SmartCard", "_enabledSmartCard"))

        for icon, text, state_attr in rows:
            self._add_toggle_row(icon, text, state_attr)

    def _add_toggle_row(self, icon, text, state_attr):
        row = lv.obj(self)
        row.set_size(lv.pct(100), 56)
        row.set_style_bg_color(BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_SM, 0)

        ico = lv.image(row)
        icon(WHITE_HEX).add_to_parent(ico, zoom=140)

        lbl = lv.label(row)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(WHITE_HEX, 0)
        lbl.set_flex_grow(1)

        sw = lv.switch(row)
        sw.set_size(50, 26)
        sw.set_style_bg_color(CYAN_HEX, lv.PART.INDICATOR | lv.STATE.CHECKED)

        enabled = bool(getattr(self.gui.specter_state, state_attr))
        if enabled:
            sw.add_state(lv.STATE.CHECKED)
        else:
            sw.remove_state(lv.STATE.CHECKED)

        def _handler(e, attr=state_attr):
            sw_obj = e.get_target_obj()
            is_on = bool(sw_obj.has_state(lv.STATE.CHECKED))
            setattr(self.gui.specter_state, attr, is_on)
            self.gui.refresh_ui()

        sw.add_event_cb(_handler, lv.EVENT.VALUE_CHANGED, None)
