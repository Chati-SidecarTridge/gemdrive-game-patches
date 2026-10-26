; GOS through the GEMDOS drive (S1, src/notes/solutions.md section 4).
; tools/build_gemdrive.sh puts this in a copy of src/lemld2/lemld2.s, before no_pp_driver, and
; sends check_pp_driver's "no PP driver" branch here.
;
; When the machine's TRAP #1 is a cartridge's (Hatari's GEMDOS drive hooks it at $FA002A, the
; SidecarTridge's GEMDRIVE from its ROM too), the launcher does not look for a disk: it puts
; gd_forward where PP's driver copy would go, points the TRAP #1 vector in GOS's image of the
; system variables at it, and starts GOS. gd_forward hands the file functions to the TRAP #1 the
; machine had, and every other call to GOS's trap1. Dsetdrv stays with GOS: the GEMDOS drive's
; hook passes it on to the ROM's GEMDOS, whose RAM the game owns. Anything else (a real disk with
; another driver, a Falcon) takes PP's own path, no_pp_driver.
;
; The SidecarTridge Multidevice's GEMDRIVE (its TRAP #1 carries the XBRA id SDGD, from v1.2.0)
; runs the calls it serves on a 1 KB stack it Mallocs at boot, near _membot: RAM the game owns.
; md_move_stack moves it to the top of PP's GEMDOS buffers ($AF100-$B70FF, set_buffers'), which
; nothing uses on this path. Everything else it reads during a call is in GOS's image: _dskbufp,
; _sysbase and its os_run, and the current drive, through a Dgetdrv that gd_forward gives GOS.
;
; gd_quiet waits, before each of GOS's loads, until no IKBD packet is on its way: file_io turns
; the keyboard ACIA's interrupt off and empties the ACIA afterwards, so a packet arriving meanwhile
; loses its last bytes, and a game that counts bytes reads every packet after it out of step.

gd_run	equ	$b7180				; reuse_pp_driver's copy of PP's driver, unused here
gd_name	equ	gd_run+gd_forward_end-gd_forward	; after gd_forward: a name cut to 8.3 (256 bytes)
md_stack	equ	$b7100				; GEMDRIVE's stack, its top: the end of PP's buffers
md_token	equ	$fa8200				; RANDOM_TOKEN_ADDR: the RP's answer, the command's token
md_seed	equ	$fa8204				; RANDOM_TOKEN_SEED_ADDR: the next command's token
md_stack_var	equ	$fa8208+(16+6)*4		; GEMDRIVE's shared variable SHARED_VARIABLE_STACK
md_cmd	equ	$fb8000				; ROM3's middle: a read at md_cmd + w sends the word w
gd_fio	equ	$c0170				; file_io: lea (L_c04b0,pc),a0 / move.w sr,(a0)
gd_fio_sr	equ	$c04b0				; L_c04b0, where file_io keeps the caller's SR
GD_QUIET	equ	1200				; gd_q_wait: 30 cycles a loop, about 4.5 ms at 8 MHz
GD_GIVE_UP	equ	200				; bytes handed on before going on anyway

gd_start:
	tst.b	(is_falcon).l
	bne.w	no_pp_driver
	move.l	($84).w,d0
	cmp.l	#$fa0000,d0
	bcs.w	no_pp_driver
	cmp.l	#$fc0000,d0
	bcc.w	no_pp_driver
	movea.l	d0,a0
	cmpi.l	#'XBRA',(-12,a0)
	bne.s	gd_install
	cmpi.l	#'SDGD',(-8,a0)
	bne.s	gd_install
	bsr.w	md_move_stack
	bne.w	no_pp_driver			; the stack did not move: PP's own path, and its message
gd_install:
	movea.l	($c07e6).l,a6
	adda.l	#$c0800,a6			; GOS's image of the system variables, as in reuse_pp_driver
	lea	gd_forward(pc),a0
	lea	(gd_run).l,a1
	move.w	#(gd_forward_end-gd_forward)/2-1,d1
