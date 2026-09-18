import base64
import json

import pytest

from MockUI.storage import SeedStorage, StorageError
from MockUI.device_screens.sd_card_menu import SDCardMenu


MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)


def test_sd_storage_classifies_seed_wallet_psbt_and_other(tmp_path, monkeypatch):
    flash = tmp_path / "flash"
    card = tmp_path / "sd"
    flash.mkdir()
    card.mkdir()
    storage = SeedStorage(str(flash), str(card))
    monkeypatch.setattr(storage, "sd_present", lambda: True)

    (card / "01-cold-seed.txt").write_text(MNEMONIC + "\n", encoding="utf-8")
    (card / "wallet.json").write_text(json.dumps({
        "label": "Savings",
        "descriptor": "wpkh([73c5da0a/84h/0h/0h]xpub-example/0/*)",
    }), encoding="utf-8")
    (card / "payment.psbt").write_bytes(b"psbt\xfftest")
    (card / "encoded.dat").write_bytes(base64.b64encode(b"psbt\xfftest"))
    (card / "README.txt").write_text("public demo file", encoding="utf-8")

    entries = {entry["name"]: entry for entry in storage.list_sd_entries()}
    assert entries["01-cold-seed.txt"]["kind"] == storage.SD_SEED
    assert entries["01-cold-seed.txt"]["label"] == "cold seed"
    assert entries["wallet.json"]["kind"] == storage.SD_WALLET
    assert entries["wallet.json"]["label"] == "Savings"
    assert entries["payment.psbt"]["kind"] == storage.SD_TRANSACTION
    assert entries["encoded.dat"]["kind"] == storage.SD_TRANSACTION
    assert entries["README.txt"]["kind"] == storage.SD_OTHER
    assert storage.load_sd_mnemonic("01-cold-seed.txt") == MNEMONIC
    assert storage.load_sd_wallet("wallet.json")["descriptor"].startswith("wpkh(")


def test_encrypted_seed_roundtrip_is_device_bound(tmp_path, monkeypatch):
    flash = tmp_path / "flash"
    card = tmp_path / "sd"
    other_flash = tmp_path / "other-flash"
    flash.mkdir()
    card.mkdir()
    other_flash.mkdir()

    storage = SeedStorage(str(flash), str(card))
    other = SeedStorage(str(other_flash), str(card))
    monkeypatch.setattr(storage, "sd_present", lambda: True)
    monkeypatch.setattr(other, "sd_present", lambda: True)

    filename = storage.save_sd_seed(MNEMONIC, "Cold seed")
    assert MNEMONIC.encode() not in (card / filename).read_bytes()
    assert storage.load_sd_seed(filename) == MNEMONIC
    other_filename = "%s.Cold_seed" % other.sd_prefix
    (card / other_filename).write_bytes((card / filename).read_bytes())
    with pytest.raises(StorageError, match="another device or is damaged"):
        other.load_sd_seed(other_filename)


def test_descriptor_metadata_is_extracted_for_wallet_import():
    descriptor = (
        "wsh(sortedmulti(2,[73c5da0a/48h/1h/0h/2h]tpub-a/0/*,"
        "[f00dbabe/48h/1h/0h/2h]tpub-b/0/*))"
    )
    assert SDCardMenu._descriptor_fingerprints(descriptor) == [
        "73c5da0a", "f00dbabe"
    ]
    assert SDCardMenu._descriptor_threshold(descriptor) == 2
    assert SDCardMenu._descriptor_path(descriptor) == "m/48h/1h/0h/2h"
