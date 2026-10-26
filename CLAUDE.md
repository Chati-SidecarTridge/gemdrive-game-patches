# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A reverse-engineering workspace for **PP's (PPera's) Gamex hard-disk launcher** for *Lemmings* on
the Atari ST: the 2011 adaptation (`LEMMINGS/README.TXT`) that runs the game from a hard disk. The
target is the launcher and the disk layer it installs (its loader D15R and a copy of PP's
resident driver), not the game. The aim is **GEMDRIVE mode**: the game started from a Hatari GEMDOS
drive (`--harddrive`) instead of a hard-disk image, for Lemmings and then for every game PP adapted.
Two iterations (D-14): first understand and classify, then the solutions.

1. **Why it fails** in Hatari's GEMDRIVE mode today. Diego's guess, to confirm first: the PPera
   driver embedded in the launcher (H-07). EPIC-01.
2. **Recompilable launcher**: every PPera launcher program reverse engineered into 68000 sources
   that reassemble to the original bytes, and our own build of them booting the game. EPIC-02.
3. **The ways PP's adaptations run from a hard disk**: PP's modes understood first, then every
   game in PP's list (<https://atari.8bitchip.info/fromhd3.php>) classified by the strategy that
   runs it from a hard disk, with one of three verdicts: as it is, fix (with the solution), not
   feasible (with the reason); and the solutions proposed; all of it, with the project's
   documentation, as a website published with the repository (designed with the frontend-design
   skill; the repository goes public only after it is cleaned, D-15). EPIC-03. The site was mirrored first (D-12): work
   from the mirror (`MIRROR` in `tools/dev/dev.cfg`), not the site.
4. **The solutions** (iteration 2): the games that do not run, ported by the test card's groups
   (D-16), in this order:
   - EPIC-04, GOS5, with Lemmings first;
   - EPIC-05, GOS4;
   - EPIC-06, the small fixes;
   - EPIC-07, the unsure games;
   - EPIC-08, the ports checked on acsi2stm's GemDrive, the other GEMDRIVE: an STM32 on the ACSI
     port, its driver in the ST's RAM (D-18);
   - EPIC-09, last, the patcher: a program that checks a user's original start files by signature
     and replaces them with our builds (D-17).
   Each is checked in Hatari, and each checkpoint also on Diego's SidecarTridge Multidevice from a
   card.

**Hatari's code is never modified** (C-02): every fix lives on the Atari side.

The work is planned and tracked in `docs/epics/` (see Backlog). This repository is not part of
the sidecartos product (`../sidecartos`, `../sidecartos-config`, `../romemul-switcher-rom`): it
borrows their procedure, not their sync contract (D-02).

**Fresh start (D-01).** A first pass (2026-04-23/24) is archived, read-only, in
`_archive/2026-04-first-pass/`: its tools, listings and notes (`src/`), the patched builds it had
left in `LEMMINGS/` (`lemmings-patched/`), the hashes of everything before the move
(`MANIFEST.before.sha256`) and an 800 MB `trace.log` (git-ignored). Its conclusions are
hypotheses `H-NN` in `docs/epics/ITERATIONS.md`, not facts: a finding counts only once a story
here observes it again, and its code is reused only after a story has verified it. Its notes
contradict its own code in places.

## The evidence: `LEMMINGS/`

PP's original files, **never modified** (C-01): runs, patches and experiments work on a copy under
`tools/dev/builds/`. After EPIC-00 STORY-01, `shasum -a 256 -c LEMMINGS.sha256` proves it.

- `START.TOS`: the program the user runs; a GEMDOS executable (`0x601A` header) whose 230-byte
  text unpacks and starts the rest.
- `GXUT260.PRG`: "Gamex utility" v2.60, a GEMDOS executable; its role is open (EPIC-02 STORY-01).
- `LEMMINGS.PCH`: read by the loader; format open. `file(1)` calls it "MIPS ECOFF" from its
  `01 40` header: wrong.
- `LS2DD.FIC`, `D15R_F5.FIC`, `D15R_H5.FIC`: start with ASCII `C3` and two zero bytes
  (`43 33 00 00`), which `file(1)` calls "Clarion Developer data": wrong. Despite the extension
  they may be packed code, not catalogues (H-02).
