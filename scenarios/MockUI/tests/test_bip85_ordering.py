from embit import bip32, bip39

from MockUI.stubs.device_state import DeviceState, _derive_bip85_mnemonic
from MockUI.stubs.seed import Seed


MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)


def _child_mnemonic(mnemonic, word_count, index):
    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(mnemonic, ""))
    return _derive_bip85_mnemonic(root, bip39, word_count, index)


def test_bip85_import_sort_is_parent_first_and_nested():
    child = _child_mnemonic(MNEMONIC, 12, 7)
    grandchild = _child_mnemonic(child, 12, 2)
    state = DeviceState()
    root_seed = Seed("Root", mnemonic=MNEMONIC)
    child_seed = Seed("Child", mnemonic=child)
    grandchild_seed = Seed("Grandchild", mnemonic=grandchild)
    state.loaded_seeds[:] = [grandchild_seed, child_seed, root_seed]

    state.sort_bip85_seeds()

    assert state.loaded_seeds == [root_seed, child_seed, grandchild_seed]
    assert child_seed.bip85_parent_fingerprint == root_seed.get_fingerprint()
    assert child_seed.bip85_index == 7
    assert grandchild_seed.bip85_parent_fingerprint == child_seed.get_fingerprint()
    assert grandchild_seed.bip85_index == 2
    assert root_seed.known_bip85_derivations(state.loaded_seeds) == [child_seed]
    assert child_seed.known_bip85_derivations(state.loaded_seeds) == [grandchild_seed]
