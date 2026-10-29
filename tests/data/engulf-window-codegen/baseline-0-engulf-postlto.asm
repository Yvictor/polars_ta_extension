
/tmp/polars-recovery/engulf-evidence/baseline/harness.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing>:
       0:      	movq	%rdi, %rax
       3:      	cmpq	$0x5f5e100, %rdx        # imm = 0x5F5E100
       a:      	jbe	0x13 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x13>
       c:      	movl	$0xc0001, (%rax)        # imm = 0xC0001
      12:      	retq
      13:      	cmpq	$0x5f5e101, %rcx        # imm = 0x5F5E101
      1a:      	setae	%sil
      1e:      	cmpq	%rdx, %rcx
      21:      	setb	%dil
      25:      	orb	%sil, %dil
      28:      	je	0x31 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x31>
      2a:      	movl	$0xd0001, (%rax)        # imm = 0xD0001
      30:      	retq
      31:      	cmpq	$0x3, %rdx
      35:      	movl	$0x2, %esi
      3a:      	cmovaeq	%rdx, %rsi
      3e:      	cmpq	%rcx, %r9
      41:      	jbe	0x10b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x10b>
      47:      	pushq	%rbp
      48:      	pushq	%r15
      4a:      	pushq	%r14
      4c:      	pushq	%r13
      4e:      	pushq	%r12
      50:      	pushq	%rbx
      51:      	subq	$0x18, %rsp
      55:      	movq	0x58(%rsp), %r10
      5a:      	cmpq	%rcx, %r10
      5d:      	jbe	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x112>
      63:      	movq	0x68(%rsp), %r11
      68:      	cmpq	%rcx, %r11
      6b:      	jbe	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x112>
      71:      	movq	0x78(%rsp), %rbx
      76:      	cmpq	%rcx, %rbx
      79:      	jbe	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x112>
      7f:      	movq	0x88(%rsp), %r15
      87:      	movq	%rcx, %rdi
      8a:      	subq	%rsi, %rdi
      8d:      	setae	%sil
      91:      	cmpq	%rdi, %r15
      94:      	setbe	%dil
      98:      	testq	%r15, %r15
      9b:      	je	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x112>
      9d:      	andb	%dil, %sil
      a0:      	jne	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x112>
      a2:      	movq	%rax, %r14
      a5:      	movq	0x80(%rsp), %rax
      ad:      	movq	0x70(%rsp), %r12
      b2:      	movq	$0x0, 0x8(%rsp)
      bb:      	movq	$0x0, 0x10(%rsp)
      c4:      	leaq	0x10(%rsp), %r13
      c9:      	leaq	0x8(%rsp), %rbp
      ce:      	movq	%rdx, %rdi
      d1:      	movq	%rcx, %rsi
      d4:      	movq	%r8, %rdx
      d7:      	movq	%r9, %rcx
      da:      	movq	%r10, %r8
      dd:      	movq	%r11, %r9
      e0:      	pushq	%r15
      e2:      	pushq	%rax
      e3:      	pushq	%r13
      e5:      	pushq	%rbp
      e6:      	pushq	%rbx
      e7:      	pushq	%r12
      e9:      	callq	0xee <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0xee>
		00000000000000ea:  R_X86_64_PLT32	_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579-0x4
      ee:      	addq	$0x30, %rsp
      f2:      	testw	%ax, %ax
      f5:      	je	0x127 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x127>
      f7:      	movl	%eax, %ecx
      f9:      	movq	%r14, %rax
      fc:      	movw	%cx, 0x2(%r14)
     101:      	movw	$0x1, %cx
     105:      	movw	%cx, (%r14)
     109:      	jmp	0x118 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x118>
     10b:      	movl	$0x20001, (%rax)        # imm = 0x20001
     111:      	retq
     112:      	movl	$0x20001, (%rax)        # imm = 0x20001
     118:      	addq	$0x18, %rsp
     11c:      	popq	%rbx
     11d:      	popq	%r12
     11f:      	popq	%r13
     121:      	popq	%r14
     123:      	popq	%r15
     125:      	popq	%rbp
     126:      	retq
     127:      	movq	0x8(%rsp), %rcx
     12c:      	movq	0x10(%rsp), %rdx
     131:      	movq	%r14, %rax
     134:      	movq	%rcx, 0x8(%r14)
     138:      	movq	%rdx, 0x10(%r14)
     13c:      	xorl	%ecx, %ecx
     13e:      	movw	%cx, (%r14)
     142:      	jmp	0x118 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core12cdlengulfing+0x118>
