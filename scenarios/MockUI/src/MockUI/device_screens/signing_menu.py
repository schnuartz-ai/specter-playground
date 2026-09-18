"""Minimal PSBT hand-off view used by the SD-card browser."""

from ..basic import GenericMenu, MenuItem, t
from ..basic.symbol_lib import BTC_ICONS


class SigningMenu(GenericMenu):
    TITLE_KEY = "SD_CARD_SIGNING_TITLE"

    def get_menu_items(self):
        filename = self.device_state.pending_psbt
        return [
            MenuItem(text=t("SD_CARD_SIGNING_FILE") % (filename or "-")),
            MenuItem(text=t("SD_CARD_SIGNING_READY")),
            MenuItem(BTC_ICONS.CARET_LEFT, t("ACTION_SCREEN_BACK"), "back"),
        ]
