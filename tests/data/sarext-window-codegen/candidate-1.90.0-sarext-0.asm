
/tmp/polars-recovery/sarext-window-evidence/candidate-static-1.90.0/library-objects/ta_lib-a99de56cdf066125.ta_lib.4f1d99721d8d97c2-cgu.00.rcgu.o:	file format elf64-x86-64

Disassembly of section .text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E:

0000000000000000 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E>:
       0:      	pushq	%rbp
       1:      	pushq	%r15
       3:      	pushq	%r14
       5:      	pushq	%r13
       7:      	pushq	%r12
       9:      	pushq	%rbx
       a:      	subq	$0xd8, %rsp
      11:      	movapd	%xmm2, %xmm8
      16:      	movq	0x130(%rsp), %rbx
      1e:      	movq	0x128(%rsp), %r13
      26:      	movq	0x120(%rsp), %r14
      2e:      	movq	0x118(%rsp), %rbp
      36:      	movq	0x110(%rsp), %r15
      3e:      	movq	(%rip), %rax            # 0x45 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x45>
		0000000000000041:  R_X86_64_GOTPCREL	_ZN10std_detect6detect5cache5CACHE17hb6755393302ff344E-0x4
      45:      	movq	(%rax), %rax
      48:      	testq	%rax, %rax
      4b:      	je	0xcf2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xcf2>
      51:      	btq	$0x36, %rax
      56:      	jb	0xda8 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xda8>
      5c:      	movw	$0xd, %ax
      60:      	cmpq	%rsi, %rdx
      63:      	jae	0x77 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x77>
      65:      	addq	$0xd8, %rsp
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
     262:      	jnp	0x2fc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x2fc>
     268:      	movsd	(%rip), %xmm1           # 0x270 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x270>
		000000000000026c:  R_X86_64_PC32	.LCPI1215_2-0x4
     270:      	ucomisd	%xmm0, %xmm1
     274:      	jae	0x2fc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x2fc>
     27a:      	cmpq	%rax, %rsi
     27d:      	cmovaq	%rsi, %rax
     281:      	cmpq	%rdx, %rax
     284:      	seta	%r10b
     288:      	cmpq	%r8, %rdx
     28b:      	setb	%r11b
     28f:      	orb	%r10b, %r11b
     292:      	je	0xdc3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdc3>
     298:      	cmpq	%rax, %rdx
     29b:      	setb	%r10b
     29f:      	cmpq	%r15, %rdx
     2a2:      	setb	%r11b
     2a6:      	orb	%r10b, %r11b
     2a9:      	je	0xddc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xddc>
     2af:      	movq	%rdx, %r10
     2b2:      	subq	%rax, %r10
     2b5:      	setb	%al
     2b8:      	cmpq	%rbx, %r10
     2bb:      	setb	%r10b
     2bf:      	orb	%al, %r10b
     2c2:      	je	0xdf5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdf5>
     2c8:      	movq	$0x0, 0xb8(%rsp)
     2d4:      	cmpq	$0x1, %rsi
     2d8:      	adcq	$0x0, %rsi
     2dc:      	movq	%rdx, %r12
     2df:      	subq	%rsi, %r12
     2e2:      	jae	0x449 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x449>
     2e8:      	movq	$0x0, (%rbp)
     2f0:      	movq	$0x0, (%r14)
     2f7:      	jmp	0xceb <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xceb>
     2fc:      	ucomisd	(%rip), %xmm12          # 0x305 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x305>
		0000000000000301:  R_X86_64_PC32	.LCPI1215_0-0x4
     305:      	jne	0x309 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x309>
     307:      	jnp	0x32b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x32b>
     309:      	xorpd	%xmm1, %xmm1
     30d:      	ucomisd	%xmm1, %xmm12
     312:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     318:      	movsd	(%rip), %xmm1           # 0x320 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x320>
		000000000000031c:  R_X86_64_PC32	.LCPI1215_2-0x4
     320:      	ucomisd	%xmm12, %xmm1
     325:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     32b:      	ucomisd	(%rip), %xmm10          # 0x334 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x334>
		0000000000000330:  R_X86_64_PC32	.LCPI1215_0-0x4
     334:      	jne	0x338 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x338>
     336:      	jnp	0x35a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x35a>
     338:      	xorpd	%xmm1, %xmm1
     33c:      	ucomisd	%xmm1, %xmm10
     341:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     347:      	movsd	(%rip), %xmm1           # 0x34f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x34f>
		000000000000034b:  R_X86_64_PC32	.LCPI1215_2-0x4
     34f:      	ucomisd	%xmm10, %xmm1
     354:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     35a:      	ucomisd	(%rip), %xmm11          # 0x363 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x363>
		000000000000035f:  R_X86_64_PC32	.LCPI1215_0-0x4
     363:      	jne	0x367 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x367>
     365:      	jnp	0x389 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x389>
     367:      	xorpd	%xmm1, %xmm1
     36b:      	ucomisd	%xmm1, %xmm11
     370:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     376:      	movsd	(%rip), %xmm1           # 0x37e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x37e>
		000000000000037a:  R_X86_64_PC32	.LCPI1215_2-0x4
     37e:      	ucomisd	%xmm11, %xmm1
     383:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     389:      	ucomisd	(%rip), %xmm4           # 0x391 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x391>
		000000000000038d:  R_X86_64_PC32	.LCPI1215_0-0x4
     391:      	jne	0x395 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x395>
     393:      	jnp	0x3b5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3b5>
     395:      	xorpd	%xmm1, %xmm1
     399:      	ucomisd	%xmm1, %xmm4
     39d:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3a3:      	movsd	(%rip), %xmm1           # 0x3ab <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3ab>
		00000000000003a7:  R_X86_64_PC32	.LCPI1215_2-0x4
     3ab:      	ucomisd	%xmm4, %xmm1
     3af:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3b5:      	ucomisd	(%rip), %xmm9           # 0x3be <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3be>
		00000000000003ba:  R_X86_64_PC32	.LCPI1215_0-0x4
     3be:      	jne	0x3c2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3c2>
     3c0:      	jnp	0x3e4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3e4>
     3c2:      	xorpd	%xmm1, %xmm1
     3c6:      	ucomisd	%xmm1, %xmm9
     3cb:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3d1:      	movsd	(%rip), %xmm1           # 0x3d9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3d9>
		00000000000003d5:  R_X86_64_PC32	.LCPI1215_2-0x4
     3d9:      	ucomisd	%xmm9, %xmm1
     3de:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     3e4:      	ucomisd	(%rip), %xmm8           # 0x3ed <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3ed>
		00000000000003e9:  R_X86_64_PC32	.LCPI1215_0-0x4
     3ed:      	jne	0x3f1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x3f1>
     3ef:      	jnp	0x413 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x413>
     3f1:      	xorpd	%xmm1, %xmm1
     3f5:      	ucomisd	%xmm1, %xmm8
     3fa:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     400:      	movsd	(%rip), %xmm1           # 0x408 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x408>
		0000000000000404:  R_X86_64_PC32	.LCPI1215_2-0x4
     408:      	ucomisd	%xmm8, %xmm1
     40d:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     413:      	ucomisd	(%rip), %xmm7           # 0x41b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x41b>
		0000000000000417:  R_X86_64_PC32	.LCPI1215_0-0x4
     41b:      	jne	0x41f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x41f>
     41d:      	jnp	0x43f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x43f>
     41f:      	xorpd	%xmm1, %xmm1
     423:      	ucomisd	%xmm1, %xmm7
     427:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     42d:      	movsd	(%rip), %xmm1           # 0x435 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x435>
		0000000000000431:  R_X86_64_PC32	.LCPI1215_2-0x4
     435:      	ucomisd	%xmm7, %xmm1
     439:      	jb	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     43f:      	movl	$0x1, %eax
     444:      	jmp	0x27a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x27a>
     449:      	movq	%r14, 0x88(%rsp)
     451:      	leaq	0x1(%rdx), %r14
     455:      	cmpq	%r8, %rdx
     458:      	jae	0xe0e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe0e>
     45e:      	cmpq	%r15, %rdx
     461:      	jae	0xe21 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe21>
     467:      	xorpd	%xmm1, %xmm1
     46b:      	ucomisd	%xmm1, %xmm2
     46f:      	movsd	%xmm7, 0x18(%rsp)
     475:      	movsd	%xmm4, 0x10(%rsp)
     47b:      	movsd	%xmm12, 0x8(%rsp)
     482:      	jne	0x518 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x518>
     488:      	jp	0x518 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x518>
     48e:      	movsd	%xmm9, 0x40(%rsp)
     495:      	movsd	%xmm8, 0x48(%rsp)
     49c:      	movsd	%xmm10, 0x50(%rsp)
     4a3:      	movsd	%xmm11, 0x30(%rsp)
     4aa:      	movq	%rdx, 0x20(%rsp)
     4af:      	subq	$0x8, %rsp
     4b3:      	leaq	0xc0(%rsp), %r10
     4bb:      	leaq	0xc8(%rsp), %rax
     4c3:      	movq	%rdi, %rdx
     4c6:      	movq	%rax, %rdi
     4c9:      	movq	%rsi, %rax
     4cc:      	movq	%rdx, %rsi
     4cf:      	movq	%rax, %rdx
     4d2:      	movq	%rax, 0x30(%rsp)
     4d7:      	movq	%rcx, %r8
     4da:      	movq	%rax, %rcx
     4dd:      	movq	%r8, 0x80(%rsp)
     4e5:      	movq	%r9, %rax
     4e8:      	movq	%r14, %r9
     4eb:      	pushq	$0x1
     4ed:      	pushq	%r10
     4ef:      	pushq	$0x1
     4f1:      	pushq	%r14
     4f3:      	movq	%rax, %r15
     4f6:      	pushq	%rax
     4f7:      	callq	*(%rip)                 # 0x4fd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x4fd>
		00000000000004f9:  R_X86_64_GOTPCREL	_ZN6ta_lib7ta_func8minus_dm46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$8minus_dm17h23b8d971195755a4E-0x4
     4fd:      	addq	$0x30, %rsp
     501:      	testb	$0x1, 0xc0(%rsp)
     509:      	je	0x548 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x548>
     50b:      	movzwl	0xc2(%rsp), %eax
     513:      	jmp	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     518:      	movq	%rsi, (%rbp)
     51c:      	leaq	-0x1(%rsi), %rdi
     520:      	cmpq	%rdx, %rdi
     523:      	ja	0xee0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xee0>
     529:      	xorl	%eax, %eax
     52b:      	ucomisd	%xmm1, %xmm2
     52f:      	seta	%al
     532:      	movq	%r9, %rdi
     535:      	cmovaq	%rcx, %rdi
     539:      	ja	0x5c9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5c9>
     53f:      	movapd	%xmm0, %xmm2
     543:      	jmp	0x5c9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5c9>
     548:      	movsd	0xb8(%rsp), %xmm0
     551:      	movq	0x28(%rsp), %rsi
     556:      	movq	%rsi, (%rbp)
     55a:      	leaq	-0x1(%rsi), %rdi
     55e:      	movq	0x20(%rsp), %rdx
     563:      	cmpq	%rdx, %rdi
     566:      	movq	0x78(%rsp), %rcx
     56b:      	movsd	0x18(%rsp), %xmm7
     571:      	movsd	0x10(%rsp), %xmm4
     577:      	movsd	0x8(%rsp), %xmm12
     57e:      	movsd	0x30(%rsp), %xmm11
     585:      	movsd	0x50(%rsp), %xmm10
     58c:      	movsd	0x48(%rsp), %xmm8
     593:      	movsd	0x40(%rsp), %xmm9
     59a:      	ja	0xee0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xee0>
     5a0:      	movq	%r15, %r9
     5a3:      	xorpd	%xmm1, %xmm1
     5a7:      	ucomisd	%xmm1, %xmm0
     5ab:      	ja	0x5be <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5be>
     5ad:      	movsd	-0x8(%r9,%rsi,8), %xmm2
     5b4:      	movl	$0x1, %eax
     5b9:      	movq	%rcx, %rdi
     5bc:      	jmp	0x5c9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5c9>
     5be:      	movsd	-0x8(%rcx,%rsi,8), %xmm2
     5c4:      	xorl	%eax, %eax
     5c6:      	movq	%r9, %rdi
     5c9:      	movapd	%xmm4, %xmm0
     5cd:      	minsd	%xmm10, %xmm0
     5d2:      	movapd	%xmm4, %xmm1
     5d6:      	minsd	%xmm11, %xmm1
     5db:      	movsd	%xmm1, 0xb0(%rsp)
     5e4:      	movapd	%xmm7, %xmm1
     5e8:      	minsd	%xmm9, %xmm1
     5ed:      	movapd	%xmm7, %xmm5
     5f1:      	minsd	%xmm8, %xmm5
     5f6:      	movsd	%xmm5, 0xa8(%rsp)
     5ff:      	movsd	(%rdi,%rsi,8), %xmm8
     605:      	leaq	(%r9,%rsi,8), %rdi
     609:      	movq	%rdi, 0x78(%rsp)
     60e:      	movsd	(%r9,%rsi,8), %xmm5
     614:      	leaq	(%rcx,%rsi,8), %rbp
     618:      	movsd	(%rcx,%rsi,8), %xmm6
     61d:      	cmpq	%rbx, %r12
     620:      	movsd	%xmm0, 0x50(%rsp)
     626:      	movsd	%xmm1, 0x48(%rsp)
     62c:      	jae	0x972 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x972>
     632:      	leaq	0x1(%r12), %rcx
     637:      	movq	%rcx, 0x80(%rsp)
     63f:      	subq	%rsi, %r14
     642:      	xorl	%r15d, %r15d
     645:      	movq	(%rip), %rbx            # 0x64c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x64c>
		0000000000000648:  R_X86_64_GOTPCREL	fma-0x4
     64c:      	xorpd	%xmm9, %xmm9
     651:      	cmpneqsd	%xmm12, %xmm9
     657:      	movapd	%xmm9, 0x90(%rsp)
     661:      	movsd	%xmm0, 0x60(%rsp)
     667:      	movsd	%xmm1, 0x38(%rsp)
     66d:      	jmp	0x6a5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x6a5>
     66f:      	movsd	0x20(%rsp), %xmm6
     675:      	movapd	%xmm6, %xmm8
     67a:      	movsd	0x50(%rsp), %xmm0
     680:      	movsd	%xmm0, 0x60(%rsp)
     686:      	movsd	0x18(%rsp), %xmm7
     68c:      	movsd	0x10(%rsp), %xmm4
     692:      	movsd	0x8(%rsp), %xmm12
     699:      	incq	%r15
     69c:      	cmpq	%r15, %r14
     69f:      	je	0xce0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xce0>
     6a5:      	movapd	%xmm5, %xmm3
     6a9:      	movapd	%xmm6, %xmm1
     6ad:      	movq	0x78(%rsp), %rcx
     6b2:      	movsd	(%rcx,%r15,8), %xmm5
     6b8:      	movsd	(%rbp,%r15,8), %xmm6
     6bf:      	cmpq	$0x1, %rax
     6c3:      	movsd	%xmm5, 0x28(%rsp)
     6c9:      	movsd	%xmm6, 0x20(%rsp)
     6cf:      	jne	0x728 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x728>
     6d1:      	ucomisd	%xmm5, %xmm2
     6d5:      	jae	0x78b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x78b>
     6db:      	cmpq	%r12, %r15
     6de:      	ja	0xeb5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xeb5>
     6e4:      	movsd	%xmm2, (%r13,%r15,8)
     6eb:      	ucomisd	%xmm8, %xmm6
     6f0:      	movsd	%xmm3, 0x58(%rsp)
     6f6:      	jbe	0x8b1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8b1>
     6fc:      	movsd	0x60(%rsp), %xmm0
     702:      	addsd	0xb0(%rsp), %xmm0
     70b:      	ucomisd	%xmm4, %xmm0
     70f:      	movapd	%xmm6, %xmm8
     714:      	jbe	0x8b7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8b7>
     71a:      	movapd	%xmm6, %xmm8
     71f:      	movapd	%xmm4, %xmm0
     723:      	jmp	0x8b7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8b7>
     728:      	ucomisd	%xmm2, %xmm6
     72c:      	jae	0x82c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x82c>
     732:      	cmpq	%r12, %r15
     735:      	ja	0xe5f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe5f>
     73b:      	movapd	%xmm2, %xmm0
     73f:      	xorpd	(%rip), %xmm0           # 0x747 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x747>
		0000000000000743:  R_X86_64_PC32	.LCPI1215_5-0x4
     747:      	movlpd	%xmm0, (%r13,%r15,8)
     74e:      	ucomisd	%xmm5, %xmm8
     753:      	movsd	%xmm1, 0x40(%rsp)
     759:      	jbe	0x913 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x913>
     75f:      	movsd	0x38(%rsp), %xmm0
     765:      	addsd	0xa8(%rsp), %xmm0
     76e:      	ucomisd	%xmm7, %xmm0
     772:      	movapd	%xmm5, %xmm8
     777:      	jbe	0x919 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x919>
     77d:      	movapd	%xmm5, %xmm8
     782:      	movapd	%xmm7, %xmm0
     786:      	jmp	0x919 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x919>
     78b:      	cmpq	%r12, %r15
     78e:      	movsd	0x48(%rsp), %xmm0
     794:      	ja	0xe8a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe8a>
     79a:      	movapd	%xmm1, %xmm2
     79e:      	maxsd	%xmm8, %xmm2
     7a3:      	movsd	%xmm1, 0x40(%rsp)
     7a9:      	movapd	%xmm6, %xmm1
     7ad:      	maxsd	%xmm2, %xmm1
     7b1:      	movapd	%xmm12, %xmm2
     7b6:      	mulsd	%xmm1, %xmm2
     7ba:      	addsd	%xmm1, %xmm2
     7be:      	movapd	0x90(%rsp), %xmm4
     7c7:      	movapd	%xmm4, %xmm3
     7cb:      	andnpd	%xmm1, %xmm3
     7cf:      	andpd	%xmm4, %xmm2
     7d3:      	orpd	%xmm3, %xmm2
     7d7:      	movapd	%xmm2, %xmm1
     7db:      	xorpd	(%rip), %xmm1           # 0x7e3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x7e3>
		00000000000007df:  R_X86_64_PC32	.LCPI1215_5-0x4
     7e3:      	movlpd	%xmm1, (%r13,%r15,8)
     7ea:      	movapd	%xmm5, %xmm1
     7ee:      	subsd	%xmm2, %xmm1
     7f2:      	callq	*%rbx
     7f4:      	movsd	0x40(%rsp), %xmm2
     7fa:      	movsd	0x20(%rsp), %xmm6
     800:      	maxsd	%xmm0, %xmm2
     804:      	ucomisd	%xmm2, %xmm6
     808:      	jbe	0x80e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x80e>
     80a:      	movapd	%xmm6, %xmm2
     80e:      	movsd	0x28(%rsp), %xmm5
     814:      	movapd	%xmm5, %xmm8
     819:      	movsd	0x48(%rsp), %xmm0
     81f:      	movsd	%xmm0, 0x38(%rsp)
     825:      	xorl	%eax, %eax
     827:      	jmp	0x686 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x686>
     82c:      	cmpq	%r12, %r15
     82f:      	movsd	0x50(%rsp), %xmm0
     835:      	ja	0xe34 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe34>
     83b:      	movapd	%xmm3, %xmm1
     83f:      	minsd	%xmm8, %xmm1
     844:      	movapd	%xmm5, %xmm2
     848:      	minsd	%xmm1, %xmm2
     84c:      	movsd	%xmm3, 0x58(%rsp)
     852:      	movapd	%xmm12, %xmm3
     857:      	mulsd	%xmm2, %xmm3
     85b:      	movapd	0x90(%rsp), %xmm4
     864:      	movapd	%xmm4, %xmm1
     868:      	andnpd	%xmm2, %xmm1
     86c:      	subsd	%xmm3, %xmm2
     870:      	andpd	%xmm4, %xmm2
     874:      	orpd	%xmm1, %xmm2
     878:      	movlpd	%xmm2, (%r13,%r15,8)
     87f:      	movapd	%xmm6, %xmm1
     883:      	subsd	%xmm2, %xmm1
     887:      	callq	*%rbx
     889:      	movsd	0x58(%rsp), %xmm2
     88f:      	movsd	0x28(%rsp), %xmm5
     895:      	minsd	%xmm0, %xmm2
     899:      	movl	$0x1, %eax
     89e:      	ucomisd	%xmm5, %xmm2
     8a2:      	jbe	0x66f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x66f>
     8a8:      	movapd	%xmm5, %xmm2
     8ac:      	jmp	0x66f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x66f>
     8b1:      	movsd	0x60(%rsp), %xmm0
     8b7:      	movsd	%xmm8, 0x30(%rsp)
     8be:      	movapd	%xmm8, %xmm1
     8c3:      	subsd	%xmm2, %xmm1
     8c7:      	movsd	%xmm0, 0x60(%rsp)
     8cd:      	callq	*%rbx
     8cf:      	movsd	0x58(%rsp), %xmm2
     8d5:      	minsd	%xmm0, %xmm2
     8d9:      	movl	$0x1, %eax
     8de:      	movsd	0x28(%rsp), %xmm5
     8e4:      	ucomisd	%xmm5, %xmm2
     8e8:      	jbe	0x8ee <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x8ee>
     8ea:      	movapd	%xmm5, %xmm2
     8ee:      	movsd	0x18(%rsp), %xmm7
     8f4:      	movsd	0x10(%rsp), %xmm4
     8fa:      	movsd	0x8(%rsp), %xmm12
     901:      	movsd	0x20(%rsp), %xmm6
     907:      	movsd	0x30(%rsp), %xmm8
     90e:      	jmp	0x699 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x699>
     913:      	movsd	0x38(%rsp), %xmm0
     919:      	movsd	%xmm8, 0x30(%rsp)
     920:      	movapd	%xmm8, %xmm1
     925:      	subsd	%xmm2, %xmm1
     929:      	movsd	%xmm0, 0x38(%rsp)
     92f:      	callq	*%rbx
     931:      	movsd	0x40(%rsp), %xmm2
     937:      	maxsd	%xmm0, %xmm2
     93b:      	movsd	0x20(%rsp), %xmm6
     941:      	ucomisd	%xmm2, %xmm6
     945:      	jbe	0x94b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x94b>
     947:      	movapd	%xmm6, %xmm2
     94b:      	xorl	%eax, %eax
     94d:      	movsd	0x18(%rsp), %xmm7
     953:      	movsd	0x10(%rsp), %xmm4
     959:      	movsd	0x8(%rsp), %xmm12
     960:      	movsd	0x28(%rsp), %xmm5
     966:      	movsd	0x30(%rsp), %xmm8
     96d:      	jmp	0x699 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x699>
     972:      	decq	%rsi
     975:      	xorl	%r14d, %r14d
     978:      	xorpd	%xmm9, %xmm9
     97d:      	cmpneqsd	%xmm12, %xmm9
     983:      	movapd	%xmm9, 0x90(%rsp)
     98d:      	movsd	%xmm0, 0x60(%rsp)
     993:      	movsd	%xmm1, 0x38(%rsp)
     999:      	movq	%rsi, %r12
     99c:      	jmp	0x9d6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x9d6>
     99e:      	movq	%r12, %rcx
     9a1:      	movq	%r15, %rdx
     9a4:      	movsd	0x18(%rsp), %xmm7
     9aa:      	movsd	0x10(%rsp), %xmm4
     9b0:      	movsd	0x8(%rsp), %xmm12
     9b7:      	movsd	0x20(%rsp), %xmm6
     9bd:      	movsd	0x30(%rsp), %xmm8
     9c4:      	addq	%r14, %rcx
     9c7:      	incq	%rcx
     9ca:      	incq	%r14
     9cd:      	cmpq	%rdx, %rcx
     9d0:      	jae	0xce0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xce0>
     9d6:      	movapd	%xmm5, %xmm3
     9da:      	movapd	%xmm6, %xmm1
     9de:      	movq	0x78(%rsp), %rcx
     9e3:      	movsd	(%rcx,%r14,8), %xmm5
     9e9:      	movsd	(%rbp,%r14,8), %xmm6
     9f0:      	cmpq	$0x1, %rax
     9f4:      	movsd	%xmm5, 0x28(%rsp)
     9fa:      	movsd	%xmm6, 0x20(%rsp)
     a00:      	jne	0xa5c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa5c>
     a02:      	ucomisd	%xmm5, %xmm2
     a06:      	jae	0xac2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xac2>
     a0c:      	cmpq	%rbx, %r14
     a0f:      	jae	0xecd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xecd>
     a15:      	movsd	%xmm2, (%r13,%r14,8)
     a1c:      	ucomisd	%xmm8, %xmm6
     a21:      	movsd	%xmm3, 0x58(%rsp)
     a27:      	movq	%rdx, %r15
     a2a:      	jbe	0xc34 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc34>
     a30:      	movsd	0x60(%rsp), %xmm0
     a36:      	addsd	0xb0(%rsp), %xmm0
     a3f:      	ucomisd	%xmm4, %xmm0
     a43:      	movapd	%xmm6, %xmm8
     a48:      	jbe	0xc3a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc3a>
     a4e:      	movapd	%xmm6, %xmm8
     a53:      	movapd	%xmm4, %xmm0
     a57:      	jmp	0xc3a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc3a>
     a5c:      	ucomisd	%xmm2, %xmm6
     a60:      	jae	0xb6a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb6a>
     a66:      	cmpq	%rbx, %r14
     a69:      	jae	0xe77 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe77>
     a6f:      	movapd	%xmm2, %xmm0
     a73:      	xorpd	(%rip), %xmm0           # 0xa7b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xa7b>
		0000000000000a77:  R_X86_64_PC32	.LCPI1215_5-0x4
     a7b:      	movlpd	%xmm0, (%r13,%r14,8)
     a82:      	ucomisd	%xmm5, %xmm8
     a87:      	movsd	%xmm1, 0x40(%rsp)
     a8d:      	movq	%rdx, %r15
     a90:      	jbe	0xc7e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc7e>
     a96:      	movsd	0x38(%rsp), %xmm0
     a9c:      	addsd	0xa8(%rsp), %xmm0
     aa5:      	ucomisd	%xmm7, %xmm0
     aa9:      	movapd	%xmm5, %xmm8
     aae:      	jbe	0xc84 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc84>
     ab4:      	movapd	%xmm5, %xmm8
     ab9:      	movapd	%xmm7, %xmm0
     abd:      	jmp	0xc84 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc84>
     ac2:      	cmpq	%rbx, %r14
     ac5:      	movsd	0x48(%rsp), %xmm0
     acb:      	jae	0xea2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xea2>
     ad1:      	movq	%rdx, %r15
     ad4:      	movapd	%xmm1, %xmm2
     ad8:      	maxsd	%xmm8, %xmm2
     add:      	movsd	%xmm1, 0x40(%rsp)
     ae3:      	movapd	%xmm6, %xmm1
     ae7:      	maxsd	%xmm2, %xmm1
     aeb:      	movapd	%xmm12, %xmm2
     af0:      	mulsd	%xmm1, %xmm2
     af4:      	addsd	%xmm1, %xmm2
     af8:      	movapd	0x90(%rsp), %xmm4
     b01:      	movapd	%xmm4, %xmm3
     b05:      	andnpd	%xmm1, %xmm3
     b09:      	andpd	%xmm4, %xmm2
     b0d:      	orpd	%xmm3, %xmm2
     b11:      	movapd	%xmm2, %xmm1
     b15:      	xorpd	(%rip), %xmm1           # 0xb1d <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb1d>
		0000000000000b19:  R_X86_64_PC32	.LCPI1215_5-0x4
     b1d:      	movlpd	%xmm1, (%r13,%r14,8)
     b24:      	movapd	%xmm5, %xmm1
     b28:      	subsd	%xmm2, %xmm1
     b2c:      	callq	*(%rip)                 # 0xb32 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb32>
		0000000000000b2e:  R_X86_64_GOTPCREL	fma-0x4
     b32:      	movsd	0x40(%rsp), %xmm2
     b38:      	movsd	0x20(%rsp), %xmm6
     b3e:      	maxsd	%xmm0, %xmm2
     b42:      	ucomisd	%xmm2, %xmm6
     b46:      	jbe	0xb4c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xb4c>
     b48:      	movapd	%xmm6, %xmm2
     b4c:      	movsd	0x28(%rsp), %xmm5
     b52:      	movapd	%xmm5, %xmm8
     b57:      	movsd	0x48(%rsp), %xmm0
     b5d:      	movsd	%xmm0, 0x38(%rsp)
     b63:      	xorl	%eax, %eax
     b65:      	jmp	0xc04 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc04>
     b6a:      	cmpq	%rbx, %r14
     b6d:      	movsd	0x50(%rsp), %xmm0
     b73:      	jae	0xe4c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe4c>
     b79:      	movq	%rdx, %r15
     b7c:      	movapd	%xmm3, %xmm1
     b80:      	minsd	%xmm8, %xmm1
     b85:      	movapd	%xmm5, %xmm2
     b89:      	minsd	%xmm1, %xmm2
     b8d:      	movsd	%xmm3, 0x58(%rsp)
     b93:      	movapd	%xmm12, %xmm3
     b98:      	mulsd	%xmm2, %xmm3
     b9c:      	movapd	0x90(%rsp), %xmm4
     ba5:      	movapd	%xmm4, %xmm1
     ba9:      	andnpd	%xmm2, %xmm1
     bad:      	subsd	%xmm3, %xmm2
     bb1:      	andpd	%xmm4, %xmm2
     bb5:      	orpd	%xmm1, %xmm2
     bb9:      	movlpd	%xmm2, (%r13,%r14,8)
     bc0:      	movapd	%xmm6, %xmm1
     bc4:      	subsd	%xmm2, %xmm1
     bc8:      	callq	*(%rip)                 # 0xbce <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xbce>
		0000000000000bca:  R_X86_64_GOTPCREL	fma-0x4
     bce:      	movsd	0x58(%rsp), %xmm2
     bd4:      	movsd	0x28(%rsp), %xmm5
     bda:      	minsd	%xmm0, %xmm2
     bde:      	movl	$0x1, %eax
     be3:      	ucomisd	%xmm5, %xmm2
     be7:      	jbe	0xbed <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xbed>
     be9:      	movapd	%xmm5, %xmm2
     bed:      	movsd	0x20(%rsp), %xmm6
     bf3:      	movapd	%xmm6, %xmm8
     bf8:      	movsd	0x50(%rsp), %xmm0
     bfe:      	movsd	%xmm0, 0x60(%rsp)
     c04:      	movq	%r12, %rcx
     c07:      	movq	%r15, %rdx
     c0a:      	movsd	0x18(%rsp), %xmm7
     c10:      	movsd	0x10(%rsp), %xmm4
     c16:      	movsd	0x8(%rsp), %xmm12
     c1d:      	addq	%r14, %rcx
     c20:      	incq	%rcx
     c23:      	incq	%r14
     c26:      	cmpq	%rdx, %rcx
     c29:      	jb	0x9d6 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x9d6>
     c2f:      	jmp	0xce0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xce0>
     c34:      	movsd	0x60(%rsp), %xmm0
     c3a:      	movsd	%xmm8, 0x30(%rsp)
     c41:      	movapd	%xmm8, %xmm1
     c46:      	subsd	%xmm2, %xmm1
     c4a:      	movsd	%xmm0, 0x60(%rsp)
     c50:      	callq	*(%rip)                 # 0xc56 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xc56>
		0000000000000c52:  R_X86_64_GOTPCREL	fma-0x4
     c56:      	movsd	0x58(%rsp), %xmm2
     c5c:      	minsd	%xmm0, %xmm2
     c60:      	movl	$0x1, %eax
     c65:      	movsd	0x28(%rsp), %xmm5
     c6b:      	ucomisd	%xmm5, %xmm2
     c6f:      	jbe	0x99e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x99e>
     c75:      	movapd	%xmm5, %xmm2
     c79:      	jmp	0x99e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x99e>
     c7e:      	movsd	0x38(%rsp), %xmm0
     c84:      	movsd	%xmm8, 0x30(%rsp)
     c8b:      	movapd	%xmm8, %xmm1
     c90:      	subsd	%xmm2, %xmm1
     c94:      	movsd	%xmm0, 0x38(%rsp)
     c9a:      	callq	*(%rip)                 # 0xca0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xca0>
		0000000000000c9c:  R_X86_64_GOTPCREL	fma-0x4
     ca0:      	movsd	0x40(%rsp), %xmm2
     ca6:      	maxsd	%xmm0, %xmm2
     caa:      	movsd	0x20(%rsp), %xmm6
     cb0:      	ucomisd	%xmm2, %xmm6
     cb4:      	jbe	0xcba <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xcba>
     cb6:      	movapd	%xmm6, %xmm2
     cba:      	xorl	%eax, %eax
     cbc:      	movq	%r12, %rcx
     cbf:      	movq	%r15, %rdx
     cc2:      	movsd	0x18(%rsp), %xmm7
     cc8:      	movsd	0x10(%rsp), %xmm4
     cce:      	movsd	0x8(%rsp), %xmm12
     cd5:      	movsd	0x28(%rsp), %xmm5
     cdb:      	jmp	0x9bd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x9bd>
     ce0:      	movq	0x88(%rsp), %rax
     ce8:      	movq	%r14, (%rax)
     ceb:      	xorl	%eax, %eax
     ced:      	jmp	0x65 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x65>
     cf2:      	movq	%rsi, 0x28(%rsp)
     cf7:      	movq	%r14, 0x88(%rsp)
     cff:      	movq	%rdx, %r14
     d02:      	movq	%r9, 0x8(%rsp)
     d07:      	movq	%rcx, %r12
     d0a:      	movq	%rdi, 0x20(%rsp)
     d0f:      	movq	%r8, 0x78(%rsp)
     d14:      	movsd	%xmm7, 0x18(%rsp)
     d1a:      	movsd	%xmm4, 0x10(%rsp)
     d20:      	movsd	%xmm6, 0x30(%rsp)
     d26:      	movsd	%xmm5, 0x50(%rsp)
     d2c:      	movsd	%xmm3, 0x48(%rsp)
     d32:      	movsd	%xmm8, 0x40(%rsp)
     d39:      	movsd	%xmm1, 0x58(%rsp)
     d3f:      	movaps	%xmm0, 0x60(%rsp)
     d44:      	callq	*(%rip)                 # 0xd4a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xd4a>
		0000000000000d46:  R_X86_64_GOTPCREL	_ZN10std_detect6detect5cache21detect_and_initialize17hd21b90854bd2a812E-0x4
     d4a:      	movapd	0x60(%rsp), %xmm0
     d50:      	movsd	0x58(%rsp), %xmm1
     d56:      	movsd	0x40(%rsp), %xmm8
     d5d:      	movsd	0x48(%rsp), %xmm3
     d63:      	movsd	0x50(%rsp), %xmm5
     d69:      	movsd	0x30(%rsp), %xmm6
     d6f:      	movsd	0x10(%rsp), %xmm4
     d75:      	movsd	0x18(%rsp), %xmm7
     d7b:      	movq	0x78(%rsp), %r8
     d80:      	movq	0x20(%rsp), %rdi
     d85:      	movq	%r12, %rcx
     d88:      	movq	0x8(%rsp), %r9
     d8d:      	movq	%r14, %rdx
     d90:      	movq	0x88(%rsp), %r14
     d98:      	movq	0x28(%rsp), %rsi
     d9d:      	btq	$0x36, %rax
     da2:      	jae	0x5c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0x5c>
     da8:      	movapd	%xmm8, %xmm2
     dad:      	addq	$0xd8, %rsp
     db4:      	popq	%rbx
     db5:      	popq	%r12
     db7:      	popq	%r13
     db9:      	popq	%r14
     dbb:      	popq	%r15
     dbd:      	popq	%rbp
     dbe:      	jmp	0xdc3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdc3>
		0000000000000dbf:  R_X86_64_PLT32	.text._ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$15sarext_impl_fma17h01a1668133c96c69E-0x4
     dc3:      	leaq	(%rip), %rdi            # 0xdca <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdca>
		0000000000000dc6:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.13.llvm.7684525917036654579-0x4
     dca:      	leaq	(%rip), %rdx            # 0xdd1 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdd1>
		0000000000000dcd:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8054-0x4
     dd1:      	movl	$0x40, %esi
     dd6:      	callq	*(%rip)                 # 0xddc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xddc>
		0000000000000dd8:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     ddc:      	leaq	(%rip), %rdi            # 0xde3 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xde3>
		0000000000000ddf:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.16.llvm.7684525917036654579-0x4
     de3:      	leaq	(%rip), %rdx            # 0xdea <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdea>
		0000000000000de6:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8055-0x4
     dea:      	movl	$0x3f, %esi
     def:      	callq	*(%rip)                 # 0xdf5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdf5>
		0000000000000df1:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     df5:      	leaq	(%rip), %rdi            # 0xdfc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xdfc>
		0000000000000df8:  R_X86_64_PC32	anon.3b8b9055443d8061808e92970181aa47.18.llvm.7684525917036654579-0x4
     dfc:      	leaq	(%rip), %rdx            # 0xe03 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe03>
		0000000000000dff:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8056-0x4
     e03:      	movl	$0x50, %esi
     e08:      	callq	*(%rip)                 # 0xe0e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe0e>
		0000000000000e0a:  R_X86_64_GOTPCREL	_ZN4core9panicking5panic17h89a5f2df32b0508aE-0x4
     e0e:      	leaq	(%rip), %rdx            # 0xe15 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe15>
		0000000000000e11:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8057-0x4
     e15:      	movq	%r14, %rdi
     e18:      	movq	%r8, %rsi
     e1b:      	callq	*(%rip)                 # 0xe21 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe21>
		0000000000000e1d:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     e21:      	leaq	(%rip), %rdx            # 0xe28 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe28>
		0000000000000e24:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8058-0x4
     e28:      	movq	%r14, %rdi
     e2b:      	movq	%r15, %rsi
     e2e:      	callq	*(%rip)                 # 0xe34 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe34>
		0000000000000e30:  R_X86_64_GOTPCREL	_ZN4core5slice5index24slice_end_index_len_fail17hb04774ae50b54dc9E-0x4
     e34:      	leaq	(%rip), %rdx            # 0xe3b <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe3b>
		0000000000000e37:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8064-0x4
     e3b:      	movq	%r15, %rdi
     e3e:      	movq	0x80(%rsp), %rsi
     e46:      	callq	*(%rip)                 # 0xe4c <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe4c>
		0000000000000e48:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     e4c:      	leaq	(%rip), %rdx            # 0xe53 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe53>
		0000000000000e4f:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8068-0x4
     e53:      	movq	%r14, %rdi
     e56:      	movq	%rbx, %rsi
     e59:      	callq	*(%rip)                 # 0xe5f <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe5f>
		0000000000000e5b:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     e5f:      	leaq	(%rip), %rdx            # 0xe66 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe66>
		0000000000000e62:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8063-0x4
     e66:      	movq	%r15, %rdi
     e69:      	movq	0x80(%rsp), %rsi
     e71:      	callq	*(%rip)                 # 0xe77 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe77>
		0000000000000e73:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     e77:      	leaq	(%rip), %rdx            # 0xe7e <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe7e>
		0000000000000e7a:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8067-0x4
     e7e:      	movq	%r14, %rdi
     e81:      	movq	%rbx, %rsi
     e84:      	callq	*(%rip)                 # 0xe8a <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe8a>
		0000000000000e86:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     e8a:      	leaq	(%rip), %rdx            # 0xe91 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xe91>
		0000000000000e8d:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8062-0x4
     e91:      	movq	%r15, %rdi
     e94:      	movq	0x80(%rsp), %rsi
     e9c:      	callq	*(%rip)                 # 0xea2 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xea2>
		0000000000000e9e:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     ea2:      	leaq	(%rip), %rdx            # 0xea9 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xea9>
		0000000000000ea5:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8066-0x4
     ea9:      	movq	%r14, %rdi
     eac:      	movq	%rbx, %rsi
     eaf:      	callq	*(%rip)                 # 0xeb5 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xeb5>
		0000000000000eb1:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     eb5:      	leaq	(%rip), %rdx            # 0xebc <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xebc>
		0000000000000eb8:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8061-0x4
     ebc:      	movq	%r15, %rdi
     ebf:      	movq	0x80(%rsp), %rsi
     ec7:      	callq	*(%rip)                 # 0xecd <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xecd>
		0000000000000ec9:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     ecd:      	leaq	(%rip), %rdx            # 0xed4 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xed4>
		0000000000000ed0:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8065-0x4
     ed4:      	movq	%r14, %rdi
     ed7:      	movq	%rbx, %rsi
     eda:      	callq	*(%rip)                 # 0xee0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xee0>
		0000000000000edc:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
     ee0:      	leaq	(%rip), %rdx            # 0xee7 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xee7>
		0000000000000ee3:  R_X86_64_PC32	.data.rel.ro..Lanon.3b8b9055443d8061808e92970181aa47.8059-0x4
     ee7:      	movq	%r14, %rsi
     eea:      	callq	*(%rip)                 # 0xef0 <_ZN6ta_lib7ta_func6sarext46_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$11sarext_impl17h3d3cd2b1bc2feed3E+0xef0>
		0000000000000eec:  R_X86_64_GOTPCREL	_ZN4core9panicking18panic_bounds_check17h5443494609ce8457E-0x4
