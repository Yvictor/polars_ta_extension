
/tmp/polars-recovery/sarext-window-evidence/candidate-static-1.97.0/static-probe.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma:

0000000000000000 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0x58, %rsp
       e:      	movw	$0xd, %ax
      12:      	cmpq	%rsi, %rdx
      15:      	jae	0x26 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x26>
      17:      	addq	$0x58, %rsp
      1b:      	popq	%rbx
      1c:      	popq	%r12
      1e:      	popq	%r13
      20:      	popq	%r14
      22:      	popq	%r15
      24:      	popq	%rbp
      25:      	retq
      26:      	vxorpd	%xmm10, %xmm10, %xmm10
      2b:      	vucomisd	(%rip), %xmm0           # 0x33 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x33>
		000000000000002f:  R_X86_64_PC32	.LCPI1_0-0x4
      33:      	vxorpd	%xmm9, %xmm9, %xmm9
      38:      	jne	0x3c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x3c>
      3a:      	jnp	0x5b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5b>
      3c:      	vandpd	(%rip), %xmm0, %xmm9    # 0x44 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x44>
		0000000000000040:  R_X86_64_PC32	.LCPI1_1-0x4
      44:      	movw	$0x2, %ax
      48:      	vmovsd	(%rip), %xmm8           # 0x50 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x50>
		000000000000004c:  R_X86_64_PC32	.LCPI1_2-0x4
      50:      	vucomisd	%xmm9, %xmm8
      55:      	vmovapd	%xmm0, %xmm9
      59:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      5b:      	vucomisd	(%rip), %xmm1           # 0x63 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x63>
		000000000000005f:  R_X86_64_PC32	.LCPI1_0-0x4
      63:      	jne	0x67 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x67>
      65:      	jnp	0x87 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x87>
      67:      	vxorpd	%xmm0, %xmm0, %xmm0
      6b:      	vucomisd	%xmm0, %xmm1
      6f:      	movw	$0x2, %ax
      73:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      75:      	vmovsd	(%rip), %xmm0           # 0x7d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x7d>
		0000000000000079:  R_X86_64_PC32	.LCPI1_2-0x4
      7d:      	vucomisd	%xmm1, %xmm0
      81:      	vmovapd	%xmm1, %xmm10
      85:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      87:      	vmovsd	(%rip), %xmm8           # 0x8f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x8f>
		000000000000008b:  R_X86_64_PC32	.LCPI1_3-0x4
      8f:      	vucomisd	(%rip), %xmm2           # 0x97 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x97>
		0000000000000093:  R_X86_64_PC32	.LCPI1_0-0x4
      97:      	vmovapd	%xmm8, %xmm11
      9c:      	jne	0xa0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xa0>
      9e:      	jnp	0xc8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xc8>
      a0:      	vxorpd	%xmm0, %xmm0, %xmm0
      a4:      	vucomisd	%xmm0, %xmm2
      a8:      	movw	$0x2, %ax
      ac:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      b2:      	vmovsd	(%rip), %xmm0           # 0xba <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xba>
		00000000000000b6:  R_X86_64_PC32	.LCPI1_2-0x4
      ba:      	vucomisd	%xmm2, %xmm0
      be:      	vmovapd	%xmm2, %xmm11
      c2:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      c8:      	vucomisd	(%rip), %xmm3           # 0xd0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xd0>
		00000000000000cc:  R_X86_64_PC32	.LCPI1_0-0x4
      d0:      	jne	0xd4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xd4>
      d2:      	jnp	0xfc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xfc>
      d4:      	vxorpd	%xmm0, %xmm0, %xmm0
      d8:      	vucomisd	%xmm0, %xmm3
      dc:      	movw	$0x2, %ax
      e0:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      e6:      	vmovsd	(%rip), %xmm0           # 0xee <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xee>
		00000000000000ea:  R_X86_64_PC32	.LCPI1_2-0x4
      ee:      	vucomisd	%xmm3, %xmm0
      f2:      	vmovapd	%xmm3, %xmm8
      f6:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      fc:      	vucomisd	(%rip), %xmm4           # 0x104 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x104>
		0000000000000100:  R_X86_64_PC32	.LCPI1_0-0x4
     104:      	jne	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x112>
     106:      	jp	0x112 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x112>
     108:      	vmovsd	(%rip), %xmm4           # 0x110 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x110>
		000000000000010c:  R_X86_64_PC32	.LCPI1_4-0x4
     110:      	jmp	0x136 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x136>
     112:      	vxorpd	%xmm0, %xmm0, %xmm0
     116:      	vucomisd	%xmm0, %xmm4
     11a:      	movw	$0x2, %ax
     11e:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     124:      	vmovsd	(%rip), %xmm0           # 0x12c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x12c>
		0000000000000128:  R_X86_64_PC32	.LCPI1_2-0x4
     12c:      	vucomisd	%xmm4, %xmm0
     130:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     136:      	vmovsd	(%rip), %xmm3           # 0x13e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x13e>
		000000000000013a:  R_X86_64_PC32	.LCPI1_3-0x4
     13e:      	vucomisd	(%rip), %xmm5           # 0x146 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x146>
		0000000000000142:  R_X86_64_PC32	.LCPI1_0-0x4
     146:      	vmovapd	%xmm3, %xmm12
     14a:      	jne	0x14e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x14e>
     14c:      	jnp	0x176 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x176>
     14e:      	vxorpd	%xmm0, %xmm0, %xmm0
     152:      	vucomisd	%xmm0, %xmm5
     156:      	movw	$0x2, %ax
     15a:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     160:      	vmovsd	(%rip), %xmm0           # 0x168 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x168>
		0000000000000164:  R_X86_64_PC32	.LCPI1_2-0x4
     168:      	vucomisd	%xmm5, %xmm0
     16c:      	vmovapd	%xmm5, %xmm12
     170:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     176:      	vucomisd	(%rip), %xmm6           # 0x17e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17e>
		000000000000017a:  R_X86_64_PC32	.LCPI1_0-0x4
     17e:      	jne	0x182 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x182>
     180:      	jnp	0x1aa <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1aa>
     182:      	vxorpd	%xmm0, %xmm0, %xmm0
     186:      	vucomisd	%xmm0, %xmm6
     18a:      	movw	$0x2, %ax
     18e:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     194:      	vmovsd	(%rip), %xmm0           # 0x19c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x19c>
		0000000000000198:  R_X86_64_PC32	.LCPI1_2-0x4
     19c:      	vucomisd	%xmm6, %xmm0
     1a0:      	vmovapd	%xmm6, %xmm3
     1a4:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     1aa:      	vucomisd	(%rip), %xmm7           # 0x1b2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1b2>
		00000000000001ae:  R_X86_64_PC32	.LCPI1_0-0x4
     1b2:      	jne	0x1c0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1c0>
     1b4:      	jp	0x1c0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1c0>
     1b6:      	vmovsd	(%rip), %xmm7           # 0x1be <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1be>
		00000000000001ba:  R_X86_64_PC32	.LCPI1_4-0x4
     1be:      	jmp	0x1e4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1e4>
     1c0:      	vxorpd	%xmm0, %xmm0, %xmm0
     1c4:      	vucomisd	%xmm0, %xmm7
     1c8:      	movw	$0x2, %ax
     1cc:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     1d2:      	vmovsd	(%rip), %xmm0           # 0x1da <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1da>
		00000000000001d6:  R_X86_64_PC32	.LCPI1_2-0x4
     1da:      	vucomisd	%xmm7, %xmm0
     1de:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     1e4:      	vandpd	(%rip), %xmm9, %xmm0    # 0x1ec <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1ec>
		00000000000001e8:  R_X86_64_PC32	.LCPI1_1-0x4
     1ec:      	movq	0x90(%rsp), %rax
     1f4:      	vmovsd	(%rip), %xmm1           # 0x1fc <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1fc>
		00000000000001f8:  R_X86_64_PC32	.LCPI1_2-0x4
     1fc:      	vucomisd	%xmm0, %xmm1
     200:      	jae	0x250 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x250>
     202:      	cmpq	%r8, %rdx
     205:      	setb	%r10b
     209:      	cmpq	%rax, %rdx
     20c:      	setb	%r11b
     210:      	cmpq	$0x1, %rsi
     214:      	adcq	$0x0, %rsi
     218:      	movq	0x98(%rsp), %r15
     220:      	movq	$0x0, 0x40(%rsp)
     229:      	movq	%rdx, %r14
     22c:      	subq	%rsi, %r14
     22f:      	jae	0x344 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x344>
     235:      	movq	$0x0, (%r15)
     23c:      	xorl	%edx, %edx
     23e:      	movq	0xa0(%rsp), %rax
     246:      	movq	%rdx, (%rax)
     249:      	xorl	%eax, %eax
     24b:      	jmp	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     250:      	vxorpd	%xmm2, %xmm2, %xmm2
     254:      	vucomisd	%xmm2, %xmm10
     258:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     25a:      	vucomisd	%xmm10, %xmm1
     25f:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     261:      	vucomisd	%xmm2, %xmm11
     265:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     267:      	vucomisd	%xmm11, %xmm1
     26c:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     26e:      	vucomisd	%xmm2, %xmm8
     272:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     274:      	vucomisd	%xmm8, %xmm1
     279:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     27b:      	vucomisd	%xmm2, %xmm4
     27f:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     281:      	vucomisd	%xmm4, %xmm1
     285:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     28b:      	vucomisd	%xmm2, %xmm12
     28f:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     295:      	vucomisd	%xmm12, %xmm1
     29a:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     2a0:      	vucomisd	%xmm2, %xmm3
     2a4:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     2aa:      	vucomisd	%xmm3, %xmm1
     2ae:      	jb	0x202 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x202>
     2b4:      	cmpq	$0x1, %rsi
     2b8:      	adcq	$0x0, %rsi
     2bc:      	vucomisd	%xmm7, %xmm1
     2c0:      	movq	$-0x1, %r10
     2c7:      	movq	%rsi, %r14
     2ca:      	cmovbq	%r10, %r14
     2ce:      	vxorpd	%xmm1, %xmm1, %xmm1
     2d2:      	vucomisd	%xmm1, %xmm7
     2d6:      	cmovbq	%r10, %r14
     2da:      	cmpq	%rdx, %r14
     2dd:      	seta	%r11b
     2e1:      	cmpq	%r8, %rdx
     2e4:      	setb	%r10b
     2e8:      	orb	%r10b, %r11b
     2eb:      	je	0x7fb <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x7fb>
     2f1:      	movq	%rdx, %rbx
     2f4:      	subq	%r14, %rbx
     2f7:      	setb	%bpl
     2fb:      	cmpq	%rax, %rdx
     2fe:      	setb	%r11b
     302:      	orb	%r11b, %bpl
     305:      	je	0x814 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x814>
     30b:      	cmpq	0xb0(%rsp), %rbx
     313:      	setb	%bl
     316:      	movb	$0x1, %bpl
     319:      	cmpq	%r14, %rdx
     31c:      	jae	0x857 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x857>
     322:      	testb	%bpl, %bpl
     325:      	jne	0x218 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x218>
     32b:      	leaq	(%rip), %rdi            # 0x332 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x332>
		000000000000032e:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.182-0x4
     332:      	leaq	(%rip), %rdx            # 0x339 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x339>
		0000000000000335:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3611-0x4
     339:      	movl	$0x50, %esi
     33e:      	callq	*(%rip)                 # 0x344 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x344>
		0000000000000340:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     344:      	testb	%r10b, %r10b
     347:      	je	0x82d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x82d>
     34d:      	vmovsd	%xmm4, 0x8(%rsp)
     353:      	vmovsd	%xmm7, 0x10(%rsp)
     359:      	testb	%r11b, %r11b
     35c:      	je	0x842 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x842>
     362:      	incq	%rdx
     365:      	vxorpd	%xmm1, %xmm1, %xmm1
     369:      	vucomisd	%xmm1, %xmm9
     36d:      	jne	0x409 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x409>
     373:      	jp	0x409 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x409>
     379:      	vmovsd	%xmm12, 0x18(%rsp)
     37f:      	vmovsd	%xmm3, 0x20(%rsp)
     385:      	vmovsd	%xmm11, 0x28(%rsp)
     38b:      	vmovsd	%xmm8, 0x30(%rsp)
     391:      	vmovsd	%xmm10, 0x38(%rsp)
     397:      	movl	0xf4(%rdi), %edi
     39d:      	leaq	0x40(%rsp), %rax
     3a2:      	leaq	0x50(%rsp), %r10
     3a7:      	leaq	0x48(%rsp), %r11
     3ac:      	movq	%rdx, %r8
     3af:      	movq	%rsi, %rbx
     3b2:      	movq	%rsi, %rdx
     3b5:      	movq	%rcx, %r12
     3b8:      	movq	%r9, %r13
     3bb:      	pushq	$0x1
     3bd:      	pushq	%rax
     3be:      	pushq	%r10
     3c0:      	pushq	%r11
     3c2:      	pushq	$0x1
     3c4:      	movq	%r8, %rbp
     3c7:      	pushq	%r8
     3c9:      	callq	0x3ce <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x3ce>
		00000000000003ca:  R_X86_64_PLT32	.text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func8minus_dmNtNtB4_5types4Core13minus_dm_impl-0x4
     3ce:      	addq	$0x30, %rsp
     3d2:      	testw	%ax, %ax
     3d5:      	jne	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     3db:      	vmovsd	0x40(%rsp), %xmm0
     3e1:      	vxorpd	%xmm1, %xmm1, %xmm1
     3e5:      	vucomisd	%xmm1, %xmm0
     3e9:      	movq	%rbx, %rsi
     3ec:      	movq	%rbx, (%r15)
     3ef:      	ja	0x436 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x436>
     3f1:      	movq	%r13, %r9
     3f4:      	vmovsd	-0x8(%r13,%rsi,8), %xmm9
     3fb:      	movl	$0x1, %r10d
     401:      	movq	%r12, %rcx
     404:      	movq	%r12, %rdi
     407:      	jmp	0x449 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x449>
     409:      	seta	%al
     40c:      	movq	%rsi, (%r15)
     40f:      	movq	%r9, %rdi
     412:      	cmovaq	%rcx, %rdi
     416:      	movzbl	%al, %r10d
     41a:      	ja	0x420 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x420>
     41c:      	vmovapd	%xmm0, %xmm9
     420:      	vmovsd	0x10(%rsp), %xmm14
     426:      	vmovsd	0x8(%rsp), %xmm15
     42c:      	movq	0xb0(%rsp), %r11
     434:      	jmp	0x47e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x47e>
     436:      	movq	%r12, %rcx
     439:      	vmovsd	-0x8(%r12,%rsi,8), %xmm9
     440:      	xorl	%r10d, %r10d
     443:      	movq	%r13, %r9
     446:      	movq	%r13, %rdi
     449:      	movq	%rbp, %rdx
     44c:      	vmovsd	0x10(%rsp), %xmm14
     452:      	vmovsd	0x8(%rsp), %xmm15
     458:      	vmovsd	0x38(%rsp), %xmm10
     45e:      	movq	0xb0(%rsp), %r11
     466:      	vmovsd	0x30(%rsp), %xmm8
     46c:      	vmovsd	0x28(%rsp), %xmm11
     472:      	vmovsd	0x20(%rsp), %xmm3
     478:      	vmovsd	0x18(%rsp), %xmm12
     47e:      	movq	0xa8(%rsp), %rax
     486:      	vminsd	%xmm11, %xmm15, %xmm0
     48b:      	vminsd	%xmm8, %xmm15, %xmm1
     490:      	vmovsd	%xmm1, 0x10(%rsp)
     496:      	vminsd	%xmm12, %xmm14, %xmm2
     49b:      	vminsd	%xmm3, %xmm14, %xmm1
     49f:      	vmovsd	%xmm1, 0x8(%rsp)
     4a5:      	vmovsd	(%rdi,%rsi,8), %xmm7
     4aa:      	leaq	(%r9,%rsi,8), %r8
     4ae:      	vmovsd	(%r9,%rsi,8), %xmm5
     4b4:      	leaq	(%rcx,%rsi,8), %r9
     4b8:      	vmovsd	(%rcx,%rsi,8), %xmm6
     4bd:      	subq	%rsi, %rdx
     4c0:      	cmpq	%r11, %r14
     4c3:      	jae	0x650 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x650>
     4c9:      	xorl	%ecx, %ecx
     4cb:      	vxorpd	%xmm8, %xmm8, %xmm8
     4d0:      	vmovapd	%xmm10, %xmm3
     4d4:      	vcmpneqsd	%xmm8, %xmm10, %xmm8
     4da:      	vmovddup	(%rip), %xmm1           # xmm1 = mem[0,0]
                                                # 0x4e2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e2>
		00000000000004de:  R_X86_64_PC32	.LCPI1_6-0x4
     4e2:      	vmovapd	%xmm0, %xmm10
     4e6:      	vmovapd	%xmm2, %xmm11
     4ea:      	jmp	0x4ff <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4ff>
     4ec:      	vmovapd	%xmm2, %xmm11
     4f0:      	xorl	%r10d, %r10d
     4f3:      	incq	%rcx
     4f6:      	cmpq	%rcx, %rdx
     4f9:      	je	0x23e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x23e>
     4ff:      	vmovapd	%xmm5, %xmm13
     503:      	vmovapd	%xmm6, %xmm12
     507:      	vmovsd	(%r8,%rcx,8), %xmm5
     50d:      	vmovsd	(%r9,%rcx,8), %xmm6
     513:      	cmpq	$0x1, %r10
     517:      	jne	0x570 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x570>
     519:      	vucomisd	%xmm5, %xmm9
     51d:      	jae	0x5c7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5c7>
     523:      	vmovsd	%xmm9, (%rax,%rcx,8)
     528:      	vucomisd	%xmm7, %xmm6
     52c:      	jbe	0x548 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x548>
     52e:      	vaddsd	0x10(%rsp), %xmm10, %xmm10
     534:      	vucomisd	%xmm15, %xmm10
     539:      	vmovapd	%xmm6, %xmm7
     53d:      	jbe	0x548 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x548>
     53f:      	vmovapd	%xmm6, %xmm7
     543:      	vmovapd	%xmm15, %xmm10
     548:      	vsubsd	%xmm9, %xmm7, %xmm12
     54d:      	vfmadd213sd	%xmm9, %xmm10, %xmm12 # xmm12 = (xmm10 * xmm12) + xmm9
     552:      	vminsd	%xmm12, %xmm13, %xmm9
     557:      	movl	$0x1, %r10d
     55d:      	vucomisd	%xmm5, %xmm9
     561:      	jbe	0x4f3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f3>
     563:      	vmovapd	%xmm5, %xmm9
     567:      	jmp	0x4f3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f3>
     569:      	nopl	(%rax)
     570:      	vucomisd	%xmm9, %xmm6
     575:      	jae	0x60b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x60b>
     57b:      	vxorpd	%xmm1, %xmm9, %xmm13
     57f:      	vmovlpd	%xmm13, (%rax,%rcx,8)
     584:      	vucomisd	%xmm5, %xmm7
     588:      	jbe	0x5a4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5a4>
     58a:      	vaddsd	0x8(%rsp), %xmm11, %xmm11
     590:      	vucomisd	%xmm14, %xmm11
     595:      	vmovapd	%xmm5, %xmm7
     599:      	jbe	0x5a4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5a4>
     59b:      	vmovapd	%xmm5, %xmm7
     59f:      	vmovapd	%xmm14, %xmm11
     5a4:      	vsubsd	%xmm9, %xmm7, %xmm13
     5a9:      	vfmadd213sd	%xmm9, %xmm11, %xmm13 # xmm13 = (xmm11 * xmm13) + xmm9
     5ae:      	vmaxsd	%xmm13, %xmm12, %xmm9
     5b3:      	vucomisd	%xmm9, %xmm6
     5b8:      	jbe	0x4f0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f0>
     5be:      	vmovapd	%xmm6, %xmm9
     5c2:      	jmp	0x4f0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f0>
     5c7:      	vmaxsd	%xmm7, %xmm12, %xmm4
     5cb:      	vmaxsd	%xmm4, %xmm6, %xmm4
     5cf:      	vmulsd	%xmm4, %xmm3, %xmm7
     5d3:      	vaddsd	%xmm7, %xmm4, %xmm7
     5d7:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     5dd:      	vxorpd	%xmm1, %xmm4, %xmm7
     5e1:      	vmovlpd	%xmm7, (%rax,%rcx,8)
     5e6:      	vsubsd	%xmm4, %xmm5, %xmm7
     5ea:      	vfmadd213sd	%xmm4, %xmm2, %xmm7 # xmm7 = (xmm2 * xmm7) + xmm4
     5ef:      	vmaxsd	%xmm7, %xmm12, %xmm9
     5f3:      	vmovapd	%xmm5, %xmm7
     5f7:      	vucomisd	%xmm9, %xmm6
     5fc:      	jbe	0x4ec <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4ec>
     602:      	vmovapd	%xmm6, %xmm9
     606:      	jmp	0x4ec <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4ec>
     60b:      	vminsd	%xmm7, %xmm13, %xmm4
     60f:      	vminsd	%xmm4, %xmm5, %xmm4
     613:      	vmulsd	%xmm4, %xmm3, %xmm7
     617:      	vsubsd	%xmm7, %xmm4, %xmm7
     61b:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     621:      	vmovlpd	%xmm4, (%rax,%rcx,8)
     626:      	vsubsd	%xmm4, %xmm6, %xmm7
     62a:      	vfmadd213sd	%xmm4, %xmm0, %xmm7 # xmm7 = (xmm0 * xmm7) + xmm4
     62f:      	vminsd	%xmm7, %xmm13, %xmm9
     633:      	movl	$0x1, %r10d
     639:      	vmovapd	%xmm6, %xmm7
     63d:      	vucomisd	%xmm5, %xmm9
     641:      	jbe	0x647 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x647>
     643:      	vmovapd	%xmm5, %xmm9
     647:      	vmovapd	%xmm0, %xmm10
     64b:      	jmp	0x4f3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f3>
     650:      	xorl	%edi, %edi
     652:      	vxorpd	%xmm8, %xmm8, %xmm8
     657:      	vmovapd	%xmm10, %xmm3
     65b:      	vcmpneqsd	%xmm8, %xmm10, %xmm8
     661:      	vmovddup	(%rip), %xmm1           # xmm1 = mem[0,0]
                                                # 0x669 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x669>
		0000000000000665:  R_X86_64_PC32	.LCPI1_6-0x4
     669:      	vmovapd	%xmm0, %xmm10
     66d:      	vmovapd	%xmm2, %xmm11
     671:      	jmp	0x686 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x686>
     673:      	vmovapd	%xmm2, %xmm11
     677:      	xorl	%r10d, %r10d
     67a:      	incq	%rdi
     67d:      	cmpq	%rdi, %rdx
     680:      	je	0x23e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x23e>
     686:      	vmovapd	%xmm5, %xmm13
     68a:      	vmovapd	%xmm6, %xmm12
     68e:      	vmovsd	(%r8,%rdi,8), %xmm5
     694:      	vmovsd	(%r9,%rdi,8), %xmm6
     69a:      	cmpq	$0x1, %r10
     69e:      	jne	0x700 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x700>
     6a0:      	vucomisd	%xmm5, %xmm9
     6a4:      	jae	0x760 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x760>
     6aa:      	cmpq	%r11, %rdi
     6ad:      	jae	0x897 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x897>
     6b3:      	vmovsd	%xmm9, (%rax,%rdi,8)
     6b8:      	vucomisd	%xmm7, %xmm6
     6bc:      	jbe	0x6d8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6d8>
     6be:      	vaddsd	0x10(%rsp), %xmm10, %xmm10
     6c4:      	vucomisd	%xmm15, %xmm10
     6c9:      	vmovapd	%xmm6, %xmm7
     6cd:      	jbe	0x6d8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6d8>
     6cf:      	vmovapd	%xmm6, %xmm7
     6d3:      	vmovapd	%xmm15, %xmm10
     6d8:      	vsubsd	%xmm9, %xmm7, %xmm12
     6dd:      	vfmadd213sd	%xmm9, %xmm10, %xmm12 # xmm12 = (xmm10 * xmm12) + xmm9
     6e2:      	vminsd	%xmm12, %xmm13, %xmm9
     6e7:      	movl	$0x1, %r10d
     6ed:      	vucomisd	%xmm5, %xmm9
     6f1:      	jbe	0x67a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x67a>
     6f3:      	vmovapd	%xmm5, %xmm9
     6f7:      	jmp	0x67a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x67a>
     6f9:      	nopl	(%rax)
     700:      	vucomisd	%xmm9, %xmm6
     705:      	jae	0x7ad <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x7ad>
     70b:      	cmpq	%r11, %rdi
     70e:      	jae	0x877 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x877>
     714:      	vxorpd	%xmm1, %xmm9, %xmm13
     718:      	vmovlpd	%xmm13, (%rax,%rdi,8)
     71d:      	vucomisd	%xmm5, %xmm7
     721:      	jbe	0x73d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x73d>
     723:      	vaddsd	0x8(%rsp), %xmm11, %xmm11
     729:      	vucomisd	%xmm14, %xmm11
     72e:      	vmovapd	%xmm5, %xmm7
     732:      	jbe	0x73d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x73d>
     734:      	vmovapd	%xmm5, %xmm7
     738:      	vmovapd	%xmm14, %xmm11
     73d:      	vsubsd	%xmm9, %xmm7, %xmm13
     742:      	vfmadd213sd	%xmm9, %xmm11, %xmm13 # xmm13 = (xmm11 * xmm13) + xmm9
     747:      	vmaxsd	%xmm13, %xmm12, %xmm9
     74c:      	vucomisd	%xmm9, %xmm6
     751:      	jbe	0x677 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x677>
     757:      	vmovapd	%xmm6, %xmm9
     75b:      	jmp	0x677 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x677>
     760:      	cmpq	%r11, %rdi
     763:      	jae	0x887 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x887>
     769:      	vmaxsd	%xmm7, %xmm12, %xmm4
     76d:      	vmaxsd	%xmm4, %xmm6, %xmm4
     771:      	vmulsd	%xmm4, %xmm3, %xmm7
     775:      	vaddsd	%xmm7, %xmm4, %xmm7
     779:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     77f:      	vxorpd	%xmm1, %xmm4, %xmm7
     783:      	vmovlpd	%xmm7, (%rax,%rdi,8)
     788:      	vsubsd	%xmm4, %xmm5, %xmm7
     78c:      	vfmadd213sd	%xmm4, %xmm2, %xmm7 # xmm7 = (xmm2 * xmm7) + xmm4
     791:      	vmaxsd	%xmm7, %xmm12, %xmm9
     795:      	vmovapd	%xmm5, %xmm7
     799:      	vucomisd	%xmm9, %xmm6
     79e:      	jbe	0x673 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x673>
     7a4:      	vmovapd	%xmm6, %xmm9
     7a8:      	jmp	0x673 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x673>
     7ad:      	cmpq	%r11, %rdi
     7b0:      	jae	0x867 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x867>
     7b6:      	vminsd	%xmm7, %xmm13, %xmm4
     7ba:      	vminsd	%xmm4, %xmm5, %xmm4
     7be:      	vmulsd	%xmm4, %xmm3, %xmm7
     7c2:      	vsubsd	%xmm7, %xmm4, %xmm7
     7c6:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     7cc:      	vmovlpd	%xmm4, (%rax,%rdi,8)
     7d1:      	vsubsd	%xmm4, %xmm6, %xmm7
     7d5:      	vfmadd213sd	%xmm4, %xmm0, %xmm7 # xmm7 = (xmm0 * xmm7) + xmm4
     7da:      	vminsd	%xmm7, %xmm13, %xmm9
     7de:      	movl	$0x1, %r10d
     7e4:      	vmovapd	%xmm6, %xmm7
     7e8:      	vucomisd	%xmm5, %xmm9
     7ec:      	jbe	0x7f2 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x7f2>
     7ee:      	vmovapd	%xmm5, %xmm9
     7f2:      	vmovapd	%xmm0, %xmm10
     7f6:      	jmp	0x67a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x67a>
     7fb:      	leaq	(%rip), %rdi            # 0x802 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x802>
		00000000000007fe:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     802:      	leaq	(%rip), %rdx            # 0x809 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x809>
		0000000000000805:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3609-0x4
     809:      	movl	$0x40, %esi
     80e:      	callq	*(%rip)                 # 0x814 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x814>
		0000000000000810:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     814:      	leaq	(%rip), %rdi            # 0x81b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x81b>
		0000000000000817:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     81b:      	leaq	(%rip), %rdx            # 0x822 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x822>
		000000000000081e:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3610-0x4
     822:      	movl	$0x3f, %esi
     827:      	callq	*(%rip)                 # 0x82d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x82d>
		0000000000000829:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     82d:      	leaq	(%rip), %rcx            # 0x834 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x834>
		0000000000000830:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3612-0x4
     834:      	xorl	%edi, %edi
     836:      	movq	%rdx, %rsi
     839:      	movq	%r8, %rdx
     83c:      	callq	*(%rip)                 # 0x842 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x842>
		000000000000083e:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     842:      	leaq	(%rip), %rcx            # 0x849 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x849>
		0000000000000845:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3613-0x4
     849:      	xorl	%edi, %edi
     84b:      	movq	%rdx, %rsi
     84e:      	movq	%rax, %rdx
     851:      	callq	*(%rip)                 # 0x857 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x857>
		0000000000000853:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     857:      	movl	%ebx, %ebp
     859:      	testb	%bpl, %bpl
     85c:      	jne	0x218 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x218>
     862:      	jmp	0x32b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x32b>
     867:      	leaq	(%rip), %rdx            # 0x86e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x86e>
		000000000000086a:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3617-0x4
     86e:      	movq	%r11, %rsi
     871:      	callq	*(%rip)                 # 0x877 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x877>
		0000000000000873:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     877:      	leaq	(%rip), %rdx            # 0x87e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x87e>
		000000000000087a:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3616-0x4
     87e:      	movq	%r11, %rsi
     881:      	callq	*(%rip)                 # 0x887 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x887>
		0000000000000883:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     887:      	leaq	(%rip), %rdx            # 0x88e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x88e>
		000000000000088a:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3615-0x4
     88e:      	movq	%r11, %rsi
     891:      	callq	*(%rip)                 # 0x897 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x897>
		0000000000000893:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     897:      	leaq	(%rip), %rdx            # 0x89e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x89e>
		000000000000089a:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3614-0x4
     89e:      	movq	%r11, %rsi
     8a1:      	callq	*(%rip)                 # 0x8a7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x8a7>
		00000000000008a3:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
