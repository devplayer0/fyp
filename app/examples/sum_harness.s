.syntax unified
.thumb
.section .text

.global do_test
do_test:
  push {lr}

  ldr r0, =arr
  ldr r1, =arr_size
  ldr r1, [r1]
  bl test

  ldr r1, =sum
  str r0, [r1]

  pop {pc}


.section .bss

.global arr_size
.global arr
.global sum

arr_size: .space 4
arr: .space ARR_SPACE
sum: .space 4
