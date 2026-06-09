#include <stdint.h>
#include <stdio.h>

#include "bsp/display.h"
#include "bsp/esp-bsp.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lvgl.h"
#include "nvs_flash.h"

static const char *TAG = "specter_p4";

typedef struct {
    const char *title;
    const char *subtitle;
    const char *primary;
    const char *secondary;
} screen_model_t;

static const screen_model_t screens[] = {
    {
        .title = "Specter DIY",
        .subtitle = "ESP32-P4 hardware prototype",
        .primary = "Wallets",
        .secondary = "Settings",
    },
    {
        .title = "Wallets",
        .subtitle = "Mock wallet state only",
        .primary = "Hot Wallet",
        .secondary = "Back",
    },
    {
        .title = "Settings",
        .subtitle = "Display and touch are active",
        .primary = "Security",
        .secondary = "Back",
    },
    {
        .title = "Security",
        .subtitle = "No real secrets. No signing. No storage.",
        .primary = "Prototype only",
        .secondary = "Back",
    },
};

static lv_obj_t *screen;
static lv_obj_t *title_label;
static lv_obj_t *subtitle_label;
static lv_obj_t *status_label;
static lv_obj_t *left_btn_label;
static lv_obj_t *right_btn_label;
static size_t screen_index;

static lv_style_t style_bg;
static lv_style_t style_card;
static lv_style_t style_button;
static lv_style_t style_button_alt;
static lv_style_t style_status;

static void show_screen(size_t index);

static void nav_event_cb(lv_event_t *event)
{
    intptr_t action = (intptr_t)lv_event_get_user_data(event);

    if (action == 0) {
        if (screen_index == 0) {
            show_screen(1);
        } else if (screen_index == 1) {
            show_screen(0);
        } else if (screen_index == 2) {
            show_screen(3);
        } else {
            show_screen(2);
        }
        return;
    }

    if (screen_index == 0) {
        show_screen(2);
    } else {
        show_screen(0);
    }
}

static lv_obj_t *make_button(lv_obj_t *parent, const char *text, const lv_style_t *style, intptr_t action)
{
    lv_obj_t *button = lv_button_create(parent);
    lv_obj_remove_style_all(button);
    lv_obj_add_style(button, style, 0);
    lv_obj_set_size(button, 136, 52);
    lv_obj_add_event_cb(button, nav_event_cb, LV_EVENT_CLICKED, (void *)action);

    lv_obj_t *label = lv_label_create(button);
    lv_label_set_text(label, text);
    lv_obj_center(label);

    if (action == 0) {
        left_btn_label = label;
    } else {
        right_btn_label = label;
    }

    return button;
}

static void init_styles(void)
{
    lv_style_init(&style_bg);
    lv_style_set_bg_color(&style_bg, lv_color_hex(0x101418));
    lv_style_set_text_color(&style_bg, lv_color_hex(0xf5f7fa));
    lv_style_set_text_font(&style_bg, &lv_font_montserrat_16);

    lv_style_init(&style_card);
    lv_style_set_bg_color(&style_card, lv_color_hex(0x1d252d));
    lv_style_set_border_color(&style_card, lv_color_hex(0x334250));
    lv_style_set_border_width(&style_card, 1);
    lv_style_set_radius(&style_card, 8);
    lv_style_set_pad_all(&style_card, 16);

    lv_style_init(&style_button);
    lv_style_set_bg_color(&style_button, lv_color_hex(0xf08a24));
    lv_style_set_text_color(&style_button, lv_color_hex(0x111111));
    lv_style_set_text_font(&style_button, &lv_font_montserrat_16);
    lv_style_set_radius(&style_button, 6);

    lv_style_init(&style_button_alt);
    lv_style_set_bg_color(&style_button_alt, lv_color_hex(0x2c3946));
    lv_style_set_text_color(&style_button_alt, lv_color_hex(0xf5f7fa));
    lv_style_set_text_font(&style_button_alt, &lv_font_montserrat_16);
    lv_style_set_radius(&style_button_alt, 6);

    lv_style_init(&style_status);
    lv_style_set_bg_color(&style_status, lv_color_hex(0x22311f));
    lv_style_set_text_color(&style_status, lv_color_hex(0xb9f6a5));
    lv_style_set_radius(&style_status, 6);
    lv_style_set_pad_all(&style_status, 8);
}

