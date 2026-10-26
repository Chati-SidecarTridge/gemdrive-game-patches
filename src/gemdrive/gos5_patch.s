; The launcher change for a GEMDOS drive, as a block that tools/build_gos5.py puts at the front of
; any GOS5 launcher's text. src/gemdrive/lemld2_gemdrive.s is the same change written into
; Lemmings' sources.
;
; Position-independent. The tool fills the five branches and the parameters below, turns the
; launcher's call of its info screen into a call of gd_info (our lines under PP's), and turns the
; launcher's PPHD check (movea.l $472.w,a1 / cmpi.l #'PPHD',-8(a1) / bne) into a bra.w to
; gd_check, which makes the check itself:
;   - PP's driver: PP's own path (x_pp), as before (our fix applies to our builds only);
;   - no PP driver, and a cartridge's TRAP #1 on a 68000 (Hatari's GEMDOS drive, the
;     Multidevice's GEMDRIVE), with GOS's file_io as gd_quiet knows it (lea (sr_save,pc),a0 /
;     move.w sr,(a0), or move.l a0,-(sp) before them in the older D15R_H5 builds G52, G55 and
;     G552): gd_forward's block copied to p_run and GOS's image pointed at it, then GOS's start
;     (x_gos);
;   - anything else: PP's fallback (x_no_pp).
; gd_forward hands the file functions to the machine's TRAP #1 (names cut to 8.3) and every other
; call to GOS's trap1; md_move_stack moves the Multidevice GEMDRIVE's stack out of the game's RAM;
; gd_quiet lets no IKBD packet be cut by a load.

	include	"src/include/atari.i"

GD_QUIET	equ	1200				; gd_q_wait: 30 cycles a loop, about 4.5 ms at 8 MHz
GD_GIVE_UP	equ	200				; bytes handed on before going on anyway
md_token	equ	$fa8200				; RANDOM_TOKEN_ADDR: the RP's answer, the command's token
md_seed	equ	$fa8204				; RANDOM_TOKEN_SEED_ADDR: the next command's token
md_stack_var	equ	$fa8208+(16+6)*4		; GEMDRIVE's shared variable SHARED_VARIABLE_STACK
md_cmd	equ	$fb8000				; ROM3's middle: a read at md_cmd + w sends the word w

	org	0
patch_start:
	bra.w	patch_start			; +0: the launcher's first instruction
x_pp:
	bra.w	x_pp				; +4: PP's driver found: PP's path
x_no_pp:
	bra.w	x_no_pp				; +8: not a GEMDOS drive: PP's fallback
x_gos:
	bra.w	x_gos				; +12: a GEMDOS drive: GOS's start
x_info:
	bra.w	x_info				; +16: PP's info screen (show_info)
	bra.w	gd_info				; +20: the info screen's call, turned to here
p_gos:
	dc.l	0				; +24: GOS's base, its entry table ($C0100)
p_img:
	dc.l	0				; +28: the long that holds the image's base ($C07E6)
p_img_add:
	dc.l	0				; +32: added to it ($C0800)
p_run:
	dc.l	0				; +36: where gd_forward's block runs ($B7180)
p_md_stack:
	dc.l	0				; +40: GEMDRIVE's stack, its top ($B7100)
p_floppy:
	dc.w	0				; +44: not 0: the game waits for a disk in drive A

gd_check:					; +46
	movea.l	(hdv_bpb).w,a1
	cmpi.l	#'PPHD',(-8,a1)
	beq.s	x_pp
	tst.w	($59e).w			; _longframe: 0 on a 68000
	bne.s	x_no_pp
	move.l	($84).w,d0
	cmp.l	#$fa0000,d0
	bcs.s	x_no_pp
	cmp.l	#$fc0000,d0
	bcc.s	x_no_pp
	movea.l	p_gos(pc),a0			; file_io, from GOS's entry table
	moveq	#0,d1
	move.w	(4,a0),d1
	adda.l	d1,a0
	moveq	#0,d2				; the lea's place in file_io
	cmpi.w	#$2f08,(a0)			; move.l a0,-(sp) first: G52, G55, G552
	bne.s	gd_lea
	moveq	#2,d2
