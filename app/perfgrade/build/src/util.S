.syntax unified
.thumb
.section .text

.global m5_exit
m5_exit:
  .short 0xEE00 | 0x21
  .short 0x0110
  bx lr