- `FILES/`: the game's data. `CODE` and `MAIN` are ICE-packed (`Ice!` magic) game code; the rest
  are levels (`LEVEL000`-`LEVEL024`, `LEVELDAT`, `ODDTABLE`), graphics (`GROUNDn`, `OBJECTSn`,
  `SPECIALn`, `LEMMINGn`, `INTROPAR`, `*.IMG`) and music and samples.
- `README.TXT`: any ST, STE, Mega ST, Mega STE or Falcon with at least 1 MB, "PP, AHDI or Hddriver"
  driver, a partition under 512 MB; on the Falcon, start from ST medium resolution (C-04).

**PP's own documentation**, on <https://atari.8bitchip.info>: `GAMEXdoc.html` (Gamex, and GOS,
his modded GEMDOS 0.15 of TOS 1.04 that runs in high RAM; H-08), `agcat.html` (his classification
of the games by floppy access), `GamexLSrc.html`, `GamexLSrc2.html` and `GamexLSrc3.html` (three of
his launcher sources, 2009), `fromhd.php` (his view of GEMdrive). All of it is in the mirror
(D-12). Cite it by URL and never copy it into the repository (D-11). A claim from them counts only once a run shows it (D-01).

`LEMMINGS/` and `_archive/` stay on this Mac and out of git (D-25): both are git-ignored and were
removed from the history before the repository went public.

## Layout

