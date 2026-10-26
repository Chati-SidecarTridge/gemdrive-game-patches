; EPIC-05 STORY-02: the launcher change for a GEMDOS drive, as a block that tools/build_gos4.py puts
; at the front of any GOS4 launcher's text, as tools/build_gos5.py puts gos5_patch.s in a GOS5 one.
;
; GOS4 (D15R_HH4) is TOS 1.04 started from RAM: the launcher loads it to p_gos ($C0100, $1C0100 for
; a 2 MB game) and jumps there, it sets up the machine as a reset would (its own TRAP #1 among the
; vectors, `move.l #trap1,$84.w`), takes the driver from the table the launcher leaves it, and
; starts the game with its own Pexec (EPIC-05 STORY-01). Position-independent. The tool fills the
; five branches and the parameters below, turns the launcher's call of its info screen into a call
; of gd_info, and its PPHD check into a bra.w to gd_check, which makes the check itself:
;   - PP's driver: PP's own path (x_pp), as before (D-17);
;   - no PP driver, a cartridge's TRAP #1 on a 68000 (Hatari's GEMDOS drive, the Multidevice's
;     GEMDRIVE), and GOS's `move.l #trap1,$84.w` found in RAM: gd_forward's block copied to p_run,
;     that long pointed at it, the driver table written as PP's path writes it but with no driver,
;     then where PP's path goes on to GOS (x_gos);
;   - anything else: PP's fallback (x_no_pp).
; GOS's code stays as PP's: only the long its start-up puts in $84 changes, in RAM.

	include	"src/include/atari.i"

md_token	equ	$fa8200				; RANDOM_TOKEN_ADDR: the RP's answer, the command's token
md_seed	equ	$fa8204				; RANDOM_TOKEN_SEED_ADDR: the next command's token
md_stack_var	equ	$fa8208+(16+6)*4		; GEMDRIVE's shared variable SHARED_VARIABLE_STACK
md_cmd	equ	$fb8000				; ROM3's middle: a read at md_cmd + w sends the word w
GD_SCAN	equ	$8000				; words of GOS searched for its move.l #trap1,$84.w
GD_BUFFERS	equ	$8080				; the four sector buffers, below p_run, as PP's ($AF100)

	org	0
patch_start:
	bra.w	patch_start			; +0: the launcher's first instruction
x_pp:
	bra.w	x_pp				; +4: PP's driver found: PP's path
x_no_pp:
	bra.w	x_no_pp				; +8: not a GEMDOS drive: PP's fallback
x_gos:
	bra.w	x_gos				; +12: where PP's path goes on to GOS
x_info:
	bra.w	x_info				; +16: PP's info screen (show_info)
	bra.w	gd_info				; +20: the info screen's call, turned to here
p_gos:
	dc.l	0				; +24: GOS's text, where the launcher jumps ($C0100)
p_table:
	dc.l	0				; +28: the driver table PP's path writes ($C00E0)
p_table_ptr:
	dc.l	0				; +32: the long GOS takes the table from ($C0030)
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
	movea.l	p_gos(pc),a0			; GOS's move.l #trap1,$84.w: 23FC, a long in GOS, $00000084
	move.l	#GD_SCAN-1,d1
gd_scan:
	cmpi.w	#$23fc,(a0)
	bne.s	gd_scan_next
	cmpi.l	#$84,(6,a0)
	bne.s	gd_scan_next
	move.l	(2,a0),d2
	sub.l	p_gos(pc),d2
	cmp.l	#GD_SCAN*2,d2
	bcs.s	gd_found
gd_scan_next:
	addq.l	#2,a0
	subq.l	#1,d1
	bne.s	gd_scan
	bra.s	x_no_pp
gd_found:
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
	move.l	(2,a0),(gd_gos-gd_forward,a1)	; GOS's trap1
	move.l	a1,(2,a0)			; and GOS will put gd_forward in $84
	movea.l	(_sysbase).w,a2			; the machine's p_run (its OS header +$28), where
	move.l	($28,a2),(gd_mach_run-gd_forward,a1)	; Hatari takes the current process
	movea.l	p_gos(pc),a2
	move.l	($28,a2),(gd_gos_run-gd_forward,a1)	; GOS's ($5622, TOS 1.04's)
	cmpi.w	#$600c,($36,a2)			; GOS's floppy routines, past its first branch (in four
	bne.s	gd_no_floppy			; builds of five; not in Defender 2's), which PP's path
	move.l	($38,a2),(gd_flop-gd_forward,a1)	; also takes for drives A and B: hdv_bpb,
	move.l	($3c,a2),(gd_flop+4-gd_forward,a1)	; hdv_rw, hdv_mediach
	move.l	($40,a2),(gd_flop+8-gd_forward,a1)
gd_no_floppy:
	movea.l	p_table(pc),a2			; the table GOS takes the driver from, as PP's path
	movea.l	p_table_ptr(pc),a3		; writes it: hdv_bpb, hdv_rw, hdv_mediach, _drvbits,
	move.l	a2,(a3)				; two lists of buffers; drives A and B GOS's floppy,
	lea	(gd_bpb-gd_forward,a1),a3	; drive C a BPB and nothing more
	move.l	a3,(a2)+
	lea	(gd_rw-gd_forward,a1),a3
	move.l	a3,(a2)+
	lea	(gd_mediach-gd_forward,a1),a3
	move.l	a3,(a2)+
	move.l	(_drvbits).w,(a2)+		; the machine's drives, for GOS's Dsetdrv
	lea	(gd_bcbs-gd_forward,a1),a3
	move.l	a1,d1
	sub.l	#GD_BUFFERS,d1
	move.l	a3,(a2)+
	bsr.s	gd_list
	move.l	a3,(a2)+
	bsr.s	gd_list
	bra.w	x_gos

; Two free buffer control blocks at a3 (link, drive -1, type, record, dirty, the buffer d1), as
; PP's path makes them; a3 and d1 move on.
gd_list:
	lea	(20,a3),a4
	move.l	a4,(a3)+
	bsr.s	gd_bcb
	clr.l	(a3)+
gd_bcb:
	move.l	#$ffff0000,(a3)+
	clr.l	(a3)+
	clr.l	(a3)+
	move.l	d1,(a3)+
	add.l	#$2000,d1
	rts

; PP's info screen, then our lines in its free rows, as gos5_patch.s's.
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

; GEMDRIVE's CMD_SET_SHARED_VAR (SHARED_VARIABLE_STACK, p_md_stack), as gos5_patch.s's. Z set when
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

; Runs at p_run as GOS's TRAP #1, for GOS and for the game. The call is on the caller's stack: the
; supervisor stack past the exception frame (6 bytes on the 68000), or the user stack. Every
; register but d0 is given back, as GEMDOS does.
;   - Pexec 0 and 3: gd_exec, the program loaded through the machine into GOS's memory.
;   - The file functions and Dfree: to the machine's TRAP #1, as a copy of the call on this stack, changed
;     there (the caller's own stays as it was): a name (Dsetpath, Fcreate, Fopen, Fdelete, Fattrib,
;     Fsfirst) in gd_name, each part cut to 8.3 as GEMDOS reads it, without a dot it ends with; a
;     handle (Fclose, Fread, Fwrite, Fseek, Fdatime) the machine's for ours.
;   - Everything else, and a handle that is not ours (0 to 5, the standard ones): GOS's trap1
;     (Dsetdrv, Dgetdrv, Fsetdta, Fgetdta, the memory, the console, Pterm, Pexec 4 to 6).
; Our handles are GOS's numbers: the machine's handle of a file Fopen or Fcreate opens is kept in
; gd_handles and the call returns 6 and up, the lowest free, as GOS would. Games count on it: PP's
; adaptation of Operation Stealth puts back a snapshot of the game's variables in which its open
; file is handle 6. Fsfirst and Fsnext: Hatari fills the DTA of the process its TOS's p_run holds
; (gemdos.c), which under GOS holds a GOS variable unless that TOS is 1.04, whose p_run is GOS's:
; elsewhere GOS's current process goes there for the call (the Multidevice asks for the DTA with
; Fgetdta, through $84: GOS's). gd_exec's own calls come back through $84, here.
GD_HANDLES	equ	16
gd_forward:
	movem.l	d1-d2/a0-a2,-(sp)		; GEMDOS keeps every register but d0, and callers count
	btst	#5,(20,sp)			; on it (gd_exec among them)
	bne.s	gd_super
	move.l	usp,a1
	bra.s	gd_fn
gd_super:
	lea	(20+6,sp),a1
gd_fn:
	move.w	(a1),d0
	cmpi.w	#$4b,d0				; Pexec
	beq.w	gd_pexec
	lea	gd_functions(pc),a0
gd_next:
	move.b	(a0)+,d1
	beq.s	gd_to_gos
	cmp.b	d1,d0
	bne.s	gd_next
	clr.l	-(sp)				; p_run's place and value, when Fsfirst or Fsnext swaps it
	clr.l	-(sp)
	movem.l	(a1),d1-d2/a0			; the call, copied: 12 bytes, Fread's, the longest
	movem.l	d1-d2/a0,-(sp)
	movea.l	sp,a2
	moveq	#2,d1				; the handle's place
	cmpi.b	#$36,d0
	beq.s	gd_call				; Dfree: the drive's free space, as it is
	cmpi.b	#$3e,d0
	bcs.s	gd_named			; Dsetpath, Fcreate, Fopen
	cmpi.b	#$41,d0
	bcs.s	gd_handle			; Fclose, Fread, Fwrite
	beq.s	gd_named			; Fdelete
	cmpi.b	#$43,d0
	beq.s	gd_named			; Fattrib
	bcs.s	gd_handle6			; Fseek
	cmpi.b	#$4e,d0
	beq.s	gd_named			; Fsfirst
	cmpi.b	#$57,d0
	bne.s	gd_call				; Dgetpath, Fsnext
gd_handle6:
	moveq	#6,d1				; Fseek, Fdatime: after a long
gd_handle:
	move.w	(a2,d1.w),d2
	subq.w	#6,d2
	cmpi.w	#GD_HANDLES,d2
	bcc.s	gd_not_ours
	add.w	d2,d2
	lea	gd_handles(pc),a0
	move.w	(a0,d2.w),(a2,d1.w)		; the machine's
	bpl.s	gd_call
gd_not_ours:
	lea	(20,sp),sp
gd_to_gos:
	movem.l	(sp)+,d1-d2/a0-a2
	move.l	gd_gos(pc),-(sp)
	rts
gd_named:
	movea.l	(2,a1),a0
	bsr.w	gd_cut
	bcs.w	gd_bad_name
	lea	gd_name(pc),a0
	move.l	a0,(2,a2)
	cmpi.b	#$3d,d0				; Fopen for reading and writing: for reading. The
	bne.s	gd_call				; Multidevice's GEMDRIVE locks a file open for writing,
	cmpi.w	#2,(6,a2)			; and Noddy's Playtime opens data\driving.dat so, never
	bne.s	gd_call				; closes it and loads it again; no game writes through
	clr.w	(6,a2)				; such a handle (Fcreate makes the files they write)
gd_call:
	cmpi.b	#$4e,d0				; Fsfirst, Fsnext: the DTA
	bcs.s	gd_go
	cmpi.b	#$4f,d0
	bhi.s	gd_go
	move.l	gd_mach_run(pc),d1
	cmp.l	gd_gos_run(pc),d1
	beq.s	gd_go
	movea.l	d1,a0
	move.l	a0,(12,a2)
	move.l	(a0),(16,a2)
	movea.l	gd_gos_run(pc),a1
	move.l	(a1),(a0)			; GOS's current process, for the call
gd_go:
	pea	gd_back(pc)			; a supervisor's call: the copy past the frame
	move.w	sr,-(sp)
	move.l	gd_machine(pc),-(sp)
	rts
gd_back:
	movea.l	sp,a2
	move.l	(12,a2),d1
	beq.s	gd_back_fn
	movea.l	d1,a0
	move.l	(16,a2),(a0)			; p_run as it was
gd_back_fn:
	move.w	(a2),d1
	cmpi.w	#$3e,d1
	beq.s	gd_closed
	cmpi.w	#$3c,d1				; Fcreate, Fopen: the machine's handle kept, ours returned
	bcs.s	gd_end
	cmpi.w	#$3d,d1
	bhi.s	gd_end
	tst.l	d0
	bmi.s	gd_end
	lea	gd_handles(pc),a0
	moveq	#GD_HANDLES-1,d1
gd_free:
	tst.w	(a0)+
	dbmi	d1,gd_free
	bmi.s	gd_slot
	moveq	#-35,d0				; ENHNDL: no handle of ours left
	bra.s	gd_end
gd_slot:
	move.w	d0,-(a0)
	lea	gd_handles(pc),a1
	move.l	a0,d0
	sub.l	a1,d0
	lsr.l	#1,d0
	addq.l	#6,d0
	bra.s	gd_end
gd_closed:					; Fclose: its place free again
	move.w	(2,a2),d1
	lea	gd_handles(pc),a0
	moveq	#GD_HANDLES-1,d2
gd_find:
	cmp.w	(a0)+,d1
	dbeq	d2,gd_find
	bne.s	gd_end
	move.w	#-1,-(a0)
gd_end:
	lea	(20,sp),sp
	movem.l	(sp)+,d1-d2/a0-a2
	rte
gd_bad_name:
	moveq	#-33,d0				; EFILNF: an empty name, or one with no end, as GOS answers
	cmpi.w	#$3b,(a2)			; Dsetpath(""): the path as it is, and 0, as GOS
	bne.s	gd_end				; (Slightly Magic sets it before each file)
	moveq	#0,d0
	bra.s	gd_end

; The name at a0, cut to 8.3 into gd_name; carry set when it is empty or has no end within 255
; bytes: Hatari passes a call with an empty name to the GEMDOS it chains to, here the ROM's (Battle
; Probe opens ""), and an endless one would run past gd_name.
gd_cut:
	tst.b	(a0)
	bne.s	gd_cut_go
	ori	#1,ccr
	rts
gd_cut_go:
	move.l	a3,-(sp)
	lea	(255,a0),a3
	lea	gd_name(pc),a1
gd_part:
	move.l	a1,d2				; the part's first character
	moveq	#8,d1				; a part's name: 8 characters
gd_char:
	cmpa.l	a3,a0
	bcc.s	gd_too_long
	move.b	(a0)+,d0
	beq.s	gd_trim
	cmpi.b	#$5c,d0				; backslash
	beq.s	gd_trim
	cmpi.b	#'.',d0
	beq.s	gd_dot
	subq.w	#1,d1
	bmi.s	gd_char				; past 8.3: GEMDOS drops it
	move.b	d0,(a1)+
	bra.s	gd_char
gd_dot:
	move.b	d0,(a1)+
	moveq	#3,d1				; its extension: 3
	bra.s	gd_char
gd_trim:					; a part ends: a dot it ends with goes, as GEMDOS reads
	cmpa.l	d2,a1				; "RESIDENT." (Video Kid); not "." or ".."
	beq.s	gd_put
	cmpi.b	#'.',(-1,a1)
	bne.s	gd_put
	move.l	a1,d1
	subq.l	#1,d1
	cmp.l	d2,d1
	beq.s	gd_put
	cmpi.b	#'.',(-2,a1)
	beq.s	gd_put
	subq.l	#1,a1
gd_put:
	move.b	d0,(a1)+
	bne.s	gd_part				; a backslash: the next part
	movea.l	(sp)+,a3
	move.w	(a2),d0				; the function again; carry clear
	rts
gd_too_long:
	movea.l	(sp)+,a3
	ori	#1,ccr
	rts

