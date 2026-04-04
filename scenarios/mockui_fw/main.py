# main.py - New Specter DIY clean UI entry point
import gc
import sys
import display
import lvgl as lv
import utime as time

_ON_HARDWARE = sys.platform not in ('linux', 'darwin')

if not _ON_HARDWARE:
    import os
    os.mount(os.VfsPosix(os.getcwd() + '/build/flash_image'), '/flash')
    display.init(False)
else:
    display.init()

from MockUI import SpecterGui, SpecterState
from MockUI.stubs.seed import Seed
from MockUI.stubs.wallet import Wallet, ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_NESTED_SEGWIT

gc.collect()

lv.theme_default_init(
    None,
    lv.color_hex(0x00B4D8),
    lv.color_hex(0xFF4444),
    True,
    lv.font_montserrat_16,
)

specter_state = SpecterState()
specter_state.has_battery = True
specter_state.battery_pct = 85

specter_state._hasQR = True
specter_state._enabledQR = True

specter_state._hasSD = True
specter_state._enabledSD = True
specter_state._detectedSD = True

specter_state._hasSmartCard = True
specter_state._enabledSmartCard = True
specter_state._detectedSmartCard = False

specter_state._hasUSB = True
specter_state._enabledUSB = True

specter_state.pin = "21"

# === Demo Seeds ===
seed_main = Seed("mainseed", fingerprint="a1b2c3d4")
seed_backup = Seed("backup-key", fingerprint="e5f6a7b8")

specter_state.add_seed(seed_main)
specter_state.add_seed(seed_backup)

# === Demo Wallets (realistic names and parameters) ===

# Default wallet is auto-created by add_seed (Native Segwit, Single Sig, Acc 0)

wallet_21btc = Wallet(
    label="21bitcoin App",
    descriptor="wpkh([a1b2c3d4/84'/0'/0']xpub...)",
    isMultiSig=False, net="mainnet",
    required_fingerprints=["a1b2c3d4"],
    address_type=ADDR_NATIVE_SEGWIT,
    account=0,
    has_been_exported=True,
)
wallet_21btc.shared_with = ["Sparrow"]
specter_state.register_wallet(wallet_21btc)

wallet_nokyc = Wallet(
    label="No KYC",
    descriptor="wpkh([a1b2c3d4/84'/0'/1']xpub...)",
    isMultiSig=False, net="mainnet",
    required_fingerprints=["a1b2c3d4"],
    address_type=ADDR_NATIVE_SEGWIT,
    account=1,
)
specter_state.register_wallet(wallet_nokyc)

wallet_pocket = Wallet(
    label="Pocket Bitcoin",
    descriptor="pkh([a1b2c3d4/44'/0'/0']xpub...)",
    isMultiSig=False, net="mainnet",
    required_fingerprints=["a1b2c3d4"],
    address_type=ADDR_LEGACY,
    account=0,
    has_been_exported=True,
)
wallet_pocket.shared_with = ["Specter Desktop", "Sparrow"]
specter_state.register_wallet(wallet_pocket)

wallet_multisig = Wallet(
    label="Multi Sig Escrow",
    descriptor="wsh(multi(2,[a1b2c3d4]xpub...,[e5f6a7b8]xpub...))",
    isMultiSig=True, net="mainnet",
    threshold=2,
    required_fingerprints=["a1b2c3d4", "e5f6a7b8"],
    address_type=ADDR_NATIVE_SEGWIT,
    account=0,
    has_been_exported=True,
)
wallet_multisig.shared_with = ["Nunchuk"]
specter_state.register_wallet(wallet_multisig)

specter_state.set_active_seed(seed_main)

gc.collect()

scr = SpecterGui(specter_state)
lv.screen_load(scr)

if not _ON_HARDWARE and '--control' in sys.argv:
    from sim_control import ControlServer
    ControlServer(scr)

while True:
    display.update(30)
    time.sleep_ms(30)
