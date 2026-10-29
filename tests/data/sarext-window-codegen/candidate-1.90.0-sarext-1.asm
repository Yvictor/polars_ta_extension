
/tmp/polars-recovery/sarext-window-evidence/candidate-static-1.90.0/library-objects/ta_lib-a99de56cdf066125.ta_lib.4f1d99721d8d97c2-cgu.00.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E:

0000000000000000 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0x68, %rsp
       e:      	movw	$0xd, %ax
      12:      	cmpq	%rsi, %rdx
      15:      	jae	0x26 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x26>
      17:      	addq	$0x68, %rsp
      1b:      	popq	%rbx
      1c:      	popq	%r12
      1e:      	popq	%r13
      20:      	popq	%r14
      22:      	popq	%r15
      24:      	popq	%rbp
      25:      	retq
      26:      	vmovapd	%xmm7, %xmm14
      2a:      	vmovapd	%xmm4, %xmm15
      2e:      	vxorpd	%xmm9, %xmm9, %xmm9
      33:      	vucomisd	(%rip), %xmm0           # 0x3b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3b>
		0000000000000037:  R_X86_64_PC32	.LCPI1216_0-0x4
      3b:      	vxorpd	%xmm4, %xmm4, %xmm4
      3f:      	jne	0x43 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x43>
      41:      	jnp	0x61 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x61>
      43:      	vandpd	(%rip), %xmm0, %xmm4    # 0x4b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x4b>
		0000000000000047:  R_X86_64_PC32	.LCPI1216_1-0x4
      4b:      	movw	$0x2, %ax
      4f:      	vmovsd	(%rip), %xmm7           # 0x57 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x57>
		0000000000000053:  R_X86_64_PC32	.LCPI1216_2-0x4
      57:      	vucomisd	%xmm4, %xmm7
      5b:      	vmovapd	%xmm0, %xmm4
      5f:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      61:      	vucomisd	(%rip), %xmm1           # 0x69 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x69>
		0000000000000065:  R_X86_64_PC32	.LCPI1216_0-0x4
      69:      	jne	0x6d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x6d>
      6b:      	jnp	0x8d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8d>
      6d:      	vxorpd	%xmm0, %xmm0, %xmm0
      71:      	vucomisd	%xmm0, %xmm1
      75:      	movw	$0x2, %ax
      79:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      7b:      	vmovsd	(%rip), %xmm0           # 0x83 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x83>
		000000000000007f:  R_X86_64_PC32	.LCPI1216_2-0x4
      83:      	vucomisd	%xmm1, %xmm0
      87:      	vmovapd	%xmm1, %xmm9
      8b:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      8d:      	vmovsd	(%rip), %xmm7           # 0x95 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x95>
		0000000000000091:  R_X86_64_PC32	.LCPI1216_3-0x4
      95:      	vucomisd	(%rip), %xmm2           # 0x9d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9d>
		0000000000000099:  R_X86_64_PC32	.LCPI1216_0-0x4
      9d:      	vmovapd	%xmm7, %xmm8
      a1:      	jne	0xa5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xa5>
      a3:      	jnp	0xcd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xcd>
      a5:      	vxorpd	%xmm0, %xmm0, %xmm0
      a9:      	vucomisd	%xmm0, %xmm2
      ad:      	movw	$0x2, %ax
      b1:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      b7:      	vmovsd	(%rip), %xmm0           # 0xbf <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xbf>
		00000000000000bb:  R_X86_64_PC32	.LCPI1216_2-0x4
      bf:      	vucomisd	%xmm2, %xmm0
      c3:      	vmovapd	%xmm2, %xmm8
      c7:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      cd:      	vucomisd	(%rip), %xmm3           # 0xd5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xd5>
		00000000000000d1:  R_X86_64_PC32	.LCPI1216_0-0x4
      d5:      	jne	0xd9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xd9>
      d7:      	jnp	0x101 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x101>
      d9:      	vxorpd	%xmm0, %xmm0, %xmm0
      dd:      	vucomisd	%xmm0, %xmm3
      e1:      	movw	$0x2, %ax
      e5:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      eb:      	vmovsd	(%rip), %xmm0           # 0xf3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xf3>
		00000000000000ef:  R_X86_64_PC32	.LCPI1216_2-0x4
      f3:      	vucomisd	%xmm3, %xmm0
      f7:      	vmovapd	%xmm3, %xmm7
      fb:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     101:      	vucomisd	(%rip), %xmm15          # 0x109 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x109>
		0000000000000105:  R_X86_64_PC32	.LCPI1216_0-0x4
     109:      	jne	0x117 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x117>
     10b:      	jp	0x117 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x117>
     10d:      	vmovsd	(%rip), %xmm15          # 0x115 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x115>
		0000000000000111:  R_X86_64_PC32	.LCPI1216_4-0x4
     115:      	jmp	0x13c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x13c>
     117:      	vxorpd	%xmm0, %xmm0, %xmm0
     11b:      	vucomisd	%xmm0, %xmm15
     11f:      	movw	$0x2, %ax
     123:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     129:      	vmovsd	(%rip), %xmm0           # 0x131 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x131>
		000000000000012d:  R_X86_64_PC32	.LCPI1216_2-0x4
     131:      	vucomisd	%xmm15, %xmm0
     136:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     13c:      	vmovsd	(%rip), %xmm3           # 0x144 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x144>
		0000000000000140:  R_X86_64_PC32	.LCPI1216_3-0x4
     144:      	vucomisd	(%rip), %xmm5           # 0x14c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x14c>
		0000000000000148:  R_X86_64_PC32	.LCPI1216_0-0x4
     14c:      	vmovapd	%xmm3, %xmm2
     150:      	jne	0x154 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x154>
     152:      	jnp	0x17c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17c>
     154:      	vxorpd	%xmm0, %xmm0, %xmm0
     158:      	vucomisd	%xmm0, %xmm5
     15c:      	movw	$0x2, %ax
     160:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     166:      	vmovsd	(%rip), %xmm0           # 0x16e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x16e>
		000000000000016a:  R_X86_64_PC32	.LCPI1216_2-0x4
     16e:      	vucomisd	%xmm5, %xmm0
     172:      	vmovapd	%xmm5, %xmm2
     176:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     17c:      	vucomisd	(%rip), %xmm6           # 0x184 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x184>
		0000000000000180:  R_X86_64_PC32	.LCPI1216_0-0x4
     184:      	jne	0x188 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x188>
     186:      	jnp	0x1b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1b0>
     188:      	vxorpd	%xmm0, %xmm0, %xmm0
     18c:      	vucomisd	%xmm0, %xmm6
     190:      	movw	$0x2, %ax
     194:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     19a:      	vmovsd	(%rip), %xmm0           # 0x1a2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1a2>
		000000000000019e:  R_X86_64_PC32	.LCPI1216_2-0x4
     1a2:      	vucomisd	%xmm6, %xmm0
     1a6:      	vmovapd	%xmm6, %xmm3
     1aa:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1b0:      	vucomisd	(%rip), %xmm14          # 0x1b8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1b8>
		00000000000001b4:  R_X86_64_PC32	.LCPI1216_0-0x4
     1b8:      	jne	0x1c6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1c6>
     1ba:      	jp	0x1c6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1c6>
     1bc:      	vmovsd	(%rip), %xmm14          # 0x1c4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1c4>
		00000000000001c0:  R_X86_64_PC32	.LCPI1216_4-0x4
     1c4:      	jmp	0x1eb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1eb>
     1c6:      	vxorpd	%xmm0, %xmm0, %xmm0
     1ca:      	vucomisd	%xmm0, %xmm14
     1ce:      	movw	$0x2, %ax
     1d2:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1d8:      	vmovsd	(%rip), %xmm0           # 0x1e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1e0>
		00000000000001dc:  R_X86_64_PC32	.LCPI1216_2-0x4
     1e0:      	vucomisd	%xmm14, %xmm0
     1e5:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1eb:      	vucomisd	(%rip), %xmm4           # 0x1f3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1f3>
		00000000000001ef:  R_X86_64_PC32	.LCPI1216_0-0x4
     1f3:      	vandpd	(%rip), %xmm4, %xmm0    # 0x1fb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1fb>
		00000000000001f7:  R_X86_64_PC32	.LCPI1216_1-0x4
     1fb:      	movq	$-0x1, %r10
     202:      	jne	0x20a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x20a>
     204:      	jnp	0x2ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2ba>
     20a:      	vmovsd	(%rip), %xmm1           # 0x212 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x212>
		000000000000020e:  R_X86_64_PC32	.LCPI1216_2-0x4
     212:      	vucomisd	%xmm0, %xmm1
     216:      	jae	0x2ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2ba>
     21c:      	cmpq	%r10, %rsi
     21f:      	cmovaq	%rsi, %r10
     223:      	cmpq	%rdx, %r10
     226:      	seta	%al
     229:      	cmpq	%r8, %rdx
     22c:      	setb	%r11b
     230:      	orb	%al, %r11b
     233:      	je	0x8d6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8d6>
     239:      	movq	0xa0(%rsp), %rax
     241:      	cmpq	%r10, %rdx
     244:      	setb	%r11b
     248:      	cmpq	%rax, %rdx
     24b:      	setb	%bl
     24e:      	orb	%r11b, %bl
     251:      	je	0x8ef <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8ef>
     257:      	movq	0xc0(%rsp), %r14
     25f:      	movq	%rdx, %r11
     262:      	subq	%r10, %r11
     265:      	setb	%r10b
     269:      	cmpq	%r14, %r11
     26c:      	setb	%r11b
     270:      	orb	%r10b, %r11b
     273:      	je	0x908 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x908>
     279:      	movq	0xa8(%rsp), %r12
     281:      	movq	$0x0, 0x10(%rsp)
     28a:      	cmpq	$0x1, %rsi
     28e:      	adcq	$0x0, %rsi
     292:      	movq	%rdx, %r15
     295:      	subq	%rsi, %r15
     298:      	jae	0x3fd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3fd>
     29e:      	movq	$0x0, (%r12)
     2a6:      	xorl	%ebx, %ebx
     2a8:      	movq	0xb0(%rsp), %rax
     2b0:      	movq	%rbx, (%rax)
     2b3:      	xorl	%eax, %eax
     2b5:      	jmp	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     2ba:      	vucomisd	(%rip), %xmm9           # 0x2c2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2c2>
		00000000000002be:  R_X86_64_PC32	.LCPI1216_0-0x4
     2c2:      	jne	0x2c6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2c6>
     2c4:      	jnp	0x2e7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2e7>
     2c6:      	vxorpd	%xmm1, %xmm1, %xmm1
     2ca:      	vucomisd	%xmm1, %xmm9
     2ce:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     2d4:      	vmovsd	(%rip), %xmm1           # 0x2dc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2dc>
		00000000000002d8:  R_X86_64_PC32	.LCPI1216_2-0x4
     2dc:      	vucomisd	%xmm9, %xmm1
     2e1:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     2e7:      	vucomisd	(%rip), %xmm8           # 0x2ef <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2ef>
		00000000000002eb:  R_X86_64_PC32	.LCPI1216_0-0x4
     2ef:      	jne	0x2f3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2f3>
     2f1:      	jnp	0x314 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x314>
     2f3:      	vxorpd	%xmm1, %xmm1, %xmm1
     2f7:      	vucomisd	%xmm1, %xmm8
     2fb:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     301:      	vmovsd	(%rip), %xmm1           # 0x309 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x309>
		0000000000000305:  R_X86_64_PC32	.LCPI1216_2-0x4
     309:      	vucomisd	%xmm8, %xmm1
     30e:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     314:      	vucomisd	(%rip), %xmm7           # 0x31c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x31c>
		0000000000000318:  R_X86_64_PC32	.LCPI1216_0-0x4
     31c:      	jne	0x320 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x320>
     31e:      	jnp	0x340 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x340>
     320:      	vxorpd	%xmm1, %xmm1, %xmm1
     324:      	vucomisd	%xmm1, %xmm7
     328:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     32e:      	vmovsd	(%rip), %xmm1           # 0x336 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x336>
		0000000000000332:  R_X86_64_PC32	.LCPI1216_2-0x4
     336:      	vucomisd	%xmm7, %xmm1
     33a:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     340:      	vucomisd	(%rip), %xmm15          # 0x348 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x348>
		0000000000000344:  R_X86_64_PC32	.LCPI1216_0-0x4
     348:      	jne	0x34c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x34c>
     34a:      	jnp	0x36d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x36d>
     34c:      	vxorpd	%xmm1, %xmm1, %xmm1
     350:      	vucomisd	%xmm1, %xmm15
     354:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     35a:      	vmovsd	(%rip), %xmm1           # 0x362 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x362>
		000000000000035e:  R_X86_64_PC32	.LCPI1216_2-0x4
     362:      	vucomisd	%xmm15, %xmm1
     367:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     36d:      	vucomisd	(%rip), %xmm2           # 0x375 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x375>
		0000000000000371:  R_X86_64_PC32	.LCPI1216_0-0x4
     375:      	jne	0x379 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x379>
     377:      	jnp	0x399 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x399>
     379:      	vxorpd	%xmm1, %xmm1, %xmm1
     37d:      	vucomisd	%xmm1, %xmm2
     381:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     387:      	vmovsd	(%rip), %xmm1           # 0x38f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x38f>
		000000000000038b:  R_X86_64_PC32	.LCPI1216_2-0x4
     38f:      	vucomisd	%xmm2, %xmm1
     393:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     399:      	vucomisd	(%rip), %xmm3           # 0x3a1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3a1>
		000000000000039d:  R_X86_64_PC32	.LCPI1216_0-0x4
     3a1:      	jne	0x3a5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3a5>
     3a3:      	jnp	0x3c5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3c5>
     3a5:      	vxorpd	%xmm1, %xmm1, %xmm1
     3a9:      	vucomisd	%xmm1, %xmm3
     3ad:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     3b3:      	vmovsd	(%rip), %xmm1           # 0x3bb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3bb>
		00000000000003b7:  R_X86_64_PC32	.LCPI1216_2-0x4
     3bb:      	vucomisd	%xmm3, %xmm1
     3bf:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     3c5:      	vucomisd	(%rip), %xmm14          # 0x3cd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3cd>
		00000000000003c9:  R_X86_64_PC32	.LCPI1216_0-0x4
     3cd:      	jne	0x3d1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3d1>
     3cf:      	jnp	0x3f2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3f2>
     3d1:      	vxorpd	%xmm1, %xmm1, %xmm1
     3d5:      	vucomisd	%xmm1, %xmm14
     3d9:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     3df:      	vmovsd	(%rip), %xmm1           # 0x3e7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3e7>
		00000000000003e3:  R_X86_64_PC32	.LCPI1216_2-0x4
     3e7:      	vucomisd	%xmm14, %xmm1
     3ec:      	jb	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     3f2:      	movl	$0x1, %r10d
     3f8:      	jmp	0x21c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x21c>
     3fd:      	leaq	0x1(%rdx), %rbx
     401:      	cmpq	%r8, %rdx
     404:      	jae	0x921 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x921>
     40a:      	cmpq	%rax, %rdx
     40d:      	jae	0x934 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x934>
     413:      	vxorpd	%xmm1, %xmm1, %xmm1
     417:      	vucomisd	%xmm1, %xmm4
     41b:      	jne	0x505 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x505>
     421:      	jp	0x505 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x505>
     427:      	vmovsd	%xmm2, 0x18(%rsp)
     42d:      	vmovsd	%xmm3, 0x20(%rsp)
     433:      	vmovsd	%xmm8, 0x28(%rsp)
     439:      	vmovsd	%xmm7, 0x30(%rsp)
     43f:      	vmovsd	%xmm9, 0x38(%rsp)
     445:      	vmovsd	%xmm15, 0x40(%rsp)
     44b:      	vmovsd	%xmm14, 0x48(%rsp)
     451:      	movq	%rdx, 0x8(%rsp)
     456:      	movl	0xf4(%rdi), %edi
     45c:      	leaq	0x10(%rsp), %rax
     461:      	leaq	0x60(%rsp), %r10
     466:      	leaq	0x58(%rsp), %r11
     46b:      	movq	%rsi, %rdx
     46e:      	movq	%rsi, %rbp
     471:      	movq	%rcx, 0x50(%rsp)
     476:      	movq	%rbx, %r8
     479:      	movq	%r9, %r13
     47c:      	pushq	$0x1
     47e:      	pushq	%rax
     47f:      	pushq	%r10
     481:      	pushq	%r11
     483:      	pushq	$0x1
     485:      	pushq	%rbx
     486:      	callq	0x48b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x48b>
		0000000000000487:  R_X86_64_PLT32	_ZN6ta_lib7ta_func8minus_dm46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$13minus_dm_impl17h2888df27879bfa4fE.llvm.7684525917036654579-0x4
     48b:      	addq	$0x30, %rsp
     48f:      	testw	%ax, %ax
     492:      	jne	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     498:      	vmovsd	0x10(%rsp), %xmm0
     49e:      	movq	%rbp, (%r12)
     4a2:      	leaq	-0x1(%rbp), %rdi
     4a6:      	movq	0x8(%rsp), %rdx
     4ab:      	cmpq	%rdx, %rdi
     4ae:      	movq	0x50(%rsp), %rcx
     4b3:      	vmovsd	0x48(%rsp), %xmm14
     4b9:      	vmovsd	0x40(%rsp), %xmm15
     4bf:      	vmovsd	0x38(%rsp), %xmm9
     4c5:      	vmovsd	0x30(%rsp), %xmm7
     4cb:      	vmovsd	0x28(%rsp), %xmm8
     4d1:      	vmovsd	0x20(%rsp), %xmm3
     4d7:      	vmovsd	0x18(%rsp), %xmm2
     4dd:      	ja	0x9d3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9d3>
     4e3:      	movq	%rbp, %rsi
     4e6:      	movq	%r13, %r9
     4e9:      	vxorpd	%xmm1, %xmm1, %xmm1
     4ed:      	vucomisd	%xmm1, %xmm0
     4f1:      	ja	0x530 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x530>
     4f3:      	vmovsd	-0x8(%r9,%rsi,8), %xmm4
     4fa:      	movl	$0x1, %r11d
     500:      	movq	%rcx, %rax
     503:      	jmp	0x53c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x53c>
     505:      	movq	%rsi, (%r12)
     509:      	leaq	-0x1(%rsi), %rdi
     50d:      	cmpq	%rdx, %rdi
     510:      	ja	0x9d3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9d3>
     516:      	xorl	%r11d, %r11d
     519:      	vucomisd	%xmm1, %xmm4
     51d:      	seta	%r11b
     521:      	movq	%r9, %rax
     524:      	cmovaq	%rcx, %rax
     528:      	ja	0x53c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x53c>
     52a:      	vmovapd	%xmm0, %xmm4
     52e:      	jmp	0x53c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x53c>
     530:      	vmovsd	-0x8(%rcx,%rsi,8), %xmm4
     536:      	xorl	%r11d, %r11d
     539:      	movq	%r9, %rax
     53c:      	movq	0xb8(%rsp), %r8
     544:      	vminsd	%xmm8, %xmm15, %xmm0
     549:      	vminsd	%xmm7, %xmm15, %xmm1
     54d:      	vmovsd	%xmm1, 0x8(%rsp)
     553:      	vminsd	%xmm2, %xmm14, %xmm2
     557:      	vminsd	%xmm3, %xmm14, %xmm3
     55b:      	vmovsd	(%rax,%rsi,8), %xmm7
     560:      	leaq	(%r9,%rsi,8), %r10
     564:      	vmovsd	(%r9,%rsi,8), %xmm5
     56a:      	leaq	(%rcx,%rsi,8), %r9
     56e:      	vmovsd	(%rcx,%rsi,8), %xmm6
     573:      	cmpq	%r14, %r15
     576:      	jae	0x724 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x724>
     57c:      	leaq	0x1(%r15), %rax
     580:      	subq	%rsi, %rbx
     583:      	xorl	%edi, %edi
     585:      	vxorpd	%xmm8, %xmm8, %xmm8
     58a:      	vmovapd	%xmm9, %xmm1
     58e:      	vcmpneqsd	%xmm8, %xmm9, %xmm8
     594:      	vmovddup	(%rip), %xmm9           # xmm9 = mem[0,0]
                                                # 0x59c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x59c>
		0000000000000598:  R_X86_64_PC32	.LCPI1216_6-0x4
     59c:      	vmovapd	%xmm0, %xmm10
     5a0:      	vmovapd	%xmm2, %xmm11
     5a4:      	jmp	0x5bd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5bd>
     5a6:      	vmovapd	%xmm5, %xmm7
     5aa:      	vmovapd	%xmm2, %xmm11
     5ae:      	xorl	%r11d, %r11d
     5b1:      	incq	%rdi
     5b4:      	cmpq	%rdi, %rbx
     5b7:      	je	0x2a8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2a8>
     5bd:      	vmovapd	%xmm5, %xmm13
     5c1:      	vmovapd	%xmm6, %xmm12
     5c5:      	vmovsd	(%r10,%rdi,8), %xmm5
     5cb:      	vmovsd	(%r9,%rdi,8), %xmm6
     5d1:      	cmpq	$0x1, %r11
     5d5:      	jne	0x630 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x630>
     5d7:      	vucomisd	%xmm5, %xmm4
     5db:      	jae	0x68c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x68c>
     5e1:      	cmpq	%r15, %rdi
     5e4:      	ja	0x9b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9b0>
     5ea:      	vmovsd	%xmm4, (%r8,%rdi,8)
     5f0:      	vucomisd	%xmm7, %xmm6
     5f4:      	jbe	0x610 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x610>
     5f6:      	vaddsd	0x8(%rsp), %xmm10, %xmm10
     5fc:      	vucomisd	%xmm15, %xmm10
     601:      	vmovapd	%xmm6, %xmm7
     605:      	jbe	0x610 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x610>
     607:      	vmovapd	%xmm6, %xmm7
     60b:      	vmovapd	%xmm15, %xmm10
     610:      	vsubsd	%xmm4, %xmm7, %xmm12
     614:      	vfmadd213sd	%xmm4, %xmm10, %xmm12 # xmm12 = (xmm10 * xmm12) + xmm4
     619:      	vminsd	%xmm12, %xmm13, %xmm4
     61e:      	movl	$0x1, %r11d
     624:      	vucomisd	%xmm5, %xmm4
     628:      	jbe	0x5b1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5b1>
     62a:      	vmovapd	%xmm5, %xmm4
     62e:      	jmp	0x5b1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5b1>
     630:      	vucomisd	%xmm4, %xmm6
     634:      	jae	0x6d5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x6d5>
     63a:      	cmpq	%r15, %rdi
     63d:      	ja	0x96a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x96a>
     643:      	vxorpd	%xmm4, %xmm9, %xmm13
     647:      	vmovlpd	%xmm13, (%r8,%rdi,8)
     64d:      	vucomisd	%xmm5, %xmm7
     651:      	jbe	0x66b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x66b>
     653:      	vaddsd	%xmm3, %xmm11, %xmm11
     657:      	vucomisd	%xmm14, %xmm11
     65c:      	vmovapd	%xmm5, %xmm7
     660:      	jbe	0x66b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x66b>
     662:      	vmovapd	%xmm5, %xmm7
     666:      	vmovapd	%xmm14, %xmm11
     66b:      	vsubsd	%xmm4, %xmm7, %xmm13
     66f:      	vfmadd213sd	%xmm4, %xmm11, %xmm13 # xmm13 = (xmm11 * xmm13) + xmm4
     674:      	vmaxsd	%xmm13, %xmm12, %xmm4
     679:      	vucomisd	%xmm4, %xmm6
     67d:      	jbe	0x5ae <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5ae>
     683:      	vmovapd	%xmm6, %xmm4
     687:      	jmp	0x5ae <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5ae>
     68c:      	cmpq	%r15, %rdi
     68f:      	ja	0x98d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x98d>
     695:      	vmaxsd	%xmm7, %xmm12, %xmm4
     699:      	vmaxsd	%xmm4, %xmm6, %xmm4
     69d:      	vmulsd	%xmm4, %xmm1, %xmm7
     6a1:      	vaddsd	%xmm7, %xmm4, %xmm7
     6a5:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     6ab:      	vxorpd	%xmm4, %xmm9, %xmm7
     6af:      	vmovlpd	%xmm7, (%r8,%rdi,8)
     6b5:      	vsubsd	%xmm4, %xmm5, %xmm7
     6b9:      	vfmadd213sd	%xmm4, %xmm2, %xmm7 # xmm7 = (xmm2 * xmm7) + xmm4
     6be:      	vmaxsd	%xmm7, %xmm12, %xmm4
     6c2:      	vucomisd	%xmm4, %xmm6
     6c6:      	jbe	0x5a6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5a6>
     6cc:      	vmovapd	%xmm6, %xmm4
     6d0:      	jmp	0x5a6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5a6>
     6d5:      	cmpq	%r15, %rdi
     6d8:      	ja	0x947 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x947>
     6de:      	vminsd	%xmm7, %xmm13, %xmm4
     6e2:      	vminsd	%xmm4, %xmm5, %xmm4
     6e6:      	vmulsd	%xmm4, %xmm1, %xmm7
     6ea:      	vsubsd	%xmm7, %xmm4, %xmm7
     6ee:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     6f4:      	vmovlpd	%xmm4, (%r8,%rdi,8)
     6fa:      	vsubsd	%xmm4, %xmm6, %xmm7
     6fe:      	vfmadd213sd	%xmm4, %xmm0, %xmm7 # xmm7 = (xmm0 * xmm7) + xmm4
     703:      	vminsd	%xmm7, %xmm13, %xmm4
     707:      	movl	$0x1, %r11d
     70d:      	vucomisd	%xmm5, %xmm4
     711:      	jbe	0x717 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x717>
     713:      	vmovapd	%xmm5, %xmm4
     717:      	vmovapd	%xmm6, %xmm7
     71b:      	vmovapd	%xmm0, %xmm10
     71f:      	jmp	0x5b1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5b1>
     724:      	decq	%rsi
     727:      	xorl	%ebx, %ebx
     729:      	vxorpd	%xmm8, %xmm8, %xmm8
     72e:      	vmovapd	%xmm9, %xmm1
     732:      	vcmpneqsd	%xmm8, %xmm9, %xmm8
     738:      	vmovddup	(%rip), %xmm9           # xmm9 = mem[0,0]
                                                # 0x740 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x740>
		000000000000073c:  R_X86_64_PC32	.LCPI1216_6-0x4
     740:      	vmovapd	%xmm0, %xmm10
     744:      	vmovapd	%xmm2, %xmm11
     748:      	jmp	0x765 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x765>
     74a:      	vmovapd	%xmm6, %xmm7
     74e:      	vmovapd	%xmm0, %xmm10
     752:      	leaq	(%rsi,%rbx), %rax
     756:      	incq	%rax
     759:      	incq	%rbx
     75c:      	cmpq	%rdx, %rax
     75f:      	jae	0x2a8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2a8>
     765:      	vmovapd	%xmm5, %xmm13
     769:      	vmovapd	%xmm6, %xmm12
     76d:      	vmovsd	(%r10,%rbx,8), %xmm5
     773:      	vmovsd	(%r9,%rbx,8), %xmm6
     779:      	cmpq	$0x1, %r11
     77d:      	jne	0x7e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7e0>
     77f:      	vucomisd	%xmm5, %xmm4
     783:      	jae	0x83b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x83b>
     789:      	cmpq	%r14, %rbx
     78c:      	jae	0x9c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9c0>
     792:      	vmovsd	%xmm4, (%r8,%rbx,8)
     798:      	vucomisd	%xmm7, %xmm6
     79c:      	jbe	0x7b8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7b8>
     79e:      	vaddsd	0x8(%rsp), %xmm10, %xmm10
     7a4:      	vucomisd	%xmm15, %xmm10
     7a9:      	vmovapd	%xmm6, %xmm7
     7ad:      	jbe	0x7b8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7b8>
     7af:      	vmovapd	%xmm6, %xmm7
     7b3:      	vmovapd	%xmm15, %xmm10
     7b8:      	vsubsd	%xmm4, %xmm7, %xmm12
     7bc:      	vfmadd213sd	%xmm4, %xmm10, %xmm12 # xmm12 = (xmm10 * xmm12) + xmm4
     7c1:      	vminsd	%xmm12, %xmm13, %xmm4
     7c6:      	movl	$0x1, %r11d
     7cc:      	vucomisd	%xmm5, %xmm4
     7d0:      	jbe	0x752 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x752>
     7d2:      	vmovapd	%xmm5, %xmm4
     7d6:      	jmp	0x752 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x752>
     7db:      	nopl	(%rax,%rax)
     7e0:      	vucomisd	%xmm4, %xmm6
     7e4:      	jae	0x88b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x88b>
     7ea:      	cmpq	%r14, %rbx
     7ed:      	jae	0x97a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x97a>
     7f3:      	vxorpd	%xmm4, %xmm9, %xmm13
     7f7:      	vmovlpd	%xmm13, (%r8,%rbx,8)
     7fd:      	vucomisd	%xmm5, %xmm7
     801:      	jbe	0x81b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x81b>
     803:      	vaddsd	%xmm3, %xmm11, %xmm11
     807:      	vucomisd	%xmm14, %xmm11
     80c:      	vmovapd	%xmm5, %xmm7
     810:      	jbe	0x81b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x81b>
     812:      	vmovapd	%xmm5, %xmm7
     816:      	vmovapd	%xmm14, %xmm11
     81b:      	vsubsd	%xmm4, %xmm7, %xmm13
     81f:      	vfmadd213sd	%xmm4, %xmm11, %xmm13 # xmm13 = (xmm11 * xmm13) + xmm4
     824:      	vmaxsd	%xmm13, %xmm12, %xmm4
     829:      	vucomisd	%xmm4, %xmm6
     82d:      	jbe	0x883 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x883>
     82f:      	vmovapd	%xmm6, %xmm4
     833:      	xorl	%r11d, %r11d
     836:      	jmp	0x752 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x752>
     83b:      	cmpq	%r14, %rbx
     83e:      	jae	0x99d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x99d>
     844:      	vmaxsd	%xmm7, %xmm12, %xmm4
     848:      	vmaxsd	%xmm4, %xmm6, %xmm4
     84c:      	vmulsd	%xmm4, %xmm1, %xmm7
     850:      	vaddsd	%xmm7, %xmm4, %xmm7
     854:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     85a:      	vxorpd	%xmm4, %xmm9, %xmm7
     85e:      	vmovlpd	%xmm7, (%r8,%rbx,8)
     864:      	vsubsd	%xmm4, %xmm5, %xmm7
     868:      	vfmadd213sd	%xmm4, %xmm2, %xmm7 # xmm7 = (xmm2 * xmm7) + xmm4
     86d:      	vmaxsd	%xmm7, %xmm12, %xmm4
     871:      	vucomisd	%xmm4, %xmm6
     875:      	jbe	0x87b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x87b>
     877:      	vmovapd	%xmm6, %xmm4
     87b:      	vmovapd	%xmm5, %xmm7
     87f:      	vmovapd	%xmm2, %xmm11
     883:      	xorl	%r11d, %r11d
     886:      	jmp	0x752 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x752>
     88b:      	cmpq	%r14, %rbx
     88e:      	jae	0x957 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x957>
     894:      	vminsd	%xmm7, %xmm13, %xmm4
     898:      	vminsd	%xmm4, %xmm5, %xmm4
     89c:      	vmulsd	%xmm4, %xmm1, %xmm7
     8a0:      	vsubsd	%xmm7, %xmm4, %xmm7
     8a4:      	vblendvpd	%xmm8, %xmm7, %xmm4, %xmm4
     8aa:      	vmovlpd	%xmm4, (%r8,%rbx,8)
     8b0:      	vsubsd	%xmm4, %xmm6, %xmm7
     8b4:      	vfmadd213sd	%xmm4, %xmm0, %xmm7 # xmm7 = (xmm0 * xmm7) + xmm4
     8b9:      	vminsd	%xmm7, %xmm13, %xmm4
     8bd:      	movl	$0x1, %r11d
     8c3:      	vucomisd	%xmm5, %xmm4
     8c7:      	jbe	0x74a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x74a>
     8cd:      	vmovapd	%xmm5, %xmm4
     8d1:      	jmp	0x74a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x74a>
     8d6:      	leaq	(%rip), %rdi            # 0x8dd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8dd>
		00000000000008d9:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.13.llvm.7684525917036654579-0x4
     8dd:      	leaq	(%rip), %rdx            # 0x8e4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8e4>
		00000000000008e0:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8054-0x4
     8e4:      	movl	$0x40, %esi
     8e9:      	callq	*(%rip)                 # 0x8ef <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8ef>
		00000000000008eb:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     8ef:      	leaq	(%rip), %rdi            # 0x8f6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8f6>
		00000000000008f2:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.16.llvm.7684525917036654579-0x4
     8f6:      	leaq	(%rip), %rdx            # 0x8fd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8fd>
		00000000000008f9:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8055-0x4
     8fd:      	movl	$0x3f, %esi
     902:      	callq	*(%rip)                 # 0x908 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x908>
		0000000000000904:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     908:      	leaq	(%rip), %rdi            # 0x90f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x90f>
		000000000000090b:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.18.llvm.7684525917036654579-0x4
     90f:      	leaq	(%rip), %rdx            # 0x916 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x916>
		0000000000000912:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8056-0x4
     916:      	movl	$0x50, %esi
     91b:      	callq	*(%rip)                 # 0x921 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x921>
		000000000000091d:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     921:      	leaq	(%rip), %rdx            # 0x928 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x928>
		0000000000000924:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8057-0x4
     928:      	movq	%rbx, %rdi
     92b:      	movq	%r8, %rsi
     92e:      	callq	*(%rip)                 # 0x934 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x934>
		0000000000000930:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     934:      	leaq	(%rip), %rdx            # 0x93b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x93b>
		0000000000000937:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8058-0x4
     93b:      	movq	%rbx, %rdi
     93e:      	movq	%rax, %rsi
     941:      	callq	*(%rip)                 # 0x947 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x947>
		0000000000000943:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     947:      	leaq	(%rip), %rdx            # 0x94e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x94e>
		000000000000094a:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8064-0x4
     94e:      	movq	%rax, %rsi
     951:      	callq	*(%rip)                 # 0x957 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x957>
		0000000000000953:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     957:      	leaq	(%rip), %rdx            # 0x95e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x95e>
		000000000000095a:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8068-0x4
     95e:      	movq	%rbx, %rdi
     961:      	movq	%r14, %rsi
     964:      	callq	*(%rip)                 # 0x96a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x96a>
		0000000000000966:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     96a:      	leaq	(%rip), %rdx            # 0x971 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x971>
		000000000000096d:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8063-0x4
     971:      	movq	%rax, %rsi
     974:      	callq	*(%rip)                 # 0x97a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x97a>
		0000000000000976:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     97a:      	leaq	(%rip), %rdx            # 0x981 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x981>
		000000000000097d:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8067-0x4
     981:      	movq	%rbx, %rdi
     984:      	movq	%r14, %rsi
     987:      	callq	*(%rip)                 # 0x98d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x98d>
		0000000000000989:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     98d:      	leaq	(%rip), %rdx            # 0x994 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x994>
		0000000000000990:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8062-0x4
     994:      	movq	%rax, %rsi
     997:      	callq	*(%rip)                 # 0x99d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x99d>
		0000000000000999:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     99d:      	leaq	(%rip), %rdx            # 0x9a4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9a4>
		00000000000009a0:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8066-0x4
     9a4:      	movq	%rbx, %rdi
     9a7:      	movq	%r14, %rsi
     9aa:      	callq	*(%rip)                 # 0x9b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9b0>
		00000000000009ac:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     9b0:      	leaq	(%rip), %rdx            # 0x9b7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9b7>
		00000000000009b3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8061-0x4
     9b7:      	movq	%rax, %rsi
     9ba:      	callq	*(%rip)                 # 0x9c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9c0>
		00000000000009bc:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     9c0:      	leaq	(%rip), %rdx            # 0x9c7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9c7>
		00000000000009c3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8065-0x4
     9c7:      	movq	%rbx, %rdi
     9ca:      	movq	%r14, %rsi
     9cd:      	callq	*(%rip)                 # 0x9d3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9d3>
		00000000000009cf:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     9d3:      	leaq	(%rip), %rdx            # 0x9da <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9da>
		00000000000009d6:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8059-0x4
     9da:      	movq	%rbx, %rsi
     9dd:      	callq	*(%rip)                 # 0x9e3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x9e3>
		00000000000009df:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
