---
id: STORY-02
epic: EPIC-04
title: The reference's first level: the address error at $2B10
status: done
---

## Goal

Know why Lemmings, booted from the PPDRIVER image in Hatari, raises an address error after
loading `LEVEL020`, and get past it, because Lemmings' play session (STORY-03) needs a first
level. This is the candidate found in EPIC-01 STORY-01 (`ITERATIONS.md`).

## Tasks

- [x] The error again, on ST TOS 1.04 and STE TOS 2.06 from PPDRIVER: `$2B10`,
      `move.l (a0)+,(a1)+`, with `a0 = $3E409` taken from `($36,a3)`.
- [x] Where `($36,a3)` gets its odd value: the game's code, PP's patches to it (EPIC-02 STORY-04),
      or Hatari. Traced back from the load.
- [x] What gets past it without changing Hatari (C-02), and its cost; or, if it is Hatari's, the
      evidence for a report (which waits for Diego, D-15).
- [x] The first level reached from PPDRIVER, and then from the GEMDOS drive with STORY-01's build.

## Acceptance

Lemmings reaches its first level in Hatari from both disks, or the cause is shown in a trace and
Diego decides what to do next.

## Notes

### The cause: an IKBD packet cut by the load (2026-10-15)

Diego's STE (TOS 1.62, 4 MB) with STORY-01's build on the Multidevice: the title, then three
bombs on a click on "1 PLAYER". The same stop as in Hatari, so not Hatari's.

- **The fault** (STE TOS 1.62, 4 MB, GEMDOS drive, `tools/dev/logs/20261015-174302-ste-162-gemdrive-crash-at`):
  at `$2B0E`, `move.l (a0)+,(a1)+` with `a0 = $2ECE7`, in the game's VBL handler (`$70` is `$2936`,
  SR `$2400`). `a0` is built at `$29C8`-`$29F4` from an object's x and y (`(6,a3)`, `(8,a3)`), a
  row table at `$C910` indexed by y, and a base at `($A0,a5)`. The object at `$26C86` is the mouse
  pointer: x `$0046` (70, where the harness put the mouse), y `$F700`. A y that large indexes
  `$1200` bytes before the table and takes an odd word.
- **The y is the next packet's header.** Lemmings keeps the IKBD in absolute mode and asks for the
  position at every VBL (`F7 buttons xh xl yh yl` back). Hatari's ACIA trace (`--trace
  acia,ikbd_cmds`, `20261015-174840-ste-162-gemdrive-ikbd3`): in VBL 9212 the game had read
  `F7 00 00 46` when it sent `AbsMouseMode 292,155` and called the loader for `level020`. PP's
  loader in the game (`$E8F0`-`$E910`) masks interrupts and calls `file_io`, which turns the MFP's
  interrupts off: `00 96` overran in the ACIA (`clock_rx overrun rsr=0x96`, the run's only overrun),
  and `file_io`'s last loop read what was left. The game, still waiting for y, took the next
  packet's `F7 08`: y `$F708`, and every packet after it two bytes out of step.
- **PP's own launcher does it too**: from PPDRIVER on ST TOS 1.04 and STE TOS 2.06, the same
  instruction with the pointer's y `$F708` and `$F700` (`20261015-180541-st-104-ppdriver-ref-crash`,
  `20261015-180602-ste-206-ppdriver-ref-crash`). It is PP's adaptation's race, whatever the disk;
  Lemmings meets it every time, as it starts the level load while an answer is arriving.

**The fix: `gd_quiet`** (`src/gemdrive/lemld2_gemdrive.s`). `gd_start` puts a `jmp` to it at
`file_io`'s first instruction (`$C0170`, in RAM, when the bytes are `41FA 033E 40D0`). With
interrupts still masked, it watches the keyboard ACIA until no byte has come for about 4.5 ms
(1,200 loops of 30 cycles at 8 MHz, longer than the IKBD takes to answer a poll). It hands each
byte that comes to the game's keyboard interrupt as the MFP would: through the vector the MFP's
vector register gives channel 6, and only while that interrupt is enabled, unmasked and not in
service, and the ACIAs' line (`GPIP4`) asks for it. Then `file_io`'s first two instructions, and on.
With no packet on its way, none is cut. During the load GOS's own VBL is in, so the game asks for
nothing. After 200 bytes it goes on anyway. Cost: about 4.5 ms per load.

Two first versions failed, and the reasons shape it:
- **Letting interrupts in to wait** (wrapping `$70` and `$118`). Lemmings' intro checks for space
  in its VBL and calls the loader from there. A VBL let in during the wait called it again. The
  second call saved the wrappers as the old vectors, and `gd_acia` jumped to itself for ever. Diego's
  STE hung after space during the intro. In Hatari, space 2 s into the intro ended in `gd_acia`
  (`20261015-182650-ste-162-gemdrive-space-quiet`). PP's original and the build without the wait go
  on to the title (`20261015-182925-ste-162-ppdriver-space-ref`).
- **Handing bytes to `$118`**. The game sets the MFP's vector register to 0 (`info mfp`: VR `$00`,
  IERB `$40`), so its keyboard interrupt is vector 6, at `$18`. `$118` still holds TOS's handler,
  which reaches its routines through TOS's RAM (`$E8A`, `$E8E`), now the game's code: an address
  error in `$E03CAC` at the click (`20261015-184842-ste-162-gemdrive-poll-pm`). The intro reads the ACIA itself, with
  the MFP's interrupt off, so there the wait steps aside.

| setup | result | run |
|---|---|---|
| STE TOS 1.62, 4 MB / ST TOS 1.04 / STE TOS 2.06 | the title, the click, `level020`, then `objects1`, `ground1`; no crash | `20261015-185257-ste-162-gemdrive-q3-normal`, `…185316-st-104…`, `…185337-ste-206…` |
| STE TOS 1.62, 4 MB, space 0.5, 2, 4, 8 or 12 s into the intro | the title, the click, the level's files; no crash | `…-q3-space-0.5` to `…-q3-space-12` |
| STE TOS 1.62, 4 MB, GEMDRIVE's RAM use emulated | the same | `…-mdemu-stack-dgetdrv-dskbuf-delay40000` (latest) |

The space tests' expect files are in `tools/dev/builds/epic04/space-1850/`.
`gemdrive-first-level.exp` now expects `ground1` after `level020`. The build goes to Diego's card
for the Multidevice. PP's own launcher from PPDRIVER is unchanged and still stops there.

**On Diego's STE from the Multidevice (2026-10-15)**: the first build with `gd_quiet` reached the
level and played; space during the intro (the balloon) then hung it, the cause above. With the
build of `START.TOS` `27c534e8…`, "it works great". The PPDRIVER half of the last task is open: PP's
own launcher is the reference and stays as it is, and our build takes `gd_quiet` only on the GEMDOS
drive's path (`gd_start`). Whether a build from a real disk with PP's driver should get it too is
Diego's to decide.

**Closed (2026-10-15).** From the GEMDOS drive, the first level is reached in Hatari and on Diego's
STE. From PPDRIVER, PP's own launcher keeps its stop: Diego, the same day, "we should only apply
to our changes, not original ppera" (D-17). The acceptance's other branch holds: the cause is shown
in a trace, and Diego decided.
