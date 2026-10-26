# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A reverse-engineering workspace for **PP's (PPera's) Gamex hard-disk launcher** for *Lemmings* on
the Atari ST: the 2011 adaptation (`LEMMINGS/README.TXT`) that runs the game from a hard disk. The
target is the launcher and the disk layer it installs (its loader D15R and a copy of PP's
resident driver), not the game. The aim is **GEMDRIVE mode**: the game started from a Hatari GEMDOS
drive (`--harddrive`) instead of a hard-disk image, for Lemmings and then for every game PP adapted.
First understand and classify, then the solutions.

1. **Why it fails** in Hatari's GEMDRIVE mode today. Diego's guess, confirmed: the PPera
   driver embedded in the launcher (`src/notes/gemdrive-failure.md`).
2. **Recompilable launcher**: every PPera launcher program reverse engineered into 68000 sources
   that reassemble to the original bytes, and our own build of them booting the game.
3. **The ways PP's adaptations run from a hard disk**: PP's modes understood first, then every
   game in PP's list (<https://atari.8bitchip.info/fromhd3.php>) classified by the strategy that
   runs it from a hard disk, with one of three verdicts: as it is, fix (with the solution), not
   feasible (with the reason); and the solutions proposed; all of it, with the project's
   documentation, as a website published with the repository (designed with the frontend-design
   skill). PP's site was mirrored first: work from the mirror (`MIRROR` in `tools/dev/dev.cfg`),
   not the site.
4. **The solutions**: the games that do not run, ported by the test card's groups: GOS5, with
   Lemmings first; GOS4; the small fixes; the unsure games; the ports checked on acsi2stm's
   GemDrive, the other GEMDRIVE (an STM32 on the ACSI port, its driver in the ST's RAM); and the
   patcher, a page of the website that checks a user's original download by signature and patches
   it with our builds. Each is checked in Hatari, and also on Diego's SidecarTridge Multidevice
   from a card.

**Hatari's code is never modified**: every fix lives on the Atari side.

The work is planned in `docs/epics/`, local only (see Planning backlog). This repository is not
part of the sidecartos product (`../sidecartos`, `../sidecartos-config`, `../romemul-switcher-rom`):
it borrows their procedure, not their sync contract.

**Fresh start.** A first pass (2026-04-23/24) is archived, read-only, in
`_archive/2026-04-first-pass/`: its tools, listings and notes (`src/`), the patched builds it had
left in `LEMMINGS/` (`lemmings-patched/`), the hashes of everything before the move
(`MANIFEST.before.sha256`) and an 800 MB `trace.log` (git-ignored). Its conclusions are
hypotheses, not facts: a finding counts only once a run here observes it again, and its code is
reused only after a run has verified it. Its notes
contradict its own code in places.

## The evidence: `LEMMINGS/`

PP's original files, **never modified**: runs, patches and experiments work on a copy under
`tools/dev/builds/`. `shasum -a 256 -c LEMMINGS.sha256` proves it.

- `START.TOS`: the program the user runs; a GEMDOS executable (`0x601A` header) whose 230-byte
  text unpacks and starts the rest.
- `GXUT260.PRG`: "Gamex utility" v2.60, a GEMDOS executable; its role is open.
- `LEMMINGS.PCH`: read by the loader; format open. `file(1)` calls it "MIPS ECOFF" from its
  `01 40` header: wrong.
- `LS2DD.FIC`, `D15R_F5.FIC`, `D15R_H5.FIC`: start with ASCII `C3` and two zero bytes
  (`43 33 00 00`), which `file(1)` calls "Clarion Developer data": wrong. Despite the extension
  they are packed code, not catalogues.
- `FILES/`: the game's data. `CODE` and `MAIN` are ICE-packed (`Ice!` magic) game code; the rest
  are levels (`LEVEL000`-`LEVEL024`, `LEVELDAT`, `ODDTABLE`), graphics (`GROUNDn`, `OBJECTSn`,
  `SPECIALn`, `LEMMINGn`, `INTROPAR`, `*.IMG`) and music and samples.
- `README.TXT`: any ST, STE, Mega ST, Mega STE or Falcon with at least 1 MB, "PP, AHDI or Hddriver"
  driver, a partition under 512 MB; on the Falcon, start from ST medium resolution.

**PP's own documentation**, on <https://atari.8bitchip.info>: `GAMEXdoc.html` (Gamex, and GOS,
his modded GEMDOS 0.15 of TOS 1.04 that runs in high RAM), `agcat.html` (his classification
of the games by floppy access), `GamexLSrc.html`, `GamexLSrc2.html` and `GamexLSrc3.html` (three of
his launcher sources, 2009), `fromhd.php` (his view of GEMdrive). All of it is in the mirror.
Cite it by URL and never copy it into the repository. A claim from them counts only once a run
shows it.

