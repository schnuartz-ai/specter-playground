"""Firmware info screen."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class FirmwareScreen(lv.obj):
    """Firmware information and update screen."""

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
        self.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text("Firmware")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        self._add_info_row("Version", gui.specter_state.fw_version)
        self._add_info_row("Platform", "STM32F469NI")
        self._add_info_row("Build", "Specter DIY")

        # Update options
        divider = lv.obj(self)
        divider.set_size(lv.pct(100), 1)
        divider.set_style_bg_color(GREY_DARK_HEX, 0)
        divider.set_style_bg_opa(lv.OPA.COVER, 0)
        divider.set_style_border_width(0, 0)

        sec_title = lv.label(self)
        sec_title.set_text("Update via")
        sec_title.set_style_text_font(lv.font_montserrat_12, 0)
        sec_title.set_style_text_color(GREY_LIGHT_HEX, 0)

        self._add_update_btn("Update from SD Card", BTC_ICONS.SD_CARD)

    def _add_info_row(self, label, value):
        row = lv.obj(self)
        row.set_size(lv.pct(100), 44)
        row.set_style_bg_color(BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        key = lv.label(row)
        key.set_text(label)
        key.set_style_text_font(lv.font_montserrat_16, 0)
        key.set_style_text_color(GREY_LIGHT_HEX, 0)
        key.align(lv.ALIGN.LEFT_MID, 0, 0)

        val = lv.label(row)
        val.set_text(value)
        val.set_style_text_font(lv.font_montserrat_16, 0)
        val.set_style_text_color(WHITE_HEX, 0)
        val.align(lv.ALIGN.RIGHT_MID, 0, 0)

    def _add_update_btn(self, text, icon):
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
        icon(CYAN_HEX).add_to_parent(ico, zoom=130)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(WHITE_HEX, 0)
        lbl.set_flex_grow(1)

        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)
