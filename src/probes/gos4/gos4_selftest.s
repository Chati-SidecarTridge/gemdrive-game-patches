; A test of src/gemdrive/gos4_patch.s's forwarder, run under GOS4 as a game's
; program (gos4_selftest.py puts it in place of one, in a copy of the game's folder). Through GOS's
; TRAP #1 it writes a file, reads it back, searches for it, makes and deletes a second one, and
; opens a name longer than 8.3; it prints PASS or the step that failed, leaves the same line in
; RESULT.OUT, and waits. Its absolute addresses (the strings, the BSS) test the forwarder's loader
; too: relocated, the BSS cleared. The handles are GOS's numbers: 6 for the first file, 7 for a
; second one open at the same time.

	text
start:
	pea	title
	move.w	#9,-(sp)			; Cconws
	trap	#1
	addq.l	#6,sp
	moveq	#1,d7				; 1: Fcreate("TEST.OUT", 0) = 6
	clr.w	-(sp)
	pea	name1
	move.w	#$3c,-(sp)
	trap	#1
	addq.l	#8,sp
	cmp.l	#6,d0
	bne.w	failure
	move.w	d0,d6
	addq.w	#1,d7				; 2: Fwrite(6, 16, written) = 16
	pea	written
	pea	(16).w
	move.w	d6,-(sp)
	move.w	#$40,-(sp)
	trap	#1
	lea	(12,sp),sp
	cmp.l	#16,d0
	bne.w	failure
	addq.w	#1,d7				; 3: Fclose(6) = 0
	move.w	d6,-(sp)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	tst.l	d0
	bne.w	failure
	addq.w	#1,d7				; 4: Fopen("TEST.OUT", 0) = 6
	clr.w	-(sp)
	pea	name1
	move.w	#$3d,-(sp)
	trap	#1
	addq.l	#8,sp
	cmp.l	#6,d0
	bne.w	failure
	move.w	d0,d6
	addq.w	#1,d7				; 5: Fseek(4, 6, 0) = 4, Fread(6, 12, buf) = 12, its bytes
	clr.w	-(sp)
	move.w	d6,-(sp)
	pea	(4).w
	move.w	#$42,-(sp)
	trap	#1
	lea	(10,sp),sp
	cmp.l	#4,d0
	bne.w	failure
	pea	buf
	pea	(12).w
	move.w	d6,-(sp)
	move.w	#$3f,-(sp)
	trap	#1
	lea	(12,sp),sp
	cmp.l	#12,d0
	bne.w	failure
	lea	written+4,a0
	lea	buf,a1
	moveq	#11,d1
same:
	cmpm.b	(a0)+,(a1)+
	dbne	d1,same
	bne.w	failure
	addq.w	#1,d7				; 6: Fcreate("TEST2.OUT", 0) = 7 with 6 open, both closed
	clr.w	-(sp)
	pea	name2
	move.w	#$3c,-(sp)
	trap	#1
	addq.l	#8,sp
	cmp.l	#7,d0
	bne.w	failure
	move.w	d0,-(sp)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	tst.l	d0
	bne.w	failure
	move.w	d6,-(sp)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	tst.l	d0
	bne.w	failure
	addq.w	#1,d7				; 7: Fsetdta(dta), Fsfirst("TEST.OUT", 0) = 0: 16 bytes, its name
	pea	dta
	move.w	#$1a,-(sp)
	trap	#1
	addq.l	#6,sp
	clr.w	-(sp)
	pea	name1
	move.w	#$4e,-(sp)
	trap	#1
	addq.l	#8,sp
	tst.l	d0
	bne.w	failure
	cmpi.l	#16,dta+26
	bne.w	failure
	lea	dta+30,a0
	lea	name1,a1
found:
	move.b	(a1)+,d0
	cmp.b	(a0)+,d0
	bne.w	failure
	tst.b	d0
	bne.s	found
	addq.w	#1,d7				; 8: Fdelete("TEST2.OUT") = 0, then Fsfirst finds nothing
	pea	name2
	move.w	#$41,-(sp)
	trap	#1
	addq.l	#6,sp
	tst.l	d0
	bne.s	failure
	clr.w	-(sp)
	pea	name2
	move.w	#$4e,-(sp)
	trap	#1
	addq.l	#8,sp
	tst.l	d0
	bpl.s	failure
	addq.w	#1,d7				; 9: Fopen("TEST.OUTPUT", 0) = 6: TEST.OUT, cut to 8.3
	clr.w	-(sp)
	pea	name3
	move.w	#$3d,-(sp)
	trap	#1
	addq.l	#8,sp
	cmp.l	#6,d0
	bne.s	failure
	move.w	d0,-(sp)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	lea	pass,a4
	bra.s	report
failure:
	lea	failed,a4
	add.b	d7,failed_step
report:
	pea	(a4)
	move.w	#9,-(sp)
	trap	#1
	addq.l	#6,sp
	clr.w	-(sp)				; RESULT.OUT: the same line
	pea	name4
	move.w	#$3c,-(sp)
	trap	#1
	addq.l	#8,sp
	tst.l	d0
	bmi.s	wait
	move.w	d0,d6
	movea.l	a4,a0
	moveq	#-1,d1
length:
	addq.l	#1,d1
	tst.b	(a0)+
	bne.s	length
	pea	(a4)
	move.l	d1,-(sp)
	move.w	d6,-(sp)
	move.w	#$40,-(sp)
	trap	#1
	lea	(12,sp),sp
	move.w	d6,-(sp)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
wait:
	bra.s	wait

	data
title:
	dc.b	27,'E',"GOS4 forwarder self-test",13,10,0
pass:
	dc.b	"PASS",13,10,0
failed:
	dc.b	"FAIL at step "
failed_step:
	dc.b	'0',13,10,0
name1:
	dc.b	"TEST.OUT",0
name2:
	dc.b	"TEST2.OUT",0
name3:
	dc.b	"TEST.OUTPUT",0
name4:
	dc.b	"RESULT.OUT",0
written:
	dc.b	"WRITTEN BY GOS4!"

	bss
buf:
	ds.b	16
dta:
	ds.b	44
