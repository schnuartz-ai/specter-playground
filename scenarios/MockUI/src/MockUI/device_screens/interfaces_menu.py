import lvgl as lv

from ..basic.templates.menu import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.utils.ui_consts import (
    BLUE_HEX,
    CARD_HEX,
    FRAME_HEX,
    WHITE_HEX,
    TEXT_FONT,
    SMALL_TEXT_FONT,
)
from ..basic.widgets.containers import flex_row
from ..basic.widgets.icon_widgets import make_icon
from ..basic.widgets.labels import body_label
from ..basic.utils.ui_utils import configure_flex


class InterfacesMenu(GenericMenu):
    """Menu to enable/disable hardware interfaces."""

    TITLE_KEY = "MENU_ENABLE_DISABLE_INTERFACES"
    ROW_HEIGHT = 92
    ROW_GAP = 14

    def fill_body(self):
        self.body.set_style_pad_left(24, 0)
        self.body.set_style_pad_right(24, 0)
        self.body.set_style_pad_row(self.ROW_GAP, 0)
        self._build_interface_rows()
        self._configure_scroll()

    def rebuild_body(self):
        from ..basic.utils.ui_utils import delete_all_children_of
        delete_all_children_of(self.body)
        self.fill_body()

    def _interfaces(self):
        state = self.device_state
        t = self.t
        items = []
        if state.hasQR():
            items.append((BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), state.QR_enabled, state.set_QR_enabled))
        if state.hasUSB():
            items.append((BTC_ICONS.USB, t("HARDWARE_USB"), state.USB_enabled, state.set_USB_enabled))
        if state.hasSD():
            items.append((BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), state.SD_enabled, state.set_SD_enabled))
        if state.hasSmartCard():
            items.append((BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), state.SmartCard_enabled, state.set_SmartCard_enabled))
        return items

    def _build_interface_rows(self):
        for icon, label, getter, setter in self._interfaces():
            self._build_interface_row(icon, label, bool(getter()), setter)

    def _build_interface_row(self, icon, label, enabled, setter):
        row = lv.obj(self.body)
        try:
            row.remove_style_all()
        except AttributeError:
            pass
        row.set_width(lv.pct(100))
        row.set_height(self.ROW_HEIGHT)
        row.set_layout(lv.LAYOUT.FLEX)
        configure_flex(row, flow=lv.FLEX_FLOW.ROW, main=lv.FLEX_ALIGN.START)
        row.set_style_bg_color(CARD_HEX if enabled else FRAME_HEX, 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(18, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(18, 0)
        row.set_style_pad_right(18, 0)
        row.set_style_pad_column(14, 0)
        row.add_flag(lv.obj.FLAG.CLICKABLE)

        icon_bg = lv.obj(row)
        try:
            icon_bg.remove_style_all()
        except AttributeError:
            pass
        icon_bg.set_size(50, 50)
        icon_bg.set_style_bg_color(BLUE_HEX if enabled else CARD_HEX, 0)
        icon_bg.set_style_bg_opa(lv.OPA.COVER, 0)
        icon_bg.set_style_radius(13, 0)
        icon_bg.set_style_border_width(0, 0)
        icon_bg.set_style_pad_all(0, 0)
        icon_bg.remove_flag(lv.obj.FLAG.CLICKABLE)
        make_icon(icon_bg, icon, WHITE_HEX).center()

        text_col = flex_row(row, width=184, height=lv.pct(100), main_align=lv.FLEX_ALIGN.START)
        text_col.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        text_col.set_style_pad_row(2, 0)
        title = body_label(text_col, label, width=184, align=lv.TEXT_ALIGN.LEFT, font=TEXT_FONT)
        title.set_style_text_color(WHITE_HEX, 0)
        status = body_label(
            text_col,
            "Enabled" if enabled else "Disabled",
            width=184,
            align=lv.TEXT_ALIGN.LEFT,
            font=SMALL_TEXT_FONT,
        )
        status.set_style_text_color(WHITE_HEX if enabled else CARD_HEX, 0)

        pill = lv.obj(row)
        try:
            pill.remove_style_all()
        except AttributeError:
            pass
        pill.set_size(92, 42)
        pill.set_style_bg_color(BLUE_HEX if enabled else CARD_HEX, 0)
        pill.set_style_bg_opa(lv.OPA.COVER, 0)
        pill.set_style_radius(21, 0)
        pill.set_style_border_width(2, 0)
        pill.set_style_border_color(BLUE_HEX if enabled else WHITE_HEX, 0)
        pill.remove_flag(lv.obj.FLAG.CLICKABLE)

        pill_text = body_label(
            pill,
            "ON" if enabled else "OFF",
            width=lv.pct(100),
            align=lv.TEXT_ALIGN.CENTER,
            font=SMALL_TEXT_FONT,
        )
        pill_text.center()

        def _cb(e):
            if e.get_code() != lv.EVENT.CLICKED:
                return
            setter(not enabled)
            self.rebuild_body()
            self.gui.refresh_ui()

        row.add_event_cb(_cb, lv.EVENT.CLICKED, None)
