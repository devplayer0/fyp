PROJECT = perfgrade
BUILD_DIR = bin

CSTD = -std=c11
INCLUDES += -Iinclude
VPATH += src
CFILES = src/main.c
AFILES = src/util.S

DEVICE = stm32f407vgt6
#OOCD_FILE = board/stm32f1nucleo.cfg
#OOCD_FILE = board/stm32f4discovery.cfg
#OOCD_FILE = openocd.cfg

# You shouldn't have to edit anything below here.
# VPATH += $(SHARED_DIR)
# INCLUDES += $(patsubst %,-I%, . $(SHARED_DIR))
# OPENCM3_DIR=libopencm3

include $(OPENCM3_DIR)/mk/genlink-config.mk
include rules.mk
include $(OPENCM3_DIR)/mk/genlink-rules.mk
