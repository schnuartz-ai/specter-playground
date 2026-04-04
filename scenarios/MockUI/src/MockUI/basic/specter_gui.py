"""Root GUI controller for the new Specter DIY clean interface."""
import lvgl as lv

from ..stubs import UIState, SpecterState
from ..i18n import I18nManager
from .top_bar import TopBar
from .seed_dropdown import SeedDropdown
from .wallet_list import WalletList
from .action_buttons import ActionButtons
from .nav_bar import NavBar
from .keyboard_manager import KeyboardManager
from .ui_consts import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TOP_BAR_HEIGHT, SEED_DROPDOWN_HEIGHT, WALLET_SECTION_HEIGHT, NAV_BAR_HEIGHT,
    BG_BLACK_HEX, WHITE_HEX,
)


# Content area geometry
_DASHBOARD_Y = TOP_BAR_HEIGHT + SEED_DROPDOWN_HEIGHT + WALLET_SECTION_HEIGHT
_DASHBOARD_H = SCREEN_HEIGHT - _DASHBOARD_Y - NAV_BAR_HEIGHT
_FULLSCREEN_Y = TOP_BAR_HEIGHT
_FULLSCREEN_H = SCREEN_HEIGHT - TOP_BAR_HEIGHT - NAV_BAR_HEIGHT


class SpecterGui(lv.obj):
    """Main GUI controller.

    Dashboard mode: TopBar + SeedDropdown + WalletList + ActionButtons + NavBar
    Fullscreen mode: TopBar + [full-height content] + NavBar
    """

    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_scroll_dir(lv.DIR.NONE)
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)

        self.on_navigate = self.show_menu

        # State
        self.i18n = I18nManager()
        self.specter_state = specter_state if specter_state else SpecterState()
        self.ui_state = ui_state if ui_state else UIState()

        self.current_screen = None
        self.keyboard_manager = KeyboardManager(self)

        # === Persistent elements ===

        # Top bar (always visible)
        self.top_bar = TopBar(self)
        self.top_bar.set_pos(0, 0)

        # Dashboard-only elements (hidden when on sub-screens)
        self.seed_dropdown = SeedDropdown(self)
        self.seed_dropdown.set_pos(0, TOP_BAR_HEIGHT)

        self.wallet_list = WalletList(self)
        self.wallet_list.set_pos(0, TOP_BAR_HEIGHT + SEED_DROPDOWN_HEIGHT)

        # Content area (resized dynamically)
        self.content = lv.obj(self)
        self.content.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.content.set_style_border_width(0, 0)
        self.content.set_style_radius(0, 0)
        self.content.set_style_pad_all(0, 0)
        self.content.set_scroll_dir(lv.DIR.VER)

        # Bottom nav (always visible)
        self.nav_bar = NavBar(self)

        # Show main dashboard
        self.show_menu("main")

        # Periodic refresh
        def _tick(timer):
            self.refresh_ui()
        lv.timer_create(_tick, 30_000, None)

    def change_language(self, lang_code):
        self.i18n.set_language(lang_code)

    def refresh_ui(self):
        self.top_bar.refresh(self.specter_state)
        if not self.seed_dropdown.has_flag(lv.obj.FLAG.HIDDEN):
            self.seed_dropdown.refresh()

    def refresh_dashboard(self):
        self.seed_dropdown.refresh()
        self.wallet_list.refresh()

    def show_menu(self, target_menu_id=None):
        """Navigate to a menu/screen by ID."""
        # Clean up current screen
        if self.current_screen:
            self.current_screen.delete()
            self.current_screen = None

        # Update navigation history
        if target_menu_id is None:
            self.ui_state.pop_menu()
        elif target_menu_id == "main":
            self.ui_state.clear_history()
            self.ui_state.current_menu_id = "main"
        else:
            self.ui_state.push_menu(target_menu_id)

        # Handle locked state
        if self.specter_state.is_locked:
            self.ui_state.clear_history()
            self.ui_state.current_menu_id = "locked"
            self._enter_fullscreen()
            self._load_screen("locked")
            return

        current = self.ui_state.current_menu_id

        if current == "main":
            self._enter_dashboard()
        else:
            self._enter_fullscreen()
            self._load_screen(current)

    def _enter_dashboard(self):
        """Show dashboard layout: seed dropdown + wallet list + action buttons."""
        self.seed_dropdown.remove_flag(lv.obj.FLAG.HIDDEN)
        self.wallet_list.remove_flag(lv.obj.FLAG.HIDDEN)
        self.wallet_list.refresh()
        self.seed_dropdown.refresh()

        # Position content below wallet list
        self.content.set_size(SCREEN_WIDTH, _DASHBOARD_H)
        self.content.set_pos(0, _DASHBOARD_Y)

        self.current_screen = ActionButtons(self, self.content)
        self.refresh_ui()

    def _enter_fullscreen(self):
        """Hide dashboard elements and expand content to full height."""
        self.seed_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
        self.wallet_list.add_flag(lv.obj.FLAG.HIDDEN)

        # Content fills everything between top bar and nav bar
        self.content.set_size(SCREEN_WIDTH, _FULLSCREEN_H)
        self.content.set_pos(0, _FULLSCREEN_Y)

    def _load_screen(self, screen_id):
        """Load a screen into the content area."""
        from ..screens import get_screen_class

        screen_cls = get_screen_class(screen_id)
        if screen_cls:
            self.current_screen = screen_cls(self, self.content)
        else:
            self._show_placeholder(screen_id)
        self.refresh_ui()

    def _show_placeholder(self, menu_id):
        """Placeholder for unimplemented screens."""
        self.current_screen = lv.obj(self.content)
        self.current_screen.set_size(lv.pct(100), lv.pct(100))
        self.current_screen.set_style_bg_color(BG_BLACK_HEX, 0)
        self.current_screen.set_style_bg_opa(lv.OPA.COVER, 0)
        self.current_screen.set_style_border_width(0, 0)

        lbl = lv.label(self.current_screen)
        title = (menu_id or "").replace("_", " ").title()
        lbl.set_text(title)
        lbl.set_style_text_color(WHITE_HEX, 0)
        lbl.set_style_text_font(lv.font_montserrat_22, 0)
        lbl.center()
