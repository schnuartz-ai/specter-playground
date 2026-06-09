# Final Status

The Waveshare ESP32-P4-WIFI6-Touch-LCD-3.5 port is not complete yet.

Current state:

- A local ESP-IDF prototype exists at `ports/esp32p4_waveshare_35`.
- The prototype uses the Waveshare BSP for LCD, touch, backlight, LVGL, and PSRAM display buffering.
- The app shows a Specter-like mock UI and includes explicit security limitation text.
- No real wallet secrets are used or handled.
- ESP-IDF v5.5.1 with ESP32-P4 support was installed outside the repository at `/tmp/esp-idf-v5.5.1`.
- A clean `idf.py set-target esp32p4 && idf.py build` completed successfully.
- The generated app binary is `ports/esp32p4_waveshare_35/build/specter_esp32p4_waveshare_35.bin`.
- App binary size is `0xc48d0` bytes, with `0x73b730` bytes free in the smallest app partition.

Unverified requirements:

- USB board detection: blocked because no `/dev/serial/by-id`, `/dev/ttyACM*`, or `/dev/ttyUSB*` device is visible.
- USB bus inspection: `lsusb` is unavailable in this shell.
- `/sys/bus/usb/devices` only shows WSL2 USB/IP virtual host controllers, not the ESP32-P4 board.
- Flashing: not attempted because no serial board is visible.
- Real hardware display/touch verification: not complete.
- Touch orientation, color order, screen rotation, and responsiveness still need hardware validation.

Security limitations:

- No secure boot configuration.
- No flash encryption configuration.
- No wallet storage, seed import, signing, PSBT processing, QR signing, or host communication.
- UI data is mock-only and suitable only for hardware bring-up.

Issue tracking note:

- `bd` is required by `AGENTS.md`, but `bd ready --json` cannot run because the `bd` executable is not installed in this environment.
