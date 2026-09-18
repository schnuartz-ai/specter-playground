import base64
import json

from MockUI.storage import SeedStorage


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
