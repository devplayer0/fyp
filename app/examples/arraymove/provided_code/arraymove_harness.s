.syntax unified
.thumb
.section .text

.global do_test
do_test:
  push {r4-ip, lr}

  ldr r0, =array
  ldr r1, =i
  ldr r1, [r1]
  ldr r2, =j
  ldr r2, [r2]
  bl Main

  pop {r4-ip, pc}

.section .bss

.global i
.global j
.global array

i: .word 0
j: .word 0
array: .space ARR_SPACE
