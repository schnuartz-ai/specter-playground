"""SD-card presence and directory access for the MockUI."""

import os
from contextlib import contextmanager


class StorageError(Exception):
    """An SD-card operation failed."""


class SeedStorage:
    """Small filesystem adapter shared by the simulator and hardware."""

    def __init__(self, flash_root="/flash", sd_root="/sd"):
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

    @staticmethod
    def _ensure_dir(path):
        try:
            os.mkdir(path)
        except OSError:
            pass

    @staticmethod
    def _as_name(value):
        if isinstance(value, bytes):
            return value.decode("utf-8", "replace")
        return value

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

    def _list_names(self):
        with self._mounted_sd():
            try:
                entries = os.ilistdir(self.sd_root)
                names = []
                for entry in entries:
                    name = self._as_name(entry[0])
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
        """Mount the physical card for one filesystem operation."""
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

    def list_sd_files(self):
        """Return the card's regular files and their byte sizes."""
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
