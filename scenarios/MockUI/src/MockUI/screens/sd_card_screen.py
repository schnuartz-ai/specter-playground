"""SD Card screen: file browser with type-coded entries."""
import lvgl as lv
from ..basic.ui_consts import (
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, ORANGE_HEX, GREEN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


# Mock SD card file entries
_MOCK_FILES = [
    ("transaction_01.psbt", "transaction", "2.1 KB"),
    ("wallet_backup.json", "descriptor", "0.8 KB"),
    ("my_address.txt", "address", "0.1 KB"),
    ("multisig_tx.psbt", "transaction", "4.3 KB"),
    ("sparrow_wallet.json", "descriptor", "1.2 KB"),
]

_TYPE_CONFIG = {
    "transaction": (BTC_ICONS.TRANSACTIONS, ORANGE_HEX, "PSBT"),
    "descriptor": (BTC_ICONS.WALLET, CYAN_HEX, "Descriptor"),
    "address": (BTC_ICONS.RECEIVE, GREEN_HEX, "Address"),
}


class SDCardScreen(lv.obj):
    """SD Card file browser with type-coded entries."""

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
        title.set_text("SD Card")
        title.set_style_text_font(lv.font_montserrat_22, 0)
        title.set_style_text_color(WHITE_HEX, 0)

        # Check if SD is detected
        if not self.gui.specter_state.SD_detected():
            no_sd = lv.label(self)
            no_sd.set_text("No SD card detected")
            no_sd.set_style_text_color(GREY_LIGHT_HEX, 0)
            no_sd.set_style_text_font(lv.font_montserrat_16, 0)
            return

        # File list sorted by type
        sorted_files = sorted(_MOCK_FILES, key=lambda f: list(_TYPE_CONFIG.keys()).index(f[1]))

        for filename, filetype, size in sorted_files:
            self._add_file_row(filename, filetype, size)

    def _add_file_row(self, filename, filetype, size):
        icon, color, type_label = _TYPE_CONFIG.get(filetype, (BTC_ICONS.FILE, WHITE_HEX, "File"))

        row = lv.button(self)
        row.set_size(lv.pct(100), 54)
        row.set_style_bg_color(BG_CARD_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_shadow_width(0, 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_SM, 0)
        row.set_style_pad_left(PAD_SM, 0)

        # Type icon (color-coded)
        ico = lv.image(row)
        icon(color).add_to_parent(ico, zoom=130)

        # File info column
        info_col = lv.obj(row)
        info_col.set_size(lv.SIZE_CONTENT, lv.SIZE_CONTENT)
        info_col.set_style_bg_opa(lv.OPA.TRANSP, 0)
        info_col.set_style_border_width(0, 0)
        info_col.set_style_pad_all(0, 0)
        info_col.set_flex_grow(1)

        name_lbl = lv.label(info_col)
        name_lbl.set_text(filename)
        name_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        name_lbl.set_style_text_color(WHITE_HEX, 0)
        name_lbl.align(lv.ALIGN.TOP_LEFT, 0, 0)

        detail_lbl = lv.label(info_col)
        detail_lbl.set_text(type_label + " | " + size)
        detail_lbl.set_style_text_font(lv.font_montserrat_12, 0)
        detail_lbl.set_style_text_color(color, 0)
        detail_lbl.align_to(name_lbl, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 2)

        # Click to process file
        row.add_event_cb(lambda e, fn=filename, ft=filetype: self._process_file(fn, ft), lv.EVENT.CLICKED, None)
        # Long press to delete
        row.add_event_cb(lambda e, fn=filename: self._long_press(fn), lv.EVENT.LONG_PRESSED, None)

    def _process_file(self, filename, filetype):
        if filetype == "transaction":
            self.gui.show_menu("signing")
        elif filetype == "descriptor":
            # Add wallet flow
            self.gui.show_menu("add_wallet")
        elif filetype == "address":
            # Verify address
            self.gui.show_menu("verify_address")

    def _long_press(self, filename):
        """Show delete option via modal overlay."""
        from ..basic.modal_overlay import ModalOverlay
        from ..basic.ui_consts import BG_CARD_HEX, BG_ELEVATED_HEX, WHITE_HEX, RED_HEX, GREY_LIGHT_HEX

        self._modal = ModalOverlay(bg_opa=200)
        overlay = self._modal.overlay

        dialog = lv.obj(overlay)
        dialog.set_size(350, 180)
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
        title.set_text("Delete " + filename + "?")
        title.set_style_text_font(lv.font_montserrat_16, 0)
        title.set_style_text_color(WHITE_HEX, 0)

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
        del_btn.add_event_cb(lambda e: self._confirm_delete(filename), lv.EVENT.CLICKED, None)

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

    def _confirm_delete(self, filename):
        self._close_modal()
        # In real implementation, delete from SD card
        # For mock, just refresh the screen
        self.gui.show_menu("sd_card")

    def _close_modal(self):
        if hasattr(self, '_modal') and self._modal:
            self._modal.close()
            self._modal = None
