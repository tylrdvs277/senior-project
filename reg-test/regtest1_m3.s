.arch armv7a
.global regtest1
regtest1:
	mov fp, sp
	push {r4, r5, r6, r7, r8, r9, r10, lr}
	sub sp, sp, #88
	
	mov r9, r0
	
	
	bl getint
	
	
	mov r3, r0
	
	
	str r3, [sp,#76]
	
	
	bl getint
	
	
	mov r3, r0
	
	
	str r3, [sp,#80]
	
	
	ldr r3, [sp,#76]
	
	
	add r3, r3, r9
	
	
	str r3, [sp,#84]
	
	
	ldr r3, [sp,#80]
	
	
	add r5, r3, r9
	
	
	ldr r3, [sp,#84]
	
	
	add r3, r3, r5
	
	
	str r3, [sp,#0]
	
	
	bl getint
	
	
	mov r6, r0
	
	
	bl getint
	
	
	mov r7, r0
	
	
	add r4, r6, #1
	
	
	add r10, r7, #-1
	
	
	add r3, r4, r10
	
	
	str r3, [sp,#4]
	
	
	bl getint
	
	
	mov r8, r0
	
	
	bl getint
	
	
	mov r2, r0
	
	
	add r0, r8, r2
	
	
	ldr r1, [sp,#76]
	
	
	ldr r3, [sp,#80]
	
	
	add r3, r1, r3
	
	
	str r3, [sp,#8]
	
	
	ldr r1, [sp,#8]
	
	
	ldr r3, [sp,#84]
	
	
	add r3, r1, r3
	
	
	str r3, [sp,#12]
	
	
	ldr r3, [sp,#12]
	
	
	add r3, r3, r5
	
	
	str r3, [sp,#16]
	
	
	ldr r5, [sp,#0]
	
	
	ldr r3, [sp,#16]
	
	
	add r3, r3, r5
	
	
	str r3, [sp,#20]
	
	
	ldr r3, [sp,#20]
	
	
	add r3, r3, r6
	
	
	str r3, [sp,#24]
	
	
	ldr r3, [sp,#24]
	
	
	add r3, r3, r7
	
	
	str r3, [sp,#28]
	
	
	ldr r3, [sp,#28]
	
	
	add r3, r3, r4
	
	
	str r3, [sp,#32]
	
	
	ldr r3, [sp,#32]
	
	
	add r3, r3, r10
	
	
	str r3, [sp,#36]
	
	
	ldr r10, [sp,#4]
	
	
	ldr r3, [sp,#36]
	
	
	add r3, r3, r10
	
	
	str r3, [sp,#40]
	
	
	ldr r3, [sp,#40]
	
	
	add r3, r3, r8
	
	
	str r3, [sp,#44]
	
	
	ldr r3, [sp,#44]
	
	
	add r3, r3, r2
	
	
	str r3, [sp,#48]
	
	
	sub r3, r8, r2
	
	
	str r3, [sp,#52]
	
	
	ldr r10, [sp,#48]
	
	
	ldr r3, [sp,#52]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#56]
	
	
	ldr r3, [sp,#56]
	
	
	add r3, r3, r0
	
	
	str r3, [sp,#60]
	
	
	add r3, r9, r0
	
	
	str r3, [sp,#64]
	
	
	ldr r10, [sp,#60]
	
	
	ldr r3, [sp,#64]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#68]
	
	
	ldr r3, [sp,#68]
	
	
	str r3, [sp,#72]
	
	
	ldr r3, [sp,#72]
	
	
	mov r0, r3
	
	add sp, sp, #88
	pop {r4, r5, r6, r7, r8, r9, r10, pc}
