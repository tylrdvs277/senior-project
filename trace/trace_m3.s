.arch armv7a
.global trace
trace:
	push {r5, r6, r7, r8, r9, r10, fp, lr}
	add fp, sp, #32
	
	mov r5, r0
	
	
	mov r9, r1
	
	
	mov r6, r2
	
	
	mov r10, r3
	
	
	lsl r7, r10, #2
	
	
	add r8, r9, r7
	
	
	ldr r9, [r8]
	
	
	cmp r9, #0
	
	
	beq L19_trace
	
	
	ldr r10, [r6]
	
	
	str r10, [r8]
	
	
	b L22_trace
	

L19_trace:

	
	ldr r9, [r5,r7]
	

L22_trace:

	
	ldr r10, [r5,r7]
	
	
	add r10, r10, r9
	
	
	str r10, [r6,r7]
	
	
	mov r0, r9
	
	pop {r5, r6, r7, r8, r9, r10, fp, pc}