gd_lea:
	cmpi.w	#$41fa,(a0,d2.w)		; lea (sr_save,pc),a0
	bne.s	x_no_pp
	cmpi.w	#$40d0,(4,a0,d2.w)		; move.w sr,(a0)
	bne.s	x_no_pp
	movea.l	d0,a2
	cmpi.l	#'XBRA',(-12,a2)
	bne.s	gd_install
	cmpi.l	#'SDGD',(-8,a2)
	bne.s	gd_install
	bsr.w	md_move_stack
	bne.w	x_no_pp				; the stack did not move: PP's fallback, and its message
gd_install:
	movea.l	p_run(pc),a1
	lea	gd_forward(pc),a2
	move.w	#(gd_forward_end-gd_forward)/2-1,d1
gd_copy:
	move.w	(a2)+,(a1)+
	dbf	d1,gd_copy
	movea.l	p_run(pc),a1
	move.l	d0,(gd_machine-gd_forward,a1)	; the machine's TRAP #1
	movea.l	p_img(pc),a6
	movea.l	(a6),a6
	adda.l	p_img_add(pc),a6		; GOS's image of the system variables
	move.l	($84,a6),(gd_gos-gd_forward,a1)	; GOS's trap1
	move.l	a1,($84,a6)
	move.l	(_drvbits).w,(1218,a6)		; the machine's drives, for GOS's Dsetdrv
	move.b	d2,(gd_push-gd_forward,a1)	; 2: file_io pushes a0 first
	lea	(2,a0,d2.w),a2			; file_io's lea: where it keeps the caller's SR
	move.w	(a2),d1
	ext.l	d1
	adda.l	d1,a2
	move.l	a2,(gd_sr_save-gd_forward,a1)
	lea	(6,a0,d2.w),a2			; after move.w sr,(a0), which gd_quiet does itself: the older
	move.l	a2,(gd_continue-gd_forward,a1)	; builds would save the SR it left masked (Muzzy then
						; ran with no VBL)
	move.w	#$4ef9,(a0)			; jmp gd_quiet, over file_io's first two instructions
	lea	(gd_quiet-gd_forward,a1),a2
	move.l	a2,(2,a0)
	bra.w	x_gos

; PP's info screen, then our lines in its free rows: PP's start at row 16, a game's cheat keys at
; row 0. Cconws, as show_info prints; the cursor home again, where show_info leaves it.
gd_info:
	bsr.w	x_info
	pea	gd_patched(pc)
	move.w	#9,-(sp)			; Cconws
	trap	#1
	addq.l	#6,sp
	move.w	p_floppy(pc),d0
	beq.s	gd_info_end
	pea	gd_floppy(pc)
	move.w	#9,-(sp)
	trap	#1
	addq.l	#6,sp
gd_info_end:
	rts
gd_patched:
	dc.b	27,'Y',32+9,32+0,"Patched for GEMDRIVE HD by SidecarTridge",27,'H',0
gd_floppy:
	dc.b	27,'Y',32+11,32+3,"Insert any floppy disk in drive A",27,'H',0
	even

; GEMDRIVE's CMD_SET_SHARED_VAR (SHARED_VARIABLE_STACK, p_md_stack), as its gemdrive_start sends
; it for the stack it Mallocs: the Multidevice's send_sync, run from RAM, five tries. Z set when
; the RP holds the new stack.
md_move_stack:
	movem.l	d0-d7/a0-a1,-(sp)
	lea	md_stack_words(pc),a1
	move.l	p_md_stack(pc),d0
	move.w	d0,(a1)+			; low word first
	swap	d0
	move.w	d0,(a1)
	moveq	#4,d6
md_try:
	move.l	(md_seed).l,d2
	lea	md_token_words(pc),a1
	move.w	d2,(a1)+
	swap	d2
	move.w	d2,(a1)
	swap	d2
	lea	(md_cmd).l,a0
	move.w	#$abcd,d1			; CMD_MAGIC_NUMBER
	tst.b	(a0,d1.w)
	moveq	#0,d7				; the checksum: every word after the magic
	lea	md_words(pc),a1
	moveq	#(md_words_end-md_words)/2-1,d5
