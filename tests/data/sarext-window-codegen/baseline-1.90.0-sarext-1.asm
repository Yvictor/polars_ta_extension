
/tmp/polars-recovery/sarext-window-evidence/baseline-static-1.90.0/library-objects/ta_lib-a99de56cdf066125.ta_lib.4f1d99721d8d97c2-cgu.00.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E:

0000000000000000 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0x58, %rsp
       e:      	movw	$0xd, %ax
      12:      	cmpq	%rsi, %rdx
      15:      	jae	0x26 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x26>
      17:      	addq	$0x58, %rsp
      1b:      	popq	%rbx
      1c:      	popq	%r12
      1e:      	popq	%r13
      20:      	popq	%r14
      22:      	popq	%r15
      24:      	popq	%rbp
      25:      	retq
      26:      	vxorpd	%xmm10, %xmm10, %xmm10
      2b:      	vucomisd	(%rip), %xmm0           # 0x33 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x33>
		000000000000002f:  R_X86_64_PC32	.LCPI1216_0-0x4
      33:      	vxorpd	%xmm15, %xmm15, %xmm15
      38:      	jne	0x3c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3c>
      3a:      	jnp	0x5b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5b>
      3c:      	vandpd	(%rip), %xmm0, %xmm9    # 0x44 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x44>
		0000000000000040:  R_X86_64_PC32	.LCPI1216_1-0x4
      44:      	movw	$0x2, %ax
      48:      	vmovsd	(%rip), %xmm8           # 0x50 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x50>
		000000000000004c:  R_X86_64_PC32	.LCPI1216_2-0x4
      50:      	vucomisd	%xmm9, %xmm8
      55:      	vmovapd	%xmm0, %xmm15
      59:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      5b:      	vucomisd	(%rip), %xmm1           # 0x63 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x63>
		000000000000005f:  R_X86_64_PC32	.LCPI1216_0-0x4
      63:      	jne	0x67 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x67>
      65:      	jnp	0x87 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x87>
      67:      	vxorpd	%xmm0, %xmm0, %xmm0
      6b:      	vucomisd	%xmm0, %xmm1
      6f:      	movw	$0x2, %ax
      73:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      75:      	vmovsd	(%rip), %xmm0           # 0x7d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7d>
		0000000000000079:  R_X86_64_PC32	.LCPI1216_2-0x4
      7d:      	vucomisd	%xmm1, %xmm0
      81:      	vmovapd	%xmm1, %xmm10
      85:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      87:      	vmovsd	(%rip), %xmm8           # 0x8f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x8f>
		000000000000008b:  R_X86_64_PC32	.LCPI1216_3-0x4
      8f:      	vucomisd	(%rip), %xmm2           # 0x97 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x97>
		0000000000000093:  R_X86_64_PC32	.LCPI1216_0-0x4
      97:      	vmovapd	%xmm8, %xmm9
      9c:      	jne	0xa0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xa0>
      9e:      	jnp	0xc8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xc8>
      a0:      	vxorpd	%xmm0, %xmm0, %xmm0
      a4:      	vucomisd	%xmm0, %xmm2
      a8:      	movw	$0x2, %ax
      ac:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      b2:      	vmovsd	(%rip), %xmm0           # 0xba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xba>
		00000000000000b6:  R_X86_64_PC32	.LCPI1216_2-0x4
      ba:      	vucomisd	%xmm2, %xmm0
      be:      	vmovapd	%xmm2, %xmm9
      c2:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      c8:      	vucomisd	(%rip), %xmm3           # 0xd0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xd0>
		00000000000000cc:  R_X86_64_PC32	.LCPI1216_0-0x4
      d0:      	jne	0xd4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xd4>
      d2:      	jnp	0xfc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xfc>
      d4:      	vxorpd	%xmm0, %xmm0, %xmm0
      d8:      	vucomisd	%xmm0, %xmm3
      dc:      	movw	$0x2, %ax
      e0:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      e6:      	vmovsd	(%rip), %xmm0           # 0xee <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0xee>
		00000000000000ea:  R_X86_64_PC32	.LCPI1216_2-0x4
      ee:      	vucomisd	%xmm3, %xmm0
      f2:      	vmovapd	%xmm3, %xmm8
      f6:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
      fc:      	vucomisd	(%rip), %xmm4           # 0x104 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x104>
		0000000000000100:  R_X86_64_PC32	.LCPI1216_0-0x4
     104:      	jne	0x112 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x112>
     106:      	jp	0x112 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x112>
     108:      	vmovsd	(%rip), %xmm4           # 0x110 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x110>
		000000000000010c:  R_X86_64_PC32	.LCPI1216_4-0x4
     110:      	jmp	0x136 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x136>
     112:      	vxorpd	%xmm0, %xmm0, %xmm0
     116:      	vucomisd	%xmm0, %xmm4
     11a:      	movw	$0x2, %ax
     11e:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     124:      	vmovsd	(%rip), %xmm0           # 0x12c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x12c>
		0000000000000128:  R_X86_64_PC32	.LCPI1216_2-0x4
     12c:      	vucomisd	%xmm4, %xmm0
     130:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     136:      	vmovsd	(%rip), %xmm3           # 0x13e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x13e>
		000000000000013a:  R_X86_64_PC32	.LCPI1216_3-0x4
     13e:      	vucomisd	(%rip), %xmm5           # 0x146 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x146>
		0000000000000142:  R_X86_64_PC32	.LCPI1216_0-0x4
     146:      	vmovapd	%xmm3, %xmm2
     14a:      	jne	0x14e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x14e>
     14c:      	jnp	0x176 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x176>
     14e:      	vxorpd	%xmm0, %xmm0, %xmm0
     152:      	vucomisd	%xmm0, %xmm5
     156:      	movw	$0x2, %ax
     15a:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     160:      	vmovsd	(%rip), %xmm0           # 0x168 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x168>
		0000000000000164:  R_X86_64_PC32	.LCPI1216_2-0x4
     168:      	vucomisd	%xmm5, %xmm0
     16c:      	vmovapd	%xmm5, %xmm2
     170:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     176:      	vucomisd	(%rip), %xmm6           # 0x17e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17e>
		000000000000017a:  R_X86_64_PC32	.LCPI1216_0-0x4
     17e:      	jne	0x182 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x182>
     180:      	jnp	0x1aa <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1aa>
     182:      	vxorpd	%xmm0, %xmm0, %xmm0
     186:      	vucomisd	%xmm0, %xmm6
     18a:      	movw	$0x2, %ax
     18e:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     194:      	vmovsd	(%rip), %xmm0           # 0x19c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x19c>
		0000000000000198:  R_X86_64_PC32	.LCPI1216_2-0x4
     19c:      	vucomisd	%xmm6, %xmm0
     1a0:      	vmovapd	%xmm6, %xmm3
     1a4:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1aa:      	vucomisd	(%rip), %xmm7           # 0x1b2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1b2>
		00000000000001ae:  R_X86_64_PC32	.LCPI1216_0-0x4
     1b2:      	jne	0x1c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1c0>
     1b4:      	jp	0x1c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1c0>
     1b6:      	vmovsd	(%rip), %xmm7           # 0x1be <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1be>
		00000000000001ba:  R_X86_64_PC32	.LCPI1216_4-0x4
     1be:      	jmp	0x1e4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1e4>
     1c0:      	vxorpd	%xmm0, %xmm0, %xmm0
     1c4:      	vucomisd	%xmm0, %xmm7
     1c8:      	movw	$0x2, %ax
     1cc:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1d2:      	vmovsd	(%rip), %xmm0           # 0x1da <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1da>
		00000000000001d6:  R_X86_64_PC32	.LCPI1216_2-0x4
     1da:      	vucomisd	%xmm7, %xmm0
     1de:      	jb	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     1e4:      	vucomisd	(%rip), %xmm15          # 0x1ec <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1ec>
		00000000000001e8:  R_X86_64_PC32	.LCPI1216_0-0x4
     1ec:      	vandpd	(%rip), %xmm15, %xmm0   # 0x1f4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x1f4>
		00000000000001f0:  R_X86_64_PC32	.LCPI1216_1-0x4
     1f4:      	movq	$-0x1, %r10
     1fb:      	jne	0x203 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x203>
     1fd:      	jnp	0x2af <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2af>
     203:      	vmovsd	(%rip), %xmm1           # 0x20b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x20b>
		0000000000000207:  R_X86_64_PC32	.LCPI1216_2-0x4
     20b:      	vucomisd	%xmm0, %xmm1
     20f:      	jae	0x2af <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2af>
     215:      	cmpq	%r10, %rsi
     218:      	cmovaq	%rsi, %r10
     21c:      	cmpq	%rdx, %r10
     21f:      	seta	%al
     222:      	cmpq	%r8, %rdx
     225:      	setb	%r11b
     229:      	orb	%al, %r11b
     22c:      	je	0x72f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x72f>
     232:      	movq	0x90(%rsp), %rax
     23a:      	cmpq	%r10, %rdx
     23d:      	setb	%r11b
     241:      	cmpq	%rax, %rdx
     244:      	setb	%bl
     247:      	orb	%r11b, %bl
     24a:      	je	0x748 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x748>
     250:      	movq	0xb0(%rsp), %rbx
     258:      	movq	%rdx, %r11
     25b:      	subq	%r10, %r11
     25e:      	setb	%r10b
     262:      	cmpq	%rbx, %r11
     265:      	setb	%r11b
     269:      	orb	%r10b, %r11b
     26c:      	je	0x761 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x761>
     272:      	movq	0x98(%rsp), %r15
     27a:      	movq	$0x0, 0x8(%rsp)
     283:      	cmpq	$0x1, %rsi
     287:      	adcq	$0x0, %rsi
     28b:      	cmpq	%rdx, %rsi
     28e:      	jbe	0x3f1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3f1>
     294:      	movq	$0x0, (%r15)
     29b:      	xorl	%edi, %edi
     29d:      	movq	0xa0(%rsp), %rax
     2a5:      	movq	%rdi, (%rax)
     2a8:      	xorl	%eax, %eax
     2aa:      	jmp	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     2af:      	vucomisd	(%rip), %xmm10          # 0x2b7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2b7>
		00000000000002b3:  R_X86_64_PC32	.LCPI1216_0-0x4
     2b7:      	jne	0x2bb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2bb>
     2b9:      	jnp	0x2dc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2dc>
     2bb:      	vxorpd	%xmm1, %xmm1, %xmm1
     2bf:      	vucomisd	%xmm1, %xmm10
     2c3:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     2c9:      	vmovsd	(%rip), %xmm1           # 0x2d1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2d1>
		00000000000002cd:  R_X86_64_PC32	.LCPI1216_2-0x4
     2d1:      	vucomisd	%xmm10, %xmm1
     2d6:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     2dc:      	vucomisd	(%rip), %xmm9           # 0x2e4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2e4>
		00000000000002e0:  R_X86_64_PC32	.LCPI1216_0-0x4
     2e4:      	jne	0x2e8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2e8>
     2e6:      	jnp	0x309 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x309>
     2e8:      	vxorpd	%xmm1, %xmm1, %xmm1
     2ec:      	vucomisd	%xmm1, %xmm9
     2f0:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     2f6:      	vmovsd	(%rip), %xmm1           # 0x2fe <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x2fe>
		00000000000002fa:  R_X86_64_PC32	.LCPI1216_2-0x4
     2fe:      	vucomisd	%xmm9, %xmm1
     303:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     309:      	vucomisd	(%rip), %xmm8           # 0x311 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x311>
		000000000000030d:  R_X86_64_PC32	.LCPI1216_0-0x4
     311:      	jne	0x315 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x315>
     313:      	jnp	0x336 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x336>
     315:      	vxorpd	%xmm1, %xmm1, %xmm1
     319:      	vucomisd	%xmm1, %xmm8
     31d:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     323:      	vmovsd	(%rip), %xmm1           # 0x32b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x32b>
		0000000000000327:  R_X86_64_PC32	.LCPI1216_2-0x4
     32b:      	vucomisd	%xmm8, %xmm1
     330:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     336:      	vucomisd	(%rip), %xmm4           # 0x33e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x33e>
		000000000000033a:  R_X86_64_PC32	.LCPI1216_0-0x4
     33e:      	jne	0x342 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x342>
     340:      	jnp	0x362 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x362>
     342:      	vxorpd	%xmm1, %xmm1, %xmm1
     346:      	vucomisd	%xmm1, %xmm4
     34a:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     350:      	vmovsd	(%rip), %xmm1           # 0x358 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x358>
		0000000000000354:  R_X86_64_PC32	.LCPI1216_2-0x4
     358:      	vucomisd	%xmm4, %xmm1
     35c:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     362:      	vucomisd	(%rip), %xmm2           # 0x36a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x36a>
		0000000000000366:  R_X86_64_PC32	.LCPI1216_0-0x4
     36a:      	jne	0x36e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x36e>
     36c:      	jnp	0x38e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x38e>
     36e:      	vxorpd	%xmm1, %xmm1, %xmm1
     372:      	vucomisd	%xmm1, %xmm2
     376:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     37c:      	vmovsd	(%rip), %xmm1           # 0x384 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x384>
		0000000000000380:  R_X86_64_PC32	.LCPI1216_2-0x4
     384:      	vucomisd	%xmm2, %xmm1
     388:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     38e:      	vucomisd	(%rip), %xmm3           # 0x396 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x396>
		0000000000000392:  R_X86_64_PC32	.LCPI1216_0-0x4
     396:      	jne	0x39a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x39a>
     398:      	jnp	0x3ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3ba>
     39a:      	vxorpd	%xmm1, %xmm1, %xmm1
     39e:      	vucomisd	%xmm1, %xmm3
     3a2:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     3a8:      	vmovsd	(%rip), %xmm1           # 0x3b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3b0>
		00000000000003ac:  R_X86_64_PC32	.LCPI1216_2-0x4
     3b0:      	vucomisd	%xmm3, %xmm1
     3b4:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     3ba:      	vucomisd	(%rip), %xmm7           # 0x3c2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3c2>
		00000000000003be:  R_X86_64_PC32	.LCPI1216_0-0x4
     3c2:      	jne	0x3c6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3c6>
     3c4:      	jnp	0x3e6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3e6>
     3c6:      	vxorpd	%xmm1, %xmm1, %xmm1
     3ca:      	vucomisd	%xmm1, %xmm7
     3ce:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     3d4:      	vmovsd	(%rip), %xmm1           # 0x3dc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x3dc>
		00000000000003d8:  R_X86_64_PC32	.LCPI1216_2-0x4
     3dc:      	vucomisd	%xmm7, %xmm1
     3e0:      	jb	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     3e6:      	movl	$0x1, %r10d
     3ec:      	jmp	0x215 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x215>
     3f1:      	leaq	0x1(%rdx), %r14
     3f5:      	cmpq	%r8, %rdx
     3f8:      	jae	0x77a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x77a>
     3fe:      	cmpq	%rax, %rdx
     401:      	jae	0x78d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x78d>
     407:      	vxorpd	%xmm1, %xmm1, %xmm1
     40b:      	vucomisd	%xmm1, %xmm15
     40f:      	jne	0x4f4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x4f4>
     415:      	jp	0x4f4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x4f4>
     41b:      	vmovsd	%xmm2, 0x10(%rsp)
     421:      	vmovsd	%xmm3, 0x18(%rsp)
     427:      	vmovsd	%xmm9, 0x20(%rsp)
     42d:      	vmovsd	%xmm8, 0x28(%rsp)
     433:      	vmovsd	%xmm10, 0x30(%rsp)
     439:      	vmovsd	%xmm4, 0x38(%rsp)
     43f:      	vmovsd	%xmm7, 0x40(%rsp)
     445:      	movq	%rdx, (%rsp)
     449:      	movl	0xf4(%rdi), %edi
     44f:      	leaq	0x8(%rsp), %rax
     454:      	leaq	0x50(%rsp), %r10
     459:      	leaq	0x48(%rsp), %r11
     45e:      	movq	%rsi, %rdx
     461:      	movq	%rsi, %r12
     464:      	movq	%rcx, %r13
     467:      	movq	%r14, %r8
     46a:      	movq	%r9, %rbp
     46d:      	pushq	$0x1
     46f:      	pushq	%rax
     470:      	pushq	%r10
     472:      	pushq	%r11
     474:      	pushq	$0x1
     476:      	pushq	%r14
     478:      	callq	0x47d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x47d>
		0000000000000479:  R_X86_64_PLT32	_ZN6ta_lib7ta_func8minus_dm46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$13minus_dm_impl17h2888df27879bfa4fE.llvm.15298552028749941447-0x4
     47d:      	addq	$0x30, %rsp
     481:      	testw	%ax, %ax
     484:      	jne	0x17 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x17>
     48a:      	vmovsd	0x8(%rsp), %xmm0
     490:      	movq	%r12, (%r15)
     493:      	leaq	-0x1(%r12), %rdi
     498:      	movq	(%rsp), %rdx
     49c:      	cmpq	%rdx, %rdi
     49f:      	vmovsd	0x40(%rsp), %xmm7
     4a5:      	vmovsd	0x38(%rsp), %xmm4
     4ab:      	vmovsd	0x30(%rsp), %xmm10
     4b1:      	vmovsd	0x28(%rsp), %xmm8
     4b7:      	vmovsd	0x20(%rsp), %xmm9
     4bd:      	vmovsd	0x18(%rsp), %xmm3
     4c3:      	vmovsd	0x10(%rsp), %xmm2
     4c9:      	ja	0x7e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7e0>
     4cf:      	movq	%r12, %rsi
     4d2:      	movq	%rbp, %r9
     4d5:      	movq	%r13, %rcx
     4d8:      	vxorpd	%xmm1, %xmm1, %xmm1
     4dc:      	vucomisd	%xmm1, %xmm0
     4e0:      	ja	0x51e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x51e>
     4e2:      	vmovsd	-0x8(%r9,%rsi,8), %xmm15
     4e9:      	movl	$0x1, %r10d
     4ef:      	movq	%rcx, %rdi
     4f2:      	jmp	0x52a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x52a>
     4f4:      	movq	%rsi, (%r15)
     4f7:      	leaq	-0x1(%rsi), %rdi
     4fb:      	cmpq	%rdx, %rdi
     4fe:      	ja	0x7e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7e0>
     504:      	xorl	%r10d, %r10d
     507:      	vucomisd	%xmm1, %xmm15
     50b:      	seta	%r10b
     50f:      	movq	%r9, %rdi
     512:      	cmovaq	%rcx, %rdi
     516:      	ja	0x52a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x52a>
     518:      	vmovapd	%xmm0, %xmm15
     51c:      	jmp	0x52a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x52a>
     51e:      	vmovsd	-0x8(%rcx,%rsi,8), %xmm15
     524:      	xorl	%r10d, %r10d
     527:      	movq	%r9, %rdi
     52a:      	movq	0xa8(%rsp), %rax
     532:      	vminsd	%xmm9, %xmm4, %xmm0
     537:      	vminsd	%xmm8, %xmm4, %xmm1
     53c:      	vmovsd	%xmm1, (%rsp)
     541:      	vminsd	%xmm2, %xmm7, %xmm2
     545:      	vminsd	%xmm3, %xmm7, %xmm3
     549:      	vmovsd	(%rcx,%rsi,8), %xmm5
     54e:      	vmovsd	(%r9,%rsi,8), %xmm6
     554:      	vmovsd	(%rdi,%rsi,8), %xmm11
     559:      	leaq	-0x1(%rsi), %r8
     55d:      	leaq	(%rcx,%rsi,8), %rcx
     561:      	leaq	(%r9,%rsi,8), %rsi
     565:      	xorl	%edi, %edi
     567:      	vxorpd	%xmm8, %xmm8, %xmm8
     56c:      	vmovapd	%xmm10, %xmm1
     570:      	vcmpneqsd	%xmm8, %xmm10, %xmm14
     576:      	vmovddup	(%rip), %xmm8           # xmm8 = mem[0,0]
                                                # 0x57e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x57e>
		000000000000057a:  R_X86_64_PC32	.LCPI1216_6-0x4
     57e:      	vmovapd	%xmm0, %xmm9
     582:      	vmovapd	%xmm2, %xmm10
     586:      	jmp	0x5ab <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5ab>
     588:      	nopl	(%rax,%rax)
     590:      	vmovapd	%xmm5, %xmm11
     594:      	vmovapd	%xmm0, %xmm9
     598:      	leaq	(%r8,%rdi), %r9
     59c:      	incq	%r9
     59f:      	incq	%rdi
     5a2:      	cmpq	%rdx, %r9
     5a5:      	jae	0x29d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x29d>
     5ab:      	vmovapd	%xmm6, %xmm13
     5af:      	vmovapd	%xmm5, %xmm12
     5b3:      	vmovsd	(%rsi,%rdi,8), %xmm6
     5b8:      	vmovsd	(%rcx,%rdi,8), %xmm5
     5bd:      	cmpq	$0x1, %r10
     5c1:      	jne	0x620 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x620>
     5c3:      	vucomisd	%xmm6, %xmm15
     5c7:      	jae	0x680 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x680>
     5cd:      	cmpq	%rbx, %rdi
     5d0:      	jae	0x7d0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7d0>
     5d6:      	vmovsd	%xmm15, (%rax,%rdi,8)
     5db:      	vucomisd	%xmm11, %xmm5
     5e0:      	jbe	0x5f9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5f9>
     5e2:      	vaddsd	(%rsp), %xmm9, %xmm9
     5e7:      	vucomisd	%xmm4, %xmm9
     5eb:      	vmovapd	%xmm5, %xmm11
     5ef:      	jbe	0x5f9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x5f9>
     5f1:      	vmovapd	%xmm5, %xmm11
     5f5:      	vmovapd	%xmm4, %xmm9
     5f9:      	vsubsd	%xmm15, %xmm11, %xmm12
     5fe:      	vfmadd213sd	%xmm15, %xmm9, %xmm12 # xmm12 = (xmm9 * xmm12) + xmm15
     603:      	vminsd	%xmm12, %xmm13, %xmm15
     608:      	movl	$0x1, %r10d
     60e:      	vucomisd	%xmm6, %xmm15
     612:      	jbe	0x598 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x598>
     614:      	vmovapd	%xmm6, %xmm15
     618:      	jmp	0x598 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x598>
     61d:      	nopl	(%rax)
     620:      	vucomisd	%xmm15, %xmm5
     625:      	jae	0x6e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x6e0>
     62b:      	cmpq	%rbx, %rdi
     62e:      	jae	0x7b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7b0>
     634:      	vxorpd	%xmm8, %xmm15, %xmm13
     639:      	vmovlpd	%xmm13, (%rax,%rdi,8)
     63e:      	vucomisd	%xmm6, %xmm11
     642:      	jbe	0x65a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x65a>
     644:      	vaddsd	%xmm3, %xmm10, %xmm10
     648:      	vucomisd	%xmm7, %xmm10
     64c:      	vmovapd	%xmm6, %xmm11
     650:      	jbe	0x65a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x65a>
     652:      	vmovapd	%xmm6, %xmm11
     656:      	vmovapd	%xmm7, %xmm10
     65a:      	vsubsd	%xmm15, %xmm11, %xmm13
     65f:      	vfmadd213sd	%xmm15, %xmm10, %xmm13 # xmm13 = (xmm10 * xmm13) + xmm15
     664:      	vmaxsd	%xmm13, %xmm12, %xmm15
     669:      	vucomisd	%xmm15, %xmm5
     66e:      	jbe	0x6ce <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x6ce>
     670:      	vmovapd	%xmm5, %xmm15
     674:      	xorl	%r10d, %r10d
     677:      	jmp	0x598 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x598>
     67c:      	nopl	(%rax)
     680:      	cmpq	%rbx, %rdi
     683:      	jae	0x7c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7c0>
     689:      	vmaxsd	%xmm11, %xmm12, %xmm10
     68e:      	vmaxsd	%xmm10, %xmm5, %xmm11
     693:      	vmulsd	%xmm1, %xmm11, %xmm10
     697:      	vaddsd	%xmm10, %xmm11, %xmm10
     69c:      	vblendvpd	%xmm14, %xmm10, %xmm11, %xmm11
     6a2:      	vxorpd	%xmm8, %xmm11, %xmm10
     6a7:      	vmovlpd	%xmm10, (%rax,%rdi,8)
     6ac:      	vsubsd	%xmm11, %xmm6, %xmm10
     6b1:      	vfmadd213sd	%xmm11, %xmm2, %xmm10 # xmm10 = (xmm2 * xmm10) + xmm11
     6b6:      	vmaxsd	%xmm10, %xmm12, %xmm15
     6bb:      	vucomisd	%xmm15, %xmm5
     6c0:      	jbe	0x6c6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x6c6>
     6c2:      	vmovapd	%xmm5, %xmm15
     6c6:      	vmovapd	%xmm6, %xmm11
     6ca:      	vmovapd	%xmm2, %xmm10
     6ce:      	xorl	%r10d, %r10d
     6d1:      	jmp	0x598 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x598>
     6d6:      	nopw	%cs:(%rax,%rax)
     6e0:      	cmpq	%rbx, %rdi
     6e3:      	jae	0x7a0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7a0>
     6e9:      	vminsd	%xmm11, %xmm13, %xmm9
     6ee:      	vminsd	%xmm9, %xmm6, %xmm11
     6f3:      	vmulsd	%xmm1, %xmm11, %xmm9
     6f7:      	vsubsd	%xmm9, %xmm11, %xmm9
     6fc:      	vblendvpd	%xmm14, %xmm9, %xmm11, %xmm11
     702:      	vmovlpd	%xmm11, (%rax,%rdi,8)
     707:      	vsubsd	%xmm11, %xmm5, %xmm9
     70c:      	vfmadd213sd	%xmm11, %xmm0, %xmm9 # xmm9 = (xmm0 * xmm9) + xmm11
     711:      	vminsd	%xmm9, %xmm13, %xmm15
     716:      	movl	$0x1, %r10d
     71c:      	vucomisd	%xmm6, %xmm15
     720:      	jbe	0x590 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x590>
     726:      	vmovapd	%xmm6, %xmm15
     72a:      	jmp	0x590 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x590>
     72f:      	leaq	(%rip), %rdi            # 0x736 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x736>
		0000000000000732:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.13.llvm.15298552028749941447-0x4
     736:      	leaq	(%rip), %rdx            # 0x73d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x73d>
		0000000000000739:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8049-0x4
     73d:      	movl	$0x40, %esi
     742:      	callq	*(%rip)                 # 0x748 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x748>
		0000000000000744:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     748:      	leaq	(%rip), %rdi            # 0x74f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x74f>
		000000000000074b:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.16.llvm.15298552028749941447-0x4
     74f:      	leaq	(%rip), %rdx            # 0x756 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x756>
		0000000000000752:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8050-0x4
     756:      	movl	$0x3f, %esi
     75b:      	callq	*(%rip)                 # 0x761 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x761>
		000000000000075d:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     761:      	leaq	(%rip), %rdi            # 0x768 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x768>
		0000000000000764:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.18.llvm.15298552028749941447-0x4
     768:      	leaq	(%rip), %rdx            # 0x76f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x76f>
		000000000000076b:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8051-0x4
     76f:      	movl	$0x50, %esi
     774:      	callq	*(%rip)                 # 0x77a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x77a>
		0000000000000776:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     77a:      	leaq	(%rip), %rdx            # 0x781 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x781>
		000000000000077d:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8052-0x4
     781:      	movq	%r14, %rdi
     784:      	movq	%r8, %rsi
     787:      	callq	*(%rip)                 # 0x78d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x78d>
		0000000000000789:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     78d:      	leaq	(%rip), %rdx            # 0x794 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x794>
		0000000000000790:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8053-0x4
     794:      	movq	%r14, %rdi
     797:      	movq	%rax, %rsi
     79a:      	callq	*(%rip)                 # 0x7a0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7a0>
		000000000000079c:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     7a0:      	leaq	(%rip), %rdx            # 0x7a7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7a7>
		00000000000007a3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8058-0x4
     7a7:      	movq	%rbx, %rsi
     7aa:      	callq	*(%rip)                 # 0x7b0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7b0>
		00000000000007ac:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     7b0:      	leaq	(%rip), %rdx            # 0x7b7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7b7>
		00000000000007b3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8057-0x4
     7b7:      	movq	%rbx, %rsi
     7ba:      	callq	*(%rip)                 # 0x7c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7c0>
		00000000000007bc:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     7c0:      	leaq	(%rip), %rdx            # 0x7c7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7c7>
		00000000000007c3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8056-0x4
     7c7:      	movq	%rbx, %rsi
     7ca:      	callq	*(%rip)                 # 0x7d0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7d0>
		00000000000007cc:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     7d0:      	leaq	(%rip), %rdx            # 0x7d7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7d7>
		00000000000007d3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8055-0x4
     7d7:      	movq	%rbx, %rsi
     7da:      	callq	*(%rip)                 # 0x7e0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7e0>
		00000000000007dc:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     7e0:      	leaq	(%rip), %rdx            # 0x7e7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7e7>
		00000000000007e3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8054-0x4
     7e7:      	movq	%r14, %rsi
     7ea:      	callq	*(%rip)                 # 0x7f0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E+0x7f0>
		00000000000007ec:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
