# Eight games with a small fix

Eight games on the 8bitchip.info website do not start from a GEMDOS drive as they come, each for a
small reason of its own (`solutions.md` §3.2–3.4). A GEMDOS drive serves files by name and has
no disk sectors: Hatari's, or the SidecarTridge Multidevice's GEMDRIVE. Each game has a small fix,
applied once to the user's copy. Seven of the eight then run, in Hatari and with the Multidevice;
Aquanaut does not yet: it reboots on the Multidevice.

| Game | Download | Why it stops | The fix |
|---|---|---|---|
| Crystals of Arborea, Targhan | `ARBOTARG.ZIP` | asks the drive for its BPB before every file | `GDBPB.PRG`, run first |
| Robinsons Requiem | `ROBINSON.ZIP` | the same | `GDBPB.PRG`, run first |
| Storm Master | `STORMMAS.ZIP` | the same | `GDBPB.PRG`, run first, and a floppy in drive A |
| Spy vs Spy 2 | `SPY2.ZIP` | the program it starts is ended at once | the fastload bit, in `SPY2.BOY` |
| Strike Force Harrier | `STRIKEFH.ZIP` | the same | the fastload bit, in `HARRIER.TOS` |
| Aquanaut | `AQUAN.ZIP` | the same, and more | not working yet (below) |
| Rody and Mastico 2 | `RODYM2.ZIP` | its download has no start program | Rody and Mastico 4's `RUNME.TOS` |

## A BPB for GEMDOS and GEMDRIVE: `GDBPB.PRG`

A BPB (BIOS parameter block) tells TOS the layout of a drive. The four Silmarils games start with a
`START.PRG` that asks BIOS `Getbpb` for the current drive's BPB before each file it opens. Once it
gets one, it opens the file by name. A GEMDOS drive has no BPB, so TOS answers with none. The
program then asks again forever, and the screen stays still.

`GDBPB.PRG` stays in memory, in 82 bytes. It answers for any drive from C: up that has no BPB of
its own, so the GEMDOS drive's letter does not matter. Floppies, and drives that a hard-disk driver
serves, keep their own answers. It is built from `src/gemdrive/gdbpb.s`. Run it once after each
reset or power-on, before the game. It prints "GEMDOS drive BPB installed", or "already installed"
when run again. A reset removes it.

Storm Master also reads the floppy drive itself at its credits, without TOS, and waits there for an
answer. Put any floppy in drive A. The game does the same from a hard disk with the PPDRIVER
driver.

## The fastload bit: `tools/set_fastload.py`

The fastload bit is bit 0 of byte 25 of a program's header. When it is set, the loader leaves the
program's free memory as it is instead of clearing it.

The start programs of Spy vs Spy 2, Strike Force Harrier and Aquanaut give their memory back with
their stack still in it, then start the game. Hatari's GEMDOS drive clears the free memory of a
program it loads, unless the program has the fastload bit, and the start program's stack is
cleared with it. The start program is then ended as soon as the game is loaded, and the desktop
comes back. `tools/set_fastload.py` sets the bit in the program that the start program loads.

## Rody and Mastico 2's start program: `tools/rody2_runme.py`

Rody and Mastico 2's download has the game's `HAGE` module, the floppy image and the data, but no
`RUNME.TOS`. HAGE is the launcher module that loads TOS 1.04 with GEM into RAM and reads the game's
floppy from an image file. Rody and Mastico 4's download has the same `HAGE`, so its `RUNME.TOS`
starts Rody and Mastico 2 too. The game's chapter menu takes the mouse only once its music has
finished.

## Fixing a copy

You need this repository and Python 3. For `GDBPB.PRG`, you also need, the first time, the
toolchain described in `tools/dev/README.md`. Unpack the downloads from the 8bitchip.info website.
The tools check each file by its SHA-256, and write nothing for a file they do not know. Run again
on a fixed file, they change nothing.

- Crystals of Arborea, Targhan, Robinsons Requiem, Storm Master: build `GDBPB.PRG` and copy it into
  the game's folder. The assembler writes only inside the repository, so build it there first.

  ```
  tools/dev/asm.sh --tos src/gemdrive/gdbpb.s tools/dev/builds/GDBPB.PRG
  cp tools/dev/builds/GDBPB.PRG GAME/
  ```

  Then, on the Atari, run `GDBPB.PRG`, then `START.PRG`.
- Spy vs Spy 2, Strike Force Harrier: set the bit in the program that the start program runs.

  ```
  python3 tools/set_fastload.py SPY2/SPY2.BOY SPY2/SPY2.BOY
  python3 tools/set_fastload.py STRIKEFH/HARRIER.TOS STRIKEFH/HARRIER.TOS
  ```

  Then start `SPY2.PRG` or `START.TOS` as before.
- Rody and Mastico 2: copy Rody and Mastico 4's start program into its folder.

  ```
  python3 tools/rody2_runme.py RODYM4/RODYM4 RODYM2/RODYM2
  ```

  Then start `RUNME.TOS`.

Copy the game's folder to the GEMDOS drive. To undo, take the files again from the download.

## Aquanaut

With the fastload bit set, Aquanaut reaches its title in Hatari: on an ST with TOS 1.04, and on an
STE with TOS 1.62 or 2.06. On TOS 2.06, its title's credit lines are garbled. On the STE with the
Multidevice, it reboots while it loads. What is known so far:

- `AQUANAUT.PRG` starts `AQUANAUT.EXE` right above itself in memory, and both put the screen at
  fixed addresses.
- When the free memory starts 64 KB higher than where Hatari's GEMDOS drive leaves it, the game
  fails in Hatari too.
- The 8bitchip.info list marks the game "Hole" on TOS 2.06, the Mega STE and the Falcon. Its
  download's `FBHOLE.PRG` writes a boot floppy that keeps the memory below 512 KB free at
  power-on. With that memory kept free, the game is loaded above 512 KB, and it still fails in
  Hatari.

It is not solved yet.

## Tested

- **Hatari**, on an ST with TOS 1.04 and an STE with TOS 1.62 and 2.06, from its GEMDOS drive:
  - the four Silmarils games play or reach their title, with no sector read on C:. Without
    `GDBPB.PRG`, Crystals of Arborea asks for the BPB 6.4 million times in a run and opens nothing;
  - Spy vs Spy 2 and Strike Force Harrier play;
  - Rody and Mastico 2 reaches its chapter menu;
  - from the PPDRIVER driver, the fastload bit changes nothing;
  - a game that needs no BPB (Stormlord) runs with `GDBPB.PRG` in memory.
- **The Multidevice's GEMDRIVE**, on a real machine, power-cycled between games: the
  seven games run, and Aquanaut reboots on the STE (TOS 1.62, 4 MB) while it loads.
