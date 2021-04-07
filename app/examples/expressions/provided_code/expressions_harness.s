.syntax unified
.thumb
.section .text

.global do_test
do_test:
  push {r4-ip, lr}

  ldr r1, =expression
  ldr r12, =user_stack_top

  bl Main

  ldr r1, =result
  str r0, [r1]

  pop {r4-ip, pc}


.section .bss

.global expression
expression: .space EXPR_SPACE

.global result
result: .word 0

user_stack: .space STACK_SIZE
user_stack_top:
