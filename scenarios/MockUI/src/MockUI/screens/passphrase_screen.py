"""Passphrase screen: enter/edit passphrase for the active seed."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout


def _sanitize_passphrase(text):
    return text.strip()


class PassphraseScreen(lv.obj):
    """Dedicated screen for entering/editing the active seed's passphrase."""

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
        self.set_style_pad_row(PAD_LG, 0)

        seed = gui.specter_state.active_seed

        # Title
        title = lv.label(self)
        title.set_text("Set Passphrase")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        # Seed info
        if seed:
            seed_info = lv.label(self)
            seed_info.set_text("For: " + seed.label)
            seed_info.set_style_text_font(lv.font_montserrat_16, 0)
            seed_info.set_style_text_color(CYAN_HEX, 0)

        # Passphrase input row
        pa_row = lv.obj(self)
        pa_row.set_size(lv.pct(100), 70)
        pa_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        pa_row.set_style_border_width(0, 0)
        pa_row.set_style_pad_all(0, 0)
        pa_row.set_layout(lv.LAYOUT.FLEX)
        pa_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        pa_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        pa_lbl = lv.label(pa_row)
        pa_lbl.set_text("Passphrase")
        pa_lbl.set_width(lv.pct(30))
        pa_lbl.set_style_text_font(lv.font_montserrat_16, 0)
        pa_lbl.set_style_text_color(WHITE_HEX, 0)

        self.pa_ta = lv.textarea(pa_row)
        val = ""
        if seed and seed.passphrase is not None:
            val = seed.passphrase
        self.pa_ta.set_text(val)
        self.pa_ta.set_width(lv.pct(65))
        self.pa_ta.set_height(50)
        self.pa_ta.set_style_text_font(lv.font_montserrat_22, 0)
        self.pa_ta.set_accepted_chars("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ ")

        def _on_commit(value):
            if gui.specter_state.active_seed:
                if not value:
                    gui.specter_state.active_seed.passphrase = None
                else:
                    gui.specter_state.active_seed.passphrase = value
            gui.refresh_dashboard()
            gui.show_menu(None)

        kb_bind = lambda e: gui.keyboard_manager.bind(self.pa_ta, Layout.FULL, _on_commit, _sanitize_passphrase)
        self.pa_ta.add_event_cb(kb_bind, lv.EVENT.CLICKED, None)

        # Info text
        info = lv.label(self)
        info.set_text("Tap the text field to type.\nA passphrase creates a different wallet.\nLeave empty to remove.")
        info.set_width(lv.pct(90))
        info.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        info.set_style_text_font(lv.font_montserrat_12, 0)
        info.set_style_text_color(GREY_LIGHT_HEX, 0)

        # Clear button
        clear_btn = lv.button(self)
        clear_btn.set_size(lv.pct(100), 48)
        clear_btn.set_style_bg_color(BG_CARD_HEX, 0)
        clear_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        clear_btn.set_style_radius(8, 0)
        clear_btn.set_style_border_width(1, 0)
        clear_btn.set_style_border_color(RED_HEX, 0)
        clear_btn.set_style_shadow_width(0, 0)

        clear_lbl = lv.label(clear_btn)
        clear_lbl.set_text("Clear Passphrase")
        clear_lbl.set_style_text_font(lv.font_montserrat_16, 0)
        clear_lbl.set_style_text_color(RED_HEX, 0)
        clear_lbl.center()

        clear_btn.add_event_cb(self._on_clear, lv.EVENT.CLICKED, None)

    def _on_clear(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        self.pa_ta.set_text("")
        if self.gui.specter_state.active_seed:
            self.gui.specter_state.active_seed.passphrase = None
        self.gui.refresh_dashboard()
