"""Seed dropdown: shows active seed name centered, tap to switch or add wallet."""
import lvgl as lv
from .ui_consts import (
    SEED_DROPDOWN_HEIGHT, SCREEN_WIDTH, PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX,
)
from .symbol_lib import BTC_ICONS
from .modal_overlay import ModalOverlay


class SeedDropdown(lv.obj):
    """Dropdown showing the currently active seed (centered). Tap to switch seeds or add wallet."""

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
        self.set_style_pad_all(0, 0)

        # Seed name label — CENTERED
        self.seed_label = lv.label(self)
        self.seed_label.set_style_text_font(lv.font_montserrat_16, 0)
        self.seed_label.set_style_text_color(CYAN_HEX, 0)

        # Dropdown arrow (next to label)
        self.arrow = lv.label(self)
        self.arrow.set_text(lv.SYMBOL.DOWN)
        self.arrow.set_style_text_color(GREY_LIGHT_HEX, 0)
        self.arrow.set_style_text_font(lv.font_montserrat_12, 0)

        # Make whole bar clickable
        self.add_flag(lv.obj.FLAG.CLICKABLE)
        self.add_event_cb(self._toggle_dropdown, lv.EVENT.CLICKED, None)

        self.refresh()

    def refresh(self):
        """Update displayed seed name, centered."""
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

        # Center the label + arrow
        self.seed_label.align(lv.ALIGN.CENTER, -10, 0)
        self.arrow.align_to(self.seed_label, lv.ALIGN.OUT_RIGHT_MID, 6, 0)

    def _toggle_dropdown(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
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

        dropdown = lv.obj(overlay)
        dropdown.set_size(SCREEN_WIDTH - 2 * PAD_MD, lv.SIZE_CONTENT)
        dropdown.set_style_bg_color(BG_CARD_HEX, 0)
        dropdown.set_style_bg_opa(lv.OPA.COVER, 0)
        dropdown.set_style_border_width(1, 0)
        dropdown.set_style_border_color(CYAN_DARK_HEX, 0)
        dropdown.set_style_radius(8, 0)
        dropdown.set_style_pad_all(PAD_SM, 0)
        dropdown.set_style_pad_row(PAD_SM, 0)
        dropdown.set_layout(lv.LAYOUT.FLEX)
        dropdown.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        dropdown.align(lv.ALIGN.TOP_MID, 0, SEED_DROPDOWN_HEIGHT + 45)

        # Seed list
        if state.loaded_seeds:
            for seed in state.loaded_seeds:
                is_active = state.active_seed is seed
                btn = lv.button(dropdown)
                btn.set_size(lv.pct(100), 44)
                btn.set_style_bg_color(BG_ELEVATED_HEX if is_active else BG_CARD_HEX, 0)
                btn.set_style_bg_opa(lv.OPA.COVER, 0)
                btn.set_style_radius(6, 0)
                btn.set_style_border_width(0, 0)
                btn.set_style_shadow_width(0, 0)

                btn.set_layout(lv.LAYOUT.FLEX)
                btn.set_flex_flow(lv.FLEX_FLOW.ROW)
                btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
                btn.set_style_pad_column(PAD_SM, 0)
                btn.set_style_pad_left(PAD_SM, 0)

                ico = lv.image(btn)
                BTC_ICONS.KEY(CYAN_HEX if is_active else GREY_LIGHT_HEX).add_to_parent(ico, zoom=110)

                lbl = lv.label(btn)
                name = seed.label
                if seed.passphrase:
                    name = name + " + PP"
                lbl.set_text(name)
                lbl.set_style_text_font(lv.font_montserrat_16, 0)
                lbl.set_style_text_color(CYAN_HEX if is_active else WHITE_HEX, 0)
                lbl.set_flex_grow(1)

                if is_active:
                    check = lv.label(btn)
                    check.set_text(lv.SYMBOL.OK)
                    check.set_style_text_color(GREEN_HEX, 0)

                btn.add_event_cb(lambda e, s=seed: self._select_seed(s), lv.EVENT.CLICKED, None)

        # Divider
        divider = lv.obj(dropdown)
        divider.set_size(lv.pct(100), 1)
        divider.set_style_bg_color(CYAN_DARK_HEX, 0)
        divider.set_style_bg_opa(lv.OPA.COVER, 0)
        divider.set_style_border_width(0, 0)

        # "Add New Wallet" button
        add_btn = lv.button(dropdown)
        add_btn.set_size(lv.pct(100), 44)
        add_btn.set_style_bg_color(BG_CARD_HEX, 0)
        add_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        add_btn.set_style_radius(6, 0)
        add_btn.set_style_border_width(0, 0)
        add_btn.set_style_shadow_width(0, 0)

        add_btn.set_layout(lv.LAYOUT.FLEX)
        add_btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        add_btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        add_btn.set_style_pad_column(PAD_SM, 0)
        add_btn.set_style_pad_left(PAD_SM, 0)

        add_ico = lv.image(add_btn)
        BTC_ICONS.PLUS(CYAN_HEX).add_to_parent(add_ico, zoom=110)

        add_lbl = lv.label(add_btn)
        add_lbl.set_text("Add New Wallet")
        add_lbl.set_style_text_font(lv.font_montserrat_16, 0)
        add_lbl.set_style_text_color(CYAN_HEX, 0)

        add_btn.add_event_cb(self._add_wallet, lv.EVENT.CLICKED, None)

        # Tap outside to close
        overlay.add_flag(lv.obj.FLAG.CLICKABLE)
        overlay.add_event_cb(lambda e: self._close_dropdown(), lv.EVENT.CLICKED, None)

    def _select_seed(self, seed):
        self.gui.specter_state.set_active_seed(seed)
        self._close_dropdown()
        self.refresh()
        if hasattr(self.gui, 'refresh_dashboard'):
            self.gui.refresh_dashboard()

    def _add_wallet(self, e):
        self._close_dropdown()
        self.gui.show_menu("add_wallet")

    def _close_dropdown(self):
        self._dropdown_open = False
        if self._modal:
            self._modal.close()
            self._modal = None