- `docs/epics/`: the backlog (committed, D-03).
- `src/`: what this project produces: unpacked stages, reconstructed sources (vasm Motorola
  syntax, D-05) that reassemble byte for byte to the original, notes (`src/notes/`; the GEMDRIVE
  cause is `gemdrive-failure.md`, every game's verdict and the solutions `solutions.md`) and
  the debugger probes of each epic (`src/probes/`).
- `tools/`: the project's own unpackers and packers (standard-library Python); `tools/survey/`,
  EPIC-03's scripts, starting with `mirror.py`, which copied PP's site into `MIRROR`; `tools/site/`,
  the website's builder, style and script, and the check of a clone before going public.
- `docs/publication/`: what leaves the repository and its history before it goes public (D-15),
  and how the site is published on GitHub Pages.
- `tools/dev/`: the development environment from EPIC-00: pinned toolchain scripts, the
  round-trip check, the Hatari disk setups and harness. `builds/`, `logs/` and `dev.cfg` are
  git-ignored.
- `_archive/2026-04-first-pass/`: the first pass, read-only (D-01).

## Commands

Everything is in `tools/dev/` (EPIC-00; details and examples in `tools/dev/README.md`). Once per
machine: Docker running with `logronoide/atarist-toolkit-docker-x86_64:1.4.0`, and
`cp tools/dev/dev.cfg.example tools/dev/dev.cfg` (paths to Hatari, the TOS images, `../atari-hd`).

```
tools/dev/all_harness.sh                       # check everything: disks, round trip, 6 Hatari runs, the site (~2 min)
tools/dev/make_disks.sh [<game folder>]        # builds/disks/: gemdrive/ and ppdriver.img from LEMMINGS/ or a patched tree
python3 tools/dev/hatari_harness.py --setup st-104|ste-162|ste-206 --disk gemdrive|ppdriver \
    [--expect tools/dev/expect/launcher-start.exp] [--parse <debugger script>] [--no-auto] [--trace <flags>]
python3 src/probes/epic01/gate_probe.py <setup> <disk>  # EPIC-01's breakpoint chains; read_probe.py <run>
tools/dev/disasm.sh <bin> <vma> <out.lst>      # objdump listing, 68000
python3 tools/dev/listing2vasm.py <out.lst> <bin> <out.s>   # a source that reassembles to <bin>
tools/dev/roundtrip.sh <src.s> <ref.bin>       # PASS, or FAIL at the first differing offset
tools/dev/asm.sh [--tos] <src.s> <out.bin> [<listing>] # vasm, 68000, -no-opt (--tos: a GEMDOS program)
python3 tools/dev/mksource.py src/<stage>/<stage>.map src/<stage>/<stage>.s   # a stage's source from its map
python3 tools/dev/shiftcheck.py [--tos] <src.s> <origin>                     # still right with a nop inserted?
python3 tools/unpack.py start|fic|text|relocate ...   # PP's formats unpacked; tools/pack.py packs them
python3 src/probes/epic02/chain_probe.py <setup>      # a dump of every launcher stage at its entry
tools/build_launcher.sh [--allow-longer] [<src folder>] [<out>]  # the launcher built from src/ into tools/dev/builds/launcher/
tools/build_gemdrive.sh [<out>]                # the launcher changed for a GEMDOS drive (EPIC-04, S1): builds/gemdrive/build/LEMMINGS
python3 tools/build_gos5.py <START.TOS> <out> [--info] [--floppy]   # a GOS5 game's start program built for a GEMDOS drive (EPIC-04)
python3 tools/build_gos4.py <START.TOS> <out> [--info] [--floppy]   # a GOS4 game's start program built for a GEMDOS drive (EPIC-05)
python3 src/probes/epic04/gos5_run.py <ZIP> [--setup <s>] [--disk <d>] [--memsize N]  # one GOS5 or GOS4 game built (src/survey/ports.tsv) and run
python3 src/probes/epic05/gos4_calls.py <ZIP> | --report <run>  # the GEMDOS calls a GOS4 game makes to GOS, from PPDRIVER
python3 src/probes/epic05/gos4_selftest.py [--setup <s>]        # the GOS4 forwarder's file calls tested under GOS4 (PASS or the step)
python3 tools/survey/mirror.py                 # resume or refresh the copy of PP's site in MIRROR (D-12)
python3 tools/survey/catalogue.py              # src/survey/catalogue.csv: PP's list, read from the mirror
python3 tools/survey/unpack_games.py           # every archive in the mirror into tools/dev/builds/survey/games/
python3 tools/survey/inventory.py              # src/survey/files.csv: every file of every adaptation
python3 tools/survey/classify.py               # src/survey/migration.csv: every game's strategy, from its files
python3 src/probes/epic03/mode_probe.py <ZIP> [--disk gemdrive|ppdriver] [--start <prg>]  # one game from the mirror, as it is
python3 tools/survey/run_all.py [--jobs 5] [--only <name> ...] [--disk ppdriver] [--setup ste-162] [--redo|--retry|--reanalyse]
                                               # every game run in Hatari: builds/survey/runs.tsv, snapshots/
python3 tools/survey/review.py [--host 0.0.0.0]  # Diego's OK/Broken/Not sure per run, into src/survey/review.tsv
python3 tools/survey/run_other.py [--jobs 5] [--only <ZIP> ...]  # the GOS games' other downloads: builds/survey/runs-other.tsv
python3 tools/survey/verdicts.py               # runs, Diego's answers, findings.tsv and solutions.tsv into migration.csv
python3 tools/survey/screens.py <png> ...      # is this screenshot the TOS desktop (its menu bar, any colours)
python3 tools/survey/sheet.py [--all]          # a contact sheet of the runs not shown yet
python3 tools/survey/sdcard.py                 # every game for the Multidevice's GEMDRIVE: builds/sdcard/, copied to a microSD
python3 tools/site/build_site.py [--check] [--no-snapshots]  # the website into tools/dev/builds/site/ (open index.html)
tools/site/deploy_site.sh [--dry-run]          # the site, with its snapshots, force-pushed to gh-pages (D-28)
python3 tools/site/check_public.py [<clone>]   # is a clone ready to go public: docs/publication/remove.txt (D-15)
./docs/epics/cockpit.sh                        # after editing any epic or story
```

The test machines are Hatari's ST with TOS 1.04 and STE with TOS 1.62 and 2.06, 1 MB, each with
two disks: `gemdrive` (Hatari's GEMDOS drive, the target) and `ppdriver` (an ACSI image booted by
PPDRIVER, built by `../atari-hd --ppdriver-bootable`, the working reference, D-09). A harness run
leaves `tools/dev/logs/<date>-<setup>-<disk>/`: `hatari.out` (GEMDOS calls with file names,
BIOS/XBIOS calls, ACSI commands, debugger output), `shots/`, the run's own disk copy and
`result.txt` (PASS/FAIL, steps reached, PC at the end). Hatari's sources (v2.6.1) are in
`../hatari`, for reading only (C-02).

## Backlog

Work is tracked in `docs/epics/`, the same procedure as the sibling repositories' (D-02).
`ITERATIONS.md` is the plan and its order, and holds the first pass's hypotheses `H-NN`;
`EPIC-NN-<slug>/epic.md` and `STORY-NN-<slug>.md` hold the work (tasks are the checkboxes);
`DECISIONS.md` holds the `D-NN` decisions and `C-NN` constraints; `STATUS.md` is generated by
`./docs/epics/cockpit.sh`, run after editing any epic or story. The rules are in
`docs/epics/README.md`: one epic at a time, each ending in a verification story that is Diego's
checkpoint; a task is checked only when it was observed; `LEMMINGS/` is never modified; the
backlog is committed, code and notes only when Diego says so (D-03). Each epic on its own branch
`epic-NN-<slug>` (D-07, proposed).

Iteration 1 is **understand and classify**: EPIC-00, the development environment, the test tools
and Hatari as the test machine (ST and STE, TOS up to 2.06; GEMDRIVE mode, and an ACSI image
booted by PP's driver, PPDRIVER, as the working reference); EPIC-01, why the game fails in
GEMDRIVE mode; EPIC-02, the launcher recompilable and tested with our own build, the groundwork
for the solutions; EPIC-03, PP's modes and every adaptation classified with a verdict. Iteration
2 is **solutions**: EPIC-04 to EPIC-07, one per group of the test card, chosen and ordered at
EPIC-03's checkpoint (D-16), then EPIC-08, the ports on acsi2stm's GemDrive (D-18), and EPIC-09,
the patcher that installs them (D-17).

## Conventions and gotchas

- **68000, big-endian**: words and longs are big-endian; a word or long access at an odd address
  is an Address Error. ST hardware registers live at `$FFFF8000` and up (DMA/ACSI at
  `$FFFF8604`-`$FFFF860D`, MFP at `$FFFFFA01` and up).
- **Docker Desktop can serve a container a file the host has just rewritten in place, at its old
  length** (vasm once assembled a source cut off mid-line). Run the toolchain only through
  `tools/dev/toolchain.sh` (`tc_stage` hands the container a fresh copy), never `stcmd`, which
  also follows `latest` instead of the pinned `1.4.0` (D-05).
- **Hatari loads its saved configuration** (`~/Library/Application Support/Hatari/hatari.cfg`)
  unless `HOME` points elsewhere; the harness gives each run its own. Control-socket keys go in
  hex (`0x39`): a single character is typed as that character.
- **Hatari's debugger writes memory behind the I/O handlers** (`STMemory_Write`): a `w` to the
  ACIA or the DMA registers changes nothing. To make the machine send an IKBD command, make its
  own code do it (the harness's `mouse` step). `w` values are in the current base: `$0e`.
- **The launcher reads the game by sectors**, not through the system's GEMDOS: the game asks
  PP's loader for a file by name, and D15R (TOS 1.04 running from RAM, H-08) swaps in its own
  TOS and reads the FAT volume with BIOS `Rwabs` through the PP driver
  (`src/notes/gemdrive-failure.md`, `src/notes/launch-chain.md`). A GEMDOS drive has no sectors;
  that is the whole GEMDRIVE problem.
- **The sources in `src/` are generated from their maps** (`src/<stage>/<stage>.map`) by
  `tools/dev/mksource.py`: change the map (names, comments, entries) and regenerate, then
  `tools/dev/all_harness.sh`. Hand edits to a `.s` are lost on the next generation. The
  launcher's sources are not committed, only their maps: START.TOS's stub, LEMLD2 and LS2DD
  reassemble to PP's files (D-25), D15R's two are TOS 1.04's code (D-13). `tools/make_sources.sh`
  makes all five from `LEMMINGS/`. Our own code (`src/gemdrive/`) is committed.
- **Never read a trace whole.** `hatari.out` is tens of thousands of lines, and a CPU trace gets
  huge (the first pass's reached 800 MB); use `grep`, `head`, `tail` or `sed -n`, and bound CPU
  traces in time.
- The first pass's tools find the repository through their own location
  (`Path(__file__).parents[2]`), so they break once archived; copy one into `tools/` only when a
  story has verified it.
- **The remote is private until the release** (D-27): `origin` is
  `github.com/sidecartridge/gemdrive-game-patches`, every branch pushed. Push only this working
  copy, never `../reverse-eng-ppera-hd` (the uncleaned history), and only on Diego's word; nothing
  under `LEMMINGS/` or `_archive/` is ever committed (D-25).
- `.DS_Store` files are macOS noise; ignore them.
- **The website speaks to its readers, never to the backlog** (Diego, 2026-10-16, D-20). Nothing the
  site publishes refers to `docs/epics/` or what is in it: no iterations, epics, stories or tasks
  (`EPIC-04 STORY-05`), no `D-NN`, `C-NN` or `H-NN`, no `ITERATIONS.md`, `DECISIONS.md` or
  `STATUS.md`. That covers `src/notes/*.md`, `tools/dev/README.md` (the Tools page), the
  catalogue's reasons and solutions (`src/survey/findings.tsv`, `solutions.tsv`, so
  `migration.csv`) and `tools/site/build_site.py`'s own text. Write what a reader follows: what was
  found, when, on which machine, and which page or tool shows it. The backlog may cite the notes;
  the notes never cite the backlog. `build_site.py --check` fails on such a reference.
- **The website does not name the adaptations' author** (Diego, 2026-10-16, D-21): PP, PPera or
  Peter Putnik means nothing to a reader. Where the games, their list and their documentation are is
  "the 8bitchip.info website"; what the adaptations are made of is "the Gamex launcher", "GOS",
  "the original files". Technical names stay: the `PPHD` signature, the `PPDRIVER` driver, a message
  quoted in code (`This prg. requires PP, AHDI or Hddriver`). The site links to the 8bitchip.info
  website only for a game's page or a technical page (`GAMEXdoc.html`, `agcat.html`, `fromhd3.php`),
  never to its home page. Same scope as the rule above, the survey's strategy names too (`launcher
  without Gamex`); `build_site.py --check` fails on PP, PPera or Putnik outside code and on a link
  to the home page.

---

## Working style

These behavioral guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think before coding

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity first

Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical changes

Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- When your changes orphan an import/variable/function, remove it. Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 4. Goal-driven execution

Define success criteria. Loop until verified.
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan with a verification check per step. For this repo the
checks are a Hatari run with an expected milestone, a memory dump compared by SHA-256, a round
trip that reassembles to the original bytes, and `shasum -a 256 -c LEMMINGS.sha256`; once EPIC-00
is done, `tools/dev/all_harness.sh` runs them all.

### 5. No AI attribution

Never add AI-tool attribution to commits, PR descriptions, code comments,
docs, or any other artifact. This means **no**:
- "Generated with Claude Code", "Co-authored by Claude", "Made with ChatGPT",
  or any similar phrasing.
- `Co-Authored-By: Claude …`, `Co-Authored-By: ChatGPT …`, or any other
  AI co-author trailer.
- "AI-assisted", "written with the help of an LLM", etc., as comments or
  changelog entries.

Write the message as the human author. Do not mention AI tools used to
produce the work.

### 6. Do the work yourself

You MUST execute every task on your own, with what this computer has:
- the emulator (Hatari), the toolchain, `../atari-hd` and the developer tools;
- the TOS images and the evidence in `LEMMINGS/`;
- scripts you write;
- the sibling sessions (`ListAgents`), whose Hatari harnesses have already solved problems this
  one will meet.

Do not hand Diego work you can do. A task is his only when it needs his decision or approval: the
checkpoints and the choice of solutions (EPIC-03's checkpoint, D-14). Do not turn "Diego does it" into a
shot list or a checklist for him.

Evidence comes from this computer: Hatari runs, memory dumps, traces, round trips.
