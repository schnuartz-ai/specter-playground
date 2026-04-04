"""Seed management menu: clean list of actions and loaded seeds.
Tapping a seed navigates to a dedicated seed detail page."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SeedMenu(lv.obj):
    """Full-screen seed management — actions + loaded seed list."""

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

        # Title
        title = lv.label(self)
        title.set_text("Seed Management")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        # Action buttons
        self._add_nav_btn("Generate New Seed", BTC_ICONS.MAGIC_WAND, "generate_seed")
        self._add_nav_btn("Import from QR", BTC_ICONS.QR_CODE, "scan")
        self._add_nav_btn("Import from SD Card", BTC_ICONS.SD_CARD, "sd_card")
        self._add_nav_btn("Enter Manually", BTC_ICONS.MNEMONIC, "enter_seed_words")

        # Loaded seeds section
        state = gui.specter_state
        if state.loaded_seeds:
            # Divider
            divider = lv.obj(self)
            divider.set_size(lv.pct(100), 1)
            divider.set_style_bg_color(GREY_DARK_HEX, 0)
            divider.set_style_bg_opa(lv.OPA.COVER, 0)
            divider.set_style_border_width(0, 0)

            seeds_title = lv.label(self)
            seeds_title.set_text("Loaded Seeds")
            seeds_title.set_style_text_font(lv.font_montserrat_16, 0)
            seeds_title.set_style_text_color(GREY_LIGHT_HEX, 0)

            for seed in state.loaded_seeds:
                self._add_seed_row(seed)

    def _add_nav_btn(self, text, icon, target):
        """Navigation button that goes to a dedicated page."""
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
        icon(CYAN_HEX).add_to_parent(ico, zoom=140)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(WHITE_HEX, 0)
        lbl.set_flex_grow(1)

        # Arrow
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _add_seed_row(self, seed):
        """Seed row — tap navigates to seed detail page."""
        state = self.gui.specter_state
        is_active = state.active_seed is seed

        btn = lv.button(self)
        btn.set_size(lv.pct(100), 56)
        btn.set_style_bg_color(BG_ELEVATED_HEX if is_active else BG_CARD_HEX, 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(8, 0)
        btn.set_style_shadow_width(0, 0)
        if is_active:
            btn.set_style_border_width(1, 0)
            btn.set_style_border_color(CYAN_HEX, 0)
        else:
            btn.set_style_border_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        # Key icon
        ico = lv.image(btn)
        BTC_ICONS.KEY(CYAN_HEX if is_active else GREY_LIGHT_HEX).add_to_parent(ico, zoom=130)

        # Seed name
        name = lv.label(btn)
        label_text = seed.label
        if seed.passphrase:
            label_text = label_text + " + PP"
        name.set_text(label_text)
        name.set_style_text_font(lv.font_montserrat_16, 0)
        name.set_style_text_color(CYAN_HEX if is_active else WHITE_HEX, 0)
        name.set_flex_grow(1)

        # Fingerprint
        fp = lv.label(btn)
        fp.set_text(seed.fingerprint[:8])
        fp.set_style_text_font(lv.font_montserrat_12, 0)
        fp.set_style_text_color(GREY_LIGHT_HEX, 0)

        # Arrow
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)

        def _on_tap(e, s=seed):
            if e.get_code() == lv.EVENT.CLICKED:
                self.gui.specter_state.set_active_seed(s)
                self.gui.show_menu("seed_detail")

        btn.add_event_cb(_on_tap, lv.EVENT.CLICKED, None)