gd_copy:
	move.w	(a0)+,(a1)+
	dbf	d1,gd_copy
	move.l	d0,(gd_run+gd_machine-gd_forward).l	; the machine's TRAP #1
	move.l	($84,a6),(gd_run+gd_gos-gd_forward).l	; GOS's trap1
	move.l	#gd_run,($84,a6)
	move.l	(_drvbits).w,(1218,a6)		; the machine's drives, for GOS's Dsetdrv
	cmpi.l	#$41fa033e,(gd_fio).l		; file_io as gd_quiet knows it
	bne.s	gd_no_quiet
	cmpi.w	#$40d0,(gd_fio+4).l
	bne.s	gd_no_quiet
	move.w	#$4ef9,(gd_fio).l		; jmp
	move.l	#gd_run+gd_quiet-gd_forward,(gd_fio+2).l
gd_no_quiet:
	bra.w	start_d15r

; GEMDRIVE's CMD_SET_SHARED_VAR (SHARED_VARIABLE_STACK, md_stack), as its gemdrive_start sends it
; for the stack it Mallocs: the Multidevice's send_sync (target/atarist/src/inc/
; sidecart_functions.s), run from RAM, five tries. Z set when the RP holds the new stack.
md_move_stack:
	movem.l	d0-d7/a0-a1,-(sp)
	moveq	#4,d6
md_try:
	move.l	(md_seed).l,d2
	lea	md_token_words(pc),a1
	move.w	d2,(a1)+			; the token, low word first
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
	cmpi.l	#md_stack,(md_stack_var).l
	movem.l	(sp)+,d0-d7/a0-a1		; keeps the flags
	rts
md_words:
	dc.w	$0487,12			; CMD_SET_SHARED_VAR, the payload's bytes with the token's
md_token_words:
	dc.w	0,0
	dc.w	16+6,0				; SHARED_VARIABLE_STACK
	dc.w	md_stack&$ffff,md_stack>>16
md_words_end:

; Runs at gd_run as the TRAP #1 of GOS's image. The call is on the caller's stack: the supervisor
; stack past the exception frame (6 bytes on the 68000), or the user stack. A name (Dsetpath,
; Fcreate, Fopen, Fdelete) goes on in gd_name, each part cut to 8.3 as GEMDOS reads it: LS2DD asks
; for "dmalogo.imgg", and the Multidevice's GEMDRIVE hands a name to FatFS as it comes.
gd_forward:
	btst	#5,(sp)
	bne.s	gd_super
	move.l	usp,a1
	bra.s	gd_check
gd_super:
	lea	(6,sp),a1
gd_check:
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
	lea	(gd_name).l,a2
	move.l	a2,(2,a1)
gd_part:
	moveq	#8,d1				; a part's name: 8 characters
gd_char:
	move.b	(a0)+,d0
	beq.s	gd_end
	cmpi.b	#$5c,d0				; '\'
	beq.s	gd_sep
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
gd_sep:
	move.b	d0,(a2)+
	bra.s	gd_part
gd_end:
	move.b	d0,(a2)
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
; Dsetpath, Fcreate, Fopen, Fclose, Fread, Fwrite, Fdelete, Fseek, Dgetpath
gd_functions:
	dc.b	$3b,$3c,$3d,$3e,$3f,$40,$41,$42,$47,0
	even

; Runs at gd_run + (gd_quiet - gd_forward), entered by the jmp at file_io's first instruction with
; interrupts masked by the caller (the game's copy of PP's loader masks them). With them still
; masked, it watches the keyboard ACIA until no byte has come for GD_QUIET loops (longer than the
; IKBD takes to answer a poll), and hands each byte to the game's keyboard interrupt as the MFP
; would: through the vector its vector register gives channel 6 (Lemmings sets it to 0: $18, not
; TOS's $118), and only while the game's own SR (kept by PP's loader) lets it in, that interrupt is
; enabled, unmasked, not in service, its handler is the game's, and the ACIAs' line asks for it. A
; game that loads with interrupts masked, reads the ACIA itself (Lemmings' intro), or has not
; taken the keyboard from TOS yet, gets no wait: the load
; goes on as PP's. Lemmings asks for the mouse's position at every VBL, and its level load came
; while an answer was arriving: the y was read from the next packet, and drawing the pointer there
; ended in an address error. Interrupts stay masked: Lemmings' intro calls the loader from its VBL
; when space is pressed, and a VBL let in here would call it again. Then file_io's first two
; instructions, and on into it.
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
	move.w	d1,(gd_fio_sr).l
	movem.l	(sp)+,d0-d2/a0-a1
	lea	(gd_fio_sr).l,a0
	jmp	(gd_fio+6).l

gd_forward_end:
