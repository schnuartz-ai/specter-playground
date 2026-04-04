"""Wallet list section: heading + pinned default wallet + sorted wallet rows.
Creative visual indicators for wallet parameters:
  - Address type: S (Segwit cyan), L (Legacy orange), T (Taproot green)
  - Sig type: Single Sig + Native Segwit = no extra symbol (cleanest)
  - Multi-sig: two-keys icon in orange
  - Account: small number badge when account > 0
  - Companion apps: small colored dots
"""
import lvgl as lv
from .ui_consts import (
    WALLET_SECTION_HEIGHT, SCREEN_WIDTH, WALLET_ROW_HEIGHT, WALLET_ICON_SIZE,
    PAD_SM, PAD_MD, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX,
    ORANGE_HEX, GREEN_HEX, GREY_HEX, RED_HEX,
)
from .symbol_lib import BTC_ICONS
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT
from .keyboard_manager import Layout


def _wallet_sort_key(wallet):
    """Sort: single-sig first, then by address type, then account."""
    sig = 1 if wallet.isMultiSig else 0
    addr_order = {ADDR_NATIVE_SEGWIT: 0, ADDR_NESTED_SEGWIT: 1, ADDR_LEGACY: 2, ADDR_TAPROOT: 3}
    addr = addr_order.get(wallet.address_type, 0)
    return (sig, addr, wallet.account)


class WalletList(lv.obj):
    """Wallet section with heading, wrench icon, and scrollable wallet rows."""

    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui

        self.set_size(SCREEN_WIDTH, WALLET_SECTION_HEIGHT)
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(PAD_SM, 0)
        self.set_style_pad_bottom(0, 0)

        # Header row
        header = lv.obj(self)
        header.set_size(SCREEN_WIDTH - 2 * PAD_MD, 28)
        header.set_style_bg_opa(lv.OPA.TRANSP, 0)
        header.set_style_border_width(0, 0)
        header.set_style_pad_all(0, 0)

        title = lv.label(header)
        title.set_text("Wallets")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)
        title.align(lv.ALIGN.LEFT_MID, 0, 0)

        # Wrench icon → Wallet Menu
        wrench_btn = lv.button(header)
        wrench_btn.set_size(32, 32)
        wrench_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        wrench_btn.set_style_border_width(0, 0)
        wrench_btn.set_style_shadow_width(0, 0)
        wrench_btn.align(lv.ALIGN.RIGHT_MID, 0, 0)

        wrench_ico = lv.image(wrench_btn)
        BTC_ICONS.GEAR(GREY_LIGHT_HEX).add_to_parent(wrench_ico, zoom=160)
        wrench_ico.center()
        wrench_btn.add_event_cb(self._wrench_cb, lv.EVENT.CLICKED, None)

        # Scrollable wallet rows
        self.wallet_container = lv.obj(self)
        self.wallet_container.set_size(SCREEN_WIDTH - 2 * PAD_MD, WALLET_SECTION_HEIGHT - 36)
        self.wallet_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.wallet_container.set_style_border_width(0, 0)
        self.wallet_container.set_style_pad_all(0, 0)
        self.wallet_container.set_style_pad_row(PAD_XS, 0)
        self.wallet_container.set_layout(lv.LAYOUT.FLEX)
        self.wallet_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.wallet_container.align_to(header, lv.ALIGN.OUT_BOTTOM_LEFT, 0, PAD_XS)

        self.refresh()

    def refresh(self):
        self.wallet_container.clean()
        state = self.gui.specter_state

        if not state.active_seed:
            lbl = lv.label(self.wallet_container)
            lbl.set_text("Load a seed to see wallets")
            lbl.set_style_text_color(GREY_LIGHT_HEX, 0)
            lbl.set_style_text_font(lv.font_montserrat_12, 0)
            return

        wallets = state.wallets_for_seed(state.active_seed) or []
        default_w = None
        others = []
        for w in wallets:
            if w.is_default_wallet():
                default_w = w
            else:
                others.append(w)

        others.sort(key=_wallet_sort_key)

        if default_w:
            self._add_row(default_w, is_default=True)
        for w in others:
            self._add_row(w, is_default=False)

    def _add_row(self, wallet, is_default=False):
        state = self.gui.specter_state
        is_active = state.active_wallet is wallet

        row = lv.button(self.wallet_container)
        row.set_size(lv.pct(100), WALLET_ROW_HEIGHT)
        row.set_style_bg_color(BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_shadow_width(0, 0)
        row.set_style_pad_left(PAD_SM, 0)
        row.set_style_pad_right(PAD_SM, 0)

        if is_active:
            row.set_style_border_width(1, 0)
            row.set_style_border_color(CYAN_HEX, 0)
        else:
            row.set_style_border_width(0, 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_XS, 0)

        # === Parameter indicators (only for non-default, non-cleanest) ===
        if not is_default:
            # Address type badge — Single Sig + Native Segwit gets NO badge (cleanest)
            needs_addr_badge = wallet.address_type != ADDR_NATIVE_SEGWIT
            needs_ms_badge = wallet.isMultiSig
            needs_acc_badge = wallet.account > 0

            if needs_ms_badge:
                ms_ico = lv.image(row)
                BTC_ICONS.TWO_KEYS(ORANGE_HEX).add_to_parent(ms_ico, zoom=110)

            if needs_addr_badge:
                addr_lbl = lv.label(row)
                if wallet.address_type == ADDR_LEGACY:
                    addr_lbl.set_text("L")
                    addr_lbl.set_style_text_color(ORANGE_HEX, 0)
                elif wallet.address_type == ADDR_TAPROOT:
                    addr_lbl.set_text("T")
                    addr_lbl.set_style_text_color(GREEN_HEX, 0)
                elif wallet.address_type == ADDR_NESTED_SEGWIT:
                    addr_lbl.set_text("nS")
                    addr_lbl.set_style_text_color(CYAN_HEX, 0)
                addr_lbl.set_style_text_font(lv.font_montserrat_12, 0)

            if needs_acc_badge:
                acc_lbl = lv.label(row)
                acc_lbl.set_text(str(wallet.account))
                acc_lbl.set_style_text_font(lv.font_montserrat_12, 0)
                acc_lbl.set_style_text_color(CYAN_HEX, 0)
                acc_lbl.set_style_text_opa(lv.OPA._70, 0)

        # Wallet name
        name_lbl = lv.label(row)
        name_lbl.set_text(wallet.label)
        name_lbl.set_style_text_font(lv.font_montserrat_16, 0)
        name_lbl.set_style_text_color(WHITE_HEX, 0)
        name_lbl.set_flex_grow(1)

        # Companion app dots (colored circles for each shared app)
        if wallet.shared_with:
            for i, app in enumerate(wallet.shared_with):
                if i >= 3:
                    break  # max 3 dots to save space
                dot = lv.label(row)
                dot.set_text("\xE2\x97\x8F")  # bullet
                dot.set_style_text_font(lv.font_montserrat_12, 0)
                dot.set_style_text_color(GREEN_HEX, 0)
        elif wallet.has_been_exported:
            ico = lv.image(row)
            BTC_ICONS.SHARE(GREEN_HEX).add_to_parent(ico, zoom=100)

        # Click to select
        row.add_event_cb(lambda e, w=wallet: self._select(w), lv.EVENT.CLICKED, None)
        # Long-press for details
        row.add_event_cb(lambda e, w=wallet: self._long_press(w), lv.EVENT.LONG_PRESSED, None)

    def _select(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.refresh()

    def _long_press(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("wallet_details")

    def _wrench_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("wallet_menu")
