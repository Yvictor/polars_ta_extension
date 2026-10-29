
/tmp/polars-recovery/engulf-evidence/baseline/harness.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%rbx
       6:      	pushq	%rax
       7:      	movw	$0xd, %ax
       b:      	cmpq	%rdi, %rsi
       e:      	jb	0x1f0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1f0>
      14:      	cmpq	$0x3, %rdi
      18:      	movl	$0x2, %r10d
      1e:      	cmovaeq	%rdi, %r10
      22:      	cmpq	$0x2, %rsi
      26:      	setb	%al
      29:      	cmpq	%rcx, %rsi
      2c:      	setb	%dil
      30:      	orb	%al, %dil
      33:      	je	0x1fb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1fb>
      39:      	cmpq	$0x2, %rsi
      3d:      	setb	%al
      40:      	cmpq	%r8, %rsi
      43:      	setb	%dil
      47:      	orb	%al, %dil
      4a:      	je	0x214 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x214>
      50:      	cmpq	$0x2, %rsi
      54:      	setb	%al
      57:      	cmpq	%r9, %rsi
      5a:      	setb	%dil
      5e:      	orb	%al, %dil
      61:      	je	0x22d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x22d>
      67:      	movq	0x38(%rsp), %r8
      6c:      	cmpq	$0x2, %rsi
      70:      	setb	%al
      73:      	cmpq	%r8, %rsi
      76:      	setb	%dil
      7a:      	orb	%al, %dil
      7d:      	je	0x246 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x246>
      83:      	movq	0x58(%rsp), %rax
      88:      	movq	%rsi, %rdi
      8b:      	subq	%r10, %rdi
      8e:      	cmpq	%rax, %rdi
      91:      	setb	%dil
      95:      	movb	$0x1, %r9b
      98:      	cmpq	$0x2, %rsi
      9c:      	jae	0x25f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x25f>
      a2:      	testb	%r9b, %r9b
      a5:      	je	0x26b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x26b>
      ab:      	movq	0x48(%rsp), %r9
      b0:      	movq	0x40(%rsp), %r11
      b5:      	cmpq	$0x2, %rsi
      b9:      	jae	0xce <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0xce>
      bb:      	movq	$0x0, (%r11)
      c2:      	movq	$0x0, (%r9)
      c9:      	jmp	0x1ee <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1ee>
      ce:      	cmpq	%rcx, %rsi
      d1:      	jae	0x284 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x284>
      d7:      	cmpq	%r8, %rsi
      da:      	jae	0x299 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x299>
      e0:      	movq	0x50(%rsp), %r8
      e5:      	movq	0x30(%rsp), %rbx
      ea:      	xorl	%edi, %edi
      ec:      	movl	$0xffffff9c, %ebp       # imm = 0xFFFFFF9C
      f1:      	movl	$0xffffffb0, %r14d      # imm = 0xFFFFFFB0
      f7:      	movq	%r10, %rcx
      fa:      	jmp	0x120 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x120>
      fc:      	nopl	(%rax)
     100:      	xorl	%r15d, %r15d
     103:      	cmpq	%rax, %rdi
     106:      	jae	0x2be <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2be>
     10c:      	movl	%r15d, (%r8,%rdi,4)
     110:      	incq	%rdi
     113:      	cmpq	%rsi, %rcx
     116:      	leaq	0x1(%rcx), %rcx
     11a:      	jae	0x1e8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1e8>
     120:      	cmpq	%rsi, %rcx
     123:      	ja	0x2ab <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2ab>
     129:      	movsd	-0x8(%rbx,%rcx,8), %xmm3
     12f:      	movsd	(%rbx,%rcx,8), %xmm0
     134:      	movsd	-0x8(%rdx,%rcx,8), %xmm2
     13a:      	movsd	(%rdx,%rcx,8), %xmm1
     13f:      	ucomisd	%xmm1, %xmm0
     143:      	jae	0x170 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x170>
     145:      	ucomisd	%xmm2, %xmm3
     149:      	jb	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     14b:      	ucomisd	%xmm3, %xmm1
     14f:      	jb	0x157 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x157>
     151:      	ucomisd	%xmm0, %xmm2
     155:      	ja	0x1a0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1a0>
     157:      	ucomisd	%xmm3, %xmm1
     15b:      	jbe	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     15d:      	ucomisd	%xmm0, %xmm2
     161:      	jae	0x1a0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1a0>
     163:      	jmp	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     165:      	nopw	%cs:(%rax,%rax)
     170:      	ucomisd	%xmm2, %xmm3
     174:      	jae	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     176:      	ucomisd	%xmm1, %xmm3
     17a:      	jbe	0x182 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x182>
     17c:      	ucomisd	%xmm2, %xmm0
     180:      	jae	0x1a0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1a0>
     182:      	ucomisd	%xmm1, %xmm3
     186:      	jb	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     18c:      	ucomisd	%xmm2, %xmm0
     190:      	jbe	0x100 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x100>
     196:      	nopw	%cs:(%rax,%rax)
     1a0:      	ucomisd	%xmm3, %xmm1
     1a4:      	jne	0x1a8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1a8>
     1a6:      	jnp	0x1cc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1cc>
     1a8:      	ucomisd	%xmm2, %xmm0
     1ac:      	jne	0x1b0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1b0>
     1ae:      	jnp	0x1cc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x1cc>
     1b0:      	cmpq	%rax, %rdi
     1b3:      	jae	0x2de <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2de>
     1b9:      	ucomisd	%xmm1, %xmm0
     1bd:      	movl	$0x64, %r15d
     1c3:      	cmovbl	%ebp, %r15d
     1c7:      	jmp	0x10c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x10c>
     1cc:      	cmpq	%rax, %rdi
     1cf:      	jae	0x2ce <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2ce>
     1d5:      	ucomisd	%xmm1, %xmm0
     1d9:      	movl	$0x50, %r15d
     1df:      	cmovbl	%r14d, %r15d
     1e3:      	jmp	0x10c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x10c>
     1e8:      	movq	%rdi, (%r9)
     1eb:      	movq	%r10, (%r11)
     1ee:      	xorl	%eax, %eax
     1f0:      	addq	$0x8, %rsp
     1f4:      	popq	%rbx
     1f5:      	popq	%r14
     1f7:      	popq	%r15
     1f9:      	popq	%rbp
     1fa:      	retq
     1fb:      	leaq	(%rip), %rdi            # 0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x202>
		00000000000001fe:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.1-0x4
     202:      	leaq	(%rip), %rdx            # 0x209 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x209>
		0000000000000205:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.606-0x4
     209:      	movl	$0x40, %esi
     20e:      	callq	*(%rip)                 # 0x214 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x214>
		0000000000000210:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     214:      	leaq	(%rip), %rdi            # 0x21b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x21b>
		0000000000000217:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     21b:      	leaq	(%rip), %rdx            # 0x222 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x222>
		000000000000021e:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.607-0x4
     222:      	movl	$0x40, %esi
     227:      	callq	*(%rip)                 # 0x22d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x22d>
		0000000000000229:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     22d:      	leaq	(%rip), %rdi            # 0x234 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x234>
		0000000000000230:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     234:      	leaq	(%rip), %rdx            # 0x23b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x23b>
		0000000000000237:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.608-0x4
     23b:      	movl	$0x3f, %esi
     240:      	callq	*(%rip)                 # 0x246 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x246>
		0000000000000242:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     246:      	leaq	(%rip), %rdi            # 0x24d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x24d>
		0000000000000249:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.8-0x4
     24d:      	leaq	(%rip), %rdx            # 0x254 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x254>
		0000000000000250:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.609-0x4
     254:      	movl	$0x41, %esi
     259:      	callq	*(%rip)                 # 0x25f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x25f>
		000000000000025b:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     25f:      	movl	%edi, %r9d
     262:      	testb	%r9b, %r9b
     265:      	jne	0xab <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0xab>
     26b:      	leaq	(%rip), %rdi            # 0x272 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x272>
		000000000000026e:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.10-0x4
     272:      	leaq	(%rip), %rdx            # 0x279 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x279>
		0000000000000275:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.610-0x4
     279:      	movl	$0x53, %esi
     27e:      	callq	*(%rip)                 # 0x284 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x284>
		0000000000000280:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     284:      	leaq	(%rip), %rax            # 0x28b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x28b>
		0000000000000287:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.611-0x4
     28b:      	xorl	%edi, %edi
     28d:      	movq	%rcx, %rdx
     290:      	movq	%rax, %rcx
     293:      	callq	*(%rip)                 # 0x299 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x299>
		0000000000000295:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     299:      	leaq	(%rip), %rcx            # 0x2a0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2a0>
		000000000000029c:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.612-0x4
     2a0:      	xorl	%edi, %edi
     2a2:      	movq	%r8, %rdx
     2a5:      	callq	*(%rip)                 # 0x2ab <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2ab>
		00000000000002a7:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     2ab:      	incq	%rsi
     2ae:      	leaq	(%rip), %rdx            # 0x2b5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2b5>
		00000000000002b1:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.613-0x4
     2b5:      	movq	%rcx, %rdi
     2b8:      	callq	*(%rip)                 # 0x2be <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2be>
		00000000000002ba:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     2be:      	leaq	(%rip), %rdx            # 0x2c5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2c5>
		00000000000002c1:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.617-0x4
     2c5:      	movq	%rax, %rsi
     2c8:      	callq	*(%rip)                 # 0x2ce <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2ce>
		00000000000002ca:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     2ce:      	leaq	(%rip), %rdx            # 0x2d5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2d5>
		00000000000002d1:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.615-0x4
     2d5:      	movq	%rax, %rsi
     2d8:      	callq	*(%rip)                 # 0x2de <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2de>
		00000000000002da:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     2de:      	leaq	(%rip), %rdx            # 0x2e5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2e5>
		00000000000002e1:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.616-0x4
     2e5:      	movq	%rax, %rsi
     2e8:      	callq	*(%rip)                 # 0x2ee <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.5944653387456274579+0x2ee>
		00000000000002ea:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
