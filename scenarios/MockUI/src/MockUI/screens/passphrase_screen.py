"""Passphrase screen: adding a passphrase creates a NEW seed entry.
The original seed without passphrase stays in the seed list.
Wallets from the passphrase seed only show under that seed."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout
from ..stubs.seed import Seed


def _sanitize_passphrase(text):
    return text.strip()


class PassphraseScreen(lv.obj):
    """Add passphrase: creates a new seed entry with passphrase applied."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.base_seed = gui.specter_state.active_seed

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

        # Title
        title = lv.label(self)
        title.set_text("Add Passphrase")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        # Info: base seed
        if self.base_seed:
            info = lv.label(self)
            info.set_text("Base seed: " + self.base_seed.label)
            info.set_style_text_font(lv.font_montserrat_16, 0)
            info.set_style_text_color(CYAN_HEX, 0)

        # Explanation
        explain = lv.label(self)
        explain.set_text("A passphrase creates a completely\ndifferent wallet. The original seed\nwithout passphrase stays untouched.")
        explain.set_width(lv.pct(90))
        explain.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        explain.set_style_text_font(lv.font_montserrat_12, 0)
        explain.set_style_text_color(GREY_LIGHT_HEX, 0)

        # Passphrase input
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
        self.pa_ta.set_text("")
        self.pa_ta.set_width(lv.pct(65))
        self.pa_ta.set_height(50)
        self.pa_ta.set_style_text_font(lv.font_montserrat_22, 0)
        self.pa_ta.set_accepted_chars("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ ")

        def _on_commit(value):
            if value and self.base_seed:
                # Create a NEW seed entry with passphrase
                # The original seed stays untouched
                new_seed = Seed(
                    label=self.base_seed.label,
                    fingerprint=self.base_seed.fingerprint + "pp",
                    passphrase=value,
                )
                gui.specter_state.add_seed(new_seed)
                gui.specter_state.set_active_seed(new_seed)
            gui.refresh_dashboard()
            gui.show_menu("main")

        kb = lambda e: gui.keyboard_manager.bind(self.pa_ta, Layout.FULL, _on_commit, _sanitize_passphrase)
        self.pa_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        # Info
        note = lv.label(self)
        note.set_text("Tap the field to type your passphrase.\nPress OK on keyboard to confirm.")
        note.set_width(lv.pct(90))
        note.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        note.set_style_text_font(lv.font_montserrat_12, 0)
        note.set_style_text_color(GREY_LIGHT_HEX, 0)
