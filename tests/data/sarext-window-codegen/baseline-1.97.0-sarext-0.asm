
/tmp/polars-recovery/sarext-window-evidence/baseline-static-1.97.0/static-probe.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0xb8, %rsp
      11:      	movapd	%xmm2, %xmm9
      16:      	movapd	%xmm0, %xmm8
      1b:      	movq	0x110(%rsp), %rbx
      23:      	movq	0x108(%rsp), %r12
      2b:      	movq	0x100(%rsp), %r11
      33:      	movq	0xf8(%rsp), %r13
      3b:      	movq	0xf0(%rsp), %r14
      43:      	movq	(%rip), %rax            # 0x4a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4a>
		0000000000000046:  R_X86_64_GOTPCREL	_RNvNtNtCsi9YoAGUbCUq_10std_detect6detect5cache5CACHE-0x4
      4a:      	movq	(%rax), %rax
      4d:      	testq	%rax, %rax
      50:      	je	0x892 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x892>
      56:      	btq	$0x38, %rax
      5b:      	jb	0x943 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x943>
      61:      	movw	$0xd, %ax
      65:      	cmpq	%rsi, %rdx
      68:      	jae	0x7c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7c>
      6a:      	addq	$0xb8, %rsp
      71:      	popq	%rbx
      72:      	popq	%r12
      74:      	popq	%r13
      76:      	popq	%r14
      78:      	popq	%r15
      7a:      	popq	%rbp
      7b:      	retq
      7c:      	xorpd	%xmm0, %xmm0
      80:      	movsd	%xmm0, 0x38(%rsp)
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
      e1:      	movsd	%xmm1, 0x38(%rsp)
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
     268:      	jae	0x2a5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x2a5>
     26a:      	cmpq	%r8, %rdx
     26d:      	setb	%al
     270:      	cmpq	%r14, %rdx
     273:      	setb	%r10b
     277:      	cmpq	$0x1, %rsi
     27b:      	adcq	$0x0, %rsi
     27f:      	movq	$0x0, 0x78(%rsp)
     288:      	cmpq	%rdx, %rsi
     28b:      	jbe	0x3a6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x3a6>
     291:      	movq	$0x0, (%r13)
     299:      	movq	$0x0, (%r11)
     2a0:      	jmp	0x88b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x88b>
     2a5:      	xorpd	%xmm3, %xmm3
     2a9:      	movsd	0x38(%rsp), %xmm5
     2af:      	ucomisd	%xmm3, %xmm5
     2b3:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2b5:      	ucomisd	0x38(%rsp), %xmm1
     2bb:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2bd:      	ucomisd	%xmm3, %xmm8
     2c2:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2c4:      	ucomisd	%xmm8, %xmm1
     2c9:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2cb:      	ucomisd	%xmm3, %xmm11
     2d0:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2d2:      	ucomisd	%xmm11, %xmm1
     2d7:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2d9:      	ucomisd	%xmm3, %xmm4
     2dd:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2df:      	ucomisd	%xmm4, %xmm1
     2e3:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2e5:      	ucomisd	%xmm3, %xmm10
     2ea:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2f0:      	ucomisd	%xmm10, %xmm1
     2f5:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     2fb:      	ucomisd	%xmm3, %xmm9
     300:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     306:      	ucomisd	%xmm9, %xmm1
     30b:      	jb	0x26a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x26a>
     311:      	movq	%r11, 0x50(%rsp)
     316:      	cmpq	$0x1, %rsi
     31a:      	adcq	$0x0, %rsi
     31e:      	ucomisd	%xmm7, %xmm1
     322:      	movq	$-0x1, %rax
     329:      	movq	%rsi, %r11
     32c:      	cmovbq	%rax, %r11
     330:      	xorpd	%xmm1, %xmm1
     334:      	ucomisd	%xmm1, %xmm7
     338:      	cmovbq	%rax, %r11
     33c:      	cmpq	%rdx, %r11
     33f:      	seta	%r10b
     343:      	cmpq	%r8, %rdx
     346:      	setb	%al
     349:      	orb	%al, %r10b
     34c:      	je	0x963 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x963>
     352:      	movq	%rdx, %r15
     355:      	subq	%r11, %r15
     358:      	setb	%bpl
     35c:      	cmpq	%r14, %rdx
     35f:      	setb	%r10b
     363:      	orb	%r10b, %bpl
     366:      	je	0x97c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x97c>
     36c:      	cmpq	%rbx, %r15
     36f:      	setb	%bpl
     373:      	movb	$0x1, %r15b
     376:      	cmpq	%r11, %rdx
     379:      	jae	0xa0b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xa0b>
     37f:      	testb	%r15b, %r15b
     382:      	movq	0x50(%rsp), %r11
     387:      	jne	0x27f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x27f>
     38d:      	leaq	(%rip), %rdi            # 0x394 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x394>
		0000000000000390:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.182-0x4
     394:      	leaq	(%rip), %rdx            # 0x39b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x39b>
		0000000000000397:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3611-0x4
     39b:      	movl	$0x50, %esi
     3a0:      	callq	*(%rip)                 # 0x3a6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x3a6>
		00000000000003a2:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     3a6:      	testb	%al, %al
     3a8:      	je	0x995 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x995>
     3ae:      	testb	%r10b, %r10b
     3b1:      	je	0x9aa <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9aa>
     3b7:      	incq	%rdx
     3ba:      	xorpd	%xmm1, %xmm1
     3be:      	ucomisd	%xmm1, %xmm2
     3c2:      	movsd	%xmm7, 0x8(%rsp)
     3c8:      	movsd	%xmm4, (%rsp)
     3cd:      	movq	%r11, 0x50(%rsp)
     3d2:      	jne	0x464 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x464>
     3d8:      	jp	0x464 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x464>
     3de:      	movsd	%xmm10, 0x30(%rsp)
     3e5:      	movsd	%xmm9, 0x20(%rsp)
     3ec:      	movsd	%xmm8, 0x28(%rsp)
     3f3:      	movsd	%xmm11, 0x10(%rsp)
     3fa:      	subq	$0x8, %rsp
     3fe:      	leaq	0x80(%rsp), %r11
     406:      	leaq	0xa8(%rsp), %rax
     40e:      	movq	%rdi, %r8
     411:      	movq	%rax, %rdi
     414:      	movq	%rsi, %rax
     417:      	movq	%r8, %rsi
     41a:      	movq	%rdx, %r10
     41d:      	movq	%rax, %rdx
     420:      	movq	%rax, %rbp
     423:      	movq	%rcx, %r8
     426:      	movq	%rax, %rcx
     429:      	movq	%r8, %r15
     42c:      	movq	%r9, %rax
     42f:      	movq	%r10, %r9
     432:      	pushq	$0x1
     434:      	pushq	%r11
     436:      	pushq	$0x1
     438:      	movq	%r10, 0x38(%rsp)
     43d:      	pushq	%r10
     43f:      	movq	%rax, %r14
     442:      	pushq	%rax
     443:      	callq	*(%rip)                 # 0x449 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x449>
		0000000000000445:  R_X86_64_GOTPCREL	_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func8minus_dmNtNtB4_5types4Core8minus_dm-0x4
     449:      	addq	$0x30, %rsp
     44d:      	cmpb	$0x0, 0xa0(%rsp)
     455:      	je	0x47d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x47d>
     457:      	movzwl	0xa2(%rsp), %eax
     45f:      	jmp	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     464:      	seta	%al
     467:      	movq	%rsi, (%r13)
     46b:      	movq	%r9, %rdi
     46e:      	cmovaq	%rcx, %rdi
     472:      	movzbl	%al, %eax
     475:      	ja	0x4e9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4e9>
     477:      	movapd	%xmm0, %xmm2
     47b:      	jmp	0x4e9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4e9>
     47d:      	movsd	0x78(%rsp), %xmm0
     483:      	xorpd	%xmm1, %xmm1
     487:      	ucomisd	%xmm1, %xmm0
     48b:      	movq	%rbp, %rsi
     48e:      	movq	%rbp, (%r13)
     492:      	ja	0x4ab <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4ab>
     494:      	movq	%r14, %r9
     497:      	movsd	-0x8(%r14,%rsi,8), %xmm2
     49e:      	movl	$0x1, %eax
     4a3:      	movq	%r15, %rcx
     4a6:      	movq	%r15, %rdi
     4a9:      	jmp	0x4bd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x4bd>
     4ab:      	movq	%r15, %rcx
     4ae:      	movsd	-0x8(%r15,%rsi,8), %xmm2
     4b5:      	xorl	%eax, %eax
     4b7:      	movq	%r14, %r9
     4ba:      	movq	%r14, %rdi
     4bd:      	movq	0x18(%rsp), %rdx
     4c2:      	movsd	0x8(%rsp), %xmm7
     4c8:      	movsd	(%rsp), %xmm4
     4cd:      	movsd	0x10(%rsp), %xmm11
     4d4:      	movsd	0x28(%rsp), %xmm8
     4db:      	movsd	0x20(%rsp), %xmm9
     4e2:      	movsd	0x30(%rsp), %xmm10
     4e9:      	movapd	%xmm4, %xmm0
     4ed:      	minsd	%xmm8, %xmm0
     4f2:      	movapd	%xmm4, %xmm1
     4f6:      	minsd	%xmm11, %xmm1
     4fb:      	movsd	%xmm1, 0x88(%rsp)
     504:      	movapd	%xmm7, %xmm1
     508:      	minsd	%xmm10, %xmm1
     50d:      	movapd	%xmm7, %xmm3
     511:      	minsd	%xmm9, %xmm3
     516:      	movsd	%xmm3, 0x80(%rsp)
     51f:      	leaq	(%rcx,%rsi,8), %r13
     523:      	movsd	(%rcx,%rsi,8), %xmm5
     528:      	leaq	(%r9,%rsi,8), %rbp
     52c:      	movsd	(%r9,%rsi,8), %xmm3
     532:      	movsd	(%rdi,%rsi,8), %xmm8
     538:      	subq	%rsi, %rdx
     53b:      	xorl	%r14d, %r14d
     53e:      	xorpd	%xmm6, %xmm6
     542:      	cmpneqsd	0x38(%rsp), %xmm6
     549:      	movapd	%xmm6, 0x90(%rsp)
     552:      	movsd	%xmm0, 0x58(%rsp)
     558:      	movsd	%xmm0, 0x40(%rsp)
     55e:      	movsd	%xmm1, 0x60(%rsp)
     564:      	movsd	%xmm1, 0x48(%rsp)
     56a:      	movq	%rdx, %r15
     56d:      	jmp	0x5a6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x5a6>
     56f:      	movsd	0x18(%rsp), %xmm3
     575:      	movapd	%xmm3, %xmm8
     57a:      	movapd	%xmm5, %xmm2
     57e:      	movsd	0x60(%rsp), %xmm0
     584:      	movsd	%xmm0, 0x48(%rsp)
     58a:      	xorl	%eax, %eax
     58c:      	movq	%r15, %rcx
     58f:      	movsd	0x8(%rsp), %xmm7
     595:      	movsd	(%rsp), %xmm4
     59a:      	incq	%r14
     59d:      	cmpq	%r14, %rcx
     5a0:      	je	0x883 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x883>
     5a6:      	movapd	%xmm5, %xmm9
     5ab:      	movsd	(%rbp,%r14,8), %xmm5
     5b2:      	movsd	(%r13,%r14,8), %xmm6
     5b9:      	cmpq	$0x1, %rax
     5bd:      	movsd	%xmm5, 0x18(%rsp)
     5c3:      	movsd	%xmm6, 0x10(%rsp)
     5c9:      	jne	0x630 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x630>
     5cb:      	ucomisd	%xmm5, %xmm2
     5cf:      	jae	0x6de <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6de>
     5d5:      	cmpq	%rbx, %r14
     5d8:      	jae	0x9f8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9f8>
     5de:      	movsd	%xmm2, (%r12,%r14,8)
     5e4:      	ucomisd	%xmm8, %xmm6
     5e9:      	movsd	%xmm3, 0x28(%rsp)
     5ef:      	jbe	0x806 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x806>
     5f5:      	movsd	0x40(%rsp), %xmm0
     5fb:      	addsd	0x88(%rsp), %xmm0
     604:      	ucomisd	%xmm4, %xmm0
     608:      	movapd	%xmm6, %xmm8
     60d:      	jbe	0x80c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x80c>
     613:      	movapd	%xmm6, %xmm8
     618:      	movapd	%xmm4, %xmm0
     61c:      	jmp	0x80c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x80c>
     621:      	nopw	%cs:(%rax,%rax)
     630:      	ucomisd	%xmm2, %xmm6
     634:      	jae	0x777 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x777>
     63a:      	cmpq	%rbx, %r14
     63d:      	movsd	0x48(%rsp), %xmm0
     643:      	jae	0x9d2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9d2>
     649:      	movapd	%xmm2, %xmm1
     64d:      	xorpd	(%rip), %xmm1           # 0x655 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x655>
		0000000000000651:  R_X86_64_PC32	.LCPI0_5-0x4
     655:      	movlpd	%xmm1, (%r12,%r14,8)
     65b:      	ucomisd	%xmm5, %xmm8
     660:      	movsd	%xmm9, 0x30(%rsp)
     667:      	jbe	0x686 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x686>
     669:      	addsd	0x80(%rsp), %xmm0
     672:      	ucomisd	%xmm7, %xmm0
     676:      	movapd	%xmm5, %xmm8
     67b:      	jbe	0x686 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x686>
     67d:      	movapd	%xmm5, %xmm8
     682:      	movapd	%xmm7, %xmm0
     686:      	movsd	%xmm8, 0x20(%rsp)
     68d:      	movapd	%xmm8, %xmm1
     692:      	subsd	%xmm2, %xmm1
     696:      	movsd	%xmm0, 0x48(%rsp)
     69c:      	callq	*(%rip)                 # 0x6a2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a2>
		000000000000069e:  R_X86_64_GOTPCREL	fma-0x4
     6a2:      	movsd	0x30(%rsp), %xmm2
     6a8:      	maxsd	%xmm0, %xmm2
     6ac:      	movsd	0x10(%rsp), %xmm5
     6b2:      	ucomisd	%xmm2, %xmm5
     6b6:      	jbe	0x6bc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6bc>
     6b8:      	movapd	%xmm5, %xmm2
     6bc:      	xorl	%eax, %eax
     6be:      	movq	%r15, %rcx
     6c1:      	movsd	0x8(%rsp), %xmm7
     6c7:      	movsd	(%rsp), %xmm4
     6cc:      	movsd	0x18(%rsp), %xmm3
     6d2:      	movsd	0x20(%rsp), %xmm8
     6d9:      	jmp	0x59a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x59a>
     6de:      	cmpq	%rbx, %r14
     6e1:      	movsd	0x60(%rsp), %xmm0
     6e7:      	jae	0x9e5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9e5>
     6ed:      	movapd	%xmm9, %xmm2
     6f2:      	maxsd	%xmm8, %xmm2
     6f7:      	movapd	%xmm6, %xmm1
     6fb:      	maxsd	%xmm2, %xmm1
     6ff:      	movsd	0x38(%rsp), %xmm2
     705:      	mulsd	%xmm1, %xmm2
     709:      	addsd	%xmm1, %xmm2
     70d:      	movapd	0x90(%rsp), %xmm4
     716:      	movapd	%xmm4, %xmm3
     71a:      	andnpd	%xmm1, %xmm3
     71e:      	andpd	%xmm4, %xmm2
     722:      	orpd	%xmm3, %xmm2
     726:      	movapd	%xmm2, %xmm1
     72a:      	xorpd	(%rip), %xmm1           # 0x732 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x732>
		000000000000072e:  R_X86_64_PC32	.LCPI0_5-0x4
     732:      	movlpd	%xmm1, (%r12,%r14,8)
     738:      	movapd	%xmm5, %xmm1
     73c:      	subsd	%xmm2, %xmm1
     740:      	movsd	%xmm9, 0x30(%rsp)
     747:      	callq	*(%rip)                 # 0x74d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x74d>
		0000000000000749:  R_X86_64_GOTPCREL	fma-0x4
     74d:      	movsd	0x30(%rsp), %xmm2
     753:      	movsd	0x10(%rsp), %xmm5
     759:      	maxsd	%xmm0, %xmm2
     75d:      	ucomisd	%xmm2, %xmm5
     761:      	ja	0x56f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x56f>
     767:      	movsd	0x18(%rsp), %xmm3
     76d:      	movapd	%xmm3, %xmm8
     772:      	jmp	0x57e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x57e>
     777:      	cmpq	%rbx, %r14
     77a:      	movsd	0x58(%rsp), %xmm0
     780:      	jae	0x9bf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9bf>
     786:      	movsd	%xmm3, 0x28(%rsp)
     78c:      	movsd	0x28(%rsp), %xmm1
     792:      	minsd	%xmm8, %xmm1
     797:      	movapd	%xmm5, %xmm2
     79b:      	minsd	%xmm1, %xmm2
     79f:      	movsd	0x38(%rsp), %xmm3
     7a5:      	mulsd	%xmm2, %xmm3
     7a9:      	movapd	0x90(%rsp), %xmm4
     7b2:      	movapd	%xmm4, %xmm1
     7b6:      	andnpd	%xmm2, %xmm1
     7ba:      	subsd	%xmm3, %xmm2
     7be:      	andpd	%xmm4, %xmm2
     7c2:      	orpd	%xmm1, %xmm2
     7c6:      	movlpd	%xmm2, (%r12,%r14,8)
     7cc:      	movapd	%xmm6, %xmm1
     7d0:      	subsd	%xmm2, %xmm1
     7d4:      	callq	*(%rip)                 # 0x7da <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x7da>
		00000000000007d6:  R_X86_64_GOTPCREL	fma-0x4
     7da:      	movsd	0x28(%rsp), %xmm2
     7e0:      	movsd	0x18(%rsp), %xmm3
     7e6:      	minsd	%xmm0, %xmm2
     7ea:      	movl	$0x1, %eax
     7ef:      	ucomisd	%xmm3, %xmm2
     7f3:      	jbe	0x867 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x867>
     7f5:      	movsd	0x10(%rsp), %xmm5
     7fb:      	movapd	%xmm5, %xmm8
     800:      	movapd	%xmm3, %xmm2
     804:      	jmp	0x872 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x872>
     806:      	movsd	0x40(%rsp), %xmm0
     80c:      	movsd	%xmm8, 0x20(%rsp)
     813:      	movapd	%xmm8, %xmm1
     818:      	subsd	%xmm2, %xmm1
     81c:      	movsd	%xmm0, 0x40(%rsp)
     822:      	callq	*(%rip)                 # 0x828 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x828>
		0000000000000824:  R_X86_64_GOTPCREL	fma-0x4
     828:      	movsd	0x28(%rsp), %xmm2
     82e:      	minsd	%xmm0, %xmm2
     832:      	movl	$0x1, %eax
     837:      	movsd	0x18(%rsp), %xmm3
     83d:      	ucomisd	%xmm3, %xmm2
     841:      	jbe	0x847 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x847>
     843:      	movapd	%xmm3, %xmm2
     847:      	movq	%r15, %rcx
     84a:      	movsd	0x8(%rsp), %xmm7
     850:      	movsd	(%rsp), %xmm4
     855:      	movsd	0x10(%rsp), %xmm5
     85b:      	movsd	0x20(%rsp), %xmm8
     862:      	jmp	0x59a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x59a>
     867:      	movsd	0x10(%rsp), %xmm5
     86d:      	movapd	%xmm5, %xmm8
     872:      	movsd	0x58(%rsp), %xmm0
     878:      	movsd	%xmm0, 0x40(%rsp)
     87e:      	jmp	0x58c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x58c>
     883:      	movq	0x50(%rsp), %rax
     888:      	movq	%rcx, (%rax)
     88b:      	xorl	%eax, %eax
     88d:      	jmp	0x6a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x6a>
     892:      	movq	%rdx, 0x18(%rsp)
     897:      	movq	%r11, 0x50(%rsp)
     89c:      	movq	%r9, %r15
     89f:      	movq	%rsi, 0x28(%rsp)
     8a4:      	movq	%rcx, %rbp
     8a7:      	movq	%rdi, 0x10(%rsp)
     8ac:      	movq	%r8, 0x38(%rsp)
     8b1:      	movsd	%xmm7, 0x8(%rsp)
     8b7:      	movsd	%xmm4, (%rsp)
     8bc:      	movsd	%xmm6, 0x20(%rsp)
     8c2:      	movsd	%xmm5, 0x30(%rsp)
     8c8:      	movsd	%xmm3, 0x48(%rsp)
     8ce:      	movsd	%xmm9, 0x40(%rsp)
     8d5:      	movsd	%xmm1, 0x58(%rsp)
     8db:      	movapd	%xmm8, 0x60(%rsp)
     8e2:      	callq	*(%rip)                 # 0x8e8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x8e8>
		00000000000008e4:  R_X86_64_GOTPCREL	_RNvNtNtCsi9YoAGUbCUq_10std_detect6detect5cache21detect_and_initialize-0x4
     8e8:      	movapd	0x60(%rsp), %xmm8
     8ef:      	movsd	0x58(%rsp), %xmm1
     8f5:      	movsd	0x40(%rsp), %xmm9
     8fc:      	movsd	0x48(%rsp), %xmm3
     902:      	movsd	0x30(%rsp), %xmm5
     908:      	movsd	0x20(%rsp), %xmm6
     90e:      	movsd	(%rsp), %xmm4
     913:      	movsd	0x8(%rsp), %xmm7
     919:      	movq	0x38(%rsp), %r8
     91e:      	movq	0x10(%rsp), %rdi
     923:      	movq	%rbp, %rcx
     926:      	movq	0x28(%rsp), %rsi
     92b:      	movq	%r15, %r9
     92e:      	movq	0x50(%rsp), %r11
     933:      	movq	0x18(%rsp), %rdx
     938:      	btq	$0x38, %rax
     93d:      	jae	0x61 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x61>
     943:      	movapd	%xmm8, %xmm0
     948:      	movapd	%xmm9, %xmm2
     94d:      	addq	$0xb8, %rsp
     954:      	popq	%rbx
     955:      	popq	%r12
     957:      	popq	%r13
     959:      	popq	%r14
     95b:      	popq	%r15
     95d:      	popq	%rbp
     95e:      	jmp	0x963 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x963>
		000000000000095f:  R_X86_64_PLT32	.text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma-0x4
     963:      	leaq	(%rip), %rdi            # 0x96a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x96a>
		0000000000000966:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     96a:      	leaq	(%rip), %rdx            # 0x971 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x971>
		000000000000096d:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3609-0x4
     971:      	movl	$0x40, %esi
     976:      	callq	*(%rip)                 # 0x97c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x97c>
		0000000000000978:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     97c:      	leaq	(%rip), %rdi            # 0x983 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x983>
		000000000000097f:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     983:      	leaq	(%rip), %rdx            # 0x98a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x98a>
		0000000000000986:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3610-0x4
     98a:      	movl	$0x3f, %esi
     98f:      	callq	*(%rip)                 # 0x995 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x995>
		0000000000000991:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     995:      	leaq	(%rip), %rcx            # 0x99c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x99c>
		0000000000000998:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3612-0x4
     99c:      	xorl	%edi, %edi
     99e:      	movq	%rdx, %rsi
     9a1:      	movq	%r8, %rdx
     9a4:      	callq	*(%rip)                 # 0x9aa <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9aa>
		00000000000009a6:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     9aa:      	leaq	(%rip), %rcx            # 0x9b1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9b1>
		00000000000009ad:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3613-0x4
     9b1:      	xorl	%edi, %edi
     9b3:      	movq	%rdx, %rsi
     9b6:      	movq	%r14, %rdx
     9b9:      	callq	*(%rip)                 # 0x9bf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9bf>
		00000000000009bb:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     9bf:      	leaq	(%rip), %rdx            # 0x9c6 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9c6>
		00000000000009c2:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3617-0x4
     9c6:      	movq	%r14, %rdi
     9c9:      	movq	%rbx, %rsi
     9cc:      	callq	*(%rip)                 # 0x9d2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9d2>
		00000000000009ce:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     9d2:      	leaq	(%rip), %rdx            # 0x9d9 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9d9>
		00000000000009d5:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3616-0x4
     9d9:      	movq	%r14, %rdi
     9dc:      	movq	%rbx, %rsi
     9df:      	callq	*(%rip)                 # 0x9e5 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9e5>
		00000000000009e1:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     9e5:      	leaq	(%rip), %rdx            # 0x9ec <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9ec>
		00000000000009e8:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3615-0x4
     9ec:      	movq	%r14, %rdi
     9ef:      	movq	%rbx, %rsi
     9f2:      	callq	*(%rip)                 # 0x9f8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9f8>
		00000000000009f4:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     9f8:      	leaq	(%rip), %rdx            # 0x9ff <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x9ff>
		00000000000009fb:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3614-0x4
     9ff:      	movq	%r14, %rdi
     a02:      	movq	%rbx, %rsi
     a05:      	callq	*(%rip)                 # 0xa0b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0xa0b>
		0000000000000a07:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     a0b:      	movl	%ebp, %r15d
     a0e:      	testb	%r15b, %r15b
     a11:      	movq	0x50(%rsp), %r11
     a16:      	jne	0x27f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x27f>
     a1c:      	jmp	0x38d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core11sarext_impl+0x38d>
