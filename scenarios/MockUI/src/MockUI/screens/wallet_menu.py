"""Wallet Menu: full-screen with structured wallet grouping.
Heading = Wallet Type (Single Sig / Multi Sig / Miniskript)
Subheading = Address Type (Native Segwit / Legacy / Taproot)
Includes seed dropdown at top. Long-press for options including delete."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX,
    RED_HEX, GREEN_HEX, ORANGE_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.modal_overlay import ModalOverlay
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT


_ADDR_NAMES = {
    ADDR_NATIVE_SEGWIT: "Native Segwit",
    ADDR_NESTED_SEGWIT: "Nested Segwit",
    ADDR_LEGACY: "Legacy",
    ADDR_TAPROOT: "Taproot",
}
_ADDR_ORDER = {ADDR_NATIVE_SEGWIT: 0, ADDR_NESTED_SEGWIT: 1, ADDR_LEGACY: 2, ADDR_TAPROOT: 3}


def _build_grouped(wallets):
    """Build hierarchy: Wallet Type → Address Type → wallets.
    Returns [(type_heading, [(addr_heading, [wallets])])]"""
    # Separate by wallet type
    singlesig = []
    multisig = []
    miniskript = []
    for w in wallets:
        if w.is_default_wallet():
            continue
        if not w.is_standard():
            miniskript.append(w)
        elif w.isMultiSig:
            multisig.append(w)
        else:
            singlesig.append(w)

    result = []

    # Single Sig group
    if singlesig:
        addr_groups = {}
        for w in singlesig:
            at = w.address_type or ADDR_NATIVE_SEGWIT
            if at not in addr_groups:
                addr_groups[at] = []
            addr_groups[at].append(w)
        for at in addr_groups:
            addr_groups[at].sort(key=lambda w: w.account)
        sub = []
        for at in sorted(addr_groups.keys(), key=lambda t: _ADDR_ORDER.get(t, 99)):
            sub.append((_ADDR_NAMES.get(at, "Other"), addr_groups[at]))
        result.append(("Single Sig", sub))

    # Multi Sig group
    if multisig:
        addr_groups = {}
        for w in multisig:
            at = w.address_type or ADDR_NATIVE_SEGWIT
            if at not in addr_groups:
                addr_groups[at] = []
            addr_groups[at].append(w)
        for at in addr_groups:
            addr_groups[at].sort(key=lambda w: w.account)
        sub = []
        for at in sorted(addr_groups.keys(), key=lambda t: _ADDR_ORDER.get(t, 99)):
            label = _ADDR_NAMES.get(at, "Other")
            for w in addr_groups[at]:
                if w.threshold:
                    label = str(w.threshold) + "/" + str(len(w.required_fingerprints)) + " " + label
                    break
            sub.append((label, addr_groups[at]))
        result.append(("Multi Sig", sub))

    # Miniskript group
    if miniskript:
        result.append(("Miniskript", [("Custom", miniskript)]))

    return result


class WalletMenu(lv.obj):
    """Full wallet management with type heading / address subheading structure."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self._modal = None

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_XS, 0)

        state = gui.specter_state

        # Seed dropdown at top of wallet menu
        seed_row = lv.obj(self)
        seed_row.set_size(lv.pct(100), 36)
        seed_row.set_style_bg_color(BG_CARD_HEX, 0)
        seed_row.set_style_bg_opa(lv.OPA.COVER, 0)
        seed_row.set_style_radius(8, 0)
        seed_row.set_style_border_width(0, 0)
        seed_row.set_style_pad_left(PAD_MD, 0)
        seed_row.add_flag(lv.obj.FLAG.CLICKABLE)

        seed_ico = lv.image(seed_row)
        BTC_ICONS.KEY(CYAN_HEX).add_to_parent(seed_ico, zoom=100)
        seed_ico.align(lv.ALIGN.LEFT_MID, 0, 0)

        seed_name = state.active_seed.label if state.active_seed else "No seed"
        if state.active_seed and state.active_seed.passphrase:
            seed_name = seed_name + " + PP"
        seed_lbl = lv.label(seed_row)
        seed_lbl.set_text("Wallets from: " + seed_name)
        seed_lbl.set_style_text_font(lv.font_montserrat_16, 0)
        seed_lbl.set_style_text_color(CYAN_HEX, 0)
        seed_lbl.align(lv.ALIGN.LEFT_MID, 30, 0)

        arrow = lv.label(seed_row)
        arrow.set_text(lv.SYMBOL.DOWN)
        arrow.set_style_text_color(GREY_LIGHT_HEX, 0)
        arrow.align(lv.ALIGN.RIGHT_MID, -PAD_SM, 0)

        seed_row.add_event_cb(lambda e: gui.show_menu("seed_management"), lv.EVENT.CLICKED, None)

        # Build grouped wallet list
        wallets = state.wallets_for_seed(state.active_seed) or state.registered_wallets
        groups = _build_grouped(wallets)

        if not groups:
            empty = lv.label(self)
            empty.set_text("No wallets registered")
            empty.set_style_text_color(GREY_LIGHT_HEX, 0)
            return

        for type_heading, addr_groups in groups:
            # === TYPE HEADING (big) ===
            th = lv.label(self)
            th.set_text(type_heading)
            th.set_style_text_font(lv.font_montserrat_22, 0)
            th.set_style_text_color(WHITE_HEX, 0)

            for addr_heading, group_wallets in addr_groups:
                # === ADDRESS SUBHEADING (small) ===
                ah = lv.label(self)
                ah.set_text(addr_heading)
                ah.set_style_text_font(lv.font_montserrat_12, 0)
                ah.set_style_text_color(GREY_LIGHT_HEX, 0)

                for w in group_wallets:
                    self._add_wallet_row(w)

    def _add_wallet_row(self, wallet):
        state = self.gui.specter_state
        is_active = state.active_wallet is wallet

        row = lv.button(self)
        row.set_size(lv.pct(100), 44)
        row.set_style_bg_color(BG_ELEVATED_HEX if is_active else BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_shadow_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
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

        # Account
        acc = lv.label(row)
        acc.set_text("Acc" + str(wallet.account))
        acc.set_style_text_font(lv.font_montserrat_12, 0)
        acc.set_style_text_color(CYAN_HEX, 0)

        # Name
        name = lv.label(row)
        name.set_text(wallet.label)
        name.set_style_text_font(lv.font_montserrat_16, 0)
        name.set_style_text_color(WHITE_HEX, 0)
        name.set_flex_grow(1)

        # Companion app logos (bigger)
        if wallet.shared_with:
            from ..basic.wallet_list import _get_app_icon
            for i, app in enumerate(wallet.shared_with[:3]):
                app_ico = lv.image(row)
                icon = _get_app_icon(app)
                if icon:
                    icon.add_to_parent(app_ico, zoom=100)

        # Click → wallet info
        row.add_event_cb(lambda e, w=wallet: self._open_wallet(w), lv.EVENT.CLICKED, None)
        # Long-press → options dropdown
        row.add_event_cb(lambda e, w=wallet: self._long_press(w), lv.EVENT.LONG_PRESSED, None)

    def _open_wallet(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("wallet_info")

    def _long_press(self, wallet):
        self._modal = ModalOverlay(bg_opa=200)
        overlay = self._modal.overlay

        dialog = lv.obj(overlay)
        dialog.set_size(360, lv.SIZE_CONTENT)
        dialog.set_style_bg_color(BG_CARD_HEX, 0)
        dialog.set_style_bg_opa(lv.OPA.COVER, 0)
        dialog.set_style_radius(12, 0)
        dialog.set_style_border_width(0, 0)
        dialog.set_style_pad_all(PAD_MD, 0)
        dialog.set_style_pad_row(PAD_SM, 0)
        dialog.center()
        dialog.set_layout(lv.LAYOUT.FLEX)
        dialog.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        title = lv.label(dialog)
        title.set_text(wallet.label)
        title.set_style_text_font(lv.font_montserrat_16, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        self._dd_opt(dialog, "Wallet Details", lambda: self._nav(wallet, "wallet_info"))
        self._dd_opt(dialog, "Receive Addresses", lambda: self._nav(wallet, "receive"))
        self._dd_opt(dialog, "Export Wallet", lambda: self._nav(wallet, "export"))
        self._dd_opt(dialog, "Connect App", lambda: self._nav(wallet, "connect_app"))
        if not wallet.is_default_wallet():
            self._dd_opt(dialog, "Delete Wallet", lambda: self._delete(wallet), color=RED_HEX)
        self._dd_opt(dialog, "Cancel", self._close_modal, color=GREY_LIGHT_HEX)

    def _dd_opt(self, parent, text, callback, color=None):
        btn = lv.button(parent)
        btn.set_size(lv.pct(100), 40)
        btn.set_style_bg_color(BG_ELEVATED_HEX, 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(6, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_16, 0)
        lbl.set_style_text_color(color if color else WHITE_HEX, 0)
        lbl.center()
        btn.add_event_cb(lambda e: callback(), lv.EVENT.CLICKED, None)

    def _nav(self, wallet, target):
        self._close_modal()
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu(target)

    def _delete(self, wallet):
        self._close_modal()
        self._modal = ModalOverlay(bg_opa=200)
        d = lv.obj(self._modal.overlay)
        d.set_size(340, 180)
        d.set_style_bg_color(BG_CARD_HEX, 0)
        d.set_style_bg_opa(lv.OPA.COVER, 0)
        d.set_style_radius(12, 0)
        d.set_style_border_width(0, 0)
        d.set_style_pad_all(PAD_MD, 0)
        d.set_style_pad_row(PAD_SM, 0)
        d.center()
        d.set_layout(lv.LAYOUT.FLEX)
        d.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        d.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        t = lv.label(d)
        t.set_text("Delete \"" + wallet.label + "\"?")
        t.set_style_text_font(lv.font_montserrat_16, 0)
        t.set_style_text_color(WHITE_HEX, 0)

        db = lv.button(d)
        db.set_size(lv.pct(100), 44)
        db.set_style_bg_color(RED_HEX, 0)
        db.set_style_radius(8, 0)
        db.set_style_border_width(0, 0)
        db.set_style_shadow_width(0, 0)
        dl = lv.label(db)
        dl.set_text("Delete")
        dl.set_style_text_color(WHITE_HEX, 0)
        dl.center()
        db.add_event_cb(lambda e, w=wallet: self._confirm_del(w), lv.EVENT.CLICKED, None)

        cb = lv.button(d)
        cb.set_size(lv.pct(100), 38)
        cb.set_style_bg_color(BG_ELEVATED_HEX, 0)
        cb.set_style_radius(8, 0)
        cb.set_style_border_width(0, 0)
        cb.set_style_shadow_width(0, 0)
        cl = lv.label(cb)
        cl.set_text("Cancel")
        cl.set_style_text_color(GREY_LIGHT_HEX, 0)
        cl.center()
        cb.add_event_cb(lambda e: self._close_modal(), lv.EVENT.CLICKED, None)

    def _confirm_del(self, wallet):
        self._close_modal()
        self.gui.specter_state.remove_wallet(wallet)
        self.gui.show_menu("wallet_menu")

    def _close_modal(self):
        if self._modal:
            self._modal.close()
            self._modal = None
