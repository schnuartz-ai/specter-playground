"""UI constants for the new Specter DIY clean interface."""
from micropython import const
import lvgl as lv

# --- Screen dimensions ---
SCREEN_WIDTH = const(480)
SCREEN_HEIGHT = const(800)

# --- Layout zone heights (pixels) ---
TOP_BAR_HEIGHT = const(40)
SEED_DROPDOWN_HEIGHT = const(45)
NAV_BAR_HEIGHT = const(56)

# Wallet section: fits ~3 wallet rows
WALLET_SECTION_HEIGHT = const(190)

# Action buttons fill remaining space
# 800 - 40 - 45 - 190 - 56 = 469px for action area

# --- Button sizes ---
BTN_SMALL_HEIGHT = const(70)
BTN_LARGE_HEIGHT = const(110)      # Scan button (larger)
BTN_RADIUS = const(12)

# --- Wallet row ---
WALLET_ROW_HEIGHT = const(48)
WALLET_ICON_SIZE = const(20)

# --- Bottom nav ---
NAV_BTN_SIZE = const(44)

# --- Font sizes ---
FONT_TITLE = const(22)
FONT_BODY = const(16)
FONT_SMALL = const(12)
FONT_ICON = const(22)

# --- Spacing ---
PAD_XS = const(4)
PAD_SM = const(8)
PAD_MD = const(12)
PAD_LG = const(16)
PAD_XL = const(24)

# --- Icon sizes ---
BTC_ICON_WIDTH = const(42)
BTC_ICON_ZOOM = const(256)
ICON_SM = const(20)
ICON_MD = const(28)
ICON_LG = const(42)

# --- Status bar (legacy compat for Battery stub) ---
STATUS_BTN_HEIGHT = const(40)
STATUS_BTN_WIDTH = const(50)

# --- Modal ---
MODAL_WIDTH_PCT = const(85)
MODAL_HEIGHT_PCT = const(80)

# --- PIN ---
PIN_BTN_HEIGHT = const(85)
PIN_BTN_WIDTH = const(115)

# --- Keyboard manager compat ---
SWITCH_HEIGHT = const(82)
SWITCH_WIDTH = const(45)
BTN_HEIGHT = const(75)
BTN_WIDTH = const(100)
MENU_PCT = const(100)
PAD_SIZE = const(5)
ONE_LETTER_SYMBOL_WIDTH = const(16)
TWO_LETTER_SYMBOL_WIDTH = const(28)
THREE_LETTER_SYMBOL_WIDTH = const(40)
MENU_TITLE_FONT_SIZE = const(22)
MENU_ITEM_FONT_SIZE = const(16)
STATUS_BAR_PCT = const(5)
CONTENT_PCT = const(90)
BACK_BTN_HEIGHT = const(70)
BACK_BTN_WIDTH = const(48)
TITLE_ROW_HEIGHT = const(60)
TITLE_PADDING = const(15)
EXPLAINER_WIDTH_PCT = const(70)
EXPLAINER_HEIGHT_PCT = const(40)
EXPLAINER_OVERLAY_OPA = const(200)

# === COLOR SCHEME — Specter Cyan/Teal on Dark ===

# Primary
CYAN = "#00B4D8"
CYAN_HEX = lv.color_hex(0x00B4D8)
CYAN_DARK = "#0077B6"
CYAN_DARK_HEX = lv.color_hex(0x0077B6)

# Backgrounds
BG_BLACK = "#000000"
BG_BLACK_HEX = lv.color_hex(0x000000)
BG_DARK = "#111111"
BG_DARK_HEX = lv.color_hex(0x111111)
BG_CARD = "#1A1A1A"
BG_CARD_HEX = lv.color_hex(0x1A1A1A)
BG_ELEVATED = "#222222"
BG_ELEVATED_HEX = lv.color_hex(0x222222)

# Text
WHITE = "#FFFFFF"
WHITE_HEX = lv.color_hex(0xFFFFFF)
GREY_LIGHT = "#AAAAAA"
GREY_LIGHT_HEX = lv.color_hex(0xAAAAAA)
GREY = "#606060"
GREY_HEX = lv.color_hex(0x606060)
GREY_DARK = "#333333"
GREY_DARK_HEX = lv.color_hex(0x333333)

# Semantic
GREEN = "#00CC66"
GREEN_HEX = lv.color_hex(0x00CC66)
ORANGE = "#FF9A00"
ORANGE_HEX = lv.color_hex(0xFF9A00)
RED = "#FF4444"
RED_HEX = lv.color_hex(0xFF4444)
YELLOW = "#FFD700"
YELLOW_HEX = lv.color_hex(0xFFD700)

BLACK = "#000000"
BLACK_HEX = lv.color_hex(0x000000)

# Warning background (subtle orange tint for address reuse, security warnings)
BG_WARN = "#2A1A00"
BG_WARN_HEX = lv.color_hex(0x2A1A00)
