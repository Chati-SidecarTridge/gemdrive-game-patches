# tools/dev: the development environment

The tools all the work of this repository runs on: a pinned 68000 toolchain, the round-trip
check for reconstructed sources, the two disk setups, and Hatari driven from the host with PASS or
FAIL at the end. Standard-library Python and bash; Docker for the toolchain; Hatari 2.6.1 as
released, never changed.

## Setup

1. Docker Desktop running, with the pinned image:
   `docker pull logronoide/atarist-toolkit-docker-x86_64:1.4.0`.
2. Hatari 2.6.1 (`/usr/local/bin/hatari`), mtools (`mcopy`), `rsync`, Python 3.
3. `cp tools/dev/dev.cfg.example tools/dev/dev.cfg` and adjust the paths: Hatari, one TOS image
   per test machine, and a checkout of `sidecartridge/atari-hd`. Relative paths are relative to
   the repository. `dev.cfg` is git-ignored; TOS images and drivers are never copied here.
4. Your own copy of Lemmings' hard-disk adaptation (`LEMMINGS.ZIP` from the 8bitchip.info
   website), unpacked at the repository's root as `LEMMINGS/`; `shasum -a 256 -c LEMMINGS.sha256`
   checks it. It is git-ignored. Then `tools/make_sources.sh` makes the launcher's sources from
   their maps.

## Check everything

```
tools/dev/all_harness.sh
```

Builds the disks, round-trips the `START.TOS` text and every source of the launcher
(reassembled to the original bytes, and checked with a `nop` inserted), runs the launcher on all
six setups, checks
that the harness reports a failure, checks `LEMMINGS/` against `LEMMINGS.sha256` and that no
Hatari is left. One line per check; exit 0 only if all pass. About two minutes.

## The scripts

| script | what it does |
| --- | --- |
| `toolchain.sh` | sourced: the pinned image (tag and digest), `tc_run`, `tc_path`, `tc_stage` |
| `disasm.sh <bin> <vma> <out> [arch]` | objdump listing of a raw binary loaded at `<vma>`; `m68k:68000` unless told otherwise; `-z`, so zero runs are listed |
| `asm.sh [--tos] <src.s> <out.bin> [<listing>]` | vasm, Motorola syntax, 68000, `-Fbin` (or with `--tos` a GEMDOS program, `-Ftos -nosym`), `-no-opt`, every error reported; includes from the source's folder and the repository |
| `listing2vasm.py [--verbose] <listing> <bin> <out.s>` | a listing turned into a vasm source that reassembles to `<bin>`; lines that will not are kept as `dc.w` with their disassembly |
| `roundtrip.sh [--tos] <src.s> <ref.bin>` | assemble and compare: PASS, or FAIL with the first differing offset |
| `m68k.py` | imported: 68000 instruction lengths, branch and call targets, absolute and PC-relative operands |
| `mksource.py [--report] <stage.map> <out.s>` | a labelled source for a launcher stage from its map (entries, data, names, comments, pointer tables, run addresses, executed addresses) and its bytes; reassembles to them |
| `shiftcheck.py [--tos] <src.s> <origin>` | inserts a `nop` mid-source, reassembles, and checks every reference moved with its target |
| `make_disks.sh [<game folder> [<out folder>]]` | `builds/disks/` (or `<out folder>`): `gemdrive/` (drive C: for GEMDRIVE mode) and `ppdriver.img` (the PPDRIVER reference: an ACSI image booted by PPDRIVER), from a copy of `LEMMINGS/` or of the folder given |
| `hatari_harness.py --setup <s> --disk <d> [...]` | one Hatari run, headless, with a run folder in `logs/`; `--start <path>` runs another program than `START.TOS` |
| `../build_launcher.sh [<src>] [<out>]` | Lemmings' launcher built from `src/` into `builds/launcher/LEMMINGS/`; then `make_disks.sh builds/launcher/LEMMINGS` |
| `../build_gemdrive.sh [<out>]` | Lemmings' launcher changed for a GEMDOS drive, from its sources (`src/gemdrive/lemld2_gemdrive.s`) into `builds/gemdrive/build/LEMMINGS` |
| `../build_gos5.py <START.TOS> <out> [--info] [--floppy]` | any GOS5 game's start program built for a GEMDOS drive from its original, found by signature: `src/gemdrive/gos5_patch.s` in front of the launcher's text (`gos5-gemdrive.md`); `--floppy` adds the info screen's "Insert any floppy disk in drive A" |
| `../../src/probes/gos5/gos5_run.py <ZIP> [--setup <s>] [--disk <d>]` | one GOS5 game from its unpacked download, built with `src/survey/ports.tsv`'s options and files, run from the GEMDOS drive with `src/probes/modes/mode_probe.py`'s generic expectation (the start, screenshots at 10 s and 30 s, the space bar, one 15 s later) |
| `all_harness.sh` | all of the above, once |

