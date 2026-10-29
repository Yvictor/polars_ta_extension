
/tmp/polars-recovery/sarext-window-evidence/candidate-static-1.97.0/static-probe.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0xc8, %rsp
      11:      	movapd	%xmm2, %xmm9
      16:      	movapd	%xmm0, %xmm8
      1b:      	movq	0x120(%rsp), %rbx
      23:      	movq	0x118(%rsp), %r12
      2b:      	movq	0x110(%rsp), %r15
      33:      	movq	0x108(%rsp), %r13
      3b:      	movq	0x100(%rsp), %r14
      43:      	movq	(%rip), %rax            # 0x4a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4a>
		0000000000000046:  R_X86_64_GOTPCREL	_RNvNtNtCsi9YoAGUbCUq_10std_detect6detect5cache5CACHE-0x4
      4a:      	movq	(%rax), %rax
      4d:      	testq	%rax, %rax
      50:      	je	0xc37 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc37>
      56:      	btq	$0x38, %rax
      5b:      	jb	0xce4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xce4>
      61:      	movw	$0xd, %ax
      65:      	cmpq	%rsi, %rdx
      68:      	jae	0x7c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7c>
      6a:      	addq	$0xc8, %rsp
      71:      	popq	%rbx
      72:      	popq	%r12
      74:      	popq	%r13
      76:      	popq	%r14
      78:      	popq	%r15
      7a:      	popq	%rbp
      7b:      	retq
      7c:      	xorpd	%xmm0, %xmm0
      80:      	movsd	%xmm0, 0x50(%rsp)
      86:      	ucomisd	(%rip), %xmm8           # 0x8f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x8f>
		000000000000008b:  R_X86_64_PC32	.LCPI0_0-0x4
      8f:      	xorpd	%xmm2, %xmm2
      93:      	jne	0x97 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x97>
      95:      	jnp	0xbb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xbb>
      97:      	movapd	(%rip), %xmm0           # 0x9f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9f>
		000000000000009b:  R_X86_64_PC32	.LCPI0_1-0x4
      9f:      	andpd	%xmm8, %xmm0
      a4:      	movw	$0x2, %ax
      a8:      	movsd	(%rip), %xmm2           # 0xb0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb0>
		00000000000000ac:  R_X86_64_PC32	.LCPI0_2-0x4
      b0:      	ucomisd	%xmm0, %xmm2
      b4:      	movapd	%xmm8, %xmm2
      b9:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
      bb:      	ucomisd	(%rip), %xmm1           # 0xc3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc3>
		00000000000000bf:  R_X86_64_PC32	.LCPI0_0-0x4
      c3:      	jne	0xc7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc7>
      c5:      	jnp	0xe9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xe9>
      c7:      	xorpd	%xmm0, %xmm0
      cb:      	ucomisd	%xmm0, %xmm1
      cf:      	movw	$0x2, %ax
      d3:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
      d5:      	movsd	(%rip), %xmm0           # 0xdd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xdd>
		00000000000000d9:  R_X86_64_PC32	.LCPI0_2-0x4
      dd:      	ucomisd	%xmm1, %xmm0
      e1:      	movsd	%xmm1, 0x50(%rsp)
      e7:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
      e9:      	movsd	(%rip), %xmm11          # 0xf2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xf2>
		00000000000000ee:  R_X86_64_PC32	.LCPI0_3-0x4
      f2:      	ucomisd	(%rip), %xmm9           # 0xfb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xfb>
		00000000000000f7:  R_X86_64_PC32	.LCPI0_0-0x4
      fb:      	movapd	%xmm11, %xmm8
     100:      	jne	0x104 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x104>
     102:      	jnp	0x12f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x12f>
     104:      	xorpd	%xmm0, %xmm0
     108:      	ucomisd	%xmm0, %xmm9
     10d:      	movw	$0x2, %ax
     111:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     117:      	movsd	(%rip), %xmm0           # 0x11f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x11f>
		000000000000011b:  R_X86_64_PC32	.LCPI0_2-0x4
     11f:      	ucomisd	%xmm9, %xmm0
     124:      	movapd	%xmm9, %xmm8
     129:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     12f:      	ucomisd	(%rip), %xmm3           # 0x137 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x137>
		0000000000000133:  R_X86_64_PC32	.LCPI0_0-0x4
     137:      	jne	0x13b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x13b>
     139:      	jnp	0x164 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x164>
     13b:      	xorpd	%xmm0, %xmm0
     13f:      	ucomisd	%xmm0, %xmm3
     143:      	movw	$0x2, %ax
     147:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     14d:      	movsd	(%rip), %xmm0           # 0x155 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x155>
		0000000000000151:  R_X86_64_PC32	.LCPI0_2-0x4
     155:      	ucomisd	%xmm3, %xmm0
     159:      	movapd	%xmm3, %xmm11
     15e:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     164:      	ucomisd	(%rip), %xmm4           # 0x16c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x16c>
		0000000000000168:  R_X86_64_PC32	.LCPI0_0-0x4
     16c:      	jne	0x17a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x17a>
     16e:      	jp	0x17a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x17a>
     170:      	movsd	(%rip), %xmm4           # 0x178 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x178>
		0000000000000174:  R_X86_64_PC32	.LCPI0_4-0x4
     178:      	jmp	0x19e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x19e>
     17a:      	xorpd	%xmm0, %xmm0
     17e:      	ucomisd	%xmm0, %xmm4
     182:      	movw	$0x2, %ax
     186:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     18c:      	movsd	(%rip), %xmm0           # 0x194 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x194>
		0000000000000190:  R_X86_64_PC32	.LCPI0_2-0x4
     194:      	ucomisd	%xmm4, %xmm0
     198:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     19e:      	movsd	(%rip), %xmm9           # 0x1a7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1a7>
		00000000000001a3:  R_X86_64_PC32	.LCPI0_3-0x4
     1a7:      	ucomisd	(%rip), %xmm5           # 0x1af <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1af>
		00000000000001ab:  R_X86_64_PC32	.LCPI0_0-0x4
     1af:      	movapd	%xmm9, %xmm10
     1b4:      	jne	0x1b8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1b8>
     1b6:      	jnp	0x1e1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1e1>
     1b8:      	xorpd	%xmm0, %xmm0
     1bc:      	ucomisd	%xmm0, %xmm5
     1c0:      	movw	$0x2, %ax
     1c4:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     1ca:      	movsd	(%rip), %xmm0           # 0x1d2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1d2>
		00000000000001ce:  R_X86_64_PC32	.LCPI0_2-0x4
     1d2:      	ucomisd	%xmm5, %xmm0
     1d6:      	movapd	%xmm5, %xmm10
     1db:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     1e1:      	ucomisd	(%rip), %xmm6           # 0x1e9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1e9>
		00000000000001e5:  R_X86_64_PC32	.LCPI0_0-0x4
     1e9:      	jne	0x1ed <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x1ed>
     1eb:      	jnp	0x216 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x216>
     1ed:      	xorpd	%xmm0, %xmm0
     1f1:      	ucomisd	%xmm0, %xmm6
     1f5:      	movw	$0x2, %ax
     1f9:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     1ff:      	movsd	(%rip), %xmm0           # 0x207 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x207>
		0000000000000203:  R_X86_64_PC32	.LCPI0_2-0x4
     207:      	ucomisd	%xmm6, %xmm0
     20b:      	movapd	%xmm6, %xmm9
     210:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     216:      	ucomisd	(%rip), %xmm7           # 0x21e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x21e>
		000000000000021a:  R_X86_64_PC32	.LCPI0_0-0x4
     21e:      	jne	0x22c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x22c>
     220:      	jp	0x22c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x22c>
     222:      	movsd	(%rip), %xmm7           # 0x22a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x22a>
		0000000000000226:  R_X86_64_PC32	.LCPI0_4-0x4
     22a:      	jmp	0x250 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x250>
     22c:      	xorpd	%xmm0, %xmm0
     230:      	ucomisd	%xmm0, %xmm7
     234:      	movw	$0x2, %ax
     238:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     23e:      	movsd	(%rip), %xmm0           # 0x246 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x246>
		0000000000000242:  R_X86_64_PC32	.LCPI0_2-0x4
     246:      	ucomisd	%xmm7, %xmm0
     24a:      	jb	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     250:      	movapd	(%rip), %xmm0           # 0x258 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x258>
		0000000000000254:  R_X86_64_PC32	.LCPI0_1-0x4
     258:      	andpd	%xmm2, %xmm0
     25c:      	movsd	(%rip), %xmm1           # 0x264 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x264>
		0000000000000260:  R_X86_64_PC32	.LCPI0_2-0x4
     264:      	ucomisd	%xmm0, %xmm1
     268:      	jae	0x2ab <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x2ab>
     26a:      	cmpq	%r8, %rdx
     26d:      	setb	%al
     270:      	cmpq	%r14, %rdx
     273:      	setb	%r10b
     277:      	cmpq	$0x1, %rsi
     27b:      	adcq	$0x0, %rsi
     27f:      	movq	$0x0, 0xa8(%rsp)
     28b:      	movq	%rdx, %rbp
     28e:      	subq	%rsi, %rbp
     291:      	jae	0x3aa <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x3aa>
     297:      	movq	$0x0, (%r13)
     29f:      	movq	$0x0, (%r15)
     2a6:      	jmp	0xc30 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc30>
     2ab:      	xorpd	%xmm3, %xmm3
     2af:      	movsd	0x50(%rsp), %xmm5
     2b5:      	ucomisd	%xmm3, %xmm5
     2b9:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2bb:      	ucomisd	0x50(%rsp), %xmm1
     2c1:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2c3:      	ucomisd	%xmm3, %xmm8
     2c8:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2ca:      	ucomisd	%xmm8, %xmm1
     2cf:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2d1:      	ucomisd	%xmm3, %xmm11
     2d6:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2d8:      	ucomisd	%xmm11, %xmm1
     2dd:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2df:      	ucomisd	%xmm3, %xmm4
     2e3:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2e5:      	ucomisd	%xmm4, %xmm1
     2e9:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2ef:      	ucomisd	%xmm3, %xmm10
     2f4:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2fa:      	ucomisd	%xmm10, %xmm1
     2ff:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     305:      	ucomisd	%xmm3, %xmm9
     30a:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     310:      	ucomisd	%xmm9, %xmm1
     315:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     31b:      	cmpq	$0x1, %rsi
     31f:      	adcq	$0x0, %rsi
     323:      	ucomisd	%xmm7, %xmm1
     327:      	movq	$-0x1, %rax
     32e:      	movq	%rsi, %r11
     331:      	cmovbq	%rax, %r11
     335:      	xorpd	%xmm1, %xmm1
     339:      	ucomisd	%xmm1, %xmm7
     33d:      	cmovbq	%rax, %r11
     341:      	cmpq	%rdx, %r11
     344:      	seta	%r10b
     348:      	cmpq	%r8, %rdx
     34b:      	setb	%al
     34e:      	orb	%al, %r10b
     351:      	je	0xd04 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd04>
     357:      	movq	%rdx, %rbp
     35a:      	subq	%r11, %rbp
     35d:      	setb	0x8(%rsp)
     362:      	cmpq	%r14, %rdx
     365:      	setb	%r10b
     369:      	orb	%r10b, 0x8(%rsp)
     36e:      	je	0xd1d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd1d>
     374:      	cmpq	%rbx, %rbp
     377:      	setb	0x8(%rsp)
     37c:      	movb	$0x1, %bpl
     37f:      	cmpq	%r11, %rdx
     382:      	jae	0xd60 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd60>
     388:      	testb	%bpl, %bpl
     38b:      	jne	0x27f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x27f>
     391:      	leaq	(%rip), %rdi            # 0x398 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x398>
		0000000000000394:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.182-0x4
     398:      	leaq	(%rip), %rdx            # 0x39f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x39f>
		000000000000039b:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3611-0x4
     39f:      	movl	$0x50, %esi
     3a4:      	callq	*(%rip)                 # 0x3aa <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x3aa>
		00000000000003a6:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     3aa:      	testb	%al, %al
     3ac:      	je	0xd36 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd36>
     3b2:      	movsd	%xmm4, 0x20(%rsp)
     3b8:      	movsd	%xmm7, 0x28(%rsp)
     3be:      	testb	%r10b, %r10b
     3c1:      	je	0xd4b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd4b>
     3c7:      	incq	%rdx
     3ca:      	xorpd	%xmm1, %xmm1
     3ce:      	ucomisd	%xmm1, %xmm2
     3d2:      	jne	0x46b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x46b>
     3d8:      	jp	0x46b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x46b>
     3de:      	movsd	%xmm10, 0x48(%rsp)
     3e5:      	movsd	%xmm9, 0x38(%rsp)
     3ec:      	movsd	%xmm8, 0x10(%rsp)
     3f3:      	movsd	%xmm11, 0x18(%rsp)
     3fa:      	subq	$0x8, %rsp
     3fe:      	leaq	0xb0(%rsp), %r11
     406:      	leaq	0xb8(%rsp), %rax
     40e:      	movq	%rdi, %r8
     411:      	movq	%rax, %rdi
     414:      	movq	%rsi, %rax
     417:      	movq	%r8, %rsi
     41a:      	movq	%rdx, %r10
     41d:      	movq	%rax, %rdx
     420:      	movq	%rcx, %r8
     423:      	movq	%rax, 0x80(%rsp)
     42b:      	movq	%rax, %rcx
     42e:      	movq	%r8, 0x38(%rsp)
     433:      	movq	%r9, %rax
     436:      	movq	%r10, %r9
     439:      	pushq	$0x1
     43b:      	pushq	%r11
     43d:      	pushq	$0x1
     43f:      	movq	%r10, 0x28(%rsp)
     444:      	pushq	%r10
     446:      	movq	%rax, %r14
     449:      	pushq	%rax
     44a:      	callq	*(%rip)                 # 0x450 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x450>
		000000000000044c:  R_X86_64_GOTPCREL	_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func8minus_dmNtNtB4_5types4Core8minus_dm-0x4
     450:      	addq	$0x30, %rsp
     454:      	cmpb	$0x0, 0xb0(%rsp)
     45c:      	je	0x490 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x490>
     45e:      	movzwl	0xb2(%rsp), %eax
     466:      	jmp	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     46b:      	seta	%al
     46e:      	movq	%rsi, (%r13)
     472:      	movq	%r9, %rdi
     475:      	cmovaq	%rcx, %rdi
     479:      	movzbl	%al, %eax
     47c:      	ja	0x482 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x482>
     47e:      	movapd	%xmm0, %xmm2
     482:      	movsd	0x28(%rsp), %xmm1
     488:      	movsd	0x20(%rsp), %xmm3
     48e:      	jmp	0x505 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x505>
     490:      	movsd	0xa8(%rsp), %xmm0
     499:      	xorpd	%xmm1, %xmm1
     49d:      	ucomisd	%xmm1, %xmm0
     4a1:      	movq	0x78(%rsp), %rsi
     4a6:      	movq	%rsi, (%r13)
     4aa:      	ja	0x4c5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4c5>
     4ac:      	movq	%r14, %r9
     4af:      	movsd	-0x8(%r14,%rsi,8), %xmm2
     4b6:      	movl	$0x1, %eax
     4bb:      	movq	0x30(%rsp), %rcx
     4c0:      	movq	%rcx, %rdi
     4c3:      	jmp	0x4d8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4d8>
     4c5:      	movq	0x30(%rsp), %rcx
     4ca:      	movsd	-0x8(%rcx,%rsi,8), %xmm2
     4d0:      	xorl	%eax, %eax
     4d2:      	movq	%r14, %r9
     4d5:      	movq	%r14, %rdi
     4d8:      	movq	0x8(%rsp), %rdx
     4dd:      	movsd	0x28(%rsp), %xmm1
     4e3:      	movsd	0x20(%rsp), %xmm3
     4e9:      	movsd	0x18(%rsp), %xmm11
     4f0:      	movsd	0x10(%rsp), %xmm8
     4f7:      	movsd	0x38(%rsp), %xmm9
     4fe:      	movsd	0x48(%rsp), %xmm10
     505:      	movapd	%xmm3, %xmm0
     509:      	minsd	%xmm8, %xmm0
     50e:      	movapd	%xmm3, %xmm4
     512:      	minsd	%xmm11, %xmm4
     517:      	movsd	%xmm4, 0xa0(%rsp)
     520:      	movapd	%xmm1, %xmm4
     524:      	minsd	%xmm10, %xmm4
     529:      	movapd	%xmm1, %xmm5
     52d:      	minsd	%xmm9, %xmm5
     532:      	movsd	%xmm5, 0x98(%rsp)
     53b:      	movsd	(%rdi,%rsi,8), %xmm7
     540:      	leaq	(%r9,%rsi,8), %rdi
     544:      	movsd	(%r9,%rsi,8), %xmm5
     54a:      	leaq	(%rcx,%rsi,8), %r8
     54e:      	movq	%r8, 0x78(%rsp)
     553:      	movsd	(%rcx,%rsi,8), %xmm6
     558:      	subq	%rsi, %rdx
     55b:      	cmpq	%rbx, %rbp
     55e:      	movq	%rdx, %r13
     561:      	movsd	%xmm0, 0x18(%rsp)
     567:      	movsd	%xmm4, 0x10(%rsp)
     56d:      	jae	0x8ba <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x8ba>
     573:      	xorl	%ebx, %ebx
     575:      	movq	(%rip), %r14            # 0x57c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x57c>
		0000000000000578:  R_X86_64_GOTPCREL	fma-0x4
     57c:      	xorpd	%xmm8, %xmm8
     581:      	cmpneqsd	0x50(%rsp), %xmm8
     589:      	movapd	%xmm8, 0x80(%rsp)
     593:      	movsd	%xmm0, 0x40(%rsp)
     599:      	movsd	%xmm4, 0x60(%rsp)
     59f:      	movq	%rdi, %rbp
     5a2:      	jmp	0x5d9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5d9>
     5a4:      	xorl	%eax, %eax
     5a6:      	movq	%r13, %rcx
     5a9:      	movsd	0x28(%rsp), %xmm1
     5af:      	movsd	0x20(%rsp), %xmm3
     5b5:      	movsd	0x18(%rsp), %xmm0
     5bb:      	movsd	0x10(%rsp), %xmm4
     5c1:      	movsd	0x8(%rsp), %xmm5
     5c7:      	movsd	0x38(%rsp), %xmm7
     5cd:      	incq	%rbx
     5d0:      	cmpq	%rbx, %rcx
     5d3:      	je	0xc2d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc2d>
     5d9:      	movapd	%xmm5, %xmm9
     5de:      	movapd	%xmm6, %xmm8
     5e3:      	movsd	(%rbp,%rbx,8), %xmm5
     5e9:      	movq	0x78(%rsp), %rcx
     5ee:      	movsd	(%rcx,%rbx,8), %xmm6
     5f3:      	cmpq	$0x1, %rax
     5f7:      	movsd	%xmm5, 0x8(%rsp)
     5fd:      	movsd	%xmm6, 0x30(%rsp)
     603:      	jne	0x650 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x650>
     605:      	ucomisd	%xmm5, %xmm2
     609:      	jae	0x6a7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a7>
     60f:      	movsd	%xmm2, (%r12,%rbx,8)
     615:      	ucomisd	%xmm7, %xmm6
     619:      	movsd	%xmm9, 0x58(%rsp)
     620:      	jbe	0x7b6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7b6>
     626:      	movsd	0x40(%rsp), %xmm0
     62c:      	addsd	0xa0(%rsp), %xmm0
     635:      	ucomisd	%xmm3, %xmm0
     639:      	movapd	%xmm6, %xmm7
     63d:      	jbe	0x7bc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7bc>
     643:      	movapd	%xmm6, %xmm7
     647:      	movapd	%xmm3, %xmm0
     64b:      	jmp	0x7bc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7bc>
     650:      	ucomisd	%xmm2, %xmm6
     654:      	jae	0x734 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x734>
     65a:      	movapd	%xmm2, %xmm0
     65e:      	xorpd	(%rip), %xmm0           # 0x666 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x666>
		0000000000000662:  R_X86_64_PC32	.LCPI0_5-0x4
     666:      	movlpd	%xmm0, (%r12,%rbx,8)
     66c:      	ucomisd	%xmm5, %xmm7
     670:      	movsd	%xmm8, 0x48(%rsp)
     677:      	jbe	0x818 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x818>
     67d:      	movsd	0x60(%rsp), %xmm0
     683:      	addsd	0x98(%rsp), %xmm0
     68c:      	ucomisd	%xmm1, %xmm0
     690:      	movapd	%xmm5, %xmm7
     694:      	jbe	0x81e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x81e>
     69a:      	movapd	%xmm5, %xmm7
     69e:      	movapd	%xmm1, %xmm0
     6a2:      	jmp	0x81e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x81e>
     6a7:      	movapd	%xmm8, %xmm0
     6ac:      	maxsd	%xmm7, %xmm0
     6b0:      	movapd	%xmm6, %xmm1
     6b4:      	maxsd	%xmm0, %xmm1
     6b8:      	movsd	0x50(%rsp), %xmm2
     6be:      	mulsd	%xmm1, %xmm2
     6c2:      	addsd	%xmm1, %xmm2
     6c6:      	movapd	0x80(%rsp), %xmm3
     6cf:      	movapd	%xmm3, %xmm0
     6d3:      	andnpd	%xmm1, %xmm0
     6d7:      	andpd	%xmm3, %xmm2
     6db:      	orpd	%xmm0, %xmm2
     6df:      	movapd	%xmm2, %xmm0
     6e3:      	xorpd	(%rip), %xmm0           # 0x6eb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6eb>
		00000000000006e7:  R_X86_64_PC32	.LCPI0_5-0x4
     6eb:      	movlpd	%xmm0, (%r12,%rbx,8)
     6f1:      	movapd	%xmm5, %xmm1
     6f5:      	subsd	%xmm2, %xmm1
     6f9:      	movapd	%xmm4, %xmm0
     6fd:      	movsd	%xmm8, 0x48(%rsp)
     704:      	callq	*%r14
     707:      	movsd	0x48(%rsp), %xmm2
     70d:      	movsd	0x30(%rsp), %xmm6
     713:      	maxsd	%xmm0, %xmm2
     717:      	ucomisd	%xmm2, %xmm6
     71b:      	jbe	0x858 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x858>
     721:      	movsd	0x8(%rsp), %xmm5
     727:      	movapd	%xmm5, %xmm7
     72b:      	movapd	%xmm6, %xmm2
     72f:      	jmp	0x862 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x862>
     734:      	movapd	%xmm9, %xmm1
     739:      	minsd	%xmm7, %xmm1
     73d:      	movapd	%xmm5, %xmm2
     741:      	minsd	%xmm1, %xmm2
     745:      	movsd	0x50(%rsp), %xmm3
     74b:      	mulsd	%xmm2, %xmm3
     74f:      	movapd	0x80(%rsp), %xmm4
     758:      	movapd	%xmm4, %xmm1
     75c:      	andnpd	%xmm2, %xmm1
     760:      	subsd	%xmm3, %xmm2
     764:      	andpd	%xmm4, %xmm2
     768:      	orpd	%xmm1, %xmm2
     76c:      	movlpd	%xmm2, (%r12,%rbx,8)
     772:      	movapd	%xmm6, %xmm1
     776:      	subsd	%xmm2, %xmm1
     77a:      	movsd	%xmm9, 0x58(%rsp)
     781:      	callq	*%r14
     784:      	movsd	0x58(%rsp), %xmm2
     78a:      	movsd	0x8(%rsp), %xmm5
     790:      	minsd	%xmm0, %xmm2
     794:      	movl	$0x1, %eax
     799:      	ucomisd	%xmm5, %xmm2
     79d:      	jbe	0x88a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x88a>
     7a3:      	movsd	0x30(%rsp), %xmm6
     7a9:      	movapd	%xmm6, %xmm7
     7ad:      	movapd	%xmm5, %xmm2
     7b1:      	jmp	0x894 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x894>
     7b6:      	movsd	0x40(%rsp), %xmm0
     7bc:      	movsd	%xmm7, 0x38(%rsp)
     7c2:      	movapd	%xmm7, %xmm1
     7c6:      	subsd	%xmm2, %xmm1
     7ca:      	movsd	%xmm0, 0x40(%rsp)
     7d0:      	callq	*%r14
     7d3:      	movsd	0x58(%rsp), %xmm2
     7d9:      	minsd	%xmm0, %xmm2
     7dd:      	movl	$0x1, %eax
     7e2:      	movsd	0x8(%rsp), %xmm5
     7e8:      	ucomisd	%xmm5, %xmm2
     7ec:      	jbe	0x7f2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7f2>
     7ee:      	movapd	%xmm5, %xmm2
     7f2:      	movq	%r13, %rcx
     7f5:      	movsd	0x28(%rsp), %xmm1
     7fb:      	movsd	0x20(%rsp), %xmm3
     801:      	movsd	0x18(%rsp), %xmm0
     807:      	movsd	0x10(%rsp), %xmm4
     80d:      	movsd	0x30(%rsp), %xmm6
     813:      	jmp	0x5c7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5c7>
     818:      	movsd	0x60(%rsp), %xmm0
     81e:      	movsd	%xmm7, 0x38(%rsp)
     824:      	movapd	%xmm7, %xmm1
     828:      	subsd	%xmm2, %xmm1
     82c:      	movsd	%xmm0, 0x60(%rsp)
     832:      	callq	*%r14
     835:      	movsd	0x48(%rsp), %xmm2
     83b:      	maxsd	%xmm0, %xmm2
     83f:      	movsd	0x30(%rsp), %xmm6
     845:      	ucomisd	%xmm2, %xmm6
     849:      	jbe	0x5a4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5a4>
     84f:      	movapd	%xmm6, %xmm2
     853:      	jmp	0x5a4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5a4>
     858:      	movsd	0x8(%rsp), %xmm5
     85e:      	movapd	%xmm5, %xmm7
     862:      	movsd	0x10(%rsp), %xmm4
     868:      	movsd	%xmm4, 0x60(%rsp)
     86e:      	xorl	%eax, %eax
     870:      	movq	%r13, %rcx
     873:      	movsd	0x28(%rsp), %xmm1
     879:      	movsd	0x20(%rsp), %xmm3
     87f:      	movsd	0x18(%rsp), %xmm0
     885:      	jmp	0x5cd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5cd>
     88a:      	movsd	0x30(%rsp), %xmm6
     890:      	movapd	%xmm6, %xmm7
     894:      	movsd	0x18(%rsp), %xmm0
     89a:      	movsd	%xmm0, 0x40(%rsp)
     8a0:      	movq	%r13, %rcx
     8a3:      	movsd	0x28(%rsp), %xmm1
     8a9:      	movsd	0x20(%rsp), %xmm3
     8af:      	movsd	0x10(%rsp), %xmm4
     8b5:      	jmp	0x5cd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5cd>
     8ba:      	xorl	%r14d, %r14d
     8bd:      	xorpd	%xmm8, %xmm8
     8c2:      	cmpneqsd	0x50(%rsp), %xmm8
     8ca:      	movapd	%xmm8, 0x80(%rsp)
     8d4:      	movsd	%xmm0, 0x40(%rsp)
     8da:      	movsd	%xmm4, 0x60(%rsp)
     8e0:      	movq	%rdi, %rbp
     8e3:      	jmp	0x91a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x91a>
     8e5:      	xorl	%eax, %eax
     8e7:      	movq	%r13, %rcx
     8ea:      	movsd	0x28(%rsp), %xmm1
     8f0:      	movsd	0x20(%rsp), %xmm3
     8f6:      	movsd	0x18(%rsp), %xmm0
     8fc:      	movsd	0x10(%rsp), %xmm4
     902:      	movsd	0x8(%rsp), %xmm5
     908:      	movsd	0x38(%rsp), %xmm7
     90e:      	incq	%r14
     911:      	cmpq	%r14, %rcx
     914:      	je	0xc2d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc2d>
     91a:      	movapd	%xmm5, %xmm9
     91f:      	movapd	%xmm6, %xmm8
     924:      	movsd	(%rbp,%r14,8), %xmm5
     92b:      	movq	0x78(%rsp), %rcx
     930:      	movsd	(%rcx,%r14,8), %xmm6
     936:      	cmpq	$0x1, %rax
     93a:      	movsd	%xmm5, 0x8(%rsp)
     940:      	movsd	%xmm6, 0x30(%rsp)
     946:      	jne	0x99c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x99c>
     948:      	ucomisd	%xmm5, %xmm2
     94c:      	jae	0x9fc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9fc>
     952:      	cmpq	%rbx, %r14
     955:      	jae	0xdac <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xdac>
     95b:      	movsd	%xmm2, (%r12,%r14,8)
     961:      	ucomisd	%xmm7, %xmm6
     965:      	movsd	%xmm9, 0x58(%rsp)
     96c:      	jbe	0xb23 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb23>
     972:      	movsd	0x40(%rsp), %xmm0
     978:      	addsd	0xa0(%rsp), %xmm0
     981:      	ucomisd	%xmm3, %xmm0
     985:      	movapd	%xmm6, %xmm7
     989:      	jbe	0xb29 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb29>
     98f:      	movapd	%xmm6, %xmm7
     993:      	movapd	%xmm3, %xmm0
     997:      	jmp	0xb29 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb29>
     99c:      	ucomisd	%xmm2, %xmm6
     9a0:      	jae	0xa95 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xa95>
     9a6:      	cmpq	%rbx, %r14
     9a9:      	jae	0xd86 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd86>
     9af:      	movapd	%xmm2, %xmm0
     9b3:      	xorpd	(%rip), %xmm0           # 0x9bb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9bb>
		00000000000009b7:  R_X86_64_PC32	.LCPI0_5-0x4
     9bb:      	movlpd	%xmm0, (%r12,%r14,8)
     9c1:      	ucomisd	%xmm5, %xmm7
     9c5:      	movsd	%xmm8, 0x48(%rsp)
     9cc:      	jbe	0xb88 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb88>
     9d2:      	movsd	0x60(%rsp), %xmm0
     9d8:      	addsd	0x98(%rsp), %xmm0
     9e1:      	ucomisd	%xmm1, %xmm0
     9e5:      	movapd	%xmm5, %xmm7
     9e9:      	jbe	0xb8e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb8e>
     9ef:      	movapd	%xmm5, %xmm7
     9f3:      	movapd	%xmm1, %xmm0
     9f7:      	jmp	0xb8e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb8e>
     9fc:      	cmpq	%rbx, %r14
     9ff:      	jae	0xd99 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd99>
     a05:      	movapd	%xmm8, %xmm0
     a0a:      	maxsd	%xmm7, %xmm0
     a0e:      	movapd	%xmm6, %xmm1
     a12:      	maxsd	%xmm0, %xmm1
     a16:      	movsd	0x50(%rsp), %xmm2
     a1c:      	mulsd	%xmm1, %xmm2
     a20:      	addsd	%xmm1, %xmm2
     a24:      	movapd	0x80(%rsp), %xmm3
     a2d:      	movapd	%xmm3, %xmm0
     a31:      	andnpd	%xmm1, %xmm0
     a35:      	andpd	%xmm3, %xmm2
     a39:      	orpd	%xmm0, %xmm2
     a3d:      	movapd	%xmm2, %xmm0
     a41:      	xorpd	(%rip), %xmm0           # 0xa49 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xa49>
		0000000000000a45:  R_X86_64_PC32	.LCPI0_5-0x4
     a49:      	movlpd	%xmm0, (%r12,%r14,8)
     a4f:      	movapd	%xmm5, %xmm1
     a53:      	subsd	%xmm2, %xmm1
     a57:      	movapd	%xmm4, %xmm0
     a5b:      	movsd	%xmm8, 0x48(%rsp)
     a62:      	callq	*(%rip)                 # 0xa68 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xa68>
		0000000000000a64:  R_X86_64_GOTPCREL	fma-0x4
     a68:      	movsd	0x48(%rsp), %xmm2
     a6e:      	movsd	0x30(%rsp), %xmm6
     a74:      	maxsd	%xmm0, %xmm2
     a78:      	ucomisd	%xmm2, %xmm6
     a7c:      	jbe	0xbcb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xbcb>
     a82:      	movsd	0x8(%rsp), %xmm5
     a88:      	movapd	%xmm5, %xmm7
     a8c:      	movapd	%xmm6, %xmm2
     a90:      	jmp	0xbd5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xbd5>
     a95:      	cmpq	%rbx, %r14
     a98:      	jae	0xd73 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd73>
     a9e:      	movapd	%xmm9, %xmm1
     aa3:      	minsd	%xmm7, %xmm1
     aa7:      	movapd	%xmm5, %xmm2
     aab:      	minsd	%xmm1, %xmm2
     aaf:      	movsd	0x50(%rsp), %xmm3
     ab5:      	mulsd	%xmm2, %xmm3
     ab9:      	movapd	0x80(%rsp), %xmm4
     ac2:      	movapd	%xmm4, %xmm1
     ac6:      	andnpd	%xmm2, %xmm1
     aca:      	subsd	%xmm3, %xmm2
     ace:      	andpd	%xmm4, %xmm2
     ad2:      	orpd	%xmm1, %xmm2
     ad6:      	movlpd	%xmm2, (%r12,%r14,8)
     adc:      	movapd	%xmm6, %xmm1
     ae0:      	subsd	%xmm2, %xmm1
     ae4:      	movsd	%xmm9, 0x58(%rsp)
     aeb:      	callq	*(%rip)                 # 0xaf1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xaf1>
		0000000000000aed:  R_X86_64_GOTPCREL	fma-0x4
     af1:      	movsd	0x58(%rsp), %xmm2
     af7:      	movsd	0x8(%rsp), %xmm5
     afd:      	minsd	%xmm0, %xmm2
     b01:      	movl	$0x1, %eax
     b06:      	ucomisd	%xmm5, %xmm2
     b0a:      	jbe	0xbfd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xbfd>
     b10:      	movsd	0x30(%rsp), %xmm6
     b16:      	movapd	%xmm6, %xmm7
     b1a:      	movapd	%xmm5, %xmm2
     b1e:      	jmp	0xc07 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc07>
     b23:      	movsd	0x40(%rsp), %xmm0
     b29:      	movsd	%xmm7, 0x38(%rsp)
     b2f:      	movapd	%xmm7, %xmm1
     b33:      	subsd	%xmm2, %xmm1
     b37:      	movsd	%xmm0, 0x40(%rsp)
     b3d:      	callq	*(%rip)                 # 0xb43 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb43>
		0000000000000b3f:  R_X86_64_GOTPCREL	fma-0x4
     b43:      	movsd	0x58(%rsp), %xmm2
     b49:      	minsd	%xmm0, %xmm2
     b4d:      	movl	$0x1, %eax
     b52:      	movsd	0x8(%rsp), %xmm5
     b58:      	ucomisd	%xmm5, %xmm2
     b5c:      	jbe	0xb62 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xb62>
     b5e:      	movapd	%xmm5, %xmm2
     b62:      	movq	%r13, %rcx
     b65:      	movsd	0x28(%rsp), %xmm1
     b6b:      	movsd	0x20(%rsp), %xmm3
     b71:      	movsd	0x18(%rsp), %xmm0
     b77:      	movsd	0x10(%rsp), %xmm4
     b7d:      	movsd	0x30(%rsp), %xmm6
     b83:      	jmp	0x908 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x908>
     b88:      	movsd	0x60(%rsp), %xmm0
     b8e:      	movsd	%xmm7, 0x38(%rsp)
     b94:      	movapd	%xmm7, %xmm1
     b98:      	subsd	%xmm2, %xmm1
     b9c:      	movsd	%xmm0, 0x60(%rsp)
     ba2:      	callq	*(%rip)                 # 0xba8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xba8>
		0000000000000ba4:  R_X86_64_GOTPCREL	fma-0x4
     ba8:      	movsd	0x48(%rsp), %xmm2
     bae:      	maxsd	%xmm0, %xmm2
     bb2:      	movsd	0x30(%rsp), %xmm6
     bb8:      	ucomisd	%xmm2, %xmm6
     bbc:      	jbe	0x8e5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x8e5>
     bc2:      	movapd	%xmm6, %xmm2
     bc6:      	jmp	0x8e5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x8e5>
     bcb:      	movsd	0x8(%rsp), %xmm5
     bd1:      	movapd	%xmm5, %xmm7
     bd5:      	movsd	0x10(%rsp), %xmm4
     bdb:      	movsd	%xmm4, 0x60(%rsp)
     be1:      	xorl	%eax, %eax
     be3:      	movq	%r13, %rcx
     be6:      	movsd	0x28(%rsp), %xmm1
     bec:      	movsd	0x20(%rsp), %xmm3
     bf2:      	movsd	0x18(%rsp), %xmm0
     bf8:      	jmp	0x90e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x90e>
     bfd:      	movsd	0x30(%rsp), %xmm6
     c03:      	movapd	%xmm6, %xmm7
     c07:      	movsd	0x18(%rsp), %xmm0
     c0d:      	movsd	%xmm0, 0x40(%rsp)
     c13:      	movq	%r13, %rcx
     c16:      	movsd	0x28(%rsp), %xmm1
     c1c:      	movsd	0x20(%rsp), %xmm3
     c22:      	movsd	0x10(%rsp), %xmm4
     c28:      	jmp	0x90e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x90e>
     c2d:      	movq	%rcx, (%r15)
     c30:      	xorl	%eax, %eax
     c32:      	jmp	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     c37:      	movq	%rdx, 0x8(%rsp)
     c3c:      	movq	%r9, %rbp
     c3f:      	movq	%rcx, 0x30(%rsp)
     c44:      	movq	%rsi, 0x78(%rsp)
     c49:      	movq	%rdi, 0x50(%rsp)
     c4e:      	movq	%r8, 0x18(%rsp)
     c53:      	movsd	%xmm7, 0x28(%rsp)
     c59:      	movsd	%xmm4, 0x20(%rsp)
     c5f:      	movsd	%xmm6, 0x10(%rsp)
     c65:      	movsd	%xmm5, 0x38(%rsp)
     c6b:      	movsd	%xmm3, 0x48(%rsp)
     c71:      	movsd	%xmm9, 0x58(%rsp)
     c78:      	movsd	%xmm1, 0x40(%rsp)
     c7e:      	movapd	%xmm8, 0x60(%rsp)
     c85:      	callq	*(%rip)                 # 0xc8b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xc8b>
		0000000000000c87:  R_X86_64_GOTPCREL	_RNvNtNtCsi9YoAGUbCUq_10std_detect6detect5cache21detect_and_initialize-0x4
     c8b:      	movapd	0x60(%rsp), %xmm8
     c92:      	movsd	0x40(%rsp), %xmm1
     c98:      	movsd	0x58(%rsp), %xmm9
     c9f:      	movsd	0x48(%rsp), %xmm3
     ca5:      	movsd	0x38(%rsp), %xmm5
     cab:      	movsd	0x10(%rsp), %xmm6
     cb1:      	movsd	0x20(%rsp), %xmm4
     cb7:      	movsd	0x28(%rsp), %xmm7
     cbd:      	movq	0x18(%rsp), %r8
     cc2:      	movq	0x50(%rsp), %rdi
     cc7:      	movq	0x78(%rsp), %rsi
     ccc:      	movq	0x30(%rsp), %rcx
     cd1:      	movq	%rbp, %r9
     cd4:      	movq	0x8(%rsp), %rdx
     cd9:      	btq	$0x38, %rax
     cde:      	jae	0x61 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x61>
     ce4:      	movapd	%xmm8, %xmm0
     ce9:      	movapd	%xmm9, %xmm2
     cee:      	addq	$0xc8, %rsp
     cf5:      	popq	%rbx
     cf6:      	popq	%r12
     cf8:      	popq	%r13
     cfa:      	popq	%r14
     cfc:      	popq	%r15
     cfe:      	popq	%rbp
     cff:      	jmp	0xd04 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd04>
		0000000000000d00:  R_X86_64_PLT32	.text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma-0x4
     d04:      	leaq	(%rip), %rdi            # 0xd0b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd0b>
		0000000000000d07:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     d0b:      	leaq	(%rip), %rdx            # 0xd12 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd12>
		0000000000000d0e:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3609-0x4
     d12:      	movl	$0x40, %esi
     d17:      	callq	*(%rip)                 # 0xd1d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd1d>
		0000000000000d19:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     d1d:      	leaq	(%rip), %rdi            # 0xd24 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd24>
		0000000000000d20:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     d24:      	leaq	(%rip), %rdx            # 0xd2b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd2b>
		0000000000000d27:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3610-0x4
     d2b:      	movl	$0x3f, %esi
     d30:      	callq	*(%rip)                 # 0xd36 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd36>
		0000000000000d32:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     d36:      	leaq	(%rip), %rcx            # 0xd3d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd3d>
		0000000000000d39:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3612-0x4
     d3d:      	xorl	%edi, %edi
     d3f:      	movq	%rdx, %rsi
     d42:      	movq	%r8, %rdx
     d45:      	callq	*(%rip)                 # 0xd4b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd4b>
		0000000000000d47:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     d4b:      	leaq	(%rip), %rcx            # 0xd52 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd52>
		0000000000000d4e:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3613-0x4
     d52:      	xorl	%edi, %edi
     d54:      	movq	%rdx, %rsi
     d57:      	movq	%r14, %rdx
     d5a:      	callq	*(%rip)                 # 0xd60 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd60>
		0000000000000d5c:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     d60:      	movzbl	0x8(%rsp), %ebp
     d65:      	testb	%bpl, %bpl
     d68:      	jne	0x27f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x27f>
     d6e:      	jmp	0x391 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x391>
     d73:      	leaq	(%rip), %rdx            # 0xd7a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd7a>
		0000000000000d76:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3617-0x4
     d7a:      	movq	%r14, %rdi
     d7d:      	movq	%rbx, %rsi
     d80:      	callq	*(%rip)                 # 0xd86 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd86>
		0000000000000d82:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     d86:      	leaq	(%rip), %rdx            # 0xd8d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd8d>
		0000000000000d89:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3616-0x4
     d8d:      	movq	%r14, %rdi
     d90:      	movq	%rbx, %rsi
     d93:      	callq	*(%rip)                 # 0xd99 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xd99>
		0000000000000d95:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     d99:      	leaq	(%rip), %rdx            # 0xda0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xda0>
		0000000000000d9c:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3615-0x4
     da0:      	movq	%r14, %rdi
     da3:      	movq	%rbx, %rsi
     da6:      	callq	*(%rip)                 # 0xdac <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xdac>
		0000000000000da8:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     dac:      	leaq	(%rip), %rdx            # 0xdb3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xdb3>
		0000000000000daf:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3614-0x4
     db3:      	movq	%r14, %rdi
     db6:      	movq	%rbx, %rsi
     db9:      	callq	*(%rip)                 # 0xdbf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xdbf>
		0000000000000dbb:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
