# MockUI/__init__.py — New clean Specter DIY interface
from .basic import (
    BTN_HEIGHT, BTN_WIDTH, MENU_PCT, PAD_SIZE,
    SWITCH_HEIGHT, SWITCH_WIDTH,
    STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH,
    ONE_LETTER_SYMBOL_WIDTH, TWO_LETTER_SYMBOL_WIDTH, THREE_LETTER_SYMBOL_WIDTH,
    GREEN, ORANGE, RED,
)
from .basic import SpecterGui
from .stubs import UIState, SpecterState, Wallet

__all__ = [
    "BTN_HEIGHT", "BTN_WIDTH",
    "MENU_PCT", "PAD_SIZE",
    "SWITCH_HEIGHT", "SWITCH_WIDTH",
    "STATUS_BTN_HEIGHT", "STATUS_BTN_WIDTH",
    "ONE_LETTER_SYMBOL_WIDTH", "TWO_LETTER_SYMBOL_WIDTH", "THREE_LETTER_SYMBOL_WIDTH",
    "GREEN", "ORANGE", "RED",
    "SpecterState", "Wallet", "UIState",
    "SpecterGui",
]
