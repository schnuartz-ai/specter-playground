from ..basic.templates.menu import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.utils.ui_consts import BLUE_HEX
from ..basic.widgets import MenuItem


def make_add_seed_items(t, state, sizes=None, generate_size=1):
    """Build the full 'Add Seed' menu block.

    Returns the Generate section header + 'Generate Seedphrase' row + Import
    section header + the conditional SmartCard / QR / Keyboard / SD / Flash
    import-source rows. Used by `AddSeedMenu.get_menu_items` and
    `MainMenu._items_no_seed`.

    ``sizes`` is an optional dict mapping import-source name to size multiplier
    (keys: ``smartcard``, ``qr``, ``keyboard``, ``sd``, ``flash``); missing keys
    default to 1. ``generate_size`` sizes the 'Generate Seedphrase' row.
    """
    sizes = sizes or {}
    items = [
        MenuItem(text=t("ADD_SEED_GENERATE_SECTION")),
        MenuItem(BTC_ICONS.DICE, t("ADD_SEED_GENERATE_SEED"), "generate_seedphrase",
                 size=generate_size, is_submenu=True),
        MenuItem(text=t("ADD_SEED_IMPORT_SECTION")),
    ]
    if state.SmartCard_hasSeed():
        items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "import_from_smartcard", size=sizes.get("smartcard", 2.45), color=BLUE_HEX, is_submenu=True))
    if state.QR_enabled():
        items.append(MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), "import_from_qr", size=sizes.get("qr", 1), width_pct=48))
    items.append(MenuItem(BTC_ICONS.KEYBOARD, t("COMMON_KEYBOARD"), "import_from_keyboard", size=sizes.get("keyboard", 1), width_pct=48 if state.QR_enabled() else 100))
    if state.SD_hasSeed():
        items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "import_from_sd", size=sizes.get("sd", 1)))
    if state.Flash_hasSeed():
        items.append(MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "import_from_flash", size=sizes.get("flash", 1)))
    return items


class AddSeedMenu(GenericMenu):
    """Menu to create or import a MasterKey (seedphrase).

    menu_id: "add_seed"
    """

    TITLE_KEY = None
    SHOW_TITLE = False
    NO_TITLE_SPACER = True
    ROW_HEIGHT = 78
    ROW_GAP = 14

    def get_menu_items(self, t, state):
        return make_add_seed_items(t, state)
