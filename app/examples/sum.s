.syntax unified
.thumb
.section .text

.global test
test:
  push {r4}

  // r0 contains the sum array, r1 its length
  mov r2, #0
  mov r3, #0
.Lloop:
  cmp r2, r1
  beq .Leloop
  ldr r4, [r0, r2, lsl #2]
  add r3, r4
  add r2, #1
  b .Lloop
.Leloop:
  mov r0, r3

  pop {r4}
  bx lr
