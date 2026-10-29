
/tmp/polars-recovery/sarext-window-evidence/baseline-static-1.97.0/static-probe.ta_lib-51fa72f709535b83.ta_lib.b5d8fdef4152009c-cgu.0.rcgu.o.rcgu.o:	file format elf64-x86-64

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
      33:      	vxorpd	%xmm15, %xmm15, %xmm15
      38:      	jne	0x3c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x3c>
      3a:      	jnp	0x5b <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5b>
      3c:      	vandpd	(%rip), %xmm0, %xmm9    # 0x44 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x44>
		0000000000000040:  R_X86_64_PC32	.LCPI1_1-0x4
      44:      	movw	$0x2, %ax
      48:      	vmovsd	(%rip), %xmm8           # 0x50 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x50>
		000000000000004c:  R_X86_64_PC32	.LCPI1_2-0x4
      50:      	vucomisd	%xmm9, %xmm8
      55:      	vmovapd	%xmm0, %xmm15
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
      97:      	vmovapd	%xmm8, %xmm9
      9c:      	jne	0xa0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xa0>
      9e:      	jnp	0xc8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xc8>
      a0:      	vxorpd	%xmm0, %xmm0, %xmm0
      a4:      	vucomisd	%xmm0, %xmm2
      a8:      	movw	$0x2, %ax
      ac:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
      b2:      	vmovsd	(%rip), %xmm0           # 0xba <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0xba>
		00000000000000b6:  R_X86_64_PC32	.LCPI1_2-0x4
      ba:      	vucomisd	%xmm2, %xmm0
      be:      	vmovapd	%xmm2, %xmm9
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
     146:      	vmovapd	%xmm3, %xmm11
     14a:      	jne	0x14e <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x14e>
     14c:      	jnp	0x176 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x176>
     14e:      	vxorpd	%xmm0, %xmm0, %xmm0
     152:      	vucomisd	%xmm0, %xmm5
     156:      	movw	$0x2, %ax
     15a:      	jb	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     160:      	vmovsd	(%rip), %xmm0           # 0x168 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x168>
		0000000000000164:  R_X86_64_PC32	.LCPI1_2-0x4
     168:      	vucomisd	%xmm5, %xmm0
     16c:      	vmovapd	%xmm5, %xmm11
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
     1e4:      	movq	0xb0(%rsp), %rbx
     1ec:      	vandpd	(%rip), %xmm15, %xmm0   # 0x1f4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x1f4>
		00000000000001f0:  R_X86_64_PC32	.LCPI1_1-0x4
     1f4:      	movq	0x90(%rsp), %rax
     1fc:      	vmovsd	(%rip), %xmm1           # 0x204 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x204>
		0000000000000200:  R_X86_64_PC32	.LCPI1_2-0x4
     204:      	vucomisd	%xmm0, %xmm1
     208:      	jae	0x255 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x255>
     20a:      	cmpq	%r8, %rdx
     20d:      	setb	%r10b
     211:      	cmpq	%rax, %rdx
     214:      	setb	%r11b
     218:      	cmpq	$0x1, %rsi
     21c:      	adcq	$0x0, %rsi
     220:      	movq	0x98(%rsp), %r14
     228:      	movq	$0x0, 0x40(%rsp)
     231:      	cmpq	%rdx, %rsi
     234:      	jbe	0x345 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x345>
     23a:      	movq	$0x0, (%r14)
     241:      	xorl	%edx, %edx
     243:      	movq	0xa0(%rsp), %rax
     24b:      	movq	%rdx, (%rax)
     24e:      	xorl	%eax, %eax
     250:      	jmp	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     255:      	vxorpd	%xmm2, %xmm2, %xmm2
     259:      	vucomisd	%xmm2, %xmm10
     25d:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     25f:      	vucomisd	%xmm10, %xmm1
     264:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     266:      	vucomisd	%xmm2, %xmm9
     26a:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     26c:      	vucomisd	%xmm9, %xmm1
     271:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     273:      	vucomisd	%xmm2, %xmm8
     277:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     279:      	vucomisd	%xmm8, %xmm1
     27e:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     280:      	vucomisd	%xmm2, %xmm4
     284:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     286:      	vucomisd	%xmm4, %xmm1
     28a:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     290:      	vucomisd	%xmm2, %xmm11
     294:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     29a:      	vucomisd	%xmm11, %xmm1
     29f:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     2a5:      	vucomisd	%xmm2, %xmm3
     2a9:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     2af:      	vucomisd	%xmm3, %xmm1
     2b3:      	jb	0x20a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x20a>
     2b9:      	cmpq	$0x1, %rsi
     2bd:      	adcq	$0x0, %rsi
     2c1:      	vucomisd	%xmm7, %xmm1
     2c5:      	movq	$-0x1, %r10
     2cc:      	movq	%rsi, %r14
     2cf:      	cmovbq	%r10, %r14
     2d3:      	vxorpd	%xmm1, %xmm1, %xmm1
     2d7:      	vucomisd	%xmm1, %xmm7
     2db:      	cmovbq	%r10, %r14
     2df:      	cmpq	%rdx, %r14
     2e2:      	seta	%r11b
     2e6:      	cmpq	%r8, %rdx
     2e9:      	setb	%r10b
     2ed:      	orb	%r10b, %r11b
     2f0:      	je	0x681 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x681>
     2f6:      	movq	%rdx, %r15
     2f9:      	subq	%r14, %r15
     2fc:      	setb	%bpl
     300:      	cmpq	%rax, %rdx
     303:      	setb	%r11b
     307:      	orb	%r11b, %bpl
     30a:      	je	0x69a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x69a>
     310:      	cmpq	%rbx, %r15
     313:      	setb	%bpl
     317:      	movb	$0x1, %r15b
     31a:      	cmpq	%r14, %rdx
     31d:      	jae	0x71d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x71d>
     323:      	testb	%r15b, %r15b
     326:      	jne	0x220 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x220>
     32c:      	leaq	(%rip), %rdi            # 0x333 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x333>
		000000000000032f:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.182-0x4
     333:      	leaq	(%rip), %rdx            # 0x33a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x33a>
		0000000000000336:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3611-0x4
     33a:      	movl	$0x50, %esi
     33f:      	callq	*(%rip)                 # 0x345 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x345>
		0000000000000341:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     345:      	testb	%r10b, %r10b
     348:      	je	0x6b3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6b3>
     34e:      	vmovsd	%xmm4, 0x8(%rsp)
     354:      	vmovsd	%xmm7, 0x10(%rsp)
     35a:      	testb	%r11b, %r11b
     35d:      	je	0x6c8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6c8>
     363:      	incq	%rdx
     366:      	vxorpd	%xmm1, %xmm1, %xmm1
     36a:      	vucomisd	%xmm1, %xmm15
     36e:      	jne	0x40a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x40a>
     374:      	jp	0x40a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x40a>
     37a:      	vmovsd	%xmm11, 0x18(%rsp)
     380:      	vmovsd	%xmm3, 0x20(%rsp)
     386:      	vmovsd	%xmm9, 0x28(%rsp)
     38c:      	vmovsd	%xmm8, 0x30(%rsp)
     392:      	vmovsd	%xmm10, 0x38(%rsp)
     398:      	movl	0xf4(%rdi), %edi
     39e:      	leaq	0x40(%rsp), %rax
     3a3:      	leaq	0x50(%rsp), %r10
     3a8:      	leaq	0x48(%rsp), %r11
     3ad:      	movq	%rdx, %r8
     3b0:      	movq	%rsi, %rbp
     3b3:      	movq	%rsi, %rdx
     3b6:      	movq	%rcx, %r15
     3b9:      	movq	%r9, %r12
     3bc:      	pushq	$0x1
     3be:      	pushq	%rax
     3bf:      	pushq	%r10
     3c1:      	pushq	%r11
     3c3:      	pushq	$0x1
     3c5:      	movq	%r8, %r13
     3c8:      	pushq	%r8
     3ca:      	callq	0x3cf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x3cf>
		00000000000003cb:  R_X86_64_PLT32	.text._RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func8minus_dmNtNtB4_5types4Core13minus_dm_impl-0x4
     3cf:      	addq	$0x30, %rsp
     3d3:      	testw	%ax, %ax
     3d6:      	jne	0x17 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x17>
     3dc:      	vmovsd	0x40(%rsp), %xmm0
     3e2:      	vxorpd	%xmm1, %xmm1, %xmm1
     3e6:      	vucomisd	%xmm1, %xmm0
     3ea:      	movq	%rbp, %rsi
     3ed:      	movq	%rbp, (%r14)
     3f0:      	ja	0x42f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x42f>
     3f2:      	movq	%r12, %r9
     3f5:      	vmovsd	-0x8(%r12,%rsi,8), %xmm15
     3fc:      	movl	$0x1, %r10d
     402:      	movq	%r15, %rcx
     405:      	movq	%r15, %rdi
     408:      	jmp	0x442 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x442>
     40a:      	seta	%al
     40d:      	movq	%rsi, (%r14)
     410:      	movq	%r9, %rdi
     413:      	cmovaq	%rcx, %rdi
     417:      	movzbl	%al, %r10d
     41b:      	ja	0x421 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x421>
     41d:      	vmovapd	%xmm0, %xmm15
     421:      	vmovsd	0x10(%rsp), %xmm14
     427:      	vmovsd	0x8(%rsp), %xmm1
     42d:      	jmp	0x46f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x46f>
     42f:      	movq	%r15, %rcx
     432:      	vmovsd	-0x8(%r15,%rsi,8), %xmm15
     439:      	xorl	%r10d, %r10d
     43c:      	movq	%r12, %r9
     43f:      	movq	%r12, %rdi
     442:      	movq	%r13, %rdx
     445:      	vmovsd	0x10(%rsp), %xmm14
     44b:      	vmovsd	0x8(%rsp), %xmm1
     451:      	vmovsd	0x38(%rsp), %xmm10
     457:      	vmovsd	0x30(%rsp), %xmm8
     45d:      	vmovsd	0x28(%rsp), %xmm9
     463:      	vmovsd	0x20(%rsp), %xmm3
     469:      	vmovsd	0x18(%rsp), %xmm11
     46f:      	movq	0xa8(%rsp), %rax
     477:      	vminsd	%xmm9, %xmm1, %xmm0
     47c:      	vminsd	%xmm8, %xmm1, %xmm2
     481:      	vmovsd	%xmm2, 0x10(%rsp)
     487:      	vminsd	%xmm11, %xmm14, %xmm2
     48c:      	vminsd	%xmm3, %xmm14, %xmm3
     490:      	vmovsd	%xmm3, 0x8(%rsp)
     496:      	leaq	(%rcx,%rsi,8), %r8
     49a:      	vmovsd	(%rcx,%rsi,8), %xmm6
     49f:      	leaq	(%r9,%rsi,8), %rcx
     4a3:      	vmovsd	(%r9,%rsi,8), %xmm5
     4a9:      	vmovsd	(%rdi,%rsi,8), %xmm11
     4ae:      	subq	%rsi, %rdx
     4b1:      	xorl	%edi, %edi
     4b3:      	vxorpd	%xmm7, %xmm7, %xmm7
     4b7:      	vmovapd	%xmm10, %xmm3
     4bb:      	vcmpneqsd	%xmm7, %xmm10, %xmm7
     4c0:      	vmovddup	(%rip), %xmm8           # xmm8 = mem[0,0]
                                                # 0x4c8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4c8>
		00000000000004c4:  R_X86_64_PC32	.LCPI1_6-0x4
     4c8:      	vmovapd	%xmm0, %xmm9
     4cc:      	vmovapd	%xmm2, %xmm10
     4d0:      	jmp	0x4f3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4f3>
     4d2:      	nopw	%cs:(%rax,%rax)
     4e0:      	vmovapd	%xmm2, %xmm10
     4e4:      	xorl	%r10d, %r10d
     4e7:      	incq	%rdi
     4ea:      	cmpq	%rdi, %rdx
     4ed:      	je	0x243 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x243>
     4f3:      	vmovapd	%xmm6, %xmm12
     4f7:      	vmovapd	%xmm5, %xmm13
     4fb:      	vmovsd	(%rcx,%rdi,8), %xmm5
     500:      	vmovsd	(%r8,%rdi,8), %xmm6
     506:      	cmpq	$0x1, %r10
     50a:      	jne	0x570 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x570>
     50c:      	vucomisd	%xmm5, %xmm15
     510:      	jae	0x5e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5e0>
     516:      	cmpq	%rbx, %rdi
     519:      	jae	0x70d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x70d>
     51f:      	vmovsd	%xmm15, (%rax,%rdi,8)
     524:      	vucomisd	%xmm11, %xmm6
     529:      	jbe	0x543 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x543>
     52b:      	vaddsd	0x10(%rsp), %xmm9, %xmm9
     531:      	vucomisd	%xmm1, %xmm9
     535:      	vmovapd	%xmm6, %xmm11
     539:      	jbe	0x543 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x543>
     53b:      	vmovapd	%xmm6, %xmm11
     53f:      	vmovapd	%xmm1, %xmm9
     543:      	vsubsd	%xmm15, %xmm11, %xmm12
     548:      	vfmadd213sd	%xmm15, %xmm9, %xmm12 # xmm12 = (xmm9 * xmm12) + xmm15
     54d:      	vminsd	%xmm12, %xmm13, %xmm15
     552:      	movl	$0x1, %r10d
     558:      	vucomisd	%xmm5, %xmm15
     55c:      	jbe	0x4e7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e7>
     55e:      	vmovapd	%xmm5, %xmm15
     562:      	jmp	0x4e7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e7>
     564:      	nopw	%cs:(%rax,%rax)
     570:      	vucomisd	%xmm15, %xmm6
     575:      	jae	0x630 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x630>
     57b:      	cmpq	%rbx, %rdi
     57e:      	jae	0x6ed <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6ed>
     584:      	vxorpd	%xmm8, %xmm15, %xmm13
     589:      	vmovlpd	%xmm13, (%rax,%rdi,8)
     58e:      	vucomisd	%xmm5, %xmm11
     592:      	jbe	0x5ae <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5ae>
     594:      	vaddsd	0x8(%rsp), %xmm10, %xmm10
     59a:      	vucomisd	%xmm14, %xmm10
     59f:      	vmovapd	%xmm5, %xmm11
     5a3:      	jbe	0x5ae <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x5ae>
     5a5:      	vmovapd	%xmm5, %xmm11
     5a9:      	vmovapd	%xmm14, %xmm10
     5ae:      	vsubsd	%xmm15, %xmm11, %xmm13
     5b3:      	vfmadd213sd	%xmm15, %xmm10, %xmm13 # xmm13 = (xmm10 * xmm13) + xmm15
     5b8:      	vmaxsd	%xmm13, %xmm12, %xmm15
     5bd:      	vucomisd	%xmm15, %xmm6
     5c2:      	jbe	0x4e4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e4>
     5c8:      	vmovapd	%xmm6, %xmm15
     5cc:      	jmp	0x4e4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e4>
     5d1:      	nopw	%cs:(%rax,%rax)
     5e0:      	cmpq	%rbx, %rdi
     5e3:      	jae	0x6fd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6fd>
     5e9:      	vmaxsd	%xmm11, %xmm12, %xmm4
     5ee:      	vmaxsd	%xmm4, %xmm6, %xmm4
     5f2:      	vmulsd	%xmm4, %xmm3, %xmm10
     5f6:      	vaddsd	%xmm4, %xmm10, %xmm10
     5fa:      	vblendvpd	%xmm7, %xmm10, %xmm4, %xmm4
     600:      	vxorpd	%xmm4, %xmm8, %xmm10
     604:      	vmovlpd	%xmm10, (%rax,%rdi,8)
     609:      	vsubsd	%xmm4, %xmm5, %xmm10
     60d:      	vfmadd213sd	%xmm4, %xmm2, %xmm10 # xmm10 = (xmm2 * xmm10) + xmm4
     612:      	vmaxsd	%xmm10, %xmm12, %xmm15
     617:      	vmovapd	%xmm5, %xmm11
     61b:      	vucomisd	%xmm15, %xmm6
     620:      	jbe	0x4e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e0>
     626:      	vmovapd	%xmm6, %xmm15
     62a:      	jmp	0x4e0 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e0>
     62f:      	nop
     630:      	cmpq	%rbx, %rdi
     633:      	jae	0x6dd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6dd>
     639:      	vminsd	%xmm11, %xmm13, %xmm4
     63e:      	vminsd	%xmm4, %xmm5, %xmm4
     642:      	vmulsd	%xmm4, %xmm3, %xmm9
     646:      	vsubsd	%xmm9, %xmm4, %xmm9
     64b:      	vblendvpd	%xmm7, %xmm9, %xmm4, %xmm4
     651:      	vmovlpd	%xmm4, (%rax,%rdi,8)
     656:      	vsubsd	%xmm4, %xmm6, %xmm9
     65a:      	vfmadd213sd	%xmm4, %xmm0, %xmm9 # xmm9 = (xmm0 * xmm9) + xmm4
     65f:      	vminsd	%xmm9, %xmm13, %xmm15
     664:      	movl	$0x1, %r10d
     66a:      	vmovapd	%xmm6, %xmm11
     66e:      	vucomisd	%xmm5, %xmm15
     672:      	jbe	0x678 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x678>
     674:      	vmovapd	%xmm5, %xmm15
     678:      	vmovapd	%xmm0, %xmm9
     67c:      	jmp	0x4e7 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x4e7>
     681:      	leaq	(%rip), %rdi            # 0x688 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x688>
		0000000000000684:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.4-0x4
     688:      	leaq	(%rip), %rdx            # 0x68f <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x68f>
		000000000000068b:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3609-0x4
     68f:      	movl	$0x40, %esi
     694:      	callq	*(%rip)                 # 0x69a <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x69a>
		0000000000000696:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     69a:      	leaq	(%rip), %rdi            # 0x6a1 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6a1>
		000000000000069d:  R_X86_64_PC32	.rodata..Lanon.03e2c2757cbcb256945785c681f0d6de.6-0x4
     6a1:      	leaq	(%rip), %rdx            # 0x6a8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6a8>
		00000000000006a4:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3610-0x4
     6a8:      	movl	$0x3f, %esi
     6ad:      	callq	*(%rip)                 # 0x6b3 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6b3>
		00000000000006af:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking5panic-0x4
     6b3:      	leaq	(%rip), %rcx            # 0x6ba <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6ba>
		00000000000006b6:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3612-0x4
     6ba:      	xorl	%edi, %edi
     6bc:      	movq	%rdx, %rsi
     6bf:      	movq	%r8, %rdx
     6c2:      	callq	*(%rip)                 # 0x6c8 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6c8>
		00000000000006c4:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     6c8:      	leaq	(%rip), %rcx            # 0x6cf <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6cf>
		00000000000006cb:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3613-0x4
     6cf:      	xorl	%edi, %edi
     6d1:      	movq	%rdx, %rsi
     6d4:      	movq	%rax, %rdx
     6d7:      	callq	*(%rip)                 # 0x6dd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6dd>
		00000000000006d9:  R_X86_64_GOTPCREL	_RNvNtNtCscI6d9CVNmLh_4core5slice5index16slice_index_fail-0x4
     6dd:      	leaq	(%rip), %rdx            # 0x6e4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6e4>
		00000000000006e0:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3617-0x4
     6e4:      	movq	%rbx, %rsi
     6e7:      	callq	*(%rip)                 # 0x6ed <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6ed>
		00000000000006e9:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     6ed:      	leaq	(%rip), %rdx            # 0x6f4 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6f4>
		00000000000006f0:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3616-0x4
     6f4:      	movq	%rbx, %rsi
     6f7:      	callq	*(%rip)                 # 0x6fd <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x6fd>
		00000000000006f9:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     6fd:      	leaq	(%rip), %rdx            # 0x704 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x704>
		0000000000000700:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3615-0x4
     704:      	movq	%rbx, %rsi
     707:      	callq	*(%rip)                 # 0x70d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x70d>
		0000000000000709:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     70d:      	leaq	(%rip), %rdx            # 0x714 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x714>
		0000000000000710:  R_X86_64_PC32	.data.rel.ro..Lanon.03e2c2757cbcb256945785c681f0d6de.3614-0x4
     714:      	movq	%rbx, %rsi
     717:      	callq	*(%rip)                 # 0x71d <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x71d>
		0000000000000719:  R_X86_64_GOTPCREL	_RNvNtCscI6d9CVNmLh_4core9panicking18panic_bounds_check-0x4
     71d:      	movl	%ebp, %r15d
     720:      	testb	%r15b, %r15b
     723:      	jne	0x220 <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x220>
     729:      	jmp	0x32c <_RNvMNtNtCsfBYb8xZ4HAC_6ta_lib7ta_func6sarextNtNtB4_5types4Core15sarext_impl_fma+0x32c>
