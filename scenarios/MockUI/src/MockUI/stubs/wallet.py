"""Wallet (descriptor) placeholder used by the MockUI state.

Keep this small and replace with the project's real Wallet model when ready.
Represents a persistent wallet descriptor — stored in flash, auto-loaded on boot.
"""


# Address types for visual indicators
ADDR_NATIVE_SEGWIT = "native_segwit"
ADDR_NESTED_SEGWIT = "nested_segwit"
ADDR_LEGACY = "legacy"
ADDR_TAPROOT = "taproot"


class Wallet:
    """Wallet descriptor placeholder used by SpecterState.

    Attributes:
        label: user-facing display name (renameable)
        descriptor: output descriptor string
        net: network ("mainnet" | "testnet" | "signet")
        isMultiSig: boolean flag indicating multisig wallet
        required_fingerprints: list of key fingerprints needed for signing
        threshold: multisig m-of-n (m value); None for singlesig
        address_type: one of ADDR_* constants
        account: BIP44 account index (0, 1, 2, ...)
        has_been_exported: whether exported to a companion app
        shared_with: list of companion app names this wallet was shared with
    """

    def __init__(self, label, descriptor=None, isMultiSig=False, net="mainnet",
                 required_fingerprints=None, threshold=None,
                 has_been_exported=False, address_type=None, account=0):
        self.label = label
        self.descriptor = descriptor
        self.isMultiSig = isMultiSig
        self.net = net
        self.threshold = threshold
        self.required_fingerprints = required_fingerprints or []
        self.address_type = address_type or ADDR_NATIVE_SEGWIT
        self.account = account or 0
        self.has_been_exported = has_been_exported
        self.shared_with = []  # list of app names e.g. ["Sparrow", "Nunchuk"]

        if isMultiSig:
            if not threshold or len(self.required_fingerprints) < threshold:
                threshold = len(self.required_fingerprints) or 1
                self.threshold = threshold

    def is_standard(self):
        return self.descriptor != "fancy script"

    def is_default_wallet(wallet):
        return wallet.label == "Default" and wallet.descriptor == "default"

    def mark_shared(self, app_name):
        """Mark this wallet as shared with a companion app."""
        self.has_been_exported = True
        if app_name not in self.shared_with:
            self.shared_with.append(app_name)
