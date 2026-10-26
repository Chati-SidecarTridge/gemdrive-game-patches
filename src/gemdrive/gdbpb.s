; EPIC-06 STORY-01: GDBPB.PRG, solution S2 (src/notes/solutions.md §3.2, §4). Run from C:\AUTO\,
; it stays resident and gives a GEMDOS drive a BPB. Silmarils' START.PRG (Crystals of Arborea,
; Targhan, Robinsons Requiem, Storm Master) asks BIOS Getbpb on its drive before every file and opens
; the file by name only once it gets one; a GEMDOS drive (Hatari's, the Multidevice's GEMDRIVE) has
; none, TOS answers 0, and the program asks again forever.
;
; gd_bpb is hdv_bpb's routine, behind an XBRA header (id GDBP): the routine before it is asked
; first, and only when it has no BPB for a drive from C: up that _drvbits holds does gd_bpb give
; its own, the BPB of the partition PPDRIVER boots in the trial (1024-byte sectors, FAT16).
; Floppies, and drives a driver serves, keep their answers. Installed once: a second run finds GDBP
; in hdv_bpb's chain and leaves.

	include	"src/include/atari.i"

	text
start:
	bra.w	install

; resident: from start to gd_end
	dc.l	'XBRA'
	dc.l	'GDBP'
gd_old:
	dc.l	0
gd_bpb:						; long Getbpb(int drive): the drive at 4(sp)
	move.w	(4,sp),-(sp)
	movea.l	gd_old(pc),a0
	jsr	(a0)
	addq.l	#2,sp
	tst.l	d0
	bne.s	gd_done				; the routine before has one
	move.w	(4,sp),d1
	cmpi.w	#2,d1
	bcs.s	gd_done				; A:, B:: a floppy's 0 stays
	cmpi.w	#32,d1
	bcc.s	gd_done
	move.l	_drvbits.w,d2
	btst	d1,d2
	beq.s	gd_done				; no such drive
	lea	gd_params(pc),a0
	move.l	a0,d0
gd_done:
	rts
gd_params:					; recsiz, clsiz, clsizb, rdlen, fsiz, fatrec, datrec, numcl, bflags
	dc.w	1024,2,2048,16,32,33,81,16343,1
gd_end:

install:
	pea	gd_hook(pc)
	move.w	#38,-(sp)			; Supexec
	trap	#14
	addq.l	#6,sp
	lea	installed,a0
	tst.l	d0
	bne.s	report
	lea	already,a0
report:
	move.l	d0,-(sp)
	pea	(a0)
	move.w	#9,-(sp)			; Cconws
	trap	#1
	addq.l	#6,sp
	move.l	(sp)+,d0
	beq.s	leave
	clr.w	-(sp)				; Ptermres(256 + the resident part, 0)
	move.l	#256+gd_end-start,-(sp)
	move.w	#$31,-(sp)
	trap	#1
leave:
	clr.w	-(sp)				; Pterm0
	trap	#1

gd_hook:					; supervisor: d0 = 0 when GDBP is in the chain already
	movea.l	hdv_bpb.w,a0
gd_look:
	cmpi.l	#'XBRA',(-12,a0)
	bne.s	gd_put
	cmpi.l	#'GDBP',(-8,a0)
	beq.s	gd_there
	movea.l	(-4,a0),a0
	bra.s	gd_look
gd_there:
	moveq	#0,d0
	rts
gd_put:
	lea	gd_old(pc),a0
	move.l	hdv_bpb.w,(a0)
	lea	gd_bpb(pc),a0
	move.l	a0,hdv_bpb.w
	moveq	#1,d0
	rts

	data
installed:
	dc.b	"GEMDOS drive BPB installed",13,10,0
already:
	dc.b	"GEMDOS drive BPB already installed",13,10,0
