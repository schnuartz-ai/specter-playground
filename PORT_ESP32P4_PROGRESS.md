# ESP32-P4 Port Progress

## 2026-06-08

- Inspected the local fork before adding port files.
- `docs/esp32p4_goal.md` was not present in the worktree, so this progress follows the goal text from the active thread.
- `bd` is required by `AGENTS.md`, but the `bd` executable is not installed in this environment.
- Local ESP32 content is the MicroPython ESP32 port under `f469-disco/micropython/ports/esp32`; its README lists ESP32, ESP32-S2, ESP32-S3, ESP32-C3, and ESP32-C6, but not ESP32-P4.
- Added `ports/esp32p4_waveshare_35`, an ESP-IDF prototype app for the Waveshare ESP32-P4-WIFI6-Touch-LCD-3.5 board.
- Vendored the Waveshare BSP component from their reference example after local inspection. The BSP configures:
  - ST7796 LCD over SPI2: MOSI GPIO20, CLK GPIO21, CS GPIO23, DC GPIO26, reset GPIO27.
  - Backlight PWM: GPIO28.
  - FT5x06-compatible touch over I2C: SDA GPIO7, SCL GPIO8, reset GPIO29, interrupt GPIO50.
  - 320x480 RGB565 LVGL display path using ESP LVGL adapter and PSRAM buffers.
- Added a minimal Specter-like LVGL UI with touch navigation and mock-only wallet/settings/security screens.
- Added security limitation text to the app and README: no real wallet secrets, no signing, no storage, no secure boot, no flash encryption.
- `idf.py build` was attempted from `ports/esp32p4_waveshare_35` and failed immediately because `idf.py` is not on `PATH`.
- Attempted to install ESP-IDF 5.5.1 outside the repo with:

```sh
git clone --depth 1 --branch v5.5.1 --recursive https://github.com/espressif/esp-idf.git /tmp/esp-idf-v5.5.1
```

  This failed with `Failed to connect to github.com port 443`.

## Current Blockers

- ESP-IDF is not installed or not exported in this shell; `idf.py` was not found.
- A temporary ESP-IDF clone/install could not be completed because GitHub was unreachable from this shell during the attempt.
- `esptool` is not installed in this Python environment.
- No USB serial device is visible under `/dev/serial/by-id`, `/dev/ttyACM*`, or `/dev/ttyUSB*`, so the board cannot be detected or flashed from this environment yet.

## Next Steps

- Install/export ESP-IDF 5.5.1 or newer with ESP32-P4 toolchain support.
- Build with:

```sh
cd ports/esp32p4_waveshare_35
idf.py set-target esp32p4
idf.py build
```

- Connect the board, identify its serial device, then flash and monitor:

```sh
idf.py -p /dev/ttyACM0 flash monitor
```

- Iterate on touch orientation, color order, and screen rotation from hardware observations.
