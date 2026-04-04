# Specter DIY — Page Hierarchy & Navigation Map

## Dashboard (Main Screen)
```
┌─────────────────────────────────────────────┐
│ [Battery]                         [≡ Menu]  │  Top Bar
├─────────────────────────────────────────────┤
│ mainseed ▼                                  │  Seed Dropdown
├─────────────────────────────────────────────┤
│ Wallets                              [🔧]   │  Wallet Section
│ ├─ Default (pinned)                         │
│ ├─ 21bitcoin App          ●                 │
│ ├─ No KYC               1                  │
│ └─ (scroll for more)                        │
├─────────────────────────────────────────────┤
│         [ Receive ]                         │
│         [   SCAN   ]  ← larger              │  Action Buttons
│         [ SD Card  ]                        │
├─────────────────────────────────────────────┤
│ [🔑 Seed]    [🏠 Home]    [← Back]         │  Nav Bar
└─────────────────────────────────────────────┘
```

## Screen Map

### From Dashboard
- **Seed Dropdown** (tap) → inline seed selector overlay
- **Wallet row** (tap) → select wallet
- **Wallet row** (long-press) → `Wallet Details` page
- **Wrench icon** → `Wallet Menu` page
- **Receive button** → `Receive Addresses` page
- **Scan button** → `QR Scanner` page
- **SD Card button** → `SD Card Browser` page
- **Hamburger (≡)** → `Settings` page
- **Seed icon (nav)** → `Seed Management` page
- **Home (nav)** → Dashboard
- **Back (nav)** → previous page

---

## Full Page Tree

```
Dashboard
│
├── Seed Dropdown (overlay)
│   └── [list of loaded seeds — tap to switch]
│
├── Wallet Menu (wrench icon)
│   ├── [all wallets listed with 3 parameters: address type | sig type | account]
│   ├── tap → select wallet → Dashboard
│   ├── long-press → Wallet Details
│   └── delete button (per wallet, except Default)
│
├── Wallet Details (long-press any wallet)
│   ├── Rename Wallet → Rename Screen (keyboard input)
│   ├── Show Advanced Details → placeholder
│   ├── Show Receive Addresses → Receive Screen
│   ├── Show Change Addresses → placeholder
│   ├── [Multi-Sig] Show Co-Signers → placeholder
│   ├── Connect Companion App → Connect App Screen
│   │   └── [8 apps: Specter Desktop, Sparrow, Nunchuk, Bitcoin Keeper,
│   │        Bitcoin Safe, BlueWallet, Bull Bitcoin, Liana Wallet]
│   ├── Export Wallet → Export Menu
│   │   ├── Export via QR Code
│   │   ├── Export to SD Card
│   │   ├── Export xPub
│   │   └── [Multi-Sig] Export Multisig Config
│   └── Sign Message → placeholder
│
├── Receive Addresses
│   ├── Address list (clickable → QR display)
│   ├── Address reuse warning (yellow highlight)
│   └── Toggle: Receive ↔ Change addresses (subtle top button)
│
├── QR Scanner
│   ├── Viewfinder
│   └── Auto-detects: Transaction → Signing | Descriptor → Add Wallet | Address → Verify
│
├── SD Card Browser
│   ├── Files sorted by type (color-coded):
│   │   ├── 🟠 Transaction (PSBT)
│   │   ├── 🔵 Descriptor
│   │   └── 🟢 Address
│   ├── tap → process file
│   └── long-press → delete
│
├── Signing Screen (from Scan or SD Card)
│   ├── Transaction summary (to, amount, fee, wallet)
│   ├── [Confirm & Sign] button (green)
│   └── [Reject] button (red outline)
│
├── Seed Management (left nav button)
│   ├── Generate New Seed → Generate Seed Screen
│   │   └── Name input + fingerprint preview + Create button
│   ├── Import from QR → QR Scanner
│   ├── Import from SD Card → SD Card Browser
│   ├── Enter Manually → Enter Seed Words Screen
│   │   └── Word-by-word input with 12/24 selector + BIP39 suggestions
│   └── [Loaded Seeds List]
│       └── tap seed → Seed Detail Screen
│           ├── Set Passphrase → Passphrase Screen (keyboard input)
│           ├── Show Seed Words → Show Seed Words Screen (reveal/hide + warning)
│           ├── BIP85 Derivation → placeholder
│           ├── Backup Seed → placeholder
│           ├── Store Seed → placeholder
│           └── Delete Seed (red, immediate)
│
└── Settings (hamburger menu) — independent page
    ├── [Interface Status Bar: QR | USB | SD | SmartCard icons]
    │
    ├── Device
    │   ├── Power toggle
    │   ├── Lock Device toggle → Lock Screen (PIN pad)
    │   ├── Manage Interfaces → Interfaces Screen
    │   │   └── [toggle switches: QR, USB, SD, SmartCard]
    │   └── Language → Language Screen
    │       └── [language list with checkmark]
    │
    ├── Security
    │   ├── Backup / Restore → placeholder
    │   └── Firmware Info → placeholder
    │
    ├── Security
    │   ├── Backup / Restore → placeholder
    │   ├── Firmware Info → Firmware Screen (version + update from SD)
    │   └── xPub Export → xPub Export Screen (derivation paths + QR)
    │
    └── Danger Zone
        └── Wipe Device → Confirm Wipe Screen (red warning + confirm/cancel)
```

## Wallet Parameter Icons (Dashboard + Wallet Menu)

| Parameter | Default (cleanest) | Non-default |
|-----------|-------------------|-------------|
| Single Sig + Native Segwit | no icon | — |
| Multi-Sig | — | 🔑🔑 orange two-keys icon |
| Legacy address | — | **L** orange letter |
| Nested Segwit | — | **nS** cyan letter |
| Taproot | — | **T** green letter |
| Account > 0 | — | small cyan number |
| Shared with app | — | green dots (one per app) |

## Bottom Navigation

| Button | Icon | Action |
|--------|------|--------|
| Left | Key | Seed Management page |
| Center | Home | Dashboard (clears history) |
| Right | ← Arrow | Back one screen |
