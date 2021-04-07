.syntax unified
.thumb
.section .text

.global do_test
do_test:
  push {r4-ip, lr}

  ldr r0, =square
  ldr r1, =size
  ldr r1, [r1]

  ldr r2, =sub
  ldr r3, =sub_size
  ldr r3, [r3]
  bl Main

  ldr r1, =result
  str r0, [r1]

  pop {r4-ip, pc}


.section .bss

.global size
.global square

.global sub
.global sub_size

size: .word 0
square: .space SQUARE_SPACE

sub_size: .word 0
sub: .space SUB_SPACE

.global result
result: .word 0