Examples:

```
# Disassemble the LS2DD payload loaded at $70000, convert, and check it reassembles.
tools/dev/disasm.sh some/ls2dd.bin 0x70000 some/ls2dd.lst
python3 tools/dev/listing2vasm.py some/ls2dd.lst some/ls2dd.bin some/ls2dd.s
tools/dev/roundtrip.sh some/ls2dd.s some/ls2dd.bin

# A patched tree onto both disks, then the launcher on the STE with TOS 2.06 in GEMDRIVE mode.
tools/dev/make_disks.sh tools/dev/builds/patched
python3 tools/dev/hatari_harness.py --setup ste-206 --disk gemdrive --expect tools/dev/expect/launcher-start.exp
```

## The harness

Setups: `st-104` (ST, TOS 1.04), `ste-162` (STE, TOS 1.62), `ste-206` (STE, TOS 2.06). Disks:
`gemdrive` (Hatari's GEMDOS drive, `--harddrive`) and `ppdriver` (the ACSI image, `--acsi`).
Options: `--expect <file>` (default: wait 20 s, screenshot), `--parse <debugger script>`,
`--memsize <MB>` (default 1, the game's minimum), `--no-auto` (desktop only, no
`START.TOS`), `--start <path>` (another program to start, for example
`C:\LEMMINGS\GXUT260.PRG`), `--step-time <s>` (default 60), `--name <suffix>`.

Each run gets `tools/dev/logs/<date>-<setup>-<disk>[-name]/` (git-ignored):

- `hatari.out`: everything Hatari printed: the trace of GEMDOS calls with file names, BIOS and
  XBIOS calls, ACSI commands (`--trace gemdos,bios,xbios,scsi_cmd`), the debugger's output, and
  the registers at the end
- `hatari.log`, `command.txt`, `SOURCE.txt` (what the disk held)
- `shots/`: one PNG per `shot` step, `fail.png` on failure, `end.png` always
- `drive/` or `ppdriver.img`: the run's own copy of the disk, with whatever the program wrote
- `result.txt`: PASS or FAIL, the steps reached, the PC at the end

Further options: `--trace <flags>` adds Hatari trace flags to the default
`gemdos,bios,xbios,scsi_cmd` (`ikbd_cmds` shows the game's IKBD commands; `cpu_exception` logs
every interrupt too and defeats `quiet`); `--key-hold <s>` is how long a key stays down.
`--monitor mono` (or `rgb`, `vga`, `tv`) for games that need a monochrome
monitor; without it Hatari's default, colour. `--drive <folder>` gives a GEMDOS-drive run its own
C: instead of `builds/disks/gemdrive` (parallel runs of different games), `--image <file>` gives a
PPDRIVER run its own image instead of `builds/disks/ppdriver.img` (`make_disks.sh <game folder>
<out folder>` builds one elsewhere), and `--log-root <folder>` puts the run folder elsewhere than
`tools/dev/logs/` (`tools/survey/run_all.py` uses all three).

Expectations file (`tools/dev/expect/*.exp`): one step per line, `#` at the start of a line for a
comment.

```
expect <name> <regex>    a line of hatari.out matching <regex> within --step-time
quiet <name> <seconds>   no new output for <seconds>
key <key>                press and release: space, return, esc, tab, backspace, f1-f10, 0-9, or a scan code (0x39)
event <name>             a raw control-socket event: doubleclick, rightdown, rightup (no left press, no motion)
debug <command>          a debugger command while the machine runs; {run} becomes the run folder
mouse <x> <y>            put Lemmings' mouse at (x, y); see below
shot <name>
sleep <seconds>
```

`tools/dev/expect/launcher-start.exp` is the launcher up to `Dsetpath("FILES")` on any disk;
`reference-first-level.exp` is the PPDRIVER reference through the title and the first level's
data load.

**The mouse.** Lemmings polls the IKBD in absolute mode once per frame; the control socket has no
mouse motion and the debugger cannot write the ACIA (its `w` writes the memory array, bypassing
the I/O handlers). `mouse x y` rewrites, for one frame, the byte table the game's own IKBD
sender reads (`$D0A0`, "01 0D") into a "load mouse position" command and restores it at the
sender's `rts` (`$E996`); the game transmits it, the IKBD reports the new position, and
`event doubleclick` clicks there. The addresses are Lemmings' title-screen code (`MOUSE_*` in
the harness). "1 PLAYER" is at (70,150).

