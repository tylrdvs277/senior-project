.arch armv7a
.global trace
trace:
	push {r5, r6, r7, r8, r9, r10, fp, lr}
	add fp, sp, #32
	
	mov r10, r3
	
	
	lsl r5, r10, #2
	
	
	mov r10, r1
	
	
	mov r6, r2
	
	
	add r7, r10, r5
	
	
	ldr r8, [r7]
	
	
	ldr r9, [r6]
	
	
	mov r10, r0
	
	
	cmp r8, #0
	
	
	beq L19_trace
	
	
	str r9, [r7]
	
	
	b L22_trace
	

L19_trace:

	
	ldr r8, [r10,r5]
	

L22_trace:

	
	ldr r10, [r10,r5]
	
	
	add r10, r10, r8
	
	
	mov r0, r8
	
	
	str r10, [r6,r5]
	
	pop {r5, r6, r7, r8, r9, r10, fp, pc}