`LEMMINGS/` and `_archive/` stay on this Mac and out of git: both are git-ignored and were
removed from the history before the repository went public.

## Layout

- `docs/`: the planning backlog, git-ignored, local only.
- `src/`: what this project produces: unpacked stages, reconstructed sources (vasm Motorola
  syntax) that reassemble byte for byte to the original, notes (`src/notes/`; the GEMDRIVE
  cause is `gemdrive-failure.md`, every game's verdict and the solutions `solutions.md`) and
  the debugger probes (`src/probes/`, one folder per subject).
- `tools/`: the project's own unpackers and packers (standard-library Python); `tools/survey/`,
  the survey's scripts, starting with `mirror.py`, which copied PP's site into `MIRROR`; `tools/site/`,
  the website's builder, style and script, and the check of a clone before going public.
- `tools/publication/`: what must never enter the repository or its history (`remove.txt`,
  checked by `tools/site/check_public.py`) and the history clean-up used before it went public.
- `tools/dev/`: the development environment: pinned toolchain scripts, the
  round-trip check, the Hatari disk setups and harness. `builds/`, `logs/` and `dev.cfg` are
  git-ignored.
- `_archive/2026-04-first-pass/`: the first pass, read-only.

## Commands

Everything is in `tools/dev/` (details and examples in `tools/dev/README.md`). Once per
machine: Docker running with `logronoide/atarist-toolkit-docker-x86_64:1.4.0`, and
`cp tools/dev/dev.cfg.example tools/dev/dev.cfg` (paths to Hatari, the TOS images, `../atari-hd`).

```
tools/dev/all_harness.sh                       # check everything: disks, round trip, 6 Hatari runs, the site (~2 min)
tools/dev/make_disks.sh [<game folder>]        # builds/disks/: gemdrive/ and ppdriver.img from LEMMINGS/ or a patched tree
python3 tools/dev/hatari_harness.py --setup st-104|ste-162|ste-206 --disk gemdrive|ppdriver \
    [--expect tools/dev/expect/launcher-start.exp] [--parse <debugger script>] [--no-auto] [--trace <flags>]
python3 src/probes/gemdrive-failure/gate_probe.py <setup> <disk>  # the GEMDRIVE failure's breakpoint chains; read_probe.py <run>
tools/dev/disasm.sh <bin> <vma> <out.lst>      # objdump listing, 68000
python3 tools/dev/listing2vasm.py <out.lst> <bin> <out.s>   # a source that reassembles to <bin>
tools/dev/roundtrip.sh <src.s> <ref.bin>       # PASS, or FAIL at the first differing offset
tools/dev/asm.sh [--tos] <src.s> <out.bin> [<listing>] # vasm, 68000, -no-opt (--tos: a GEMDOS program)
python3 tools/dev/mksource.py src/<stage>/<stage>.map src/<stage>/<stage>.s   # a stage's source from its map
python3 tools/dev/shiftcheck.py [--tos] <src.s> <origin>                     # still right with a nop inserted?
python3 tools/unpack.py start|fic|text|relocate ...   # PP's formats unpacked; tools/pack.py packs them
python3 src/probes/stages/chain_probe.py <setup>      # a dump of every launcher stage at its entry
tools/build_launcher.sh [--allow-longer] [<src folder>] [<out>]  # the launcher built from src/ into tools/dev/builds/launcher/
tools/build_gemdrive.sh [<out>]                # the launcher changed for a GEMDOS drive: builds/gemdrive/build/LEMMINGS
python3 tools/build_gos5.py <START.TOS> <out> [--info] [--floppy]   # a GOS5 game's start program built for a GEMDOS drive
python3 tools/build_gos4.py <START.TOS> <out> [--info] [--floppy]   # a GOS4 game's start program built for a GEMDOS drive
python3 src/probes/gos5/gos5_run.py <ZIP> [--setup <s>] [--disk <d>] [--memsize N]  # one GOS5 or GOS4 game built (src/survey/ports.tsv) and run
python3 src/probes/gos4/gos4_calls.py <ZIP> | --report <run>  # the GEMDOS calls a GOS4 game makes to GOS, from PPDRIVER
python3 src/probes/gos4/gos4_selftest.py [--setup <s>]        # the GOS4 forwarder's file calls tested under GOS4 (PASS or the step)
python3 tools/survey/mirror.py                 # resume or refresh the copy of PP's site in MIRROR
python3 tools/survey/catalogue.py              # src/survey/catalogue.csv: PP's list, read from the mirror
python3 tools/survey/unpack_games.py           # every archive in the mirror into tools/dev/builds/survey/games/
python3 tools/survey/inventory.py              # src/survey/files.csv: every file of every adaptation
python3 tools/survey/classify.py               # src/survey/migration.csv: every game's strategy, from its files
python3 src/probes/modes/mode_probe.py <ZIP> [--disk gemdrive|ppdriver] [--start <prg>]  # one game from the mirror, as it is
python3 tools/survey/run_all.py [--jobs 5] [--only <name> ...] [--disk ppdriver] [--setup ste-162] [--redo|--retry|--reanalyse]
                                               # every game run in Hatari: builds/survey/runs.tsv, snapshots/
python3 tools/survey/review.py [--host 0.0.0.0]  # Diego's OK/Broken/Not sure per run, into src/survey/review.tsv
python3 tools/survey/run_other.py [--jobs 5] [--only <ZIP> ...]  # the GOS games' other downloads: builds/survey/runs-other.tsv
python3 tools/survey/verdicts.py               # runs, Diego's answers, findings.tsv and solutions.tsv into migration.csv
python3 tools/survey/screens.py <png> ...      # is this screenshot the TOS desktop (its menu bar, any colours)
python3 tools/survey/sheet.py [--all]          # a contact sheet of the runs not shown yet
python3 tools/survey/sdcard.py                 # every game for the Multidevice's GEMDRIVE: builds/sdcard/, copied to a microSD
python3 tools/site/build_site.py [--check] [--no-snapshots]  # the website into tools/dev/builds/site/ (open index.html)
tools/site/deploy_site.sh [--dry-run]          # the site, with its snapshots, force-pushed to gh-pages
make tag                                       # the release: no backlog reference, deploy_site.sh, then version.txt's tag pushed
python3 tools/site/check_public.py [<clone>]   # is a clone ready to go public: tools/publication/remove.txt
./docs/epics/cockpit.sh                        # after editing any epic or story (local only)
```

The test machines are Hatari's ST with TOS 1.04 and STE with TOS 1.62 and 2.06, 1 MB, each with
two disks: `gemdrive` (Hatari's GEMDOS drive, the target) and `ppdriver` (an ACSI image booted by
PPDRIVER, built by `../atari-hd --ppdriver-bootable`, the working reference). A harness run
leaves `tools/dev/logs/<date>-<setup>-<disk>/`: `hatari.out` (GEMDOS calls with file names,
BIOS/XBIOS calls, ACSI commands, debugger output), `shots/`, the run's own disk copy and
`result.txt` (PASS/FAIL, steps reached, PC at the end). Hatari's sources (v2.6.1) are in
`../hatari`, for reading only.

## Planning backlog (`docs/`)

`docs/epics/` holds the local planning notes, the same procedure as the sibling repositories':
`ITERATIONS.md` is the plan and its order; `EPIC-NN-<slug>/epic.md` and `STORY-NN-<slug>.md` hold
the work (tasks are the checkboxes); `DECISIONS.md` holds the `D-NN` decisions and `C-NN`
constraints; `STATUS.md` is generated by `./docs/epics/cockpit.sh`, run after editing any epic or
story. The rules are in `docs/epics/README.md`: one epic at a time, each ending in a verification
story that is Diego's checkpoint; a task is checked only when it was observed; `LEMMINGS/` is never
modified; code and notes are committed only when Diego says so. **The whole `docs/` tree is
git-ignored** and lives only on this Mac.

- **Never name an epic, story, iteration, task, decision or constraint in anything that is
  committed**: code comments, documentation, data, `CHANGELOG.md`, commit messages, tags,
  branch names, folder names. `EPIC-03 STORY-01` or `D-17` tells a reader of this repository
  nothing and cannot be looked up, and a commit message cannot be scrubbed afterwards. Write what
  the code does and why instead; work happens on `main` or a branch named for what it does.
- **Never reference a path under `docs/`** from anything that ships: someone who clones the repo
  has no `docs/`. Inline the information itself.
- Traceability runs the other way: once work lands, record the commit hash in the planning note.
- `make tag` refuses to release while
  `git grep -IiE "EPIC-|STORY-|\bepics?\b|\bstor(y|ies)\b|docs/|\b[DCH]-[0-9]{2}\b" -- . ':!CLAUDE.md' ':!.gitignore' ':!Makefile' ':!src/survey/*.csv' ':!src/survey/patches.tsv'`
  finds anything (the CSVs and `patches.tsv` are excluded for game and archive names such as *New Zealand Story* or `EPIC.ZIP`).

## Conventions and gotchas

- **68000, big-endian**: words and longs are big-endian; a word or long access at an odd address
  is an Address Error. ST hardware registers live at `$FFFF8000` and up (DMA/ACSI at
  `$FFFF8604`-`$FFFF860D`, MFP at `$FFFFFA01` and up).
- **Docker Desktop can serve a container a file the host has just rewritten in place, at its old
  length** (vasm once assembled a source cut off mid-line). Run the toolchain only through
  `tools/dev/toolchain.sh` (`tc_stage` hands the container a fresh copy), never `stcmd`, which
  also follows `latest` instead of the pinned `1.4.0`.
- **Hatari loads its saved configuration** (`~/Library/Application Support/Hatari/hatari.cfg`)
  unless `HOME` points elsewhere; the harness gives each run its own. Control-socket keys go in
  hex (`0x39`): a single character is typed as that character.
- **Hatari's debugger writes memory behind the I/O handlers** (`STMemory_Write`): a `w` to the
  ACIA or the DMA registers changes nothing. To make the machine send an IKBD command, make its
  own code do it (the harness's `mouse` step). `w` values are in the current base: `$0e`.
- **The launcher reads the game by sectors**, not through the system's GEMDOS: the game asks
  PP's loader for a file by name, and D15R (TOS 1.04 running from RAM) swaps in its own
  TOS and reads the FAT volume with BIOS `Rwabs` through the PP driver
  (`src/notes/gemdrive-failure.md`, `src/notes/launch-chain.md`). A GEMDOS drive has no sectors;
  that is the whole GEMDRIVE problem.
- **The sources in `src/` are generated from their maps** (`src/<stage>/<stage>.map`) by
  `tools/dev/mksource.py`: change the map (names, comments, entries) and regenerate, then
  `tools/dev/all_harness.sh`. Hand edits to a `.s` are lost on the next generation. The
  launcher's sources are not committed, only their maps: START.TOS's stub, LEMLD2 and LS2DD
  reassemble to PP's files, D15R's two are TOS 1.04's code. `tools/make_sources.sh`
  makes all five from `LEMMINGS/`. Our own code (`src/gemdrive/`) is committed.
- **Never read a trace whole.** `hatari.out` is tens of thousands of lines, and a CPU trace gets
  huge (the first pass's reached 800 MB); use `grep`, `head`, `tail` or `sed -n`, and bound CPU
  traces in time.
- The first pass's tools find the repository through their own location
  (`Path(__file__).parents[2]`), so they break once archived; copy one into `tools/` only when a
  run has verified it.
- **The repository is public** (since v1.0.0): `origin` is
  `github.com/sidecartridge/gemdrive-game-patches`. Push only this working copy, never
  `../reverse-eng-ppera-hd` (the uncleaned history), and only on Diego's word; nothing under
  `LEMMINGS/`, `_archive/` or `docs/` is ever committed.
- `.DS_Store` files are macOS noise; ignore them.
- **The website speaks to its readers, never to the backlog** (Diego, 2026-10-16), and so does
  everything else committed (above). The site's sources include `src/notes/*.md`,
  `tools/dev/README.md` (the Tools page), the catalogue's reasons and solutions
  (`src/survey/findings.tsv`, `solutions.tsv`, so `migration.csv`) and
  `tools/site/build_site.py`'s own text. Write what a reader follows: what was found, when, on
  which machine, and which page or tool shows it. `build_site.py --check` fails on such a
  reference.
- **The website does not name the adaptations' author** (Diego, 2026-10-16): PP, PPera or
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
trip that reassembles to the original bytes, and `shasum -a 256 -c LEMMINGS.sha256`;
`tools/dev/all_harness.sh` runs them all.

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
checkpoints and the choice of solutions. Do not turn "Diego does it" into a
shot list or a checklist for him.

Evidence comes from this computer: Hatari runs, memory dumps, traces, round trips.
