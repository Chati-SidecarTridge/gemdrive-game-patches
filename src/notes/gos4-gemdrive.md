# The GOS4 games from a GEMDOS drive

117 games on the 8bitchip.info website start from a hard disk with a Gamex launcher and GOS4: TOS
1.04 started from RAM, whose GEMDOS the game itself calls while it runs (`hd-strategies.md` §3.1).
As they come, they need the PPDRIVER hard-disk driver and a partition that GOS reads by sectors,
so they do not start from a GEMDOS drive: Hatari's, or the SidecarTridge Multidevice's GEMDRIVE.
Built again with `tools/build_gos4.py`, all 117 do in Hatari (2026-10-16).

## What the build changes

Only the game's start program (`START.TOS`). The game's data, GOS (`D15R_HH4.FIC`) and the other
files stay as they are.

- The Gamex launcher still runs: its info screen, its keys, the cover picture, GOS.
- When PPDRIVER is there, the launcher goes on as it was made.
- When it is not, and a GEMDOS drive answers `TRAP #1` from the cartridge port, the launcher points
  the `TRAP #1` that GOS sets up at a forwarder of its own, in GOS's copy in memory, before GOS
  starts. The forwarder hands the file calls to the GEMDOS drive by name and everything else to
  GOS:
  - each part of a name is cut to 8.3, as TOS does; an empty name is answered as GOS would;
  - the drive's file handles are numbered as GOS numbers its own, 6 and up: some adaptations put
    back a snapshot of a game's variables that holds such a number (Operation Stealth's);
  - a program the launcher or the game starts (`Pexec`) is read through the drive into GOS's
    memory, then GOS runs it;
  - `Fsfirst` and `Fsnext` fill the game's DTA;
  - drives A and B stay GOS's floppy; drive C answers the games that ask for its BPB (Starblade,
    Windsurf Willy) and reads no sector.
- On the Multidevice, the build also moves GEMDRIVE's stack out of the game's memory.
- The info screen says "Patched for GEMDRIVE HD by SidecarTridge".

## Building a game

You need this repository, Python 3, and, the first time, the toolchain of `tools/dev/README.md`
(it assembles the change once, into `tools/dev/builds/gos4/`).

1. Unpack the game's download from the 8bitchip.info website, and keep the original start program
   aside (`START.ORG`).
2. Build:

   ```
   python3 tools/build_gos4.py GAME/START.ORG GAME/START.TOS
   ```

   The tool checks the original by its signature: a start program it does not know, or one built
   already, it refuses, and it writes nothing. It prints both files' SHA-256. Five start programs
   are not packed (Herman, Hoog, Ranx, Grandad, Grandad 2): the tool writes them back unpacked.
3. Copy the game's folder to the GEMDOS drive and start `START.TOS` from it.

To undo, put `START.ORG` back as `START.TOS`.

## Games that need more

| Game | What it needs |
|---|---|
| F16 Falcon | 2 MB: its launcher puts GOS at the top of a 2 MB machine. |
| Asterix Operation Getafix | It reads drive A at the start and asks whether to start a saved game, as with PPDRIVER. |
| Winter Games | It reads drive A and asks for disk 2 in drive B, as with PPDRIVER. |
| King's Quest, King's Quest III, Space Quest | They ask for a backup copy of disk 1 in drive C: press Return, as with PPDRIVER. |
| Manhunter, Manhunter 2, Emmanuelle | Their copy protection asks a question from the manual, or a colour from the chart, as with PPDRIVER. |

## Tested

- Hatari: all 117 on an ST with TOS 1.04, at each game's RAM (1 or 2 MB), from its GEMDOS drive,
  each to the screen it reaches from PPDRIVER at the same moment; Operation Stealth also on an STE
  with TOS 1.62 and 2.06; from PPDRIVER, the same builds take the launcher's own path, all 117.
- A test program in place of a game's program, on the three machines: a file written, read back,
  searched for, a second open at the same time, one deleted, a name longer than 8.3
  (`src/probes/epic05/gos4_selftest.py`). Guild of Thieves saves a game to the GEMDOS drive and
  restores it.
- Not yet on a real machine with the Multidevice.
