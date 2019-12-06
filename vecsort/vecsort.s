.arch armv7a
.global vecsort
vecsort:
	mov fp, sp
	push {r4, r5, r6, r7, r8, r9, r10, lr}
	
	mov r10, r1
	
	
	add r4, r10, #-1
	
	
	mov r3, r0
	
	
	cmp r4, #0
	
	
	beq L77_vecsort
	
	
	add r10, r10, #1073741823
	
	
	lsl r10, r10, #2
	
	
	add r5, r3, r10
	
	
	mov r6, #0
	

L72_vecsort:

	
	mov r7, r3
	
	
	b L52_vecsort
	

L60_vecsort:

	
	add r7, r7, #4
	

L52_vecsort:

	
	cmp r7, r5
	
	
	beq L68_vecsort
	
	
	mov r8, r7
	
	
	ldr r9, [r8]
	
	
	ldr r10, [r8,#2]
	
	
	cmp r9, r10
	
	
	ble L60_vecsort
	
	
	str r10, [r8]
	
	
	str r9, [r8,#2]
	
	
	b L60_vecsort
	

L68_vecsort:

	
	add r6, r6, #1
	
	
	add r5, r5, #-4
	
	
	cmp r6, r4
	
	
	bne L72_vecsort
	

L77_vecsort:

	pop {r4, r5, r6, r7, r8, r9, r10, pc}
