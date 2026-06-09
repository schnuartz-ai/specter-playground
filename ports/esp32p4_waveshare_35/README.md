# ESP32-P4 Waveshare 3.5 Prototype

This is a local ESP-IDF prototype for the Waveshare ESP32-P4-WIFI6-Touch-LCD-3.5 board.

It keeps the local Specter fork as the source of truth and vendors only the Waveshare board support component needed to bring up display, touch, and LVGL on the target hardware.

## Build

Install and export ESP-IDF 5.5.1 or newer for `esp32p4`, then run:

```sh
cd ports/esp32p4_waveshare_35
idf.py set-target esp32p4
idf.py build
```

## Flash

Connect the board over USB, then run:

```sh
idf.py -p /dev/ttyACM0 flash monitor
```

Adjust the port to the device shown under `/dev/serial/by-id`, `/dev/ttyACM*`, or `/dev/ttyUSB*`.

## Security Status

This firmware is a hardware bring-up prototype. It does not implement secure boot, flash encryption, wallet storage, signing, seed import, QR signing, or host protocol handling. It uses mock screen state only and must not be used with real wallet secrets.