Debugger script: Hatari's own syntax. Copied into the run folder with every `:file` it names,
recursively, so `savebin` with a relative path writes into the run folder (`loadbin` is not
staged: give it an absolute path). To stop at a program's first instruction:
`b pc = TEXT && pc < $e00000 :once :trace :file dump.ini`. Chains of single-shot breakpoints,
each file setting the next, are how `src/probes/gemdrive-failure/*.py` follow a path and answer the disk
by hand (`r d0=0`, `loadbin <file> <address>`); `trace <flags>` in a file switches tracing on or
off from there, which keeps instruction traces bounded.

## Gotchas

- **Docker Desktop can serve a container a file the host has just rewritten in place, at its old
  length.** Every input reaches the container as a fresh copy in `builds/.stage/`
  (`tc_stage`); never pass a host-written file to `tc_run` directly.
- objdump hides runs of zero bytes behind `...` unless given `-z`, stops before a last
  instruction cut short by the end of the file, and prints an indexed displacement as 16 hex
  digits without `0x`. `listing2vasm.py` copes with all three; give it listings from
  `disasm.sh`.
- `stcmd` follows `latest`, a different image from the pinned `1.4.0`, and passes its arguments
  unquoted: use `toolchain.sh`.
- Hatari loads `~/Library/Application Support/Hatari/hatari.cfg` unless `HOME` points
  elsewhere; the harness gives each run its own `HOME`.
- Control-socket keys go in hex: Hatari takes a single character as a character.
- `TEXT` in a breakpoint first matches TOS's own ROM program; add `&& pc < $e00000`.
- A trap's traced PC (`… at PC 0x…`) is the return address, two bytes past the `trap`.
- A `:once` breakpoint set, from a hit's file, on the same PC fires at once: the CPU has not
  moved yet. Set it on a later instruction.
- Breakpoint conditions take `(pc).w` but no arithmetic inside the parentheses, and `m`/`d`
  take `a1` but not `a1-8`; `d $start-$end` disassembles a range.
- `w` values are in the current number base, decimal by default: write `$0e`, not `0e`.
- TOS 1.04 fills its exception vectors with the vector number in the high byte, so its handler
  is reached at `$3FC0B0A` for an address error, `$2FC0B0A` for a bus error; break there, with
  `m a7 16` for the frame (access address, instruction, SR, PC).
- `cpu_exception` tracing logs every interrupt (26, 28, 30 each frame) and traps; bus and
  address errors print as `Bus error …` lines, not as `cpu exception 2`.
- Hatari matches GEMDOS-drive file names without regard to case, whatever the host file system.
- Hatari's CPU profiler (`profile on`) compiles its data only when the emulation stops in the
  debugger, and starts a new profile each time it leaves it: every `:file` breakpoint and every
  `hatari-debug` command does both. Save with a real (not `:trace`) breakpoint whose file ends in
  `profile save <file>` and `c`; the disassembly goes to `hatari.out`, not to the file
  (`src/probes/stages/profile_probe.py`).
- Docker Desktop can wedge: containers stay "Created" and `docker rm` hangs. `docker desktop
  restart` brings it back (an `osascript` quit did not).
- objdump with `-m m68k:68000` reads `movec` and `pmove` as one-word `.short`s and loses step
  after them: `mksource.py` hides them from objdump and writes them as `dc.w`.
- A CPU trace (`--trace cpu_disasm`) gets huge: the first pass's reached 800 MB
  (`_archive/2026-04-first-pass/trace.log`). Bound it in time, and read traces with `grep`,
  `head`, `tail`, never whole.