md_send:
	move.w	(a1)+,d1
	add.w	d1,d7
	tst.b	(a0,d1.w)
	dbf	d5,md_send
	tst.b	(a0,d7.w)
	move.l	#$6ffff,d5			; COMMAND_TIMEOUT
md_wait:
	cmp.l	(md_token).l,d2
	bne.s	md_not_yet
	cmp.l	(md_seed).l,d2			; the seed moved on: a real answer
	bne.s	md_answered
md_not_yet:
	subq.l	#1,d5
	bne.s	md_wait
	dbf	d6,md_try
md_answered:
	move.l	p_md_stack(pc),d0
	cmp.l	(md_stack_var).l,d0
	movem.l	(sp)+,d0-d7/a0-a1		; keeps the flags
	rts
md_words:
	dc.w	$0487,12			; CMD_SET_SHARED_VAR, the payload's bytes with the token's
md_token_words:
	dc.w	0,0
	dc.w	16+6,0				; SHARED_VARIABLE_STACK
md_stack_words:
	dc.w	0,0
md_words_end:

; Runs at p_run as the TRAP #1 of GOS's image. The call is on the caller's stack: the supervisor
; stack past the exception frame (6 bytes on the 68000), or the user stack. A name (Dsetpath,
; Fcreate, Fopen, Fdelete) goes on in gd_name, each part cut to 8.3 as GEMDOS reads it, without a
; dot it ends with.
gd_forward:
	btst	#5,(sp)
	bne.s	gd_super
	move.l	usp,a1
	bra.s	gd_fn
gd_super:
	lea	(6,sp),a1
gd_fn:
	move.w	(a1),d0
	lea	gd_functions(pc),a0
gd_next:
	move.b	(a0)+,d1
	beq.s	gd_to_gos
	cmp.b	d1,d0
	bne.s	gd_next
	cmpi.b	#$3e,d0
	bcs.s	gd_83				; Dsetpath, Fcreate, Fopen (the list has none lower)
	cmpi.b	#$41,d0				; Fdelete
	bne.s	gd_to_machine
gd_83:
	movea.l	(2,a1),a0
	lea	gd_name(pc),a2
	move.l	a2,(2,a1)
gd_part:
	move.l	a2,d2				; the part's first character
	moveq	#8,d1				; a part's name: 8 characters
gd_char:
	move.b	(a0)+,d0
	beq.s	gd_trim
	cmpi.b	#$5c,d0				; backslash
	beq.s	gd_trim
	cmpi.b	#'.',d0
	beq.s	gd_dot
	subq.w	#1,d1
	bmi.s	gd_char				; past 8.3: GEMDOS drops it
	move.b	d0,(a2)+
	bra.s	gd_char
gd_dot:
	move.b	d0,(a2)+
	moveq	#3,d1				; its extension: 3
	bra.s	gd_char
gd_trim:					; a part ends: a dot it ends with goes, as GEMDOS reads
	cmpa.l	d2,a2				; "RESIDENT." (Video Kid); not "." or ".."
	beq.s	gd_put
	cmpi.b	#'.',(-1,a2)
	bne.s	gd_put
	move.l	a2,d1
	subq.l	#1,d1
	cmp.l	d2,d1
	beq.s	gd_put
	cmpi.b	#'.',(-2,a2)
	beq.s	gd_put
	subq.l	#1,a2
gd_put:
	move.b	d0,(a2)+
	bne.s	gd_part				; a backslash: the next part
gd_to_machine:
	move.l	gd_machine(pc),-(sp)
	rts
gd_to_gos:
	move.l	gd_gos(pc),-(sp)
	rts
gd_machine:
	dc.l	0
gd_gos:
	dc.l	0
gd_sr_save:
	dc.l	0				; file_io's place for the caller's SR
gd_continue:
	dc.l	0				; after file_io's move.w sr,(a0): +6, or +8 in the older builds
gd_push:
	dc.b	0				; not 0: file_io starts with move.l a0,-(sp)
; Dsetpath, Fcreate, Fopen, Fclose, Fread, Fwrite, Fdelete, Fseek, Dgetpath
gd_functions:
	dc.b	$3b,$3c,$3d,$3e,$3f,$40,$41,$42,$47,0
	even

