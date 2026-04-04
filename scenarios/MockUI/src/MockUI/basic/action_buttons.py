"""Three main action buttons: Receive, Scan (large), SD Card."""
import lvgl as lv
from .ui_consts import (
    SCREEN_WIDTH, BTN_SMALL_HEIGHT, BTN_LARGE_HEIGHT, BTN_RADIUS,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, CYAN_HEX, CYAN_DARK_HEX, WHITE_HEX,
    BTC_ICON_ZOOM,
)
from .symbol_lib import BTC_ICONS


class ActionButtons(lv.obj):
    """Three vertically stacked action buttons: Receive, Scan (larger), SD Card."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui

        self.set_width(SCREEN_WIDTH)
        self.set_height(lv.SIZE_CONTENT)
        self.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(PAD_SM, 0)
        self.set_style_pad_bottom(PAD_SM, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_SM, 0)

        # Receive button (normal size)
        self._make_btn(
            "Receive",
            BTC_ICONS.RECEIVE,
            BTN_SMALL_HEIGHT,
            self._receive_cb,
        )

        # Scan button (LARGER)
        self._make_btn(
            "Scan",
            BTC_ICONS.QR_CODE,
            BTN_LARGE_HEIGHT,
            self._scan_cb,
            is_primary=True,
        )

        # SD Card button (normal size)
        self._make_btn(
            "SD Card",
            BTC_ICONS.SD_CARD,
            BTN_SMALL_HEIGHT,
            self._sd_cb,
        )

    def _make_btn(self, text, icon, height, callback, is_primary=False):
        btn = lv.button(self)
        btn.set_size(SCREEN_WIDTH - 2 * PAD_MD, height)
        btn.set_style_radius(BTN_RADIUS, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        if is_primary:
            btn.set_style_bg_color(CYAN_HEX, 0)
            btn.set_style_bg_color(CYAN_DARK_HEX, lv.PART.MAIN | lv.STATE.PRESSED)
            txt_color = WHITE_HEX
        else:
            btn.set_style_bg_color(BG_CARD_HEX, 0)
            txt_color = WHITE_HEX

        btn.set_style_bg_opa(lv.OPA.COVER, 0)

        # Layout: icon + text centered
        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)

        ico = lv.image(btn)
        zoom = 200 if is_primary else 170
        icon(txt_color).add_to_parent(ico, zoom=zoom)

        lbl = lv.label(btn)
        lbl.set_text(text)
        font = lv.font_montserrat_22 if is_primary else lv.font_montserrat_16
        lbl.set_style_text_font(font, 0)
        lbl.set_style_text_color(txt_color, 0)

        btn.add_event_cb(callback, lv.EVENT.CLICKED, None)
        return btn

    def _receive_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("receive")

    def _scan_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("scan")

    def _sd_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("sd_card")
