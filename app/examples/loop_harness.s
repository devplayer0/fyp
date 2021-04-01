.syntax unified
.thumb
.section .text

.global do_test
do_test:
  push {lr}
  ldr r0, =loop_size
  ldr r0, [r0]
  bl test
  pop {pc}


.section .bss

.global loop_size
loop_size: .space LOOP_SIZE_SPACE
