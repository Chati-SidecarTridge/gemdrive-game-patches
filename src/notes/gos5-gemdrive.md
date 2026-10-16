# The GOS5 games from a GEMDOS drive

PP adapted 87 games to start from a hard disk with a Gamex launcher and GOS5, his GEMDOS 0.15
running from RAM (`hd-strategies.md` §3.1). As PP made them, they need his hard-disk driver and
a partition that GOS reads by sectors, so they do not start from a GEMDOS drive: Hatari's, or the
SidecarTridge Multidevice's GEMDRIVE. Built again with `tools/build_gos5.py`, 84 of them do
(2026-10-16), in Hatari and on an STE with the Multidevice.

## What the build changes

Only the game's start program (`START.TOS`, or the one its folder starts, as Chaos Engine's
`START2M.TOS`). The game's data and PP's other files stay as they are.

- PP's launcher still runs: its info screen, its cheat keys, his cover picture, GOS.
- When PP's driver is there, the launcher goes on as PP made it.
- When it is not, and a GEMDOS drive answers `TRAP #1` from the cartridge port (Hatari's, the
  Multidevice's), GOS's file requests go to that drive by name instead of reading sectors, each
  name cut to 8.3 as TOS does. On the Multidevice, the build also moves GEMDRIVE's stack out of
  the game's memory.
- Before each load it lets a keyboard message that is under way finish, so that a load does not
  cut it in two.
- The info screen says "Patched for GEMDRIVE HD by SidecarTridge", and for the games below that
  need a floppy, "Insert any floppy disk in drive A".

## Building a game

You need this repository, Python 3, and, the first time, the toolchain of `tools/dev/README.md`
(it assembles the change once, into `tools/dev/builds/gos5/`).

1. Unpack PP's download of the game, and keep the original start program aside (`START.ORG`; the
   start program is `START.TOS` in every game but Chaos Engine, `START2M.TOS`).
2. Build:

   ```
   python3 tools/build_gos5.py GAME/START.ORG GAME/START.TOS
   ```

   Add `--floppy` for the games below that need a disk in drive A. The tool checks the original by
   its signature: a start program it does not know, or one built already, it refuses, and it
   writes nothing. It prints both files' SHA-256.
3. Copy the game's folder to the GEMDOS drive and start `START.TOS` from it.

To undo, put `START.ORG` back as `START.TOS`.

## Games that need more

| Game | What it needs |
|---|---|
| Pit Fighter, Chaos Engine, Fire and Forget II, Venus the Flytrap, Jetsons | A floppy disk in drive A, any: the game waits for the drive's motor to stop, which an empty drive never lets it do. Build with `--floppy`. |
| Forgotten Worlds | Its launcher asks for `D15R_5H.FIC` and `D15R_5F.FIC`; its download has an older GOS under other names. Copy those two files from any other GOS5 game's download, beside its `START.TOS` (all 56 games that carry them carry the same files). |
| Awesome | It stops on its title while a cartridge is in the port, the Multidevice or Hatari's own: the game itself checks. Two bytes of its file `AWE` change that (the two `beq` after its check, at offsets `$141E` and `$1CD0`, made `nop`); the build does not. |
| Heimdall | Its first screen is black with a question: skip the intro, y or n. |
| Cadaver | Dying in the swamp's water halts it, as with PP's own driver. |
| Popeye 2 | A key pressed while it loads crashes it, as with PP's own driver. |

## Still not working on every machine

Three games, built, fail on an ST with TOS 1.04 and 1 MB, as they do with PP's own driver there,
and run in Hatari on an STE with TOS 1.62 and 4 MB:

- **Magic Boy** needs 2 MB or more: below that, PP's launcher unpacks its loader from 32 bytes too
  far into `MAGICC.FIC` and crashes. One long of the launcher fixes it; the build does not yet.
- **Muzzy** takes another branch on the ST, whose unpacker writes over its own code and halts the
  CPU. It runs on the STE.
- **Prison**'s first load writes over its own stack. TOS 1.62's error handler lets it go on to its
  game screen; TOS 1.04's does not.

## Tested

- Hatari: ST, TOS 1.04, at each game's RAM (1 or 2 MB), from its GEMDOS drive.
- An STE, TOS 1.62, 4 MB, with the SidecarTridge Multidevice's GEMDRIVE, from a card holding every
  game, power-cycled between games.
