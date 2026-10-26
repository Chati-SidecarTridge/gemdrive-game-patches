# The GOS4 games from GEMDOS and GEMDRIVE

117 games on the 8bitchip.info website start from a hard disk with the Gamex launcher and GOS4. As
they come, they do not start from a GEMDOS drive, a drive that serves files by name and has no
disk sectors: Hatari's, or the SidecarTridge Multidevice's GEMDRIVE. `tools/build_gos4.py`
rebuilds their start program so that they do. All 117 run that way in Hatari, and the
ten tried with the Multidevice run there too.

GOS4 is TOS 1.04 that the launcher starts from RAM, and the game itself calls its GEMDOS while it
runs. GOS reads the hard disk by sectors through PPDRIVER, a hard-disk driver that must be
resident. A GEMDOS drive has neither the driver nor the sectors (`solutions.md` §3.1).

## What the build changes

The build changes only the game's start program (`START.TOS`). The game's data, GOS
(`D15R_HH4.FIC`) and the other files stay as they are.

- The Gamex launcher still runs: its info screen, its keys, the cover picture, and GOS.
- With PPDRIVER present, the launcher runs as it was made.
- Without PPDRIVER, if a GEMDOS drive answers `TRAP #1` from the cartridge port, the launcher
  installs a forwarder before GOS starts. A forwarder is a short routine that passes each call on.
  GOS sets up its own `TRAP #1`, and the launcher points it, in GOS's copy in memory, at the
  forwarder. The forwarder passes the file calls to the GEMDOS drive by name, and every other call
  to GOS (below).
- On the Multidevice, the build also moves GEMDRIVE's stack out of the game's memory.
- The info screen says "Patched for GEMDRIVE HD by SidecarTridge".

## What the forwarder does

- **Names.** Each part of a name is cut to 8.3, as TOS does. An empty name gets the answer GOS
  would give.
- **File handles.** The drive's file handles are numbered as GOS numbers its own, 6 and up. Some
  adaptations put back a snapshot of a game's variables that holds such a number, as Operation
  Stealth's does.
- **Programs.** A program that the launcher or the game starts with `Pexec` is read through the
  drive into GOS's memory. GOS then runs it.
- **Files opened for reading and writing.** The forwarder opens them on the drive for reading
  only. The Multidevice's GEMDRIVE refuses to open a file again while it is open for writing.
  Noddy's Playtime opens `data\driving.dat` for reading and writing, never closes it, and then
  loads it. On the Multidevice, it asked for disk 1 forever. No game writes through such a file:
  the files the games write, they create.
- **Searches.** `Fsfirst` and `Fsnext` fill the game's DTA.
- **Drives.** Drives A and B stay with GOS's floppy code. Drive C gives a BPB, the block that
  describes a drive's layout, to the games that ask for one (Starblade, Windsurf Willy). It reads
  no sector.

## Building a game

You need this repository and Python 3. The first time, you also need the toolchain described in
`tools/dev/README.md`: the tool assembles the change once, into `tools/dev/builds/gos4/`.

1. Unpack the game's download from the 8bitchip.info website. Keep the original start program
   aside as `START.ORG`.
2. Build:

   ```
   python3 tools/build_gos4.py GAME/START.ORG GAME/START.TOS
   ```

   The tool checks the original by its signature. It refuses a start program it does not know, or
   one already built, and then writes nothing. It prints the SHA-256 of both files. Five start
   programs are not packed: Herman, Hoog, Ranx, Grandad and Grandad 2. The tool writes their builds
   unpacked too.
3. Copy the game's folder to the GEMDOS drive and start `START.TOS` from it.

To undo, put `START.ORG` back as `START.TOS`.

## Games that need more

| Game | What it needs |
|---|---|
| F16 Falcon | 2 MB: its launcher puts GOS at the top of a 2 MB machine. |
| Asterix Operation Getafix | It reads drive A at the start and asks whether to start a saved game, as it does with PPDRIVER. |
| Winter Games | It reads drive A and asks for disk 2 in drive B, as it does with PPDRIVER. |
| King's Quest, King's Quest III, Space Quest | They ask for a backup copy of disk 1 in drive C: press Return, as with PPDRIVER. |
| Manhunter, Manhunter 2, Emmanuelle | Their copy protection asks a question from the manual, or a colour from the chart, as with PPDRIVER. |

## Tested

- **Hatari, all 117.** An ST with TOS 1.04, at each game's RAM (1 or 2 MB), from its GEMDOS drive.
  Each game reached the screen it reaches from PPDRIVER at the same moment. Operation Stealth was
  also run on an STE with TOS 1.62 and 2.06. From PPDRIVER, the same 117 builds take the
  launcher's own path.
- **A test program** in place of a game's program, on the three machines. It writes a file, reads
  it back, searches for it, makes a second open at the same time, deletes a file, and uses a name
  longer than 8.3 (`src/probes/epic05/gos4_selftest.py`). Guild of Thieves also saves a game to
  the GEMDOS drive and restores it.
- **The Multidevice's GEMDRIVE**, on a real machine, power-cycled between games. Operation Stealth, Guild of Thieves (a game saved to the card and restored), Erik,
  Defender 2, Grandad, Starblade, Gravity, Strider and F16 Falcon run. F16 Falcon's "Read mission
  disk" needs the Falcon Mission Disk, which this adaptation does not include. Noddy's Playtime
  first asked for disk 1 forever. With the change for files opened for reading and writing (above),
  it runs too.
