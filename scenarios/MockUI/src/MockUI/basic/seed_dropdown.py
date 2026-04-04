"""Seed dropdown: shows active seed name, tap to switch between loaded seeds."""
import lvgl as lv
from .ui_consts import (
    SEED_DROPDOWN_HEIGHT, SCREEN_WIDTH, PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX,
    FONT_BODY, FONT_SMALL,
)
from .modal_overlay import ModalOverlay


class SeedDropdown(lv.obj):
    """Dropdown showing the currently active seed. Tap to switch seeds."""

    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui
        self._dropdown_open = False
        self._modal = None

        self.set_size(SCREEN_WIDTH, SEED_DROPDOWN_HEIGHT)
        self.set_style_bg_color(BG_BLACK_HEX, 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(0, 0)
        self.set_style_pad_bottom(0, 0)

        # Seed name label
        self.seed_label = lv.label(self)
        self.seed_label.set_style_text_font(lv.font_montserrat_16, 0)
        self.seed_label.set_style_text_color(CYAN_HEX, 0)
        self.seed_label.align(lv.ALIGN.LEFT_MID, 0, 0)

        # Dropdown arrow
        self.arrow = lv.label(self)
        self.arrow.set_text(lv.SYMBOL.DOWN)
        self.arrow.set_style_text_color(GREY_LIGHT_HEX, 0)
        self.arrow.set_style_text_font(lv.font_montserrat_12, 0)

        # Make whole bar clickable
        self.add_flag(lv.obj.FLAG.CLICKABLE)
        self.add_event_cb(self._toggle_dropdown, lv.EVENT.CLICKED, None)

        self.refresh()

    def refresh(self):
        """Update displayed seed name."""
        state = self.gui.specter_state
        if state.active_seed:
            name = state.active_seed.label
            if state.active_seed.passphrase:
                name = name + " + Passphrase"
            self.seed_label.set_text(name)
        elif state.loaded_seeds:
            self.seed_label.set_text("Select seed...")
        else:
            self.seed_label.set_text("No seed loaded")

        # Reposition arrow after seed label
        self.arrow.align_to(self.seed_label, lv.ALIGN.OUT_RIGHT_MID, 8, 0)

    def _toggle_dropdown(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        state = self.gui.specter_state
        if not state.loaded_seeds:
            return
        if self._dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        self._dropdown_open = True
        state = self.gui.specter_state

        self._modal = ModalOverlay(bg_opa=180)
        overlay = self._modal.overlay

        # Position dropdown below the seed bar
        dropdown = lv.obj(overlay)
        dropdown.set_size(SCREEN_WIDTH - 2 * PAD_MD, lv.SIZE_CONTENT)
        dropdown.set_style_bg_color(BG_CARD_HEX, 0)
        dropdown.set_style_bg_opa(lv.OPA.COVER, 0)
        dropdown.set_style_border_width(1, 0)
        dropdown.set_style_border_color(CYAN_DARK_HEX, 0)
        dropdown.set_style_radius(8, 0)
        dropdown.set_style_pad_all(PAD_SM, 0)
        dropdown.set_layout(lv.LAYOUT.FLEX)
        dropdown.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        dropdown.set_style_flex_main_place(lv.FLEX_ALIGN.START, 0)
        dropdown.align(lv.ALIGN.TOP_MID, 0, SEED_DROPDOWN_HEIGHT + 45)

        for seed in state.loaded_seeds:
            btn = lv.button(dropdown)
            btn.set_size(lv.pct(100), 44)
            btn.set_style_bg_color(BG_ELEVATED_HEX, 0)
            btn.set_style_bg_opa(lv.OPA.COVER, 0)
            btn.set_style_radius(6, 0)
            btn.set_style_border_width(0, 0)

            lbl = lv.label(btn)
            name = seed.label
            if seed.passphrase:
                name = name + " + Passphrase"
            lbl.set_text(name)
            lbl.set_style_text_font(lv.font_montserrat_16, 0)
            if state.active_seed is seed:
                lbl.set_style_text_color(CYAN_HEX, 0)
            else:
                lbl.set_style_text_color(WHITE_HEX, 0)
            lbl.center()

            btn.add_event_cb(lambda e, s=seed: self._select_seed(s), lv.EVENT.CLICKED, None)

        # Tap outside to close
        overlay.add_flag(lv.obj.FLAG.CLICKABLE)
        overlay.add_event_cb(lambda e: self._close_dropdown(), lv.EVENT.CLICKED, None)

    def _select_seed(self, seed):
        self.gui.specter_state.set_active_seed(seed)
        self._close_dropdown()
        self.refresh()
        # Refresh main dashboard to update wallet list
        if hasattr(self.gui, 'refresh_dashboard'):
            self.gui.refresh_dashboard()

    def _close_dropdown(self):
        self._dropdown_open = False
        if self._modal:
            self._modal.close()
            self._modal = None
