"""Seed detail screen: dedicated page for a specific seed's options."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SeedDetailScreen(lv.obj):
    """Dedicated page showing details and options for the active seed."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.seed = gui.specter_state.active_seed

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        if not self.seed:
            lbl = lv.label(self)
            lbl.set_text("No seed selected")
            lbl.set_style_text_color(GREY_LIGHT_HEX, 0)
            return

        # Seed info card
        info_card = lv.obj(self)
        info_card.set_size(lv.pct(100), 90)
        info_card.set_style_bg_color(BG_CARD_HEX, 0)
        info_card.set_style_bg_opa(lv.OPA.COVER, 0)
        info_card.set_style_radius(12, 0)
        info_card.set_style_border_width(1, 0)
        info_card.set_style_border_color(CYAN_HEX, 0)
        info_card.set_style_pad_all(PAD_MD, 0)

        # Key icon + name
        key_ico = lv.image(info_card)
        BTC_ICONS.KEY(CYAN_HEX).add_to_parent(key_ico, zoom=180)
        key_ico.align(lv.ALIGN.LEFT_MID, 0, -10)

        name_lbl = lv.label(info_card)
        name_lbl.set_text(self.seed.label)
        name_lbl.set_style_text_font(lv.font_montserrat_22, 0)
        name_lbl.set_style_text_color(WHITE_HEX, 0)
        name_lbl.align(lv.ALIGN.LEFT_MID, 55, -10)

        fp_lbl = lv.label(info_card)
        fp_lbl.set_text("Fingerprint: " + self.seed.fingerprint[:8])
        fp_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        fp_lbl.set_style_text_color(GREY_LIGHT_HEX, 0)
        fp_lbl.align(lv.ALIGN.LEFT_MID, 55, 14)

        # Passphrase status
        if self.seed.passphrase:
            pp_lbl = lv.label(info_card)
            pp_lbl.set_text("+ Passphrase")
            pp_lbl.set_style_text_font(lv.font_montserrat_12, 0)
            pp_lbl.set_style_text_color(GREEN_HEX, 0)
            pp_lbl.align(lv.ALIGN.RIGHT_MID, 0, 0)

        # Action options - each is a proper navigable item
        self._add_option("Set Passphrase", BTC_ICONS.PASSWORD, "set_passphrase")
        self._add_option("Show Seed Words", BTC_ICONS.VISIBLE, "show_seed_words")
        self._add_option("BIP85 Derivation", BTC_ICONS.KEY, "bip85")
        self._add_option("Backup Seed", BTC_ICONS.SAFE, "backup")
        self._add_option("Store Seed", BTC_ICONS.SD_CARD, "store_seed")

        # Spacer
        spacer = lv.obj(self)
        spacer.set_size(lv.pct(100), 10)
        spacer.set_style_bg_opa(lv.OPA.TRANSP, 0)
        spacer.set_style_border_width(0, 0)

        # Delete (danger)
        self._add_option("Delete Seed", BTC_ICONS.TRASH, "delete_seed", color=RED_HEX)

    def _add_option(self, text, icon, target, color=None):
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
        txt_color = color if color else CYAN_HEX
        icon(txt_color).add_to_parent(ico, zoom=140)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(color if color else WHITE_HEX, 0)
        lbl.set_flex_grow(1)

        # Arrow indicator
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)

        btn.add_event_cb(lambda e, t=target: self._navigate(t), lv.EVENT.CLICKED, None)

    def _navigate(self, target):
        if target == "delete_seed":
            self.gui.specter_state.remove_seed(self.seed)
            self.gui.show_menu("seed_management")
        else:
            self.gui.show_menu(target)
