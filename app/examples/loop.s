.syntax unified
.thumb
.section .text

.global test
test:
  // r0 contains the loop count
  mov r1, #0
.Lloop:
  cmp r1, r0
  beq .Leloop

  mov r2, #0
.Lloop2:
  cmp r2, r0
  beq .Leloop2

#  mov r3, #0
#.Lloop3:
#  cmp r3, r0
#  beq .Leloop3
#  add r3, #1
#  b .Lloop3
#.Leloop3:

  add r2, #1
  b .Lloop2
.Leloop2:

  add r1, #1
  b .Lloop
.Leloop:
  bx lr
