
/tmp/polars-recovery/sarext-window-evidence/baseline-static-1.90.0/library-objects/ta_lib-a99de56cdf066125.ta_lib.4f1d99721d8d97c2-cgu.00.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E:

0000000000000000 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0xc8, %rsp
      11:      	movapd	%xmm2, %xmm8
      16:      	movq	0x120(%rsp), %rbx
      1e:      	movq	0x118(%rsp), %r13
      26:      	movq	0x110(%rsp), %r12
      2e:      	movq	0x108(%rsp), %rbp
      36:      	movq	0x100(%rsp), %r14
      3e:      	movq	(%rip), %rax            # 0x45 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x45>
		0000000000000041:  R_X86_64_GOTPCREL	_ZN10std_detect6detect5cache5CACHE17hb6755393302ff344E-0x4
      45:      	movq	(%rax), %rax
      48:      	testq	%rax, %rax
      4b:      	je	0x97b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x97b>
      51:      	btq	$0x36, %rax
      56:      	jb	0xa2b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa2b>
      5c:      	movw	$0xd, %ax
      60:      	cmpq	%rsi, %rdx
      63:      	jae	0x77 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x77>
      65:      	addq	$0xc8, %rsp
      6c:      	popq	%rbx
      6d:      	popq	%r12
      6f:      	popq	%r13
      71:      	popq	%r14
      73:      	popq	%r15
      75:      	popq	%rbp
      76:      	retq
      77:      	xorpd	%xmm12, %xmm12
      7c:      	ucomisd	(%rip), %xmm0           # 0x84 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x84>
		0000000000000080:  R_X86_64_PC32	.LCPI1215_0-0x4
      84:      	xorpd	%xmm2, %xmm2
      88:      	jne	0x8c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8c>
      8a:      	jnp	0xb1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb1>
      8c:      	movapd	(%rip), %xmm9           # 0x95 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x95>
		0000000000000091:  R_X86_64_PC32	.LCPI1215_1-0x4
      95:      	andpd	%xmm0, %xmm9
      9a:      	movw	$0x2, %ax
      9e:      	movsd	(%rip), %xmm2           # 0xa6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa6>
		00000000000000a2:  R_X86_64_PC32	.LCPI1215_2-0x4
      a6:      	ucomisd	%xmm9, %xmm2
      ab:      	movapd	%xmm0, %xmm2
      af:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
      b1:      	ucomisd	(%rip), %xmm1           # 0xb9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb9>
		00000000000000b5:  R_X86_64_PC32	.LCPI1215_0-0x4
      b9:      	jne	0xbd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xbd>
      bb:      	jnp	0xde <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xde>
      bd:      	xorpd	%xmm0, %xmm0
      c1:      	ucomisd	%xmm0, %xmm1
      c5:      	movw	$0x2, %ax
      c9:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
      cb:      	movsd	(%rip), %xmm0           # 0xd3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xd3>
		00000000000000cf:  R_X86_64_PC32	.LCPI1215_2-0x4
      d3:      	ucomisd	%xmm1, %xmm0
      d7:      	movapd	%xmm1, %xmm12
      dc:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
      de:      	movsd	(%rip), %xmm11          # 0xe7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe7>
		00000000000000e3:  R_X86_64_PC32	.LCPI1215_3-0x4
      e7:      	ucomisd	(%rip), %xmm8           # 0xf0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xf0>
		00000000000000ec:  R_X86_64_PC32	.LCPI1215_0-0x4
      f0:      	movapd	%xmm11, %xmm10
      f5:      	jne	0xf9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xf9>
      f7:      	jnp	0x124 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x124>
      f9:      	xorpd	%xmm0, %xmm0
      fd:      	ucomisd	%xmm0, %xmm8
     102:      	movw	$0x2, %ax
     106:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     10c:      	movsd	(%rip), %xmm0           # 0x114 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x114>
		0000000000000110:  R_X86_64_PC32	.LCPI1215_2-0x4
     114:      	ucomisd	%xmm8, %xmm0
     119:      	movapd	%xmm8, %xmm10
     11e:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     124:      	ucomisd	(%rip), %xmm3           # 0x12c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x12c>
		0000000000000128:  R_X86_64_PC32	.LCPI1215_0-0x4
     12c:      	jne	0x130 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x130>
     12e:      	jnp	0x159 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x159>
     130:      	xorpd	%xmm0, %xmm0
     134:      	ucomisd	%xmm0, %xmm3
     138:      	movw	$0x2, %ax
     13c:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     142:      	movsd	(%rip), %xmm0           # 0x14a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x14a>
		0000000000000146:  R_X86_64_PC32	.LCPI1215_2-0x4
     14a:      	ucomisd	%xmm3, %xmm0
     14e:      	movapd	%xmm3, %xmm11
     153:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     159:      	ucomisd	(%rip), %xmm4           # 0x161 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x161>
		000000000000015d:  R_X86_64_PC32	.LCPI1215_0-0x4
     161:      	jne	0x16f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x16f>
     163:      	jp	0x16f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x16f>
     165:      	movsd	(%rip), %xmm4           # 0x16d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x16d>
		0000000000000169:  R_X86_64_PC32	.LCPI1215_4-0x4
     16d:      	jmp	0x193 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x193>
     16f:      	xorpd	%xmm0, %xmm0
     173:      	ucomisd	%xmm0, %xmm4
     177:      	movw	$0x2, %ax
     17b:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     181:      	movsd	(%rip), %xmm0           # 0x189 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x189>
		0000000000000185:  R_X86_64_PC32	.LCPI1215_2-0x4
     189:      	ucomisd	%xmm4, %xmm0
     18d:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     193:      	movsd	(%rip), %xmm8           # 0x19c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x19c>
		0000000000000198:  R_X86_64_PC32	.LCPI1215_3-0x4
     19c:      	ucomisd	(%rip), %xmm5           # 0x1a4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1a4>
		00000000000001a0:  R_X86_64_PC32	.LCPI1215_0-0x4
     1a4:      	movapd	%xmm8, %xmm9
     1a9:      	jne	0x1ad <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1ad>
     1ab:      	jnp	0x1d6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1d6>
     1ad:      	xorpd	%xmm0, %xmm0
     1b1:      	ucomisd	%xmm0, %xmm5
     1b5:      	movw	$0x2, %ax
     1b9:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     1bf:      	movsd	(%rip), %xmm0           # 0x1c7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1c7>
		00000000000001c3:  R_X86_64_PC32	.LCPI1215_2-0x4
     1c7:      	ucomisd	%xmm5, %xmm0
     1cb:      	movapd	%xmm5, %xmm9
     1d0:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     1d6:      	ucomisd	(%rip), %xmm6           # 0x1de <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1de>
		00000000000001da:  R_X86_64_PC32	.LCPI1215_0-0x4
     1de:      	jne	0x1e2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1e2>
     1e0:      	jnp	0x20b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x20b>
     1e2:      	xorpd	%xmm0, %xmm0
     1e6:      	ucomisd	%xmm0, %xmm6
     1ea:      	movw	$0x2, %ax
     1ee:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     1f4:      	movsd	(%rip), %xmm0           # 0x1fc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x1fc>
		00000000000001f8:  R_X86_64_PC32	.LCPI1215_2-0x4
     1fc:      	ucomisd	%xmm6, %xmm0
     200:      	movapd	%xmm6, %xmm8
     205:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     20b:      	ucomisd	(%rip), %xmm7           # 0x213 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x213>
		000000000000020f:  R_X86_64_PC32	.LCPI1215_0-0x4
     213:      	jne	0x221 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x221>
     215:      	jp	0x221 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x221>
     217:      	movsd	(%rip), %xmm7           # 0x21f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x21f>
		000000000000021b:  R_X86_64_PC32	.LCPI1215_4-0x4
     21f:      	jmp	0x245 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x245>
     221:      	xorpd	%xmm0, %xmm0
     225:      	ucomisd	%xmm0, %xmm7
     229:      	movw	$0x2, %ax
     22d:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     233:      	movsd	(%rip), %xmm0           # 0x23b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x23b>
		0000000000000237:  R_X86_64_PC32	.LCPI1215_2-0x4
     23b:      	ucomisd	%xmm7, %xmm0
     23f:      	jb	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     245:      	ucomisd	(%rip), %xmm2           # 0x24d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x24d>
		0000000000000249:  R_X86_64_PC32	.LCPI1215_0-0x4
     24d:      	movapd	(%rip), %xmm0           # 0x255 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x255>
		0000000000000251:  R_X86_64_PC32	.LCPI1215_1-0x4
     255:      	andpd	%xmm2, %xmm0
     259:      	movq	$-0x1, %rax
     260:      	jne	0x268 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x268>
     262:      	jnp	0x2fa <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x2fa>
     268:      	movsd	(%rip), %xmm1           # 0x270 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x270>
		000000000000026c:  R_X86_64_PC32	.LCPI1215_2-0x4
     270:      	ucomisd	%xmm0, %xmm1
     274:      	jae	0x2fa <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x2fa>
     27a:      	cmpq	%rax, %rsi
     27d:      	cmovaq	%rsi, %rax
     281:      	cmpq	%rdx, %rax
     284:      	seta	%r10b
     288:      	cmpq	%r8, %rdx
     28b:      	setb	%r11b
     28f:      	orb	%r10b, %r11b
     292:      	je	0xa46 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa46>
     298:      	cmpq	%rax, %rdx
     29b:      	setb	%r10b
     29f:      	cmpq	%r14, %rdx
     2a2:      	setb	%r11b
     2a6:      	orb	%r10b, %r11b
     2a9:      	je	0xa5f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa5f>
     2af:      	movq	%rdx, %r10
     2b2:      	subq	%rax, %r10
     2b5:      	setb	%al
     2b8:      	cmpq	%rbx, %r10
     2bb:      	setb	%r10b
     2bf:      	orb	%al, %r10b
     2c2:      	je	0xa78 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa78>
     2c8:      	movq	$0x0, 0x88(%rsp)
     2d4:      	cmpq	$0x1, %rsi
     2d8:      	adcq	$0x0, %rsi
     2dc:      	cmpq	%rdx, %rsi
     2df:      	jbe	0x447 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x447>
     2e5:      	movq	$0x0, (%rbp)
     2ed:      	movq	$0x0, (%r12)
     2f5:      	jmp	0x974 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x974>
     2fa:      	ucomisd	(%rip), %xmm12          # 0x303 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x303>
		00000000000002ff:  R_X86_64_PC32	.LCPI1215_0-0x4
     303:      	jne	0x307 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x307>
     305:      	jnp	0x329 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x329>
     307:      	xorpd	%xmm1, %xmm1
     30b:      	ucomisd	%xmm1, %xmm12
     310:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     316:      	movsd	(%rip), %xmm1           # 0x31e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x31e>
		000000000000031a:  R_X86_64_PC32	.LCPI1215_2-0x4
     31e:      	ucomisd	%xmm12, %xmm1
     323:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     329:      	ucomisd	(%rip), %xmm10          # 0x332 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x332>
		000000000000032e:  R_X86_64_PC32	.LCPI1215_0-0x4
     332:      	jne	0x336 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x336>
     334:      	jnp	0x358 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x358>
     336:      	xorpd	%xmm1, %xmm1
     33a:      	ucomisd	%xmm1, %xmm10
     33f:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     345:      	movsd	(%rip), %xmm1           # 0x34d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x34d>
		0000000000000349:  R_X86_64_PC32	.LCPI1215_2-0x4
     34d:      	ucomisd	%xmm10, %xmm1
     352:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     358:      	ucomisd	(%rip), %xmm11          # 0x361 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x361>
		000000000000035d:  R_X86_64_PC32	.LCPI1215_0-0x4
     361:      	jne	0x365 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x365>
     363:      	jnp	0x387 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x387>
     365:      	xorpd	%xmm1, %xmm1
     369:      	ucomisd	%xmm1, %xmm11
     36e:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     374:      	movsd	(%rip), %xmm1           # 0x37c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x37c>
		0000000000000378:  R_X86_64_PC32	.LCPI1215_2-0x4
     37c:      	ucomisd	%xmm11, %xmm1
     381:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     387:      	ucomisd	(%rip), %xmm4           # 0x38f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x38f>
		000000000000038b:  R_X86_64_PC32	.LCPI1215_0-0x4
     38f:      	jne	0x393 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x393>
     391:      	jnp	0x3b3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3b3>
     393:      	xorpd	%xmm1, %xmm1
     397:      	ucomisd	%xmm1, %xmm4
     39b:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3a1:      	movsd	(%rip), %xmm1           # 0x3a9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3a9>
		00000000000003a5:  R_X86_64_PC32	.LCPI1215_2-0x4
     3a9:      	ucomisd	%xmm4, %xmm1
     3ad:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3b3:      	ucomisd	(%rip), %xmm9           # 0x3bc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3bc>
		00000000000003b8:  R_X86_64_PC32	.LCPI1215_0-0x4
     3bc:      	jne	0x3c0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3c0>
     3be:      	jnp	0x3e2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3e2>
     3c0:      	xorpd	%xmm1, %xmm1
     3c4:      	ucomisd	%xmm1, %xmm9
     3c9:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3cf:      	movsd	(%rip), %xmm1           # 0x3d7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3d7>
		00000000000003d3:  R_X86_64_PC32	.LCPI1215_2-0x4
     3d7:      	ucomisd	%xmm9, %xmm1
     3dc:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3e2:      	ucomisd	(%rip), %xmm8           # 0x3eb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3eb>
		00000000000003e7:  R_X86_64_PC32	.LCPI1215_0-0x4
     3eb:      	jne	0x3ef <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3ef>
     3ed:      	jnp	0x411 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x411>
     3ef:      	xorpd	%xmm1, %xmm1
     3f3:      	ucomisd	%xmm1, %xmm8
     3f8:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3fe:      	movsd	(%rip), %xmm1           # 0x406 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x406>
		0000000000000402:  R_X86_64_PC32	.LCPI1215_2-0x4
     406:      	ucomisd	%xmm8, %xmm1
     40b:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     411:      	ucomisd	(%rip), %xmm7           # 0x419 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x419>
		0000000000000415:  R_X86_64_PC32	.LCPI1215_0-0x4
     419:      	jne	0x41d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x41d>
     41b:      	jnp	0x43d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x43d>
     41d:      	xorpd	%xmm1, %xmm1
     421:      	ucomisd	%xmm1, %xmm7
     425:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     42b:      	movsd	(%rip), %xmm1           # 0x433 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x433>
		000000000000042f:  R_X86_64_PC32	.LCPI1215_2-0x4
     433:      	ucomisd	%xmm7, %xmm1
     437:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     43d:      	movl	$0x1, %eax
     442:      	jmp	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     447:      	leaq	0x1(%rdx), %r15
     44b:      	cmpq	%r8, %rdx
     44e:      	jae	0xa91 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa91>
     454:      	cmpq	%r14, %rdx
     457:      	jae	0xaa4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaa4>
     45d:      	xorpd	%xmm1, %xmm1
     461:      	ucomisd	%xmm1, %xmm2
     465:      	movsd	%xmm7, 0x18(%rsp)
     46b:      	movsd	%xmm4, 0x10(%rsp)
     471:      	movsd	%xmm12, 0x8(%rsp)
     478:      	movq	%r12, 0x60(%rsp)
     47d:      	jne	0x50e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x50e>
     483:      	jp	0x50e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x50e>
     489:      	movsd	%xmm9, 0x48(%rsp)
     490:      	movsd	%xmm8, 0x50(%rsp)
     497:      	movsd	%xmm10, 0x30(%rsp)
     49e:      	movsd	%xmm11, 0x58(%rsp)
     4a5:      	movq	%rdx, 0x28(%rsp)
     4aa:      	subq	$0x8, %rsp
     4ae:      	leaq	0x90(%rsp), %r10
     4b6:      	leaq	0xb8(%rsp), %rax
     4be:      	movq	%rdi, %rdx
     4c1:      	movq	%rax, %rdi
     4c4:      	movq	%rsi, %rax
     4c7:      	movq	%rdx, %rsi
     4ca:      	movq	%rax, %rdx
     4cd:      	movq	%rcx, %r8
     4d0:      	movq	%rax, %r14
     4d3:      	movq	%rax, %rcx
     4d6:      	movq	%r8, 0x28(%rsp)
     4db:      	movq	%r9, %rax
     4de:      	movq	%r15, %r9
     4e1:      	pushq	$0x1
     4e3:      	pushq	%r10
     4e5:      	pushq	$0x1
     4e7:      	pushq	%r15
     4e9:      	movq	%rax, %r12
     4ec:      	pushq	%rax
     4ed:      	callq	*(%rip)                 # 0x4f3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x4f3>
		00000000000004ef:  R_X86_64_GOTPCREL	_ZN6ta_lib7ta_func8minus_dm46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$8minus_dm17h23b8d971195755a4E-0x4
     4f3:      	addq	$0x30, %rsp
     4f7:      	testb	$0x1, 0xb0(%rsp)
     4ff:      	je	0x53b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x53b>
     501:      	movzwl	0xb2(%rsp), %eax
     509:      	jmp	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     50e:      	movq	%rsi, (%rbp)
     512:      	leaq	-0x1(%rsi), %rdi
     516:      	cmpq	%rdx, %rdi
     519:      	ja	0xb03 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb03>
     51f:      	xorl	%eax, %eax
     521:      	ucomisd	%xmm1, %xmm2
     525:      	seta	%al
     528:      	movq	%r9, %rdi
     52b:      	cmovaq	%rcx, %rdi
     52f:      	ja	0x5ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5ba>
     535:      	movapd	%xmm0, %xmm2
     539:      	jmp	0x5ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5ba>
     53b:      	movsd	0x88(%rsp), %xmm0
     544:      	movq	%r14, (%rbp)
     548:      	leaq	-0x1(%r14), %rdi
     54c:      	movq	0x28(%rsp), %rdx
     551:      	cmpq	%rdx, %rdi
     554:      	movq	0x20(%rsp), %rcx
     559:      	movsd	0x18(%rsp), %xmm7
     55f:      	movsd	0x10(%rsp), %xmm4
     565:      	movsd	0x8(%rsp), %xmm12
     56c:      	movsd	0x58(%rsp), %xmm11
     573:      	movsd	0x30(%rsp), %xmm10
     57a:      	movsd	0x50(%rsp), %xmm8
     581:      	movsd	0x48(%rsp), %xmm9
     588:      	ja	0xb03 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb03>
     58e:      	movq	%r14, %rsi
     591:      	movq	%r12, %r9
     594:      	xorpd	%xmm1, %xmm1
     598:      	ucomisd	%xmm1, %xmm0
     59c:      	ja	0x5af <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5af>
     59e:      	movsd	-0x8(%r9,%rsi,8), %xmm2
     5a5:      	movl	$0x1, %eax
     5aa:      	movq	%rcx, %rdi
     5ad:      	jmp	0x5ba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5ba>
     5af:      	movsd	-0x8(%rcx,%rsi,8), %xmm2
     5b5:      	xorl	%eax, %eax
     5b7:      	movq	%r9, %rdi
     5ba:      	movapd	%xmm4, %xmm0
     5be:      	minsd	%xmm10, %xmm0
     5c3:      	movapd	%xmm4, %xmm1
     5c7:      	minsd	%xmm11, %xmm1
     5cc:      	movsd	%xmm1, 0x98(%rsp)
     5d5:      	movapd	%xmm7, %xmm1
     5d9:      	minsd	%xmm9, %xmm1
     5de:      	movapd	%xmm7, %xmm5
     5e2:      	minsd	%xmm8, %xmm5
     5e7:      	movsd	%xmm5, 0x90(%rsp)
     5f0:      	movsd	(%rcx,%rsi,8), %xmm5
     5f5:      	movsd	(%r9,%rsi,8), %xmm6
     5fb:      	movsd	(%rdi,%rsi,8), %xmm9
     601:      	leaq	-0x1(%rsi), %rdi
     605:      	movq	%rdi, 0x58(%rsp)
     60a:      	leaq	(%rcx,%rsi,8), %rbp
     60e:      	leaq	(%r9,%rsi,8), %r12
     612:      	xorl	%r14d, %r14d
     615:      	xorpd	%xmm8, %xmm8
     61a:      	cmpneqsd	%xmm12, %xmm8
     620:      	movapd	%xmm8, 0xa0(%rsp)
     62a:      	movsd	%xmm0, 0x70(%rsp)
     630:      	movsd	%xmm0, 0x40(%rsp)
     636:      	movsd	%xmm1, 0x68(%rsp)
     63c:      	movsd	%xmm1, 0x38(%rsp)
     642:      	jmp	0x67e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x67e>
     644:      	movq	%r15, %rdx
     647:      	movsd	0x18(%rsp), %xmm7
     64d:      	movsd	0x10(%rsp), %xmm4
     653:      	movsd	0x8(%rsp), %xmm12
     65a:      	movsd	0x28(%rsp), %xmm5
     660:      	movsd	0x30(%rsp), %xmm9
     667:      	movq	0x58(%rsp), %rcx
     66c:      	addq	%r14, %rcx
     66f:      	incq	%rcx
     672:      	incq	%r14
     675:      	cmpq	%rdx, %rcx
     678:      	jae	0x96c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x96c>
     67e:      	movapd	%xmm6, %xmm3
     682:      	movapd	%xmm5, %xmm1
     686:      	movsd	(%r12,%r14,8), %xmm6
     68c:      	movsd	(%rbp,%r14,8), %xmm5
     693:      	cmpq	$0x1, %rax
     697:      	movsd	%xmm5, 0x28(%rsp)
     69d:      	movsd	%xmm6, 0x20(%rsp)
     6a3:      	jne	0x700 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x700>
     6a5:      	ucomisd	%xmm6, %xmm2
     6a9:      	jae	0x766 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x766>
     6af:      	cmpq	%rbx, %r14
     6b2:      	jae	0xaf0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaf0>
     6b8:      	movsd	%xmm2, (%r13,%r14,8)
     6bf:      	ucomisd	%xmm9, %xmm5
     6c4:      	movsd	%xmm3, 0x48(%rsp)
     6ca:      	movq	%rdx, %r15
     6cd:      	jbe	0x8c3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8c3>
     6d3:      	movsd	0x40(%rsp), %xmm0
     6d9:      	addsd	0x98(%rsp), %xmm0
     6e2:      	ucomisd	%xmm4, %xmm0
     6e6:      	movapd	%xmm5, %xmm9
     6eb:      	jbe	0x8c9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8c9>
     6f1:      	movapd	%xmm5, %xmm9
     6f6:      	movapd	%xmm4, %xmm0
     6fa:      	jmp	0x8c9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8c9>
     6ff:      	nop
     700:      	ucomisd	%xmm2, %xmm5
     704:      	jae	0x80e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x80e>
     70a:      	cmpq	%rbx, %r14
     70d:      	jae	0xaca <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaca>
     713:      	movapd	%xmm2, %xmm0
     717:      	xorpd	(%rip), %xmm0           # 0x71f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x71f>
		000000000000071b:  R_X86_64_PC32	.LCPI1215_5-0x4
     71f:      	movlpd	%xmm0, (%r13,%r14,8)
     726:      	ucomisd	%xmm6, %xmm9
     72b:      	movsd	%xmm1, 0x50(%rsp)
     731:      	movq	%rdx, %r15
     734:      	jbe	0x90d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x90d>
     73a:      	movsd	0x38(%rsp), %xmm0
     740:      	addsd	0x90(%rsp), %xmm0
     749:      	ucomisd	%xmm7, %xmm0
     74d:      	movapd	%xmm6, %xmm9
     752:      	jbe	0x913 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x913>
     758:      	movapd	%xmm6, %xmm9
     75d:      	movapd	%xmm7, %xmm0
     761:      	jmp	0x913 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x913>
     766:      	cmpq	%rbx, %r14
     769:      	movsd	0x68(%rsp), %xmm0
     76f:      	jae	0xadd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xadd>
     775:      	movq	%rdx, %r15
     778:      	movapd	%xmm1, %xmm2
     77c:      	maxsd	%xmm9, %xmm2
     781:      	movsd	%xmm1, 0x50(%rsp)
     787:      	movapd	%xmm5, %xmm1
     78b:      	maxsd	%xmm2, %xmm1
     78f:      	movapd	%xmm12, %xmm2
     794:      	mulsd	%xmm1, %xmm2
     798:      	addsd	%xmm1, %xmm2
     79c:      	movapd	0xa0(%rsp), %xmm4
     7a5:      	movapd	%xmm4, %xmm3
     7a9:      	andnpd	%xmm1, %xmm3
     7ad:      	andpd	%xmm4, %xmm2
     7b1:      	orpd	%xmm3, %xmm2
     7b5:      	movapd	%xmm2, %xmm1
     7b9:      	xorpd	(%rip), %xmm1           # 0x7c1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x7c1>
		00000000000007bd:  R_X86_64_PC32	.LCPI1215_5-0x4
     7c1:      	movlpd	%xmm1, (%r13,%r14,8)
     7c8:      	movapd	%xmm6, %xmm1
     7cc:      	subsd	%xmm2, %xmm1
     7d0:      	callq	*(%rip)                 # 0x7d6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x7d6>
		00000000000007d2:  R_X86_64_GOTPCREL	fma-0x4
     7d6:      	movsd	0x50(%rsp), %xmm2
     7dc:      	movsd	0x28(%rsp), %xmm5
     7e2:      	maxsd	%xmm0, %xmm2
     7e6:      	ucomisd	%xmm2, %xmm5
     7ea:      	jbe	0x7f0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x7f0>
     7ec:      	movapd	%xmm5, %xmm2
     7f0:      	movsd	0x20(%rsp), %xmm6
     7f6:      	movapd	%xmm6, %xmm9
     7fb:      	movsd	0x68(%rsp), %xmm0
     801:      	movsd	%xmm0, 0x38(%rsp)
     807:      	xorl	%eax, %eax
     809:      	jmp	0x8a8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8a8>
     80e:      	cmpq	%rbx, %r14
     811:      	movsd	0x70(%rsp), %xmm0
     817:      	jae	0xab7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xab7>
     81d:      	movq	%rdx, %r15
     820:      	movapd	%xmm3, %xmm1
     824:      	minsd	%xmm9, %xmm1
     829:      	movapd	%xmm6, %xmm2
     82d:      	minsd	%xmm1, %xmm2
     831:      	movsd	%xmm3, 0x48(%rsp)
     837:      	movapd	%xmm12, %xmm3
     83c:      	mulsd	%xmm2, %xmm3
     840:      	movapd	0xa0(%rsp), %xmm4
     849:      	movapd	%xmm4, %xmm1
     84d:      	andnpd	%xmm2, %xmm1
     851:      	subsd	%xmm3, %xmm2
     855:      	andpd	%xmm4, %xmm2
     859:      	orpd	%xmm1, %xmm2
     85d:      	movlpd	%xmm2, (%r13,%r14,8)
     864:      	movapd	%xmm5, %xmm1
     868:      	subsd	%xmm2, %xmm1
     86c:      	callq	*(%rip)                 # 0x872 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x872>
		000000000000086e:  R_X86_64_GOTPCREL	fma-0x4
     872:      	movsd	0x48(%rsp), %xmm2
     878:      	movsd	0x20(%rsp), %xmm6
     87e:      	minsd	%xmm0, %xmm2
     882:      	movl	$0x1, %eax
     887:      	ucomisd	%xmm6, %xmm2
     88b:      	jbe	0x891 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x891>
     88d:      	movapd	%xmm6, %xmm2
     891:      	movsd	0x28(%rsp), %xmm5
     897:      	movapd	%xmm5, %xmm9
     89c:      	movsd	0x70(%rsp), %xmm0
     8a2:      	movsd	%xmm0, 0x40(%rsp)
     8a8:      	movq	%r15, %rdx
     8ab:      	movsd	0x18(%rsp), %xmm7
     8b1:      	movsd	0x10(%rsp), %xmm4
     8b7:      	movsd	0x8(%rsp), %xmm12
     8be:      	jmp	0x667 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x667>
     8c3:      	movsd	0x40(%rsp), %xmm0
     8c9:      	movsd	%xmm9, 0x30(%rsp)
     8d0:      	movapd	%xmm9, %xmm1
     8d5:      	subsd	%xmm2, %xmm1
     8d9:      	movsd	%xmm0, 0x40(%rsp)
     8df:      	callq	*(%rip)                 # 0x8e5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8e5>
		00000000000008e1:  R_X86_64_GOTPCREL	fma-0x4
     8e5:      	movsd	0x48(%rsp), %xmm2
     8eb:      	minsd	%xmm0, %xmm2
     8ef:      	movl	$0x1, %eax
     8f4:      	movsd	0x20(%rsp), %xmm6
     8fa:      	ucomisd	%xmm6, %xmm2
     8fe:      	jbe	0x644 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x644>
     904:      	movapd	%xmm6, %xmm2
     908:      	jmp	0x644 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x644>
     90d:      	movsd	0x38(%rsp), %xmm0
     913:      	movsd	%xmm9, 0x30(%rsp)
     91a:      	movapd	%xmm9, %xmm1
     91f:      	subsd	%xmm2, %xmm1
     923:      	movsd	%xmm0, 0x38(%rsp)
     929:      	callq	*(%rip)                 # 0x92f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x92f>
		000000000000092b:  R_X86_64_GOTPCREL	fma-0x4
     92f:      	movsd	0x50(%rsp), %xmm2
     935:      	maxsd	%xmm0, %xmm2
     939:      	movsd	0x28(%rsp), %xmm5
     93f:      	ucomisd	%xmm2, %xmm5
     943:      	jbe	0x949 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x949>
     945:      	movapd	%xmm5, %xmm2
     949:      	xorl	%eax, %eax
     94b:      	movq	%r15, %rdx
     94e:      	movsd	0x18(%rsp), %xmm7
     954:      	movsd	0x10(%rsp), %xmm4
     95a:      	movsd	0x8(%rsp), %xmm12
     961:      	movsd	0x20(%rsp), %xmm6
     967:      	jmp	0x660 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x660>
     96c:      	movq	0x60(%rsp), %rax
     971:      	movq	%r14, (%rax)
     974:      	xorl	%eax, %eax
     976:      	jmp	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     97b:      	movq	%rdx, 0x28(%rsp)
     980:      	movq	%r9, %r15
     983:      	movq	%rcx, 0x20(%rsp)
     988:      	movq	%r12, 0x60(%rsp)
     98d:      	movq	%rsi, %r12
     990:      	movq	%rdi, 0x8(%rsp)
     995:      	movq	%r8, 0x58(%rsp)
     99a:      	movsd	%xmm7, 0x18(%rsp)
     9a0:      	movsd	%xmm4, 0x10(%rsp)
     9a6:      	movsd	%xmm6, 0x30(%rsp)
     9ac:      	movsd	%xmm5, 0x50(%rsp)
     9b2:      	movsd	%xmm3, 0x48(%rsp)
     9b8:      	movsd	%xmm8, 0x40(%rsp)
     9bf:      	movsd	%xmm1, 0x38(%rsp)
     9c5:      	movaps	%xmm0, 0x70(%rsp)
     9ca:      	callq	*(%rip)                 # 0x9d0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x9d0>
		00000000000009cc:  R_X86_64_GOTPCREL	_ZN10std_detect6detect5cache21detect_and_initialize17hd21b90854bd2a812E-0x4
     9d0:      	movapd	0x70(%rsp), %xmm0
     9d6:      	movsd	0x38(%rsp), %xmm1
     9dc:      	movsd	0x40(%rsp), %xmm8
     9e3:      	movsd	0x48(%rsp), %xmm3
     9e9:      	movsd	0x50(%rsp), %xmm5
     9ef:      	movsd	0x30(%rsp), %xmm6
     9f5:      	movsd	0x10(%rsp), %xmm4
     9fb:      	movsd	0x18(%rsp), %xmm7
     a01:      	movq	0x58(%rsp), %r8
     a06:      	movq	0x8(%rsp), %rdi
     a0b:      	movq	%r12, %rsi
     a0e:      	movq	0x60(%rsp), %r12
     a13:      	movq	0x20(%rsp), %rcx
     a18:      	movq	%r15, %r9
     a1b:      	movq	0x28(%rsp), %rdx
     a20:      	btq	$0x36, %rax
     a25:      	jae	0x5c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5c>
     a2b:      	movapd	%xmm8, %xmm2
     a30:      	addq	$0xc8, %rsp
     a37:      	popq	%rbx
     a38:      	popq	%r12
     a3a:      	popq	%r13
     a3c:      	popq	%r14
     a3e:      	popq	%r15
     a40:      	popq	%rbp
     a41:      	jmp	0xa46 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa46>
		0000000000000a42:  R_X86_64_PLT32	.text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E-0x4
     a46:      	leaq	(%rip), %rdi            # 0xa4d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa4d>
		0000000000000a49:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.13.llvm.15298552028749941447-0x4
     a4d:      	leaq	(%rip), %rdx            # 0xa54 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa54>
		0000000000000a50:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8049-0x4
     a54:      	movl	$0x40, %esi
     a59:      	callq	*(%rip)                 # 0xa5f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa5f>
		0000000000000a5b:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     a5f:      	leaq	(%rip), %rdi            # 0xa66 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa66>
		0000000000000a62:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.16.llvm.15298552028749941447-0x4
     a66:      	leaq	(%rip), %rdx            # 0xa6d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa6d>
		0000000000000a69:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8050-0x4
     a6d:      	movl	$0x3f, %esi
     a72:      	callq	*(%rip)                 # 0xa78 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa78>
		0000000000000a74:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     a78:      	leaq	(%rip), %rdi            # 0xa7f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa7f>
		0000000000000a7b:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.18.llvm.15298552028749941447-0x4
     a7f:      	leaq	(%rip), %rdx            # 0xa86 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa86>
		0000000000000a82:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8051-0x4
     a86:      	movl	$0x50, %esi
     a8b:      	callq	*(%rip)                 # 0xa91 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa91>
		0000000000000a8d:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     a91:      	leaq	(%rip), %rdx            # 0xa98 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa98>
		0000000000000a94:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8052-0x4
     a98:      	movq	%r15, %rdi
     a9b:      	movq	%r8, %rsi
     a9e:      	callq	*(%rip)                 # 0xaa4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaa4>
		0000000000000aa0:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     aa4:      	leaq	(%rip), %rdx            # 0xaab <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaab>
		0000000000000aa7:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8053-0x4
     aab:      	movq	%r15, %rdi
     aae:      	movq	%r14, %rsi
     ab1:      	callq	*(%rip)                 # 0xab7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xab7>
		0000000000000ab3:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     ab7:      	leaq	(%rip), %rdx            # 0xabe <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xabe>
		0000000000000aba:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8058-0x4
     abe:      	movq	%r14, %rdi
     ac1:      	movq	%rbx, %rsi
     ac4:      	callq	*(%rip)                 # 0xaca <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaca>
		0000000000000ac6:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     aca:      	leaq	(%rip), %rdx            # 0xad1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xad1>
		0000000000000acd:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8057-0x4
     ad1:      	movq	%r14, %rdi
     ad4:      	movq	%rbx, %rsi
     ad7:      	callq	*(%rip)                 # 0xadd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xadd>
		0000000000000ad9:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     add:      	leaq	(%rip), %rdx            # 0xae4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xae4>
		0000000000000ae0:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8056-0x4
     ae4:      	movq	%r14, %rdi
     ae7:      	movq	%rbx, %rsi
     aea:      	callq	*(%rip)                 # 0xaf0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaf0>
		0000000000000aec:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     af0:      	leaq	(%rip), %rdx            # 0xaf7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xaf7>
		0000000000000af3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8055-0x4
     af7:      	movq	%r14, %rdi
     afa:      	movq	%rbx, %rsi
     afd:      	callq	*(%rip)                 # 0xb03 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb03>
		0000000000000aff:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     b03:      	leaq	(%rip), %rdx            # 0xb0a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb0a>
		0000000000000b06:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8054-0x4
     b0a:      	movq	%r15, %rsi
     b0d:      	callq	*(%rip)                 # 0xb13 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb13>
		0000000000000b0f:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
