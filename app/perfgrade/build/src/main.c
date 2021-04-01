#include <libopencm3/cm3/scb.h>
#include <libopencm3/cm3/dwt.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/flash.h>

#include "util.h"
#include "harness.h"
#include "uut.h"

const struct rcc_clock_scale hsi_2mhz = {
    // Division factor for PLL VCO input (HSI = 16MHz -> /16 = 1MHz)
    .pllm = 16,
    // Multiplication for PLL VCO output (1MHz x 64 = 192MHz)
    .plln = 192,
    // Division factor of VCO output for system clock (192MHz / 8 = 32MHz)
    .pllp = 6,
    // Division factor of VCO output for USB etc. clock (should be 48MHz, 192/4 = 48MHz)
    .pllq = 4,
    .pllr = 0,
    .pll_source = RCC_CFGR_PLLSRC_HSI_CLK,
    // AHB prescale = (PLLP / 16 -> 32MHz / 16 = 2MHz)
    .hpre = RCC_CFGR_HPRE_DIV16,
    // APB1 (low speed) prescale = (HCLK / 1 -> 2MHz)
    .ppre1 = RCC_CFGR_PPRE_NODIV,
    // APB2 (high speed) prescale = (HCLK / 1 -> 2MHz)
    .ppre2 = RCC_CFGR_PPRE_NODIV,
    .voltage_scale = PWR_SCALE1,
    .flash_config = FLASH_ACR_DCEN | FLASH_ACR_ICEN |
                    FLASH_ACR_LATENCY_0WS,
    .ahb_frequency  = 1000000,
    .apb1_frequency = 1000000,
    .apb2_frequency = 1000000,
};

static inline bool is_sim(void) {
    return SCB_CPUID == 0xcafebabe;
}

static inline void null_do(void) {
    test();
}
static inline void null_finish(void) {}

#pragma weak do_test = null_do
#pragma weak finish_test = null_finish

int main(void) {
    if (!is_sim()) {
        // Bring the clock up to 168MHz
        rcc_clock_setup_pll(&rcc_hse_8mhz_3v3[RCC_CLOCK_3V3_168MHZ]);

        // TODO: Fine-grained cycle counting
        dwt_enable_cycle_counter();
        DWT_CYCCNT = 0;
    }

    do_test();
__asm__("test_end:");
    finish_test();

    if (!is_sim()) {
        // Clock down the CPU now that we're done
        rcc_clock_setup_pll(&hsi_2mhz);
    } else {
        m5_exit(0);
    }

__asm__("eval_done:");

    return 0;
}
