"""Categorized SD-card browser and importer for the MockUI."""

import re

from ..basic import GenericMenu, BTC_ICONS, MenuItem, t
from ..storage import StorageError
from ..stubs.seed import Seed
from ..stubs.wallet import Wallet


def _format_size(size):
    if size < 1024:
        return "%d B" % size
    if size < 1024 * 1024:
        return "%.1f KB" % (size / 1024)
    return "%.1f MB" % (size / (1024 * 1024))


class SDCardMenu(GenericMenu):
    """Browse, label, and import the files on the inserted SD card."""

    TITLE_KEY = "STORAGE_MENU_SD_CARD"

    _CATEGORIES = (
        ("seed", "SD_CARD_SEEDS", BTC_ICONS.MNEMONIC),
        ("wallet", "SD_CARD_WALLETS", BTC_ICONS.WALLET),
        ("transaction", "SD_CARD_TRANSACTIONS", BTC_ICONS.SEND),
        ("other", "SD_CARD_OTHER", BTC_ICONS.FILE),
    )

    def __init__(self, parent):
        self._status = None
        super().__init__(parent)

    @property
    def storage(self):
        return self.device_state.storage

    def get_menu_items(self):
        if not self.storage.sd_present():
            return [MenuItem(text=t("SD_CARD_NO_CARD"))]

        entries = self.storage.list_sd_entries()
        counts = {}
        for entry in entries:
            counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1

        items = []
        if self._status:
            items.append(MenuItem(text=self._status, modifier="Highlight"))

        items.append(MenuItem(
            BTC_ICONS.RECEIVE,
            t("SD_CARD_LOAD_ALL"),
            target=self._import_all,
            modifier="Highlight" if counts.get("seed", 0) or counts.get("wallet", 0) else None,
        ))
        if self.current_menu == "store_to_sd" and self.active_seed is not None:
            items.insert(0, MenuItem(
                BTC_ICONS.SD_CARD,
                t("SD_CARD_SAVE_ACTIVE"),
                target=self._save_active_seed,
                modifier="Highlight",
            ))

        items.append(MenuItem(text=t("SD_CARD_SUMMARY") % (
            counts.get("seed", 0),
            counts.get("wallet", 0),
            counts.get("transaction", 0),
            counts.get("other", 0),
        )))

        if not entries:
            items.append(MenuItem(text=t("SD_CARD_EMPTY")))
            return items

        for kind, title_key, icon in self._CATEGORIES:
            group = [entry for entry in entries if entry["kind"] == kind]
            if not group:
                continue
            items.append(MenuItem(icon, t(title_key)))
            for entry in group:
                imported = (
                    kind == self.storage.SD_SEED
                    and self._seed_is_imported(entry)
                )
                text = "%s\n%s | %s" % (
                    entry["label"], entry["detail"], _format_size(entry["size"])
                )
                if imported:
                    text = "✓ " + text
                items.append(MenuItem(
                    icon,
                    text,
                    target=lambda item=entry: self._open_file(item),
                    modifier="Highlight" if imported else None,
                ))
        return items

    def _seed_is_imported(self, entry):
        try:
            mnemonic = self.storage.load_sd_mnemonic(entry["name"])
        except Exception:
            return False
        return any(
            getattr(seed, "mnemonic", None) == mnemonic
            for seed in self.device_state.loaded_seeds
        )

    def _show_status(self, message, error=False):
        self._status = ("Error: " if error else "") + message
        self.rebuild_body()

    def _save_active_seed(self):
        seed = self.active_seed or self.device_state.active_seed
        if seed is None or not getattr(seed, "mnemonic", None):
            self._show_status(t("SD_CARD_NO_ACTIVE_SEED"), True)
            return
        try:
            filename = self.storage.save_sd_seed(seed.mnemonic, seed.label)
            self.device_state.refresh_peripherals()
            self._show_status(t("SD_CARD_SAVED") % filename)
        except Exception as exc:
            self._show_status(str(exc), True)

    def _open_file(self, entry):
        try:
            if entry["kind"] == self.storage.SD_SEED:
                seed, _ = self._import_seed(entry["name"], entry["label"])
                self.on_navigate("manage_seedphrase", target_seed=seed)
            elif entry["kind"] == self.storage.SD_WALLET:
                wallet, _ = self._import_wallet(entry["name"], entry["label"])
                self.on_navigate("manage_wallet", target_wallet=wallet)
            elif entry["kind"] == self.storage.SD_TRANSACTION:
                self.device_state.pending_psbt = entry["name"]
                self.on_navigate("signing")
        except Exception as exc:
            self._show_status(str(exc), True)

    def _import_seed(self, filename, label, sort=True):
        mnemonic = self.storage.load_sd_mnemonic(filename)
        state = self.device_state
        seed = next(
            (
                item for item in state.loaded_seeds
                if getattr(item, "mnemonic", None) == mnemonic
            ),
            None,
        )
        imported = seed is None
        if imported:
            seed = Seed(label=label, mnemonic=mnemonic, is_backed_up=True)
            state.add_seed(seed)
        else:
            state.set_active_seed(seed)
        if sort:
            state.sort_bip85_seeds()
        self.ui_state.set_active_seed(seed)
        return seed, imported

    def _import_all(self):
        imported_seeds = 0
        imported_wallets = 0
        failures = 0

        # Read all entries first.  BIP85 sorting happens once after the full
        # set is available, so children cannot be left detached by ordering.
        for entry in self.storage.list_sd_entries():
            try:
                if entry["kind"] == self.storage.SD_SEED:
                    _, imported = self._import_seed(
                        entry["name"], entry["label"], sort=False
                    )
                    imported_seeds += int(imported)
                elif entry["kind"] == self.storage.SD_WALLET:
                    _, imported = self._import_wallet(
                        entry["name"], entry["label"], navigate=False
                    )
                    imported_wallets += int(imported)
            except Exception as exc:
                failures += 1
                print("SD bulk import:", entry["name"], exc)

        self.device_state.sort_bip85_seeds()
        self.device_state.refresh_peripherals()
        if not imported_seeds and not imported_wallets and not failures:
            self._show_status(t("SD_CARD_ALREADY_IMPORTED"))
        else:
            message = t("SD_CARD_IMPORTED") % (imported_seeds, imported_wallets)
            if failures:
                message += " | " + (t("SD_CARD_FAILED") % failures)
            self._show_status(message, bool(failures))

    @staticmethod
    def _descriptor_fingerprints(descriptor):
        fingerprints = []
        position = 0
        while True:
            start = descriptor.find("[", position)
            if start < 0:
                break
            end = descriptor.find("]", start + 1)
            if end < 0:
                break
            fingerprint = descriptor[start + 1:end].split("/", 1)[0]
            if re.match(r"^[0-9a-fA-F]{8}$", fingerprint):
                fingerprint = fingerprint.lower()
                if fingerprint not in fingerprints:
                    fingerprints.append(fingerprint)
            position = end + 1
        return fingerprints

    @staticmethod
    def _descriptor_threshold(descriptor):
        for marker in ("sortedmulti(", "multi("):
            start = descriptor.find(marker)
            if start >= 0:
                try:
                    return int(descriptor[start + len(marker):].split(",", 1)[0])
                except ValueError:
                    return None
        return None

    @staticmethod
    def _descriptor_path(descriptor):
        match = re.search(r"\[[0-9a-fA-F]{8}(/[^\]]+)\]", descriptor)
        return "m" + match.group(1) if match else None

    def _import_wallet(self, filename, fallback_label, navigate=True):
        payload = self.storage.load_sd_wallet(filename)
        descriptor = payload["descriptor"].strip()
        state = self.device_state
        wallet = next(
            (item for item in state.registered_wallets
             if item.descriptor == descriptor),
            None,
        )
        imported = wallet is None
        if wallet is None:
            fingerprints = self._descriptor_fingerprints(descriptor)
            threshold = self._descriptor_threshold(descriptor)
            is_multisig = threshold is not None
            if is_multisig and len(fingerprints) < threshold:
                raise StorageError("Wallet descriptor has too few signers")
            lower = descriptor.lower()
            testnet_markers = ("tpub", "upub", "vpub", "tb1", "[1/")
            network = "testnet" if any(marker in lower for marker in testnet_markers) else "mainnet"
            wallet = Wallet(
                label=payload.get("label") or fallback_label,
                descriptor=descriptor,
                isMultiSig=is_multisig,
                net=network,
                required_fingerprints=fingerprints,
                threshold=threshold,
                derivation_path=self._descriptor_path(descriptor),
            )
            state.register_wallet(wallet, imported=True, source="SD card")
        else:
            state.set_active_wallet(wallet)
        self.ui_state.set_active_wallet(wallet)
        if navigate:
            self.on_navigate("manage_wallet", target_wallet=wallet)
        return wallet, imported
