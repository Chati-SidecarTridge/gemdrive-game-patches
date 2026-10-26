# The GOS5 games from GEMDOS and GEMDRIVE

87 games on the 8bitchip.info website start from a hard disk with the Gamex launcher and GOS5. As
they come, they do not start from a GEMDOS drive, a drive that serves files by name and has no
disk sectors: Hatari's, or the SidecarTridge Multidevice's GEMDRIVE. `tools/build_gos5.py`
rebuilds their start program so that they do. 85 of the 87 run that way, in Hatari
and with the Multidevice.

GOS5 is a GEMDOS 0.15 that the launcher runs from RAM, and it serves the game's file requests. It
reads the hard disk by sectors through PPDRIVER, a hard-disk driver that must be resident. A
GEMDOS drive has neither the driver nor the sectors, so the launcher gives up
(`solutions.md` §3.1).

## What the build changes

The build changes only the game's start program: `START.TOS`, or the one its folder starts, such
as Chaos Engine's `START2M.TOS`. The game's data and the adaptation's other files stay as they are.

- The Gamex launcher still runs: its info screen, its cheat keys, the adaptation's cover picture,
  and GOS.
- With PPDRIVER present, the launcher runs unchanged.
- Without PPDRIVER, if a GEMDOS drive answers `TRAP #1` from the cartridge port (Hatari's or the
  Multidevice's), GOS's file requests go to that drive by name instead of reading sectors. Each
  name is cut to 8.3, as TOS does.
- On the Multidevice, the build also moves GEMDRIVE's stack out of the game's memory.
- Before each load, the build lets a keyboard message already under way finish, so that the load
  does not cut it in two.
- The info screen says "Patched for GEMDRIVE HD by SidecarTridge". For the games below that need a
  floppy, it also says "Insert any floppy disk in drive A".

## Building a game

You need this repository and Python 3. The first time, you also need the toolchain described in
`tools/dev/README.md`: the tool assembles the change once, into `tools/dev/builds/gos5/`.

1. Unpack the game's download from the 8bitchip.info website. Keep the original start program
   aside as `START.ORG`. The start program is `START.TOS` in every game but Chaos Engine, where it
   is `START2M.TOS`.
2. Build:

   ```
   python3 tools/build_gos5.py GAME/START.ORG GAME/START.TOS
   ```

   For the games below that need a disk in drive A, add `--floppy`. The tool checks the original
   by its signature. It refuses a start program it does not know, or one already built, and then
   writes nothing. It prints the SHA-256 of both files.
3. Copy the game's folder to the GEMDOS drive and start `START.TOS` from it.

To undo, put `START.ORG` back as `START.TOS`.

## Games that need more

| Game | What it needs |
|---|---|
| Pit Fighter, Chaos Engine, Fire and Forget II, Venus the Flytrap, Jetsons | Any floppy disk in drive A. The game waits for the drive's motor to stop, and an empty drive never lets it. Build with `--floppy`. |
| Forgotten Worlds | Its launcher asks for `D15R_5H.FIC` and `D15R_5F.FIC`, but its download has an older GOS under other names. Copy those two files from any other GOS5 game's download, next to its `START.TOS`. All 56 games that carry them carry the same files. |
| Heimdall | Its first screen is black, with a question: skip the intro, y or n. |
| Cadaver | Dying in the swamp's water halts it, as it does with PPDRIVER. |
| Popeye 2 | A key pressed while it loads crashes it, as it does with PPDRIVER. |

## Not on every machine

Two games, once built, fail on an ST with TOS 1.04 and 1 MB, as they do there with PPDRIVER. They
run on an STE with TOS 1.62 and 4 MB, in Hatari and on the real machine.

- **Magic Boy** needs 2 MB or more. With less, the launcher unpacks its loader from 32 bytes too
  far into `MAGICC.FIC`, and crashes. Changing one long of the launcher fixes it; the build does
  not do that yet.
- **Muzzy** takes another branch on the ST. There, its unpacker writes over its own code and halts
  the CPU. It runs on the STE.

## Still not working

Awesome and Prison refuse a cartridge in the port, and GEMDRIVE needs one there: the Multidevice,
or Hatari's own. The check is in the game itself, so the build starts the game, and the game then
stops. Changing two bytes of one of its files turns the check off, but the build does not change
game files.

- **Awesome** stops on its title. With interrupts off, it compares the cartridge's first long with
  the two cartridge signatures (`$ABCDEF42`, `$FA52235F`), and loops while one matches. The fix
  tried: in its file `AWE`, the two `beq` after the `$ABCDEF42` compares, at offsets `$141E` and
  `$1CD0`, made `nop`. With that, it goes on to its options menu in Hatari, on an ST with 1 MB and
  an STE with 4 MB.
- **Prison** halts when play starts. It compares the cartridge's first long with the same two
  signatures, whose constants an XOR hides in its file `PR1`. On a match, it wipes its own memory.
  The fix tried: in `PR1`, the two `beq.w` after the compares, at offsets `$11890` and `$118A4`,
  made `nop`. With that, it plays in Hatari, on an ST with 1 MB and an STE with 4 MB.

## Tested

- Hatari: an ST with TOS 1.04, at each game's RAM (1 or 2 MB), from its GEMDOS drive.
- The SidecarTridge Multidevice's GEMDRIVE, on a real machine, from a card holding every game,
  power-cycled between games.
