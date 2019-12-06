.arch armv7a
.global regtest2
regtest2:
	mov fp, sp
	push {r4, r5, r6, r7, r8, r9, r10, lr}
	sub sp, sp, #140
	
	mov r6, r0
	
	
	bl getint
	
	
	mov r3, r0
	
	
	str r3, [sp,#136]
	
	
	bl getint
	
	
	mov r7, r0
	
	
	cmp r6, #0
	
	
	ble L17_regtest2
	
	
	ldr r3, [sp,#136]
	
	
	add r8, r3, r6
	
	
	add r10, r7, r6
	
	
	b L21_regtest2
	

L17_regtest2:

	
	ldr r3, [sp,#136]
	
	
	sub r8, r3, r6
	
	
	sub r10, r7, r6
	

L21_regtest2:

	
	bl getint
	
	
	mov r4, r0
	
	
	bl getint
	
	
	mov r5, r0
	
	
	add r3, r8, r10
	
	
	str r3, [sp,#112]
	
	
	cmp r4, r5
	
	
	ble L35_regtest2
	
	
	add r3, r4, #1
	
	
	str r3, [sp,#128]
	
	
	add r3, r5, #-1
	
	
	str r3, [sp,#132]
	
	
	b L39_regtest2
	

L35_regtest2:

	
	add r3, r4, #1
	
	
	str r3, [sp,#132]
	
	
	add r3, r5, #-1
	
	
	str r3, [sp,#128]
	

L39_regtest2:

	
	bl getint
	
	
	mov r9, r0
	
	
	bl getint
	
	
	ldr r2, [sp,#128]
	
	
	ldr r3, [sp,#132]
	
	
	add r3, r2, r3
	
	
	mov r2, r0
	
	
	str r3, [sp,#104]
	
	
	cmp r9, r2
	
	
	ble L56_regtest2
	

L53_regtest2:

	
	bl getint
	
	
	mov r9, r0
	
	
	bl getint
	
	
	mov r2, r0
	
	
	cmp r9, r2
	
	
	bgt L53_regtest2
	

L56_regtest2:

	
	add r3, r9, r2
	
	
	str r3, [sp,#120]
	
	
	ldr r3, [sp,#120]
	
	
	add r3, r6, r3
	
	
	str r3, [sp,#124]
	
	
	sub r3, r9, r2
	
	
	str r3, [sp,#116]
	
	
	ldr r3, [sp,#124]
	
	
	cmp r3, #0
	
	
	ble L80_regtest2
	
	
	ldr r3, [sp,#136]
	
	
	add r3, r3, r7
	
	
	str r3, [sp,#20]
	
	
	ldr r3, [sp,#20]
	
	
	add r3, r3, r8
	
	
	str r3, [sp,#24]
	
	
	ldr r3, [sp,#24]
	
	
	add r3, r3, r10
	
	
	str r3, [sp,#28]
	
	
	ldr r10, [sp,#28]
	
	
	ldr r3, [sp,#112]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#32]
	
	
	ldr r3, [sp,#32]
	
	
	add r3, r3, r4
	
	
	str r3, [sp,#36]
	
	
	ldr r3, [sp,#36]
	
	
	add r3, r3, r5
	
	
	str r3, [sp,#40]
	
	
	ldr r10, [sp,#40]
	
	
	ldr r3, [sp,#128]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#44]
	
	
	ldr r10, [sp,#44]
	
	
	ldr r3, [sp,#132]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#48]
	
	
	ldr r10, [sp,#48]
	
	
	ldr r3, [sp,#104]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#52]
	
	
	ldr r3, [sp,#52]
	
	
	add r3, r3, r9
	
	
	str r3, [sp,#56]
	
	
	ldr r3, [sp,#56]
	
	
	add r3, r3, r2
	
	
	str r3, [sp,#60]
	
	
	ldr r10, [sp,#60]
	
	
	ldr r3, [sp,#116]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#64]
	
	
	ldr r10, [sp,#64]
	
	
	ldr r3, [sp,#120]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#68]
	
	
	ldr r10, [sp,#68]
	
	
	ldr r3, [sp,#124]
	
	
	add r3, r10, r3
	
	
	str r3, [sp,#108]
	
	
	b L100_regtest2
	

L80_regtest2:

	
	ldr r3, [sp,#136]
	
	
	sub r3, r3, r7
	
	
	str r3, [sp,#72]
	
	
	ldr r3, [sp,#72]
	
	
	sub r3, r3, r8
	
	
	str r3, [sp,#76]
	
	
	ldr r3, [sp,#76]
	
	
	sub r3, r3, r10
	
	
	str r3, [sp,#80]
	
	
	ldr r10, [sp,#80]
	
	
	ldr r3, [sp,#112]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#84]
	
	
	ldr r3, [sp,#84]
	
	
	sub r3, r3, r4
	
	
	str r3, [sp,#92]
	
	
	ldr r3, [sp,#92]
	
	
	sub r3, r3, r5
	
	
	str r3, [sp,#88]
	
	
	ldr r10, [sp,#88]
	
	
	ldr r3, [sp,#128]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#96]
	
	
	ldr r10, [sp,#96]
	
	
	ldr r3, [sp,#132]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#100]
	
	
	ldr r10, [sp,#100]
	
	
	ldr r3, [sp,#104]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#16]
	
	
	ldr r3, [sp,#16]
	
	
	sub r3, r3, r9
	
	
	str r3, [sp,#12]
	
	
	ldr r3, [sp,#12]
	
	
	sub r3, r3, r2
	
	
	str r3, [sp,#4]
	
	
	ldr r10, [sp,#4]
	
	
	ldr r3, [sp,#116]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#8]
	
	
	ldr r10, [sp,#8]
	
	
	ldr r3, [sp,#120]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#0]
	
	
	ldr r10, [sp,#0]
	
	
	ldr r3, [sp,#124]
	
	
	sub r3, r10, r3
	
	
	str r3, [sp,#108]
	

L100_regtest2:

	
	ldr r3, [sp,#108]
	
	
	mov r0, r3
	
	add sp, sp, #140
	pop {r4, r5, r6, r7, r8, r9, r10, pc}
