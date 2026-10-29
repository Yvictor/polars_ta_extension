
/tmp/polars-recovery/engulf-evidence/candidate/harness.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	pushq	%rax
       b:      	movw	$0xd, %ax
       f:      	cmpq	%rdi, %rsi
      12:      	jb	0x332 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x332>
      18:      	cmpq	$0x3, %rdi
      1c:      	movl	$0x2, %r10d
      22:      	cmovaeq	%rdi, %r10
      26:      	cmpq	$0x2, %rsi
      2a:      	setb	%al
      2d:      	cmpq	%rcx, %rsi
      30:      	setb	%dil
      34:      	orb	%al, %dil
      37:      	je	0x341 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x341>
      3d:      	cmpq	$0x2, %rsi
      41:      	setb	%al
      44:      	cmpq	%r8, %rsi
      47:      	setb	%dil
      4b:      	orb	%al, %dil
      4e:      	je	0x35a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x35a>
      54:      	cmpq	$0x2, %rsi
      58:      	setb	%al
      5b:      	cmpq	%r9, %rsi
      5e:      	setb	%dil
      62:      	orb	%al, %dil
      65:      	je	0x373 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x373>
      6b:      	movq	0x48(%rsp), %r9
      70:      	cmpq	$0x2, %rsi
      74:      	setb	%al
      77:      	cmpq	%r9, %rsi
      7a:      	setb	%dil
      7e:      	orb	%al, %dil
      81:      	je	0x38c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x38c>
      87:      	movq	0x68(%rsp), %rax
      8c:      	movq	%rsi, %r8
      8f:      	subq	%r10, %r8
      92:      	cmpq	%rax, %r8
      95:      	setb	%dil
      99:      	movb	$0x1, %r11b
      9c:      	cmpq	$0x2, %rsi
      a0:      	jae	0x3a5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3a5>
      a6:      	testb	%r11b, %r11b
      a9:      	je	0x3b1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3b1>
      af:      	movq	0x58(%rsp), %r11
      b4:      	movq	0x50(%rsp), %rbx
      b9:      	cmpq	$0x2, %rsi
      bd:      	jae	0xd2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0xd2>
      bf:      	movq	$0x0, (%rbx)
      c6:      	movq	$0x0, (%r11)
      cd:      	jmp	0x330 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x330>
      d2:      	cmpq	%rcx, %rsi
      d5:      	jae	0x3ca <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3ca>
      db:      	cmpq	%r9, %rsi
      de:      	jae	0x3df <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3df>
      e4:      	movq	0x40(%rsp), %r15
      e9:      	leaq	0x1(%rsi), %rcx
      ed:      	leaq	0x1(%r8), %rdi
      f1:      	leaq	-0x1(%r10), %r14
      f5:      	movq	%rcx, %r12
      f8:      	subq	%r14, %r12
      fb:      	jae	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x112>
      fd:      	xorl	%r12d, %r12d
     100:      	xorl	%r13d, %r13d
     103:      	movq	0x60(%rsp), %r14
     108:      	cmpq	%rax, %rdi
     10b:      	jbe	0x139 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x139>
     10d:      	jmp	0x229 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x229>
     112:      	leaq	0x2(%r8), %r9
     116:      	xorl	%ebp, %ebp
     118:      	cmpq	%r12, %r9
     11b:      	leaq	(%r15,%r14,8), %r12
     11f:      	cmovaq	%rbp, %r12
     123:      	leaq	(%rdx,%r14,8), %r13
     127:      	cmovaq	%rbp, %r13
     12b:      	movq	0x60(%rsp), %r14
     130:      	cmpq	%rax, %rdi
     133:      	ja	0x229 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x229>
     139:      	testq	%r12, %r12
     13c:      	je	0x229 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x229>
     142:      	testq	%r13, %r13
     145:      	je	0x229 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x229>
     14b:      	addq	$0x2, %r8
     14f:      	cmpq	%r9, %r8
     152:      	ja	0x3f1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3f1>
     158:      	testq	%rdi, %rdi
     15b:      	je	0x328 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x328>
     161:      	xorl	%eax, %eax
     163:      	movl	$0xffffff9c, %ecx       # imm = 0xFFFFFF9C
     168:      	movl	$0xffffffb0, %edx       # imm = 0xFFFFFFB0
     16d:      	jmp	0x190 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x190>
     16f:      	ucomisd	%xmm1, %xmm0
     173:      	movl	$0x50, %esi
     178:      	cmovbl	%edx, %esi
     17b:      	nopl	(%rax,%rax)
     180:      	movl	%esi, (%r14,%rax,4)
     184:      	incq	%rax
     187:      	cmpq	%rax, %rdi
     18a:      	je	0x32a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x32a>
     190:      	movsd	(%r12,%rax,8), %xmm3
     196:      	movsd	0x8(%r12,%rax,8), %xmm0
     19d:      	movsd	(%r13,%rax,8), %xmm2
     1a4:      	movsd	0x8(%r13,%rax,8), %xmm1
     1ab:      	xorl	%esi, %esi
     1ad:      	ucomisd	%xmm1, %xmm0
     1b1:      	jae	0x1e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x1e0>
     1b3:      	ucomisd	%xmm2, %xmm3
     1b7:      	jb	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1b9:      	ucomisd	%xmm3, %xmm1
     1bd:      	jb	0x1c5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x1c5>
     1bf:      	ucomisd	%xmm0, %xmm2
     1c3:      	ja	0x200 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x200>
     1c5:      	ucomisd	%xmm3, %xmm1
     1c9:      	jbe	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1cb:      	ucomisd	%xmm0, %xmm2
     1cf:      	jae	0x200 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x200>
     1d1:      	jmp	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1d3:      	nopw	%cs:(%rax,%rax)
     1e0:      	ucomisd	%xmm2, %xmm3
     1e4:      	jae	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1e6:      	ucomisd	%xmm1, %xmm3
     1ea:      	jbe	0x1f2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x1f2>
     1ec:      	ucomisd	%xmm2, %xmm0
     1f0:      	jae	0x200 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x200>
     1f2:      	ucomisd	%xmm1, %xmm3
     1f6:      	jb	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1f8:      	ucomisd	%xmm2, %xmm0
     1fc:      	jbe	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     1fe:      	nop
     200:      	ucomisd	%xmm3, %xmm1
     204:      	jne	0x20c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x20c>
     206:      	jnp	0x16f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x16f>
     20c:      	ucomisd	%xmm2, %xmm0
     210:      	jne	0x218 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x218>
     212:      	jnp	0x16f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x16f>
     218:      	ucomisd	%xmm1, %xmm0
     21c:      	movl	$0x64, %esi
     221:      	cmovbl	%ecx, %esi
     224:      	jmp	0x180 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x180>
     229:      	xorl	%edi, %edi
     22b:      	movl	$0xffffff9c, %r9d       # imm = 0xFFFFFF9C
     231:      	movl	$0xffffffb0, %ebp       # imm = 0xFFFFFFB0
     236:      	movq	%r10, %r8
     239:      	jmp	0x260 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x260>
     23b:      	nopl	(%rax,%rax)
     240:      	xorl	%r12d, %r12d
     243:      	cmpq	%rax, %rdi
     246:      	jae	0x419 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x419>
     24c:      	movl	%r12d, (%r14,%rdi,4)
     250:      	incq	%rdi
     253:      	cmpq	%rsi, %r8
     256:      	leaq	0x1(%r8), %r8
     25a:      	jae	0x32a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x32a>
     260:      	cmpq	%rsi, %r8
     263:      	ja	0x406 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x406>
     269:      	movsd	-0x8(%r15,%r8,8), %xmm3
     270:      	movsd	(%r15,%r8,8), %xmm0
     276:      	movsd	-0x8(%rdx,%r8,8), %xmm2
     27d:      	movsd	(%rdx,%r8,8), %xmm1
     283:      	ucomisd	%xmm1, %xmm0
     287:      	jae	0x2b0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2b0>
     289:      	ucomisd	%xmm2, %xmm3
     28d:      	jb	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     28f:      	ucomisd	%xmm3, %xmm1
     293:      	jb	0x29b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x29b>
     295:      	ucomisd	%xmm0, %xmm2
     299:      	ja	0x2e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2e0>
     29b:      	ucomisd	%xmm3, %xmm1
     29f:      	jbe	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     2a1:      	ucomisd	%xmm0, %xmm2
     2a5:      	jae	0x2e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2e0>
     2a7:      	jmp	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     2a9:      	nopl	(%rax)
     2b0:      	ucomisd	%xmm2, %xmm3
     2b4:      	jae	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     2b6:      	ucomisd	%xmm1, %xmm3
     2ba:      	jbe	0x2c2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2c2>
     2bc:      	ucomisd	%xmm2, %xmm0
     2c0:      	jae	0x2e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2e0>
     2c2:      	ucomisd	%xmm1, %xmm3
     2c6:      	jb	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     2cc:      	ucomisd	%xmm2, %xmm0
     2d0:      	jbe	0x240 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x240>
     2d6:      	nopw	%cs:(%rax,%rax)
     2e0:      	ucomisd	%xmm3, %xmm1
     2e4:      	jne	0x2e8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2e8>
     2e6:      	jnp	0x30c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x30c>
     2e8:      	ucomisd	%xmm2, %xmm0
     2ec:      	jne	0x2f0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x2f0>
     2ee:      	jnp	0x30c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x30c>
     2f0:      	cmpq	%rax, %rdi
     2f3:      	jae	0x439 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x439>
     2f9:      	ucomisd	%xmm1, %xmm0
     2fd:      	movl	$0x64, %r12d
     303:      	cmovbl	%r9d, %r12d
     307:      	jmp	0x24c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x24c>
     30c:      	cmpq	%rax, %rdi
     30f:      	jae	0x429 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x429>
     315:      	ucomisd	%xmm1, %xmm0
     319:      	movl	$0x50, %r12d
     31f:      	cmovbl	%ebp, %r12d
     323:      	jmp	0x24c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x24c>
     328:      	xorl	%edi, %edi
     32a:      	movq	%rdi, (%r11)
     32d:      	movq	%r10, (%rbx)
     330:      	xorl	%eax, %eax
     332:      	addq	$0x8, %rsp
     336:      	popq	%rbx
     337:      	popq	%r12
     339:      	popq	%r13
     33b:      	popq	%r14
     33d:      	popq	%r15
     33f:      	popq	%rbp
     340:      	retq
     341:      	leaq	(%rip), %rdi            # 0x348 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x348>
		0000000000000344:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.1-0x4
     348:      	leaq	(%rip), %rdx            # 0x34f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x34f>
		000000000000034b:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.606-0x4
     34f:      	movl	$0x40, %esi
     354:      	callq	*(%rip)                 # 0x35a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x35a>
		0000000000000356:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     35a:      	leaq	(%rip), %rdi            # 0x361 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x361>
		000000000000035d:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     361:      	leaq	(%rip), %rdx            # 0x368 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x368>
		0000000000000364:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.607-0x4
     368:      	movl	$0x40, %esi
     36d:      	callq	*(%rip)                 # 0x373 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x373>
		000000000000036f:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     373:      	leaq	(%rip), %rdi            # 0x37a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x37a>
		0000000000000376:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     37a:      	leaq	(%rip), %rdx            # 0x381 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x381>
		000000000000037d:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.608-0x4
     381:      	movl	$0x3f, %esi
     386:      	callq	*(%rip)                 # 0x38c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x38c>
		0000000000000388:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     38c:      	leaq	(%rip), %rdi            # 0x393 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x393>
		000000000000038f:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.8-0x4
     393:      	leaq	(%rip), %rdx            # 0x39a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x39a>
		0000000000000396:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.609-0x4
     39a:      	movl	$0x41, %esi
     39f:      	callq	*(%rip)                 # 0x3a5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3a5>
		00000000000003a1:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     3a5:      	movl	%edi, %r11d
     3a8:      	testb	%r11b, %r11b
     3ab:      	jne	0xaf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0xaf>
     3b1:      	leaq	(%rip), %rdi            # 0x3b8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3b8>
		00000000000003b4:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.10-0x4
     3b8:      	leaq	(%rip), %rdx            # 0x3bf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3bf>
		00000000000003bb:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.610-0x4
     3bf:      	movl	$0x53, %esi
     3c4:      	callq	*(%rip)                 # 0x3ca <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3ca>
		00000000000003c6:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     3ca:      	leaq	(%rip), %rax            # 0x3d1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3d1>
		00000000000003cd:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.611-0x4
     3d1:      	xorl	%edi, %edi
     3d3:      	movq	%rcx, %rdx
     3d6:      	movq	%rax, %rcx
     3d9:      	callq	*(%rip)                 # 0x3df <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3df>
		00000000000003db:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     3df:      	leaq	(%rip), %rcx            # 0x3e6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3e6>
		00000000000003e2:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.612-0x4
     3e6:      	xorl	%edi, %edi
     3e8:      	movq	%r9, %rdx
     3eb:      	callq	*(%rip)                 # 0x3f1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3f1>
		00000000000003ed:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     3f1:      	leaq	(%rip), %rcx            # 0x3f8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x3f8>
		00000000000003f4:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.614-0x4
     3f8:      	xorl	%edi, %edi
     3fa:      	movq	%r8, %rsi
     3fd:      	movq	%r9, %rdx
     400:      	callq	*(%rip)                 # 0x406 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x406>
		0000000000000402:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     406:      	leaq	(%rip), %rdx            # 0x40d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x40d>
		0000000000000409:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.615-0x4
     40d:      	movq	%r8, %rdi
     410:      	movq	%rcx, %rsi
     413:      	callq	*(%rip)                 # 0x419 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x419>
		0000000000000415:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     419:      	leaq	(%rip), %rdx            # 0x420 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x420>
		000000000000041c:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.619-0x4
     420:      	movq	%rax, %rsi
     423:      	callq	*(%rip)                 # 0x429 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x429>
		0000000000000425:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     429:      	leaq	(%rip), %rdx            # 0x430 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x430>
		000000000000042c:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.617-0x4
     430:      	movq	%rax, %rsi
     433:      	callq	*(%rip)                 # 0x439 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x439>
		0000000000000435:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     439:      	leaq	(%rip), %rdx            # 0x440 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x440>
		000000000000043c:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.618-0x4
     440:      	movq	%rax, %rsi
     443:      	callq	*(%rip)                 # 0x449 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func12cdlengulfingNtNtB4_5types4Core17cdlengulfing_impl.llvm.9382974871970357297+0x449>
		0000000000000445:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