; Entered by the jmp at file_io's first instruction, with interrupts masked by the caller (the
; game's copy of PP's loader masks them). With them still masked, it watches the keyboard ACIA
; until no byte has come for GD_QUIET loops (longer than the IKBD takes to answer a poll), and
; hands each byte to the game's keyboard interrupt as the MFP would: through the vector its vector
; register gives channel 6, and only while the game's own SR lets it in, that interrupt is
; enabled, unmasked, not in service, its handler is the game's, and the ACIAs' line asks for it.
; A game that loads with interrupts masked, reads the ACIA itself, or has not taken the keyboard
; from TOS yet, gets no wait. Then what
; file_io starts with (move.l a0,-(sp) in the older builds, the lea, the caller's SR kept), and on
; into it, interrupts still masked: a VBL that came meanwhile waits until file_io gives the SR
; back, as it would have if it had come during the load.
gd_quiet:
	movem.l	d0-d2/a0-a1,-(sp)
	move.w	sr,d1				; the caller's, which file_io gives back
	move.w	#$2700,sr
	move.w	d1,d0				; the game's SR: the caller's, or the one PP's loader
	movea.l	(20,sp),a0			; keeps in loader_sr before it masks them (after jsr
	cmpi.l	#$4279000c,(a0)			; (a0): clr.w $c0734.l, then move.w (loader_sr,pc),sr)
	bne.s	gd_q_loader
	addq.l	#6,a0
gd_q_loader:
	cmpi.w	#$46fa,(a0)
	bne.s	gd_q_ipl
	adda.w	(2,a0),a0
	move.w	(2,a0),d0
gd_q_ipl:
	andi.w	#$0700,d0			; masked for the keyboard's level 6 (Warp loads at
	cmpi.w	#$0600,d0			; $2700, its handler using a3 as it is in its own code):
	bcc.s	gd_q_done			; no interrupt could come, as on PP's path
	btst	#6,(mfp_ierb).w			; the keyboard ACIA's interrupt: enabled
	beq.s	gd_q_done
	btst	#6,(mfp_imrb).w			; unmasked
	beq.s	gd_q_done
	btst	#6,(mfp_isrb).w			; and not in service
	bne.s	gd_q_done
	moveq	#0,d0
	move.b	(mfp_vr).w,d0
	andi.w	#$f0,d0
	addq.w	#6,d0				; channel 6's vector
	lsl.w	#2,d0
	movea.w	d0,a0
	move.l	(a0),d0				; the handler: the game's, below this block; not TOS's or
	andi.l	#$ffffff,d0			; GOS's, which would run on the game's RAM (Robocop 2
	lea	gd_forward(pc),a1		; loads before it takes the keyboard)
	cmp.l	a1,d0
	bcc.s	gd_q_done
	lea	(acia_kbd_ctrl).w,a1
	move.w	#GD_GIVE_UP,d2
gd_q_start:
	move.w	#GD_QUIET,d0
gd_q_wait:
	btst	#0,(a1)				; a byte received
	bne.s	gd_q_byte
	dbf	d0,gd_q_wait
	bra.s	gd_q_done
gd_q_byte:
	btst	#4,(mfp_gpip).w			; the ACIAs' line, low when one asks for its interrupt
	bne.s	gd_q_done
	pea	gd_q_back(pc)			; the frame of a 68000 interrupt: PC, then SR
	move.w	sr,-(sp)
	move.l	(a0),-(sp)
	rts
gd_q_back:
	dbf	d2,gd_q_start
gd_q_done:
	movea.l	gd_sr_save(pc),a0
	move.w	d1,(a0)				; file_io's move.w sr,(a0): the caller's SR, which it gives back
	movem.l	(sp)+,d0-d2/a0-a1
	btst	#1,gd_push(pc)
	beq.s	gd_q_lea
	move.l	a0,-(sp)			; file_io's move.l a0,-(sp)
gd_q_lea:
	movea.l	gd_sr_save(pc),a0		; its lea
	move.l	gd_continue(pc),-(sp)
	rts
gd_name:
	dcb.b	256,0				; a name cut to 8.3
gd_forward_end:
patch_end:
