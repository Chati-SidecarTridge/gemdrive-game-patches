# Why Lemmings fails in Hatari's GEMDRIVE mode

EPIC-01, 2026-10-11. Every claim below was observed in a Hatari 2.6.1 run on this Mac
(`tools/dev/logs/<run>`), on the pristine files (`LEMMINGS.sha256`), with the launcher's
inner program at the text bases of `src/probes/epic01/gate_probe.py` (`text+` offsets are its).
Hypotheses `H-NN` are those of `docs/epics/ITERATIONS.md`.

## The cause, in one paragraph

PP's launcher does not read the game's files through GEMDOS. It demands a **resident PP
hard-disk driver**, recognised by the XBRA header `"XBRA" "PPHD"` twelve bytes before the
routine `hdv_bpb` (`$472`) points to; it copies that driver (7,204 bytes) to `$B7180`,
relocates it, rewires its internals, and installs its own loader, D15R (`D15R_H5.FIC`, at
`$C0100`), which then reads the **FAT volume by sectors** through BIOS `Getbpb`, `Mediach` and
`Rwabs` on drive C, with 1,024-byte logical sectors: the root directory, the `LEMMINGS` and
`FILES` directories, a FAT copy, then every file's clusters. Hatari's GEMDRIVE mode is a
GEMDOS-level emulation: it serves `Fopen`/`Fread` from a host folder through a cartridge hook on
`TRAP #1` and has **no driver, no `BPB` and no sectors**. So the launcher's driver check fails,
its fallback (a raw sector-0 read through the ACSI DMA registers on TOS 1.x, through XBIOS
`DMAread` on TOS 2.x) fails too, and it prints "This prg. requires PP, AHDI or Hddriver hard disk
driver …" and exits. Answering each step by hand from the debugger only exposes the next one:
sector 0, then `Getbpb(2)` (TOS returns 0), then `Rwabs` (TOS returns -15, EUNDEV), then D15R's
error path, which the fallback never initialised. Diego's guess (H-07) holds in substance: it is
the driver, with the correction that the launcher does not embed it but requires PP's own,
resident, and that its loader needs a block device behind it.

## 1. The two setups

Both built by `tools/dev/make_disks.sh` from a copy of `LEMMINGS/` (EPIC-00 STORY-04):

- **GEMDRIVE**: `hatari --harddrive <folder>`; Hatari logs `GEMDOS HDD emulation, C: <-> …` and
  `Gemdos_Boot(GEMDOS_EMU_ON=1)`. Its GEMDOS drive is served by a cartridge program at
  `$FA0000` that intercepts `TRAP #1` (`../hatari/src/cart.c`, `Cart_UseBuiltinCartridge`;
  `$84` held `$FA002A` at the launcher's driver check in every run). BIOS and XBIOS calls are only
  traced (`bios.c`, `xbios.c`), never answered: they reach TOS ROM.
- **PPDRIVER** (the reference): a 32 MB ACSI image from `../atari-hd --ppdriver-bootable`,
  `hatari --acsi 0=<image>`; `GEMDOS_EMU_ON=0`. At boot PPDRIVER's IPL reads LBA 0 and 11
  sectors from LBA 2 (its driver), which stays resident below the TPA.

Three machines: ST TOS 1.04, STE TOS 1.62, STE TOS 2.06, 1 MB.

## 2. What the reference does (`tools/dev/expect/reference-first-level.exp`)

Run `20261011-144024-st-104-ppdriver-first-level`, ST TOS 1.04. After the launcher's own
`Fopen`/`Fread` of `LEMMINGS.PCH`, `D15R_H5.FIC` and `LS2DD.FIC` and `Dsetpath("FILES")`, every
disk access is a BIOS call from D15R's trampoline (`$C83CC` `trap #13`, return `$C83CE`). Mapped
onto the image's directories and FAT (record numbers are 1,024-byte logical sectors; logical
*n* = DOS sectors 2*n*+1, 2*n*+2 of the partition):

| Rwabs recno × count → buffer | what it is |
| --- | --- |
| 65 × 1 → `$B1100` | root directory |
| 81 × 1 → `$B5100` | `LEMMINGS` directory |
| 263 × 1, 264 × 1 → `$B3100`/`$B5100` | `LEMMINGS\FILES` directory |
| 33 × 1 → `$AF100` | FAT copy 2 |
| 387 × 8 → `$60000`, 395, 396 | `PSYGLOGO.IMG` |
| 397 × 8 → `$68000`, 405, 406 | `DMALOGO.IMG` |
| 813, 814, 815 × 100 → `$A00`, 915 | `MAIN` (105,220 bytes) |
| 415 × 80 → `$10000`, 495, 496 | `INTROPAR` (83,362 bytes) |
| 497, 498, 499 × 76 → `$A00`, 575 | `CODE` (80,639 bytes), over `MAIN` |
| 677 × 2, 679, 680 | `LEVELDAT`, at the title, before any click (first written here as after the click; corrected in EPIC-02 STORY-01) |
| 407 × 2 → `$41800`, 409 | `LEVEL020`, the first level's data |

Partial first and last sectors go through the driver's bounce buffers at `$B3100`/`$B5100`; the
directory sector is re-read before each file; `Mediach(2)` is called 7 to 16 times between reads
(PPDRIVER answers 0). The title menu is up about 17 s (host time, fast-forward) after start.
Before all that, on this disk even TOS's own loading of `START.TOS`, `LEMMINGS.PCH`,
`D15R_H5.FIC` and `LS2DD.FIC` is `Rwabs` through PPDRIVER (the reads at 83–91, 141–241,
1047–1092, 243–247 from PC `$FC9206`).

**The title menu is mouse-driven in IKBD absolute mode** (`AbsMouseMode 295,155`,
`SetInternalMousePos 152,72`, then `ReadAbsMousePos` once per frame, 25,597 times in one run; F1,
F2, Return and Space do nothing). Hatari's control socket has no mouse motion, and its debugger's
memory writes bypass the I/O handlers (`STMemory_Write` writes the memory array, so a `w` to
`$FFFC02` never reaches the ACIA). The harness's `mouse x y` step therefore rewrites, for one
frame, the table the game's own IKBD sender reads (`$D0A0`: `01 0D`, one byte, the poll) into
`06 0E 00 xh xl yh yl` (load mouse position) and restores it at the sender's `rts` (`$E996`);
the IKBD then reports the new position and `event doubleclick` clicks there. Clicking "1 PLAYER"
at (70,150) loads `LEVEL020`.

**Open issue: the reference does not reach the first level in Hatari.** Right after the level
load the game raises an address error: `move.l (a0)+,(a1)+` at `$2B10` with `a0 = $3E409` (odd),
taken from `($36,a3)` at `$26CBC`; TOS's handler (vector 3, PC `$3FC0B0A`) ends in `Pterm(-1)`
27 times and the CPU in LS2DD's fault catcher at `$700C8`. The 3,048 bytes at `$41800` equal
`FILES/LEVEL020` byte for byte (run `…-click-exc3`), so the loader is not the cause. The same
happens with X = 72, with 4 MB, and on STE TOS 2.06 (no `Pterm` there, same end). A click that
misses the button (70,125) crashes nothing. Not pursued further in this epic: it is the game's
preview code, or its interaction with Hatari, and it is listed as a candidate in `ITERATIONS.md`.

## 3. Where the GEMDRIVE runs part from the reference (STORY-02)

All three GEMDRIVE runs stop at the same instruction. After `Dgetpath` the launcher executes, at
text+`$324`:

```
movea.l $472.w,a1              ; hdv_bpb
cmpi.l  #$50504844,-8(a1)      ; "PPHD"
bne.w   text+$482              ; no PP driver: the fallback
```

Observed at the `cmpi` and the `bne` (`src/probes/epic01/gate_probe.py`, runs `…-gate`):

| setup | `$472` (hdv_bpb) | long at hdv_bpb−8 | `$516` (pun_ptr) | TOS major | path |
| --- | --- | --- | --- | --- | --- |
| ST 1.04 GEMDRIVE | `$FC173C` (ROM) | `$FFFC4280` | 0 | 1 | fallback, raw ACSI |
| ST 1.04 PPDRIVER | `$12960` | `"PPHD"` | `$12FEC` | – | primary |
| STE 1.62 GEMDRIVE | `$E01914` (ROM) | `$FFFC4280` | 0 | 1 | fallback, raw ACSI |
| STE 1.62 PPDRIVER | `$129A4` | `"PPHD"` | `$13030` | – | primary |
| STE 2.06 GEMDRIVE | `$E05210` (ROM) | `$FFFC4280` | 0 | 2 | fallback, XBIOS DMAread |
| STE 2.06 PPDRIVER | `$14DC4` | `"PPHD"` | `$15450` | – | primary |

The first difference is the value of `hdv_bpb`: TOS's own ROM routine with a GEMDOS drive,
PPDRIVER's with the image. (The first pass called `$472` `_hdv_init`; it is `hdv_bpb`.)

### The fallback, TOS 1.x (text+`$482` → `$BC6`)

`cmp.b #2,text+$832` (TOS major) → `bsr text+$BC6`: `lea text+$8864,a1; moveq #0,d1; moveq #1,d2;
bsr text+$BE8`, which writes the buffer address to `$FFFF860D/860B/8609`, `$0198` and `$0098` to
`$FFFF8606`, the command bytes to `$FFFF8604`, starts the transfer (`$0008`/`$0088`) and waits on
MFP GPIP bit 5 (`$FFFFFA01`) with a 10-tick `_hz_200` timeout (text+`$C90`). With no ACSI device
the wait times out, `d0 = -1` at text+`$BD4`, `bne.w text+$CC0`: the IDE probe saves vector 2,
installs its handler (text+`$D2E`), does `tst.b $FFF00039`, which bus-errors on an ST, lands in
the handler, `d7 = -33`, and the error exit at text+`$83C` prints the message (`Cconws`), waits
for a key (`Cconin`) and ends. Traced instruction by instruction in run
`20261011-141008-st-104-gemdrive-gate` (`windows.txt`).

### The fallback, TOS 2.x (text+`$482` → `$49E`)

`movea.l $516.w,a1; move.b 4(a1),d7` reads the device number from the `PUN_INFO` table a
hard-disk driver installs; with none, `pun_ptr` is 0 and `d7` comes from address 4. Then XBIOS
`DMAread(0, 1, text+$8864, d7)`, TOS's own raw ACSI read, returns -1 and the same error exit
follows (run `20261011-141116-ste-206-gemdrive-gate`). So TOS 2.06 does not "work through
whatever driver is installed" (H-06): it needs a `PUN_INFO` and an ACSI device all the same.

### What the primary path does with the driver (run `…-st-104-ppdriver-gate`, `…-drv`)

From the XBRA header at `$12954` (`"XBRA" "PPHD" $00FC173C`, the chained TOS vector) the launcher
copies 7,204 bytes to `$B7180` (`move.w #$708,d2; move.l (a1)+,(a2)+; dbf`), the driver's code,
data and its variables. Then it:

- writes D15R's routines into the copy's three XBRA "old vector" slots and vector table
  (`$00FC173C → $000C19BE`, `$00FC1A24 → $000C1CA4`, `$00FC18EC → $000C1B6E`, at copy offsets
  `+$9`, `+$3F`, `+$43B`, `+$495..+$49D`), so that what the driver chains to is D15R;
- rewrites the driver's BPB and buffer pointers (`+$771..+$78B`: `$0130D8 → $0B7904`,
  `$00A94E → $0AF100`, …), which is why the reference reads land in `$AF100`–`$B5100`;
- installs the copy's entries in `$472/$476/$47E` (`$B718C`, `$B71C2`, `$B75BE`), sets `$47A`
  to `$C1F3E` (D15R), clears `pun_ptr`;
- by the first `Rwabs`, `TRAP #1` (`$84`) points to `$C84A0` in D15R: a handler that returns 0
  for GEMDOS functions 1 to 11, treats `Super` (`$20`) apart, and saves the context of the rest
  (`src/…/d15r_area.lst`); LEMLD2's own Malloc/Mshrink stub (H-05) is not the vector at that
  point. H-05 stays with EPIC-02.

The resident driver is what PPDRIVER's boot sector installed (LBA 2–14 at boot). Its 5,076
comparable bytes differ from the blob's `.PRG` text in 4,948 places, in 115 runs: the blob's
program is not a plain copy of the resident code (packed or self-relocating), so "is it the same
driver" is settled by provenance, not by bytes.

## 4. The embedded driver (STORY-03): H-07

Restated and confirmed: the launcher carries no driver of its own. It **requires** PP's resident
driver (the XBRA `PPHD` check), reuses it (copied, relocated, patched at fixed offsets, so a
replacement would have to match PPDRIVER's layout at those offsets), and carries its own
**loader**, D15R, which reads the FAT volume by sectors through that driver. Hatari's GEMDRIVE
has neither: no driver signature, no `BPB`, no sectors.

The experiments (`src/probes/epic01/fallback_probe.py`, `serve_rwabs.py`, ST TOS 1.04, GEMDRIVE,
pristine files, the debugger answering the disk by hand):

| answered by hand | what happened next | run |
| --- | --- | --- |
| nothing | error message after the fallback's reads fail | `…-st-104-gemdrive-gate` |
| sector 0 = the image's real PP boot sector (word sum `$1234`) | the launcher goes on (`Kbshift`, 29 `Vsync`), D15R: `Drvmap`, `Getbpb(2)` → TOS returns **0**, address error, `Pterm(-1)` | `…-gemdrive-fallback` (real sector) |
| + `Getbpb(2)` = PPDRIVER's BPB | `Rwabs(0,$D5DB8,1,65,2)` → TOS returns **-15** (EUNDEV), twice; LS2DD address error at `$5FFED` with that -15 in `d0` | `…-gemdrive-fallback` (`--bpb`) |
| + `Mediach(2)` = 0, + `Rwabs` 65 and 81 = the image's sectors | D15R re-reads 81, then runs its error restore at `$C8486` (`movea.l (a0)+,sp` from a context never saved, sp = 0) → bus error on the next push, Hatari halts | `…-gemdrive-serve-02` |

A synthetic sector 0 (first word `$1234`, rest zero) passes the sum check too and leads to the
same `Getbpb` stop. Reverting any answer brings the earlier stop back (the plain runs). The
fallback path never initialises D15R the way the primary path does (the launcher's `jsr` into
D15R's entry table at `$C0100` happens on the primary path), so this is the stop that cannot be
passed by hand: everything past it needs the real driver.

PPDRIVER's BPB for the image, as handed to the launcher's `Getbpb(2)` on the reference
(`…-ppdriver-bpb`, at `$B7620`): recsiz 1024, clsiz 2, clsizb 2048, rdlen 16, fsiz 32, fatrec 33,
datrec 81, numcl 16343, bflags 1.

## 5. Everything GEMDRIVE lacks (STORY-04)

In the order the launcher needs them:

1. **A resident driver with the XBRA `PPHD` header before `hdv_bpb`**, PPDRIVER-shaped: the
   launcher copies 7,204 bytes from the header and patches offsets `+$9`, `+$3F`, `+$43B`,
   `+$495..+$49D`, `+$771..+$78B` of the copy.
2. Failing that, **a raw-readable PP boot sector**: ACSI DMA registers and MFP GPIP 5 (TOS 1.x),
   XBIOS `DMAread` plus a `PUN_INFO` at `$516` (TOS 2.x), word sum `$1234`. And this path still
   does not initialise D15R (above).
3. **BIOS `Getbpb(2)`** returning PPDRIVER's BPB (1,024-byte sectors, the layout above).
4. **BIOS `Mediach(2)`** returning 0 (D15R calls it before each read; its TOS return in GEMDRIVE
   mode was not observed, the runs answered it or crashed before it).
5. **BIOS `Rwabs` on drive 2** serving the whole FAT volume: root directory (65), `LEMMINGS`
   (81), `FILES` (263–264), FAT copy 2 (33), then the clusters of `PSYGLOGO.IMG`, `DMALOGO.IMG`,
   `MAIN`, `INTROPAR`, `CODE`, `LEVELDAT`, `LEVELnnn` and, during play, whatever else the game
   opens (not observed past the first level load, see the open issue).
6. **Fixed memory**: the driver copy at `$B7180`, its buffers at `$AF100`–`$B5100`, D15R at
   `$C0100`, LS2DD at `$70000` (staged from `$81000`, depacked by code at `$80100`, trampoline at
   `$85000`), `MAIN`/`CODE` at `$A00`, `INTROPAR` at `$10000`, the logos at `$60000`/`$68000`,
   the level at `$41800`.
7. **`TRAP #1`** goes to D15R's hook from the first `Rwabs` on; in GEMDRIVE mode Hatari's own
   cartridge hook on `TRAP #1` is what serves the GEMDOS drive. Any fix that wants GEMDOS file
   calls from inside the game has to live with both (to be checked in EPIC-04).

Case of file names (H-04) plays no part: no file name is looked up on the disk after
`Dsetpath("FILES")`; D15R walks directories itself, and Hatari matches GEMDOS-drive names
without regard to case anyway (EPIC-00 STORY-04).

## 6. Hypotheses

| | verdict | where |
| --- | --- | --- |
| H-03 | confirmed, with corrections: `$472` is `hdv_bpb`; on TOS 2.x the device comes from `pun_ptr`; after a good sector 0 the launcher continues into D15R | §3, §4 |
| H-04 | refuted: the pristine launcher never reaches LS2DD's load loop on a GEMDOS drive; pushed past the gate by hand it stops on TOS's -15 from `Rwabs`, not on a name; names are matched case-insensitively | §4, §5 |
| H-05 | left to EPIC-02; observed: the vector at the first `Rwabs` is D15R's `$C84A0`, which does more than Malloc/Mshrink | §3 |
| H-06 | refuted: TOS 2.06 takes the XBIOS path, which is a raw ACSI read on the `PUN_INFO` device; no driver, no `PUN_INFO`, -1 | §3 |
| H-07 | confirmed in substance, restated: not embedded but required and resident; the loader needs a block device | §4 |
| H-01, H-02 | EPIC-02's; consistent with what was seen (LS2DD unpacked to `$70000` from `$81000`, D15R at `$C0100`) | §3 |

## 7. Tools left behind

- `src/probes/epic01/gate_probe.py <setup> <disk>`: the chained breakpoints of §3, with
  bounded instruction traces; `read_probe.py <run>` prints a run's chain and writes
  `windows.txt`.
- `src/probes/epic01/fallback_probe.py <setup> [--synthetic] [--bpb]`: the by-hand answers of §4.
- `src/probes/epic01/serve_rwabs.py <setup>`: one run per `Rwabs`, each answered from the image.
- `tools/dev/hatari_harness.py`: `--trace`, `--key-hold`, and the steps `event`, `debug`,
  `mouse`; `tools/dev/expect/reference-first-level.exp`.
