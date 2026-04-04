"""Connect companion app screen: share wallet with software wallets."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


_COMPANION_APPS = [
    "Specter Desktop",
    "Sparrow",
    "Nunchuk",
    "Bitcoin Keeper",
    "Bitcoin Safe",
    "BlueWallet",
    "Bull Bitcoin",
    "Liana Wallet",
]


class ConnectAppScreen(lv.obj):
    """Share wallet descriptor with a companion app. Tracks which apps."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.wallet = gui.specter_state.active_wallet

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
        title.set_text("Connect Companion App")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        if self.wallet:
            info = lv.label(self)
            info.set_text("Share: " + self.wallet.label)
            info.set_style_text_font(lv.font_montserrat_16, 0)
            info.set_style_text_color(CYAN_HEX, 0)

        for app_name in _COMPANION_APPS:
            already_shared = self.wallet and app_name in self.wallet.shared_with
            self._add_app_row(app_name, already_shared)

    def _add_app_row(self, app_name, already_shared):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), 48)
        btn.set_style_bg_color(BG_ELEVATED_HEX if already_shared else BG_CARD_HEX, 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(8, 0)
        btn.set_style_shadow_width(0, 0)
        if already_shared:
            btn.set_style_border_width(1, 0)
            btn.set_style_border_color(GREEN_HEX, 0)
        else:
            btn.set_style_border_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        ico = lv.image(btn)
        BTC_ICONS.LINK(GREEN_HEX if already_shared else CYAN_HEX).add_to_parent(ico, zoom=130)

        lbl = lv.label(btn)
        lbl.set_text(app_name)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(GREEN_HEX if already_shared else WHITE_HEX, 0)
        lbl.set_flex_grow(1)

        if already_shared:
            check = lv.label(btn)
            check.set_text(lv.SYMBOL.OK)
            check.set_style_text_color(GREEN_HEX, 0)
        else:
            arrow = lv.label(btn)
            arrow.set_text(lv.SYMBOL.RIGHT)
            arrow.set_style_text_color(GREY_LIGHT_HEX, 0)

        btn.add_event_cb(lambda e, name=app_name: self._select_app(name), lv.EVENT.CLICKED, None)

    def _select_app(self, app_name):
        if self.wallet:
            self.wallet.mark_shared(app_name)
        # Refresh to show the checkmark
        self.gui.show_menu("connect_app")