static void build_ui(void)
{
    init_styles();

    screen = lv_obj_create(NULL);
    lv_obj_remove_style_all(screen);
    lv_obj_add_style(screen, &style_bg, 0);
    lv_obj_set_size(screen, BSP_LCD_H_RES, BSP_LCD_V_RES);
    lv_obj_set_flex_flow(screen, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(screen, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_all(screen, 16, 0);
    lv_obj_set_style_pad_gap(screen, 12, 0);

    lv_obj_t *top = lv_obj_create(screen);
    lv_obj_remove_style_all(top);
    lv_obj_set_width(top, LV_PCT(100));
    lv_obj_set_height(top, 52);
    lv_obj_set_flex_flow(top, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(top, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    lv_obj_t *brand = lv_label_create(top);
    lv_label_set_text(brand, "SPECTER");
    lv_obj_set_style_text_font(brand, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(brand, lv_color_hex(0xf08a24), 0);

    lv_obj_t *battery = lv_label_create(top);
    lv_label_set_text(battery, "USB 100%");
    lv_obj_set_style_text_color(battery, lv_color_hex(0xa7b0ba), 0);

    lv_obj_t *card = lv_obj_create(screen);
    lv_obj_remove_style_all(card);
    lv_obj_add_style(card, &style_card, 0);
    lv_obj_set_width(card, LV_PCT(100));
    lv_obj_set_height(card, 230);
    lv_obj_set_flex_flow(card, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_gap(card, 12, 0);

    title_label = lv_label_create(card);
    lv_obj_set_style_text_font(title_label, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(title_label, lv_color_hex(0xffffff), 0);
    lv_label_set_long_mode(title_label, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(title_label, LV_PCT(100));

    subtitle_label = lv_label_create(card);
    lv_obj_set_style_text_color(subtitle_label, lv_color_hex(0xc7d0d9), 0);
    lv_label_set_long_mode(subtitle_label, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(subtitle_label, LV_PCT(100));

    status_label = lv_label_create(card);
    lv_obj_add_style(status_label, &style_status, 0);
    lv_label_set_long_mode(status_label, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(status_label, LV_PCT(100));

    lv_obj_t *buttons = lv_obj_create(screen);
    lv_obj_remove_style_all(buttons);
    lv_obj_set_width(buttons, LV_PCT(100));
    lv_obj_set_height(buttons, 68);
    lv_obj_set_flex_flow(buttons, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(buttons, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    make_button(buttons, "Wallets", &style_button, 0);
    make_button(buttons, "Settings", &style_button_alt, 1);

    lv_obj_t *footer = lv_label_create(screen);
    lv_label_set_text(footer, "Display: ST7796 SPI 320x480 | Touch: FT5x06 I2C | Demo data only");
    lv_obj_set_style_text_color(footer, lv_color_hex(0x8d98a3), 0);
    lv_label_set_long_mode(footer, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(footer, LV_PCT(100));

    show_screen(0);
    lv_screen_load(screen);
}

static void show_screen(size_t index)
{
    screen_index = index;
    const screen_model_t *model = &screens[index];

    lv_label_set_text(title_label, model->title);
    lv_label_set_text(subtitle_label, model->subtitle);
    lv_label_set_text(status_label, "Security limitation: this build has no secure boot, flash encryption, entropy validation, or wallet secret handling.");
    lv_label_set_text(left_btn_label, model->primary);
    lv_label_set_text(right_btn_label, model->secondary);
}

void app_main(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Starting Specter ESP32-P4 Waveshare 3.5 prototype");

    bsp_display_cfg_t cfg = {
        .lv_adapter_cfg = ESP_LV_ADAPTER_DEFAULT_CONFIG(),
    };
    lv_display_t *disp = bsp_display_start_with_config(&cfg);
    ESP_ERROR_CHECK(disp ? ESP_OK : ESP_FAIL);
    ESP_ERROR_CHECK(bsp_display_backlight_on());

    if (bsp_display_lock((uint32_t)-1)) {
        build_ui();
        bsp_display_unlock();
    } else {
        ESP_LOGE(TAG, "Timed out waiting for LVGL lock");
    }

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
