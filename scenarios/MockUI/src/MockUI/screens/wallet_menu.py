"""Wallet Menu: full-screen overlay listing all wallets with full details.
Supports rename, delete, and shows all three parameters with icons."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX,
    RED_HEX, GREEN_HEX, ORANGE_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT


_ADDR_LABELS = {
    ADDR_NATIVE_SEGWIT: ("Native Segwit", CYAN_HEX),
    ADDR_NESTED_SEGWIT: ("Nested Segwit", CYAN_HEX),
    ADDR_LEGACY: ("Legacy", ORANGE_HEX),
    ADDR_TAPROOT: ("Taproot", GREEN_HEX),
}


class WalletMenu(lv.obj):
    """Full-screen wallet management. Self-explanatory — no legend needed."""

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
        title.set_text("All Wallets")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        state = gui.specter_state
        if not state.registered_wallets:
            empty = lv.label(self)
            empty.set_text("No wallets registered")
            empty.set_style_text_color(GREY_LIGHT_HEX, 0)
            return

        # Sort: default first, then single-sig, then multi-sig
        wallets = list(state.registered_wallets)
        default_w = [w for w in wallets if w.is_default_wallet()]
        single = sorted([w for w in wallets if not w.is_default_wallet() and not w.isMultiSig],
                        key=lambda w: (w.account, w.label))
        multi = sorted([w for w in wallets if w.isMultiSig], key=lambda w: w.label)

        for wallet in default_w + single + multi:
            self._add_entry(wallet)

    def _add_entry(self, wallet):
        state = self.gui.specter_state
        is_active = state.active_wallet is wallet
        is_default = wallet.is_default_wallet()

        card = lv.obj(self)
        card.set_size(lv.pct(100), 72)
        card.set_style_bg_color(BG_ELEVATED_HEX if is_active else BG_CARD_HEX, 0)
        card.set_style_bg_opa(lv.OPA.COVER, 0)
        card.set_style_radius(10, 0)
        card.set_style_pad_all(PAD_SM, 0)
        if is_active:
            card.set_style_border_width(1, 0)
            card.set_style_border_color(CYAN_HEX, 0)
        else:
            card.set_style_border_width(0, 0)

        # Top line: type icon + name + actions
        top = lv.obj(card)
        top.set_size(lv.pct(100), 28)
        top.set_style_bg_opa(lv.OPA.TRANSP, 0)
        top.set_style_border_width(0, 0)
        top.set_style_pad_all(0, 0)
        top.set_layout(lv.LAYOUT.FLEX)
        top.set_flex_flow(lv.FLEX_FLOW.ROW)
        top.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        top.set_style_pad_column(PAD_XS, 0)

        # Sig type icon
        if wallet.isMultiSig:
            ico = lv.image(top)
            BTC_ICONS.TWO_KEYS(ORANGE_HEX).add_to_parent(ico, zoom=110)
        elif not is_default:
            ico = lv.image(top)
            BTC_ICONS.KEY(CYAN_HEX).add_to_parent(ico, zoom=110)

        # Name (clickable to rename)
        name = lv.label(top)
        name.set_text(wallet.label)
        name.set_style_text_font(lv.font_montserrat_16, 0)
        name.set_style_text_color(WHITE_HEX, 0)
        name.set_flex_grow(1)

        # Companion app indicators
        if wallet.shared_with:
            for i, app in enumerate(wallet.shared_with[:2]):
                dot = lv.label(top)
                dot.set_text("\xE2\x97\x8F")
                dot.set_style_text_font(lv.font_montserrat_12, 0)
                dot.set_style_text_color(GREEN_HEX, 0)

        # Delete button (only in Wallet Menu, not for default)
        if not is_default:
            del_btn = lv.button(top)
            del_btn.set_size(28, 28)
            del_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            del_btn.set_style_border_width(0, 0)
            del_btn.set_style_shadow_width(0, 0)
            del_ico = lv.image(del_btn)
            BTC_ICONS.TRASH(RED_HEX).add_to_parent(del_ico, zoom=100)
            del_ico.center()
            del_btn.add_event_cb(lambda e, w=wallet: self._delete(w), lv.EVENT.CLICKED, None)

        # Bottom line: three parameters clearly shown
        bottom = lv.obj(card)
        bottom.set_size(lv.pct(100), 22)
        bottom.set_style_bg_opa(lv.OPA.TRANSP, 0)
        bottom.set_style_border_width(0, 0)
        bottom.set_style_pad_all(0, 0)
        bottom.set_layout(lv.LAYOUT.FLEX)
        bottom.set_flex_flow(lv.FLEX_FLOW.ROW)
        bottom.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        bottom.set_style_pad_column(PAD_SM, 0)
        bottom.align_to(top, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 2)

        if is_default:
            detail = lv.label(bottom)
            detail.set_text("Native Segwit | Single Sig | Acc 0")
            detail.set_style_text_font(lv.font_montserrat_12, 0)
            detail.set_style_text_color(GREY_LIGHT_HEX, 0)
        else:
            # Address type
            addr_name, addr_color = _ADDR_LABELS.get(wallet.address_type, ("Segwit", CYAN_HEX))
            at = lv.label(bottom)
            at.set_text(addr_name)
            at.set_style_text_font(lv.font_montserrat_12, 0)
            at.set_style_text_color(addr_color, 0)

            sep1 = lv.label(bottom)
            sep1.set_text("|")
            sep1.set_style_text_font(lv.font_montserrat_12, 0)
            sep1.set_style_text_color(GREY_LIGHT_HEX, 0)

            # Sig type
            sig = lv.label(bottom)
            if wallet.isMultiSig and wallet.threshold:
                sig.set_text(str(wallet.threshold) + "-of-" + str(len(wallet.required_fingerprints)))
                sig.set_style_text_color(ORANGE_HEX, 0)
            else:
                sig.set_text("Single Sig")
                sig.set_style_text_color(WHITE_HEX, 0)
            sig.set_style_text_font(lv.font_montserrat_12, 0)

            sep2 = lv.label(bottom)
            sep2.set_text("|")
            sep2.set_style_text_font(lv.font_montserrat_12, 0)
            sep2.set_style_text_color(GREY_LIGHT_HEX, 0)

            # Account
            acc = lv.label(bottom)
            acc.set_text("Acc " + str(wallet.account))
            acc.set_style_text_font(lv.font_montserrat_12, 0)
            acc.set_style_text_color(CYAN_HEX, 0)

        # Click to select, long-press for details
        card.add_flag(lv.obj.FLAG.CLICKABLE)
        card.add_event_cb(lambda e, w=wallet: self._select(w), lv.EVENT.CLICKED, None)
        card.add_event_cb(lambda e, w=wallet: self._long_press(w), lv.EVENT.LONG_PRESSED, None)

    def _select(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("main")

    def _long_press(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("wallet_details")

    def _delete(self, wallet):
        """Show confirmation dialog before deleting wallet."""
        from ..basic.modal_overlay import ModalOverlay

        self._modal = ModalOverlay(bg_opa=200)
        overlay = self._modal.overlay

        dialog = lv.obj(overlay)
        dialog.set_size(360, 200)
        dialog.set_style_bg_color(BG_CARD_HEX, 0)
        dialog.set_style_bg_opa(lv.OPA.COVER, 0)
        dialog.set_style_radius(12, 0)
        dialog.set_style_border_width(0, 0)
        dialog.set_style_pad_all(PAD_LG, 0)
        dialog.center()

        dialog.set_layout(lv.LAYOUT.FLEX)
        dialog.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        dialog.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        dialog.set_style_pad_row(PAD_MD, 0)

        title = lv.label(dialog)
        title.set_text("Delete \"" + wallet.label + "\"?")
        title.set_style_text_font(lv.font_montserrat_16, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        warn = lv.label(dialog)
        warn.set_text("This cannot be undone.")
        warn.set_style_text_font(lv.font_montserrat_12, 0)
        warn.set_style_text_color(GREY_LIGHT_HEX, 0)

        del_btn = lv.button(dialog)
        del_btn.set_size(lv.pct(100), 44)
        del_btn.set_style_bg_color(RED_HEX, 0)
        del_btn.set_style_radius(8, 0)
        del_btn.set_style_border_width(0, 0)
        del_btn.set_style_shadow_width(0, 0)
        del_lbl = lv.label(del_btn)
        del_lbl.set_text("Delete")
        del_lbl.set_style_text_color(WHITE_HEX, 0)
        del_lbl.center()
        del_btn.add_event_cb(lambda e, w=wallet: self._confirm_delete(w), lv.EVENT.CLICKED, None)

        cancel_btn = lv.button(dialog)
        cancel_btn.set_size(lv.pct(100), 40)
        cancel_btn.set_style_bg_color(BG_ELEVATED_HEX, 0)
        cancel_btn.set_style_radius(8, 0)
        cancel_btn.set_style_border_width(0, 0)
        cancel_btn.set_style_shadow_width(0, 0)
        cancel_lbl = lv.label(cancel_btn)
        cancel_lbl.set_text("Cancel")
        cancel_lbl.set_style_text_color(GREY_LIGHT_HEX, 0)
        cancel_lbl.center()
        cancel_btn.add_event_cb(lambda e: self._close_modal(), lv.EVENT.CLICKED, None)

    def _confirm_delete(self, wallet):
        self._close_modal()
        self.gui.specter_state.remove_wallet(wallet)
        self.gui.show_menu("wallet_menu")

    def _close_modal(self):
        if hasattr(self, '_modal') and self._modal:
            self._modal.close()
            self._modal = None
