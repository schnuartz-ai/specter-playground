"""SD-card storage services used by the MockUI.

The MockUI is also used with the unix simulator, so this module deliberately
keeps the filesystem seam small: on hardware ``/sd`` is provided by the
existing ``platform.sdcard`` driver, while tests and the browser-style
simulator can inject a directory directly.

Encrypted Specter seed files use the same ``specterdiy<id>.<label>`` naming
convention and AEAD primitives as the firmware keystore.  The small
device-secret fallback is only for the standalone MockUI state, where the
full application keystore is not constructed.
"""

import base64
import json
import os
from contextlib import contextmanager
from binascii import hexlify

from embit import bip39

from helpers import aead_decrypt, aead_encrypt, tagged_hash
from rng import get_random_bytes


class StorageError(Exception):
    """An SD-card operation failed or the file contents are invalid."""


class SeedStorage:
    SD_SEED = "seed"
    SD_TRANSACTION = "transaction"
    SD_WALLET = "wallet"
    SD_OTHER = "other"

    def __init__(self, flash_root="/flash", sd_root="/sd", encryption_key=None):
        # The browser/simulator can expose the virtual card below /state/sd.
        if sd_root == "/sd":
            try:
                import platform
                fpath = getattr(platform, "fpath", None)
                if fpath is not None:
                    sd_root = fpath("/sd")
            except (ImportError, AttributeError):
                pass
            try:
                os.stat("/state/sd")
                sd_root = "/state/sd"
            except OSError:
                pass

        self.flash_root = flash_root.rstrip("/") or "/"
        self.sd_root = sd_root.rstrip("/") or "/"
        self._ensure_dir(self.flash_root)
        self._encryption_key = encryption_key
        self.device_secret = self._load_or_create_secret()

    @staticmethod
    def _ensure_dir(path):
        try:
            os.mkdir(path)
        except OSError:
            pass

    def _load_or_create_secret(self):
        path = self.flash_root + "/mockui-device-secret"
        try:
            with open(path, "rb") as stream:
                secret = stream.read()
            if len(secret) == 32:
                return secret
        except OSError:
            pass

        secret = get_random_bytes(32)
        try:
            with open(path, "wb") as stream:
                stream.write(secret)
        except OSError:
            # A read-only test/simulator root can still browse public files.
            pass
        return secret

    @property
    def encryption_key(self):
        if self._encryption_key is not None:
            return self._encryption_key
        return tagged_hash("scenc", self.device_secret)

    @property
    def sd_prefix(self):
        card_id = hexlify(tagged_hash("sdid", self.device_secret)[:4]).decode()
        return "specterdiy" + card_id

    def sd_present(self):
        """Return the live card state without touching card contents."""
        try:
            with open("/bridge/sd-inserted", "rb") as marker:
                return marker.read(1) in (b"1", b"\x01")
        except OSError:
            pass

        try:
            import platform
            card = getattr(platform, "sdcard", None)
            if card is not None:
                return bool(card.is_present)
        except (ImportError, AttributeError, RuntimeError):
            pass

        try:
            os.stat(self.sd_root)
            return True
        except OSError:
            return False

    @staticmethod
    def _safe_name(name):
        clean = "".join(
            char for char in (name or "seed")
            if char.isalnum() or char in "-_ "
        ).strip()
        return clean.replace(" ", "_") or "seed"

    @staticmethod
    def _as_name(value):
        if isinstance(value, bytes):
            return value.decode("utf-8", "replace")
        return value

    def _list_names(self):
        with self._mounted_sd():
            try:
                entries = os.ilistdir(self.sd_root)
                names = []
                for entry in entries:
                    name = self._as_name(entry[0])
                    # MicroPython marks directories as 0x4000.
                    if len(entry) < 2 or entry[1] != 0x4000:
                        names.append(name)
                return names
            except AttributeError:
                try:
                    return [
                        name for name in os.listdir(self.sd_root)
                        if not os.path.isdir(self.sd_root + "/" + name)
                    ]
                except OSError:
                    return []
            except OSError:
                return []

    @contextmanager
    def _mounted_sd(self):
        """Mount the real card for the duration of one filesystem operation."""
        card = None
        mounted_here = False
        try:
            import platform
            card = getattr(platform, "sdcard", None)
            if (
                card is not None
                and self.sd_root != "/state/sd"
                and bool(card.is_present)
            ):
                card.mount()
                mounted_here = True
        except (ImportError, AttributeError, RuntimeError, OSError):
            card = None
        try:
            yield
        finally:
            if mounted_here and card is not None:
                try:
                    card.unmount()
                except (RuntimeError, OSError):
                    pass

    def list_sd_seeds(self):
        if not self.sd_present():
            return []
        prefix = self.sd_prefix.lower()
        return sorted(
            name for name in self._list_names()
            if name.lower().startswith(prefix)
        )

    def list_sd_files(self):
        if not self.sd_present():
            return []
        files = []
        for name in sorted(self._list_names(), key=lambda item: item.lower()):
            try:
                size = os.stat(self.sd_root + "/" + name)[6]
            except OSError:
                size = 0
            files.append((name, size))
        return files

    def _path(self, filename):
        if not filename or "/" in filename or "\\" in filename:
            raise StorageError("Invalid SD card filename")
        return self.sd_root + "/" + filename

    def _read_sd_file(self, filename):
        try:
            with self._mounted_sd():
                with open(self._path(filename), "rb") as stream:
                    return stream.read()
        except OSError as exc:
            raise StorageError("SD card file could not be read") from exc

    @staticmethod
    def _text_payload(data):
        try:
            text = data.decode().strip()
        except (UnicodeError, ValueError):
            return None
        if text.startswith("\ufeff"):
            text = text[1:].strip()
        return text

    @staticmethod
    def _mnemonic_from_text(text):
        if not text:
            return None
        mnemonic = " ".join(text.split())
        try:
            return mnemonic if bip39.mnemonic_is_valid(mnemonic) else None
        except Exception:
            return None

    @staticmethod
    def _wallet_from_text(text):
        if not text:
            return None
        try:
            payload = json.loads(text)
        except (TypeError, ValueError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("descriptor"), str):
            return payload

        descriptor_prefixes = ("pkh(", "wpkh(", "sh(", "wsh(", "tr(", "combo(")
        if text.startswith(descriptor_prefixes):
            return {"descriptor": text}
        return None

    @staticmethod
    def _is_psbt(data, text):
        if data.startswith(b"psbt\xff"):
            return True
        if text and text.startswith("cHNidP"):
            try:
                try:
                    decoded = base64.b64decode(text, validate=True)
                except TypeError:
                    # MicroPython's base64 module has no ``validate`` kwarg.
                    decoded = base64.b64decode(text)
                return decoded.startswith(b"psbt\xff")
            except (ValueError, TypeError):
                return False
        return False

    @staticmethod
    def _display_name(filename):
        name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
        parts = name.split()
        if parts and parts[0].isdigit():
            parts = parts[1:]
        return " ".join(parts) or filename

    @staticmethod
    def _transaction_detail(filename):
        lowered = filename.lower()
        if ".signed." in lowered or ".completed." in lowered or lowered.startswith("signed"):
            return "Signed transaction | PSBT"
        return "Bitcoin transaction | PSBT"

    def classify_sd_file(self, filename, size=None):
        """Return UI metadata while keeping the original filename for actions."""
        if size is None:
            try:
                size = os.stat(self._path(filename))[6]
            except (OSError, StorageError):
                size = 0

        if filename.lower().startswith(self.sd_prefix.lower()):
            return {
                "name": filename,
                "size": size,
                "kind": self.SD_SEED,
                "label": self._display_name(filename.split(".", 1)[-1]),
                "detail": "Encrypted seed phrase",
                "word_count": None,
                "encrypted": True,
            }

        try:
            data = self._read_sd_file(filename)
        except StorageError:
            data = b""
        text = self._text_payload(data)
        mnemonic = self._mnemonic_from_text(text)
        if mnemonic:
            return {
                "name": filename,
                "size": size,
                "kind": self.SD_SEED,
                "label": self._display_name(filename),
                "detail": "Seed phrase | %d words" % len(mnemonic.split()),
                "word_count": len(mnemonic.split()),
                "encrypted": False,
            }

        if self._is_psbt(data, text) or filename.lower().endswith(".psbt"):
            return {
                "name": filename,
                "size": size,
                "kind": self.SD_TRANSACTION,
                "label": self._display_name(filename),
                "detail": self._transaction_detail(filename),
            }

        wallet = self._wallet_from_text(text)
        if wallet:
            return {
                "name": filename,
                "size": size,
                "kind": self.SD_WALLET,
                "label": wallet.get("label") or self._display_name(filename),
                "detail": "Wallet descriptor",
            }

        return {
            "name": filename,
            "size": size,
            "kind": self.SD_OTHER,
            "label": self._display_name(filename),
            "detail": "Other file",
        }

    def list_sd_entries(self):
        return [
            self.classify_sd_file(filename, size)
            for filename, size in self.list_sd_files()
        ]

    def load_sd_mnemonic(self, filename):
        if filename.lower().startswith(self.sd_prefix.lower()):
            return self.load_sd_seed(filename)
        mnemonic = self._mnemonic_from_text(
            self._text_payload(self._read_sd_file(filename))
        )
        if not mnemonic:
            raise StorageError("File does not contain a valid BIP39 seed phrase")
        return mnemonic

    def load_sd_wallet(self, filename):
        payload = self._wallet_from_text(
            self._text_payload(self._read_sd_file(filename))
        )
        if not payload:
            raise StorageError("File does not contain a wallet descriptor")
        return payload

    def save_sd_seed(self, mnemonic, name):
        if not self.sd_present():
            raise StorageError("SD card is not inserted")
        if not bip39.mnemonic_is_valid(mnemonic):
            raise StorageError("Recovery phrase is not valid BIP39")
        filename = "%s.%s" % (self.sd_prefix, self._safe_name(name))
        with self._mounted_sd():
            with open(self._path(filename), "wb") as stream:
                stream.write(aead_encrypt(self.encryption_key, b"", mnemonic.encode()))
        return filename

    def load_sd_seed(self, filename):
        if filename not in self.list_sd_seeds():
            raise StorageError("Seed file was not found on this SD card")
        try:
            with self._mounted_sd():
                with open(self._path(filename), "rb") as stream:
                    payload = stream.read()
            _, plaintext = aead_decrypt(payload, self.encryption_key)
            mnemonic = plaintext.decode()
        except Exception as exc:
            raise StorageError(
                "Seed file belongs to another device or is damaged"
            ) from exc
        if not bip39.mnemonic_is_valid(mnemonic):
            raise StorageError("Stored recovery phrase is invalid")
        return mnemonic

    def delete_sd_file(self, filename):
        path = self._path(filename)
        try:
            with self._mounted_sd():
                os.remove(path)
        except OSError as exc:
            raise StorageError("SD card file could not be deleted") from exc

    def delete_sd_seed(self, filename):
        if filename not in self.list_sd_seeds():
            raise StorageError("Seed file was not found on this SD card")
        self.delete_sd_file(filename)
