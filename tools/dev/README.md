# tools/dev: the development environment

The tools every story of this repository runs (EPIC-00): a pinned 68000 toolchain, the round-trip
check for reconstructed sources, the two disk setups, and Hatari driven from the host with PASS or
FAIL at the end. Standard-library Python and bash; Docker for the toolchain; Hatari 2.6.1 as
released (C-02).

## Setup

1. Docker Desktop running, with the pinned image:
   `docker pull logronoide/atarist-toolkit-docker-x86_64:1.4.0`.
2. Hatari 2.6.1 (`/usr/local/bin/hatari`), mtools (`mcopy`), `rsync`, Python 3.
3. `cp tools/dev/dev.cfg.example tools/dev/dev.cfg` and adjust the paths: Hatari, one TOS image
   per test machine, and a checkout of `sidecartridge/atari-hd`. Relative paths are relative to
   the repository. `dev.cfg` is git-ignored; TOS images and drivers are never copied here (C-03).

## Check everything

```
tools/dev/all_harness.sh
```

Builds the disks, round-trips the `START.TOS` text, runs the launcher on all six setups, checks
that the harness reports a failure, checks `LEMMINGS/` against `LEMMINGS.sha256` and that no
Hatari is left. One line per check; exit 0 only if all pass. About two minutes.

## The scripts

| script | what it does |
| --- | --- |
| `toolchain.sh` | sourced: the pinned image (tag and digest), `tc_run`, `tc_path`, `tc_stage` |
| `disasm.sh <bin> <vma> <out> [arch]` | objdump listing of a raw binary loaded at `<vma>`; `m68k:68000` unless told otherwise; `-z`, so zero runs are listed |
| `asm.sh <src.s> <out.bin> [<listing>]` | vasm, Motorola syntax, 68000, `-Fbin`, `-no-opt`, every error reported |
| `listing2vasm.py [--verbose] <listing> <bin> <out.s>` | a listing turned into a vasm source that reassembles to `<bin>`; lines that will not are kept as `dc.w` with their disassembly |
| `roundtrip.sh <src.s> <ref.bin>` | assemble and compare: PASS, or FAIL with the first differing offset |
| `make_disks.sh [<game folder>]` | `builds/disks/`: `gemdrive/` (drive C: for GEMDRIVE mode) and `ppdriver.img` (the PPDRIVER reference, D-09), from a copy of `LEMMINGS/` or of the folder given |
| `hatari_harness.py --setup <s> --disk <d> [...]` | one Hatari run, headless, with a run folder in `logs/` |
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
`START.TOS`), `--step-time <s>` (default 60), `--name <suffix>`.

Each run gets `tools/dev/logs/<date>-<setup>-<disk>[-name]/` (git-ignored):

- `hatari.out`: everything Hatari printed: the trace of GEMDOS calls with file names, BIOS and
  XBIOS calls, ACSI commands (`--trace gemdos,bios,xbios,scsi_cmd`), the debugger's output, and
  the registers at the end
- `hatari.log`, `command.txt`, `SOURCE.txt` (what the disk held)
- `shots/`: one PNG per `shot` step, `fail.png` on failure, `end.png` always
- `drive/` or `ppdriver.img`: the run's own copy of the disk, with whatever the program wrote
- `result.txt`: PASS or FAIL, the steps reached, the PC at the end

Expectations file (`tools/dev/expect/*.exp`): one step per line, `#` at the start of a line for a
comment.

```
expect <name> <regex>    a line of hatari.out matching <regex> within --step-time
quiet <name> <seconds>   no new output for <seconds>
key <key>                press and release: space, return, esc, tab, backspace, f1-f10, 0-9, or a scan code (0x39)
shot <name>
sleep <seconds>
```

Debugger script: Hatari's own syntax. Copied into the run folder with every `:file` it names, so
`savebin` with a relative path writes into the run folder. To stop at a program's first
instruction: `b pc = TEXT && pc < $e00000 :once :trace :file dump.ini`.

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
- Hatari matches GEMDOS-drive file names without regard to case, whatever the host file system.
- A CPU trace (`--trace cpu_disasm`) gets huge: the first pass's reached 800 MB
  (`_archive/2026-04-first-pass/trace.log`). Bound it in time, and read traces with `grep`,
  `head`, `tail`, never whole.
