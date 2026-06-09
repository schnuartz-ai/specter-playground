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

## 2026-06-09

- Installed ESP-IDF v5.5.1 outside the repository at `/tmp/esp-idf-v5.5.1` with ESP32-P4 toolchain support.
- Generated a clean `esp32p4` configuration from `sdkconfig.defaults`.
- Fixed the obsolete ESP-IDF option `CONFIG_SPIRAM_ALLOW_STACK_EXTERNAL_MEMORY` by using `CONFIG_FREERTOS_TASK_CREATE_ALLOW_EXT_MEM`.
- Added `.gitignore` entries for generated ESP-IDF output: `build/`, `managed_components/`, `sdkconfig`, and `sdkconfig.old`.
- Built the prototype successfully from `ports/esp32p4_waveshare_35`:

```sh
source /tmp/esp-idf-v5.5.1/export.sh
cd ports/esp32p4_waveshare_35
idf.py set-target esp32p4
idf.py build
```

- Build output generated:
  - `build/bootloader/bootloader.bin`
  - `build/partition_table/partition-table.bin`
  - `build/specter_esp32p4_waveshare_35.bin`
- App binary size: `0xc48d0` bytes. The smallest app partition is `0x800000` bytes, leaving `0x73b730` bytes free.
- The only remaining configure/build warning observed is the vendored BSP duplicate Kconfig symbol:

```text
Symbol BSP_I2S_NUM defined in multiple locations:
  components/esp32_p4_wifi6_touch_lcd_35/Kconfig:30
  components/bsp_extra/Kconfig:2
```

- Rechecked USB serial devices after the successful build. No board is visible under `/dev/serial/by-id`, `/dev/ttyACM*`, or `/dev/ttyUSB*`.
- `lsusb` is not installed in this shell, so USB bus-level inspection is unavailable here.
- `/sys/bus/usb/devices` only shows WSL2 USB/IP virtual host controllers, not the ESP32-P4 board.

## Current Blockers

- No USB serial device is visible under `/dev/serial/by-id`, `/dev/ttyACM*`, or `/dev/ttyUSB*`, so the board cannot be detected or flashed from this environment yet.
- The WSL2 environment does not currently have the board attached via USB/IP.
- Real hardware display, touch, rotation, color order, and UI interaction are not verified.
- `bd` is required by `AGENTS.md`, but the `bd` executable is not installed in this environment.

## Next Steps

- Connect the board, identify its serial device, then flash and monitor:

```sh
source /tmp/esp-idf-v5.5.1/export.sh
cd ports/esp32p4_waveshare_35
idf.py -p /dev/ttyACM0 flash monitor
```

- Iterate on touch orientation, color order, and screen rotation from hardware observations.