; Pexec 0 (load and go) and 3 (load): GOS's Pexec would read the program through its own file
; code, by sectors. So: Fopen and Fread through the machine, GOS's Pexec 5 for the basepage and
; its TPA, the text and data read into it, relocated, the BSS cleared (and the rest of the TPA,
; unless the program's fastload bit is set, as TOS 1.04 does), the basepage filled in. Pexec 3
; returns the basepage; for Pexec 0 the caller's call is made Pexec 6 (the memory given to the
; program, as TOS 1.04's Pexec 0 does) and handed to GOS. Other modes: GOS's.
gd_pexec:
	move.w	(2,a1),d0
	beq.s	gd_exec
	cmpi.w	#3,d0
	bne.w	gd_to_gos
gd_exec:
	movem.l	d3-d7/a3-a6,-(sp)
	movea.l	a1,a5				; function, mode, name, command line, environment
	lea	(-28,sp),sp
	movea.l	sp,a4				; the program's header
	clr.w	-(sp)				; Fopen(name, 0)
	move.l	(4,a5),-(sp)
	move.w	#$3d,-(sp)
	trap	#1
	addq.l	#8,sp
	move.l	d0,d7
	bmi.w	gd_exec_end
	pea	(a4)				; Fread(handle, 28, header)
	pea	(28).w
	move.w	d7,-(sp)
	move.w	#$3f,-(sp)
	trap	#1
	lea	(12,sp),sp
	moveq	#-66,d3				; EPLFMT
	cmpi.l	#28,d0
	bne.w	gd_exec_close
	cmpi.w	#$601a,(a4)
	bne.w	gd_exec_close
	move.l	(12,a5),-(sp)			; Pexec(5, 0, command line, environment): GOS's
	move.l	(8,a5),-(sp)
	clr.l	-(sp)
	move.w	#5,-(sp)
	move.w	#$4b,-(sp)
	trap	#1
	lea	(16,sp),sp
	move.l	d0,d3
	bmi.w	gd_exec_close
	movea.l	d0,a6				; the basepage
	lea	(256,a6),a3			; the text's place
	move.l	(2,a4),d4			; text
	move.l	(6,a4),d5			; data
	move.l	(10,a4),d6			; BSS
	move.l	d4,d1
	add.l	d5,d1
	add.l	d6,d1
	move.l	(4,a6),d2			; p_hitpa
	sub.l	a3,d2
	moveq	#-39,d3				; ENSMEM
	cmp.l	d1,d2
	bcs.w	gd_exec_free
	move.l	a3,-(sp)			; Fread(handle, text + data, text's place)
	move.l	d4,d1
	add.l	d5,d1
	move.l	d1,-(sp)
	move.w	d7,-(sp)
	move.w	#$3f,-(sp)
	trap	#1
	lea	(12,sp),sp
	moveq	#-66,d3
	move.l	d4,d1
	add.l	d5,d1
	cmp.l	d1,d0
	bne.w	gd_exec_free
	lea	(a3,d1.l),a2			; the BSS's place
	tst.w	(26,a4)				; ph_absflag: no relocation
	bne.s	gd_exec_bss
	clr.w	-(sp)				; Fseek(28 + text + data + symbols, handle, 0)
	move.w	d7,-(sp)
	moveq	#28,d0
	add.l	d1,d0
	add.l	(14,a4),d0
	move.l	d0,-(sp)
	move.w	#$42,-(sp)
	trap	#1
	lea	(10,sp),sp
	move.l	a2,-(sp)			; Fread(handle, the TPA left, BSS's place): the fixups
	move.l	(4,a6),d0
	sub.l	a2,d0
	move.l	d0,-(sp)
	move.w	d7,-(sp)
	move.w	#$3f,-(sp)
	trap	#1
	lea	(12,sp),sp
	moveq	#4,d1
	cmp.l	d1,d0
	blt.s	gd_exec_bss			; none
	movea.l	a2,a0
	move.l	(a0)+,d1
	beq.s	gd_exec_bss
	lea	(a3,d1.l),a1
	move.l	a3,d2
	add.l	d2,(a1)
gd_fix:
	moveq	#0,d1
	move.b	(a0)+,d1
	beq.s	gd_exec_bss
	cmpi.b	#1,d1
	bne.s	gd_fix_at
	lea	(254,a1),a1
	bra.s	gd_fix
gd_fix_at:
	adda.l	d1,a1
	add.l	d2,(a1)
	bra.s	gd_fix
gd_exec_bss:
	move.l	(4,a6),d1			; up to p_hitpa, or the BSS alone with fastload
	sub.l	a2,d1
	btst	#0,(25,a4)			; ph_prgflags bit 0: fastload
	beq.s	gd_exec_clear
	move.l	d6,d1
gd_exec_clear:
	movea.l	a2,a0
	move.l	d1,d0
	lsr.l	#2,d0
	bra.s	gd_clear_next
gd_clear:
	clr.l	(a0)+
gd_clear_next:
	subq.l	#1,d0
	bpl.s	gd_clear
	andi.w	#3,d1
	bra.s	gd_clear_byte_next
gd_clear_byte:
	clr.b	(a0)+
gd_clear_byte_next:
	dbf	d1,gd_clear_byte
	move.l	a3,(8,a6)			; p_tbase, p_tlen, p_dbase, p_dlen, p_bbase, p_blen
	move.l	d4,(12,a6)
	lea	(a3,d4.l),a0
	move.l	a0,(16,a6)
	move.l	d5,(20,a6)
	move.l	a2,(24,a6)
	move.l	d6,(28,a6)
	move.w	d7,-(sp)			; Fclose(handle)
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	move.l	a6,d0
	tst.w	(2,a5)
	bne.s	gd_exec_end			; Pexec 3: the basepage
	move.w	#6,(2,a5)			; Pexec 0: the caller's own call becomes Pexec(6, 0,
	clr.l	(4,a5)				; basepage, 0), and goes to GOS as the caller made it,
	move.l	a6,(8,a5)			; its frame on the caller's stack: GOS keeps the
	clr.l	(12,a5)				; caller's context there while the program runs, as
	lea	(28,sp),sp			; for its own Pexec 0 (a call from here kept it on the
	movem.l	(sp)+,d3-d7/a3-a6		; supervisor stack, which the program then overwrote:
	bra.w	gd_to_gos			; Erik's intro returned through garbage)
gd_exec_free:
	move.l	(44,a6),-(sp)			; Mfree its environment and basepage
	move.w	#$49,-(sp)
	trap	#1
	addq.l	#6,sp
	move.l	a6,-(sp)
	move.w	#$49,-(sp)
	trap	#1
	addq.l	#6,sp
gd_exec_close:
	move.w	d7,-(sp)			; Fclose(handle), the error in d3
	move.w	#$3e,-(sp)
	trap	#1
	addq.l	#4,sp
	move.l	d3,d0
gd_exec_end:
	lea	(28,sp),sp
	movem.l	(sp)+,d3-d7/a3-a6
	movem.l	(sp)+,d1-d2/a0-a2
	rte

; The driver GOS takes: drives A and B go to GOS's own floppy routines, as PP's path has them;
; drive C has a BPB, so that a game that asks for it before its files (Getbpb(2): Starblade,
; Windsurf Willy, as the Silmarils games of solutions.md 3.2) goes on to read them by name;
; it is never changed, and its sectors fail.
gd_bpb:
	cmpi.w	#2,(4,sp)
	bcc.s	gd_bpb_c
	move.l	gd_flop(pc),-(sp)
	bne.s	gd_chain
	addq.l	#4,sp
	moveq	#0,d0				; no floppy routine: no BPB
	rts
gd_bpb_c:
	lea	gd_bpb_data(pc),a0
	move.l	a0,d0
	rts
gd_rw:
	cmpi.w	#2,(14,sp)			; rwflag, buffer, count, record, drive
	bcc.s	gd_fail
	move.l	gd_flop+4(pc),-(sp)
	bne.s	gd_chain
	addq.l	#4,sp
gd_fail:
	moveq	#-1,d0
	rts
gd_mediach:
	cmpi.w	#2,(4,sp)
	bcc.s	gd_not_changed
	move.l	gd_flop+8(pc),-(sp)
	bne.s	gd_chain
	addq.l	#4,sp
	moveq	#-1,d0
	rts
gd_not_changed:
	moveq	#0,d0
	rts
gd_chain:
	rts					; to the routine pushed
gd_flop:
	dc.l	0,0,0				; GOS's hdv_bpb, hdv_rw, hdv_mediach for drives A and B
gd_bpb_data:					; FAT16, 512-byte records, 1 KB clusters
	dc.w	512,2,1024,32,128,129,289,32000,1
gd_machine:
	dc.l	0
gd_gos:
	dc.l	0
gd_mach_run:
	dc.l	0				; the machine's p_run
gd_gos_run:
	dc.l	0				; GOS's
; Dfree, Dsetpath, Fcreate, Fopen, Fclose, Fread, Fwrite, Fdelete, Fseek, Fattrib, Dgetpath,
; Fsfirst, Fsnext, Fdatime
gd_functions:
	dc.b	$36,$3b,$3c,$3d,$3e,$3f,$40,$41,$42,$43,$47,$4e,$4f,$57,0
	even
gd_handles:
	dcb.w	GD_HANDLES,-1			; the machine's handle of each of ours, -1 when free
gd_bcbs:
	dcb.b	4*20,0				; the two lists' buffer control blocks
gd_name:
	dcb.b	256,0				; a name cut to 8.3
gd_forward_end:
patch_end:
