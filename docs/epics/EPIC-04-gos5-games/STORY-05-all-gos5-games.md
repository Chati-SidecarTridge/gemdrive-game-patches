---
id: STORY-05
epic: EPIC-04
title: The 87 GOS5 games from the GEMDOS drive
status: in-progress
---

## Goal

Every game of the `FIXGOS5` group, patched by STORY-04's tool, is run from the GEMDOS drive with
`run_all.py`'s rules. The verdicts are updated, and each failure is listed with its cause.

## Tasks

- [x] The 87 games patched (copies under `tools/dev/builds/`) and run from the GEMDOS drive on ST
      TOS 1.04, and on STE TOS 1.62 for the STE games, each at the RAM of its STORY-05 run.
      (batch-1311, at the card's RAM; none of the 87 is an STE game: "STE" is only inside
      Jupiter's Masterdrive's and Grand Monster Slam's names.)
- [ ] Each run looked at, as in EPIC-03 STORY-05. A game that does not run is traced, and its
      cause is listed.
- [ ] `migration.csv`: a game that runs patched gets its new verdict, with the tool as its
      solution, through `verdicts.py` (findings with the evidence).
- [ ] The games that remain, each with what would take it further.

## Acceptance

Every game of the 87 has a run of its patched copy and a verdict, and the counts are recorded
here.

## Notes

### Diego's STE, TOS 1.62, Multidevice GEMDRIVE (2026-10-15)

The card's `FIXGOS5` holds the 78 builds that reached their title, menu or play in Hatari
(batch-2205; the 9 others keep PP's originals). Diego plays them in the card's order, power-cycling
between games. 73 of the 78 work:

| Game | On the STE |
|---|---|
| The 66 builds of `1MB/ALI-ZOU`, Alien Storm to Z-Out, but for the four below (its 8 others keep PP's originals: Fire and Forget II, Forgotten Worlds, Jetsons, Magic Boy, Muzzy, Popeye 2, Prison, Venus the Flytrap) | work (62) |
| Awesome | hangs on its title screen, after the Psygnosis screen |
| Cadaver | slow to start; in the first area he walks to the swamp, presses the key, "Expanding data" shows again, then it halts |
| Pit Fighter | black screen after its "Loading" screen, the music playing; works with a floppy in drive A (2026-10-16) |
| Robocop 2 | two bombs on its picture screen |
| Chaos Engine | black screen, not responding, after its first loading screen; works with a floppy in drive A (2026-10-16) |
| The other 11 builds of `2MB/BAT-WRA`, Bat 2 to Wrath of the Demon (Heimdall keeps PP's original) | work (11) |

Hatari's batch runs press no key, so they ended on Awesome's title and on Cadaver's language
menu: neither was tested past the screen where it fails on the STE.

**Awesome: the game refuses a cartridge.** Its start code at `$400` (`AWE` offset 5120, loaded
through GOS's `$80400` bounce) masks interrupts and loops on `cmpi.l #$ABCDEF42,$0FFA0000 / beq $400`
(and `#$FA52235F`, the diagnostic cartridge's); an interrupt handler at `$CB8` (offset `$1CB8`)
repeats the check. The Multidevice's ROM starts with `$ABCDEF42`, so the game stops on its title
whatever the path. Hatari shows the same (PC `$412`, SR `$2709`) on both disks: it inserts its own
cartridge whenever a GEMDOS drive, GEMDOS tracing or autostart is on (`../hatari/src/cart.c`,
`Cart_UseBuiltinCartridge`), so the harness's PPDRIVER reference has a cartridge too and is no
reference for such a check. The two `beq` after the `$ABCDEF42` compare made NOPs in a copy of
`AWE` (offset `$141E` `67E0`, `$1CD0` `6700F72E`): it goes on to the options menu and the credits
on ST 1 MB and STE 4 MB (`tools/dev/builds/gos5/diag/AWESOME-cartfix/`). A data file's patch,
not START.TOS's: the patcher's choice (EPIC-09). A scan of every `FIXGOS5` file found no other
`$ABCDEF42` compare (packed data not covered; NINJARMX's `N1A` compares `$FA52235F` only).

**Cadaver: not reproduced in Hatari.** Past the story and the language menu, the game's GOS loads
(11 opens of `CA2`, 512 B to 72 KB) go through gd_forward on both disks alike, also with keys
pressed during them; the first room shows the same on both, on ST 1 MB and STE 4 MB; GEMDRIVE's
stack area and the forwarder stay intact; F9 (PP's Gamex hook) quits to the desktop on both.
PP's README: "Ingame load/save is disabled. Instead use gamex (F9)". Waiting for what was on
screen when it failed on the STE.

**Pit Fighter: the game waits for the floppy drive's motor to stop.** After `P1A`'s 210,000-byte
load ("LOADING" on the screen at `$78300`), the code at `$B698` clears both screens and calls
`$708E`, which loops at `$7094`-`$70AC`, interrupts on (the music plays), until the FDC's status
bit 7 (motor on) clears. TOS's floppy probe at boot (PC `$FC160A`) turns the motor on, and the
WD1772 turns it off only after 9 index pulses, which an empty drive never gives. The same hang in
Hatari with drive A empty, on ST 1 MB, STE 4 MB and PP's PPDRIVER path alike
(`tools/dev/logs/20261016-002753`, `-002755`, `-002759`; FDC traces `20261016-003448`, `-003449`).
With a blank disk in A (the debugger's `setopt --disk-a`) the motor stops and the game goes on to
the fighter selection, the fight and the high scores, its `P2A`/`P2B` loads through gd_forward
(`20261016-004027`, `-004031`). The wait's `bne.s` made a NOP in a copy of `P1A` (`66F6` at offsets
`$1249C` and `$4018`, the routine's two copies) plays with drive A empty
(`tools/dev/builds/gos5/diag/PITFIG-motorfix/`, `20261016-004431`, `-004433`): another data
file's patch. The game turns keys into the joystick in its keyboard handler (`$6756`, table
`$6A3E`): Z, X, P, L and left Shift for fire. The same wait's bytes are in Venus the Flytrap's
`VF1` and Fire and Forget II's `FF2.FIC` (both black in Hatari), and in Exile, Flimbo's Quest,
Jim Power, Last Ninja 3, Pegasus, Shadow of the Beast, Shadow Warriors, Shinobi and Nose Cop,
some of which work on the STE: the bytes alone do not make a hang.

**Robocop 2: our change's fault, fixed.** During its five `R2A` loads (the box-art picture on the
screen, about 10 s) the keyboard ACIA's vector (MFP VR `$48`: `$118`) is still TOS 1.62's handler
(`$E03CA0`); the game takes it only about 91 VBLs after the last load (PC `$3C49E`), and has by
then written over TOS's variables in low RAM (`etv_timer`, `vblqueue`, `colorptr`). A key, the
mouse or the joystick during a load: gd_quiet found the byte in the ACIA and handed it to `$118`,
TOS's handler ran on the game's RAM, and TOS's VBL faulted on `colorptr` (two bombs, then a double
bus fault). PP's path leaves the byte in the ACIA. Space pressed during the start crashes it on
STE 4 MB (`tools/dev/logs/20261016-004001-ste-162-gemdrive-diag-robocop2-space-ours`) and not on
PP's path (`…-ppdriver-diag-robocop2-space-pp`). Fix: gd_quiet hands a byte only to a handler below
its own block, the game's (not TOS's in ROM nor GOS's), in `gos5_patch.s` and `lemld2_gemdrive.s`:
Robocop 2 with space pressed through its loads reaches the title on STE 4 MB and ST 1 MB, and plays
level 1; Lemmings' first level 12/12 on both, its bytes still handed over (through `$18`). Ruled
out first: the Multidevice's RAM use and timing emulated (its stack at `$B7100`, ILLEGAL over GOS's
`_dskbufp` `$D1D44`, a nested `Dgetdrv`, slow masked loads), no change; the game never writes
`$B6000`-`$B7180`; no cartridge check (`tools/dev/builds/gos5/diag/ROBOCOP2-20261016-002000/`).

**After the keyboard fix** (batch-0049, all 87 on ST TOS 1.04 at the card's RAM): the same results
as batch-2205 but one, Popeye 2, which now plays (its s45 is the game, score 1220): its crash came
from the space bar handed to TOS's handler during a load, Robocop 2's cause.

**Chaos Engine: not reproduced in Hatari.** Our build and PP's PPDRIVER path alike on STE 4 MB:
PP's "Press L" screen, his picture (`CHAOSE.PCH`, 5-12 s), the intro (about 70 s of mostly black
screens with dim text fading, which ignores space at first), the game's "LOADING", Select Players,
the attract mode; with L pressed, with space every 1.6 s for 120 s (play, the shop), with a disk in
A, and with the Multidevice's RAM use and slow reads emulated at the 2 MB addresses. The keyboard
interrupt is off at the first load, then the intro's (`$61ED8`) and the game's (`$A7B4`) handlers:
never TOS's. No cartridge compare in its RAM; nothing written in `$190000`-`$197180`; GOS's
`_dskbufp` `$1B1ABE`. Asked Diego which loading screen, and how long he waited
(`tools/dev/builds/gos5/diag/CHAOSE-20261016-005246/`).

**The info screen's lines.** Every launcher's info screen (show_info, which starts with lea of
ESC E ESC Y '0' ' ', called once by a bsr.w after Vsync: all 87) is turned to gd_info, which adds
"Patched for GEMDRIVE HD by SidecarTridge" at row 9 and, built with `--floppy`, "Insert any floppy
disk in drive A" at row 11, between the game's cheat keys (row 0) and PP's machine lines (row 16)
(`tools/dev/logs/20261016-012411-ste-162-gemdrive-info2-pitfig`, `…-012420-…-info2-aliensto`).

**Fire and Forget II, Venus the Flytrap: the floppy motor wait; Heimdall: prompts.** Built by the
tool and run beside PP's PPDRIVER path on ST at the game's RAM and STE 4 MB, both paths alike:
- Fire and Forget II: drive A empty, black, at PC `$2CD0A` in `move.w #$80,$FFFF8606 / move.w
  $FFFF8604,d0 / tst.b d0 / bmi.s` (`20261016-004820` to `-004831`); a disk in A, the title, the
  high scores and the demo, its loads through gd_forward (`-004932` to `-004946`, `-012126`,
  `-012130`). `FF2.FIC` is packed, but the wait's `bmi.s` is literal at offset `$6EC0` (`6BF8` to
  `4E71` changes only `$CD26` unpacked): with A empty it reaches the title and the demo
  (`tools/dev/builds/gos5/diag/FIREFORG-motorfix/`; `-010725`, `-010851`, `-012336`, `-012445`).
- Venus the Flytrap: drive A empty, black after the trainer screen, at PC `$CA1E`, interrupts
  masked, waiting for the motor bit (`-005001` to `-005118`); a disk in A, the story, the title and
  play, `VF2` loaded through gd_forward (joystick 1 at `$7498`; `-005135`, `-010654`, `-010743`,
  `-010854`). `VF1` offset `$1E1E` `66F6` to `4E71`: plays with A empty on ST and STE
  (`tools/dev/builds/gos5/diag/VENUSFT-motorfix/`; `-011011`, `-011855`).
- Heimdall: not black: "Do you wish to skip the intro (y,n)" (the key at `$C9F9`, `$15` or `$31`);
  y, then 2 ("Play but skip attribute sections") reaches the crew selection on ST 2 MB and STE
  4 MB, ours and PP's alike, drive A empty, its `HE0` loads through gd_forward (`-012249` to
  `-012446`, `-013318` to `-013850`). It runs.

**Cadaver: the game's own restart, on PP's path too.** The "swamp" is the water of the first room
("Cavern"): the hero walks in (fire and down on the joystick byte `$18C95`), his energy empties,
fire and up restarts, "EXPANDING DATA" shows again, the same 11 GOS loads of `CA2` run (3,584 to
133,120, 512 B to 72 KB, through the game's GOS stub at `$140`), and the main loop's object-script
interpreter (`jsr $10132` at `$7564`) jumps into level data at `$6C04C`: an illegal instruction
whose vector (`$10`) is the game's bare `rte` (`$15510`), forever, the VBL (`$1552E`) still
running. The same on the card's build (`tools/dev/logs/20261016-013315-…-old`), the current block
(`-013320-…-new`), PP's original through PPDRIVER (`-013918-…-orig2`, 59 Rwabs) and with a disk in A
(`-033912-…-floppy`), STE 4 MB. PP's README: in-game load and save disabled, F9 for Gamex's state.
Its slow start is the game's own unpacking: from the language key to the first room 11 loads
(44 GEMDOS calls, 138,240 bytes) and about 1,470 VBLs on either path (907 after the 72 KB load,
386 after the 29.7 KB one); on the Multidevice, ours is about 1-2 s of it (the round trips, the
transfer, gd_quiet's 11 × 4.5 ms).

**With the info screen's lines** (batch-0125, and batch-0125-redo for six of its runs): Warp and
Popeye 2 end in crashes (TOS's `Pterm(-1)` after their first GOS load), the rest as batch-0049.
Not settled. Warp's batch-0049 "runs" was wrong: its s45 is black, the machine in a loop at `$5B6`
with interrupts masked (`20261016-011235`). Its first load comes about 30 s in (PP's info screen
times out after 1,177 VBLs), when the generic expectation presses space, so where that key lands
decides the run; Diego's STE plays the batch-2205 build. The night's runs are no evidence either:
with the Mac's display asleep Hatari ran up to 120 times slower (one 60 s run took 7,188 s), and
the expectation's keys go by the host's clock. Next: Warp and Popeye 2 with a key pressed at a
fixed point of the first load, on the batch-2205, batch-0049 and current builds and on PP's path.

**Warp and Popeye 2, settled** (`tools/dev/builds/gos5/keytest-1250/`, ST 1 MB, each build with no
key and with space every 0.5 s from 20 s): Popeye 2 crashes with the keys on every build and on
PP's PPDRIVER path alike, and runs without them on all: the game's, not ours. Warp with the keys:
PP's path reaches its title; the batch-2205, batch-0049 and batch-0125 builds end black or in
`Pterm(-1)`: ours. At gd_quiet's delivery (`20261016-130039-…-warp-0125-deliver`) the caller is
Warp's own loader at `$5BE`-`$610` (no SR saved, `jsr (a0)` into file_io at `$602`, return `$604`),
running at `$2700`; `$118` is its handler at `$590`, which reads the ACIA through `a3`
(`move.b (a3),d1`), set to `$FFFC00` in Warp's own code only: called from file_io with `a3`
`$0FF0F00F` it loops at `$594`-`$5B6` forever. PP's path never calls it there, the game's own SR
masking it. Fix: gd_quiet hands a byte on only when the game's SR is below level 6: the caller's,
or, after PP's loader (`jsr (a0)` returning to `clr.w $c0734.l` and/or `move.w (loader_sr,pc),sr`),
the one it keeps in `loader_sr` (`gos5_patch.s` and `lemld2_gemdrive.s`). With it, keys as above
(`tools/dev/builds/gos5/keytest-1250/sr/`, `tools/dev/logs/20261016-130352-*`): Warp reaches its
title as PP's (10 loads, 2 bytes handed on), Lemmings' first level 12/12 (3 handed on), Robocop 2
on STE 4 MB with space no crash (1 handed on), Popeye 2 as PP's; `all_harness.sh` 0 failures.

**On the STE with a floppy in drive A** (2026-10-16): Pit Fighter and Chaos Engine play. Chaos
Engine's wait does not show in Hatari (it ran there with drive A empty), so it is known from the STE
only. The builds that show "Insert any floppy disk in drive A" (`--floppy`): Pit Fighter, Chaos
Engine, Fire and Forget II, Venus the Flytrap.

**With the game's-SR check** (batch-1311, all 87, ST TOS 1.04): 83 run, Forgotten Worlds back to
the desktop, Jetsons, Magic Boy and Prison crash, as batch-0049; every 45 s screenshot of the 82
games for the card looked at: black only for Fire and Forget II, Pit Fighter and Venus the Flytrap
(drive A empty), Heimdall at its y/n prompt, Warp at its title.

**The five left** (`tools/dev/builds/gos5/five-1338/`, our builds, no key and with a disk in A):
- Forgotten Worlds' launcher asks for `D15R_5H.FIC` and `D15R_5F.FIC`; its download has
  `D15R_H5.FIC` and `D15R_F5.FIC`, an older GOS build (`c2964ac2…`, also Jetsons', Magic Boy's,
  Muzzy's, Matrix Marauders' and Shadow Warriors'). With the `D15R_5H.FIC` 56 games carry
  (`0dcbaa0e…`, all alike) it reaches its title, with and without keys and a disk; with its own
  file under that name the CPU halts once it is loaded. Fixed by the two files added beside it.
- Jetsons: drive A empty, the CPU halts after `EXE1`; a disk in A, no halt: its title, and with
  space its picture (`20261016-134319-…-JETSONS-disk-keys`). Built with `--floppy`, to try on the
  STE.
- Muzzy (CPU halt), Prison (`PR1`, then `Pterm(-1)` in a loop) and Magic Boy (CPU halt after its
  GOS file) fail the same with a disk in A: still open.

**The card's builds** (`tools/dev/builds/gos5/card-1335/`, `written.txt`): 84 start programs, the
batch-1311 builds byte for byte (the five games with `--floppy` one byte apart, the flag), and
Forgotten Worlds' two GOS files.
Written to Diego's card 2026-10-16 (`/Volumes/IMG/PPHD/FIXGOS5/`): the 86 files of `card-1335`, each
read back by SHA-256; what they replaced checked first: 78 of our batch-2205 builds, 6 PP originals
(Fire and Forget II, Popeye 2, Venus the Flytrap, Heimdall, Forgotten Worlds, Jetsons), and 2 new
files (Forgotten Worlds' `D15R_5H.FIC`, `D15R_5F.FIC`). Muzzy, Magic Boy and Prison keep PP's.
Diego, 2026-10-16, on the STE from that card: "it works. i have not tested all the previously
teste games, but it is ok."

**The verdicts** (2026-10-16): the 84 games that run with their build have a finding each
(`src/survey/findings.tsv`: verdict fix, the build and what else they need) and their solution
(`src/survey/solutions.tsv`: "S1: GOS reads through the GEMDOS drive (tools/build_gos5.py,
EPIC-04)", with a disk in drive A for five, Awesome's cartridge check, Forgotten Worlds' files);
`verdicts.py`: the counts unchanged (1,608 as it is, 212 fix, 10 unsure, 1 not feasible), 87 rows'
reason and solution new; `build_site.py --check` 0 problems. Muzzy, Magic Boy and Prison wait for
their traces.
