from MockUI.storage import SeedStorage


def test_sd_storage_detects_and_lists_regular_files(tmp_path, monkeypatch):
    card = tmp_path / "sd"
    card.mkdir()
    (card / "wallet.dat").write_bytes(b"wallet")
    (card / "nested").mkdir()

    storage = SeedStorage(str(tmp_path / "flash"), str(card))
    monkeypatch.setattr(storage, "sd_present", lambda: True)

    assert storage.list_sd_files() == [("wallet.dat", 6)]
