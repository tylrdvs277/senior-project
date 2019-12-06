.arch armv7a
.global matadd
matadd:
	mov fp, sp
	push {r4, r5, r6, r7, r8, r9, r10, lr}
	
	mov r4, r3
	
	
	ldr r5, [fp]
	
	
	cmp r4, #0
	
	
	beq L69_matadd
	
	
	mov r6, #0
	

L64_matadd:

	
	cmp r5, #0
	
	
	beq L61_matadd
	
	
	mov r7, #0
	

L58_matadd:

	
	lsl r8, r7, #2
	
	
	ldr r9, [r0,r6,lsl#2]
	
	
	ldr r3, [r1,r6,lsl#2]
	
	
	ldr r10, [r2,r6,lsl#2]
	
	
	ldr r3, [r3,r8]
	
	
	ldr r10, [r10,r8]
	
	
	add r10, r3, r10
	
	
	str r10, [r9,r8]
	
	
	add r7, r7, #1
	
	
	cmp r5, r7
	
	
	bne L58_matadd
	

L61_matadd:

	
	add r6, r6, #1
	
	
	cmp r4, r6
	
	
	bne L64_matadd
	

L69_matadd:

	pop {r4, r5, r6, r7, r8, r9, r10, pc}
