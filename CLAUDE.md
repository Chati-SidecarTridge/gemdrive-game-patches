# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A reverse-engineering workspace for **PP's (PPera's) Gamex hard-disk launcher** for *Lemmings* on
the Atari ST: the 2011 adaptation (`LEMMINGS/README.TXT`) that runs the game from a hard disk. The
target is the launcher and its embedded driver, not the game. The aim is **GEMDRIVE mode**: the
game started from a Hatari GEMDOS drive (`--harddrive`) instead of a hard-disk image. Three goals,
one epic each, in this order (D-08):

1. **Why it fails** in Hatari's GEMDRIVE mode today. Diego's guess, to confirm first: the PPera
   driver embedded in the launcher (H-07). EPIC-01.
2. **Recompilable launcher**: every PPera launcher program reverse engineered into 68000 sources
   that reassemble to the original bytes, and our own build of them booting the game. EPIC-02.
3. **The fix**: GEMDRIVE mode as an alternative way to launch Lemmings. EPIC-03. Other PPera
   games and the SidecarTridge's GEMDRIVE come later (`ITERATIONS.md` candidates).

**Hatari's code is never modified** (C-02): every fix lives on the Atari side.

The work is planned and tracked in `docs/epics/` (see Backlog). This repository is not part of
the sidecartos product (`../sidecartos`, `../sidecartos-config`, `../romemul-switcher-rom`): it
borrows their procedure, not their sync contract (D-02).

**Fresh start (D-01).** A first pass (2026-04-23/24) is being archived to
`_archive/2026-04-first-pass/` by EPIC-00 STORY-01. Until that story is done, its work still sits
in `src/`, a patched build sits in `LEMMINGS/START.TOS` (original: `START.TOS.orig`), and an
800 MB `trace.log` sits in the root. Its conclusions are hypotheses `H-NN` in
`docs/epics/ITERATIONS.md`, not facts: a finding counts only once a story here observes it
again, and its code is reused only after a story has verified it. Its notes contradict its own
code in places.

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

`DESKTOP.INF` in the root is the first pass's emulated `C:` desktop: it pointed a Hatari GEMDOS
drive at this repository's root.

## Layout

- `docs/epics/`: the backlog (committed, D-03).
- `src/`: what this project produces: unpacked stages, reconstructed sources (vasm Motorola
  syntax, D-05) that reassemble byte for byte to the original, and notes (`src/notes/`).
- `tools/`: the project's own unpackers and packers (standard-library Python).
- `tools/dev/`: the development environment from EPIC-00: pinned toolchain scripts, the
  round-trip check, the Hatari disk setups and harness. `builds/`, `logs/` and `dev.cfg` are
  git-ignored.
- `_archive/2026-04-first-pass/`: the first pass, read-only (D-01).

## Tools on this Mac

Until EPIC-00 delivers `tools/dev/`, these are the tools, checked on 2026-10-11:

- Hatari 2.6.1 at `/usr/local/bin/hatari`; its sources in `../hatari`.
- `stcmd` (Diego's `atarist-toolkit-docker`) runs `logronoide/atarist-toolkit-docker-x86_64:latest`
  with the current folder mounted at `/tmp`, so a file is passed as `/tmp/<relative path>`. That
  image has `vasmm68k_mot`, `vlink` and `m68k-atari-mint-objdump`/`-as`/`-gcc`. Disassembling a
  raw binary loaded at an address:
  ```
  STCMD_NO_TTY=1 STCMD_QUIET=1 stcmd m68k-atari-mint-objdump -D -b binary -m m68k --adjust-vma=0x70000 /tmp/<bin>
  ```
- Python 3.14 (`python3`), standard library only; mtools (`mcopy`, `mformat`).
- `../atari-hd` (sidecartridge/atari-hd): builds Atari hard-disk images. `--ppdriver-bootable`
  makes the self-booting PPDRIVER image of the working reference (D-09) from its bundled boot
  blob; it cannot copy files in, so the game goes in with `mcopy`.
- TOS images: C-03 in `docs/epics/DECISIONS.md` (in `../sidecartos`, never copied here).

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

Iteration 1 is **GEMDRIVE**: EPIC-00, the development environment, the test tools and Hatari as
the test machine (ST and STE, TOS up to 2.06; GEMDRIVE mode, and an ACSI image booted by PP's
driver, PPDRIVER, as the working reference); EPIC-01, why the game fails in GEMDRIVE mode;
EPIC-02, the launcher recompilable and tested with our own build; EPIC-03, the GEMDRIVE fix for
Lemmings.

## Conventions and gotchas

- **68000, big-endian**: words and longs are big-endian; a word or long access at an odd address
  is an Address Error. ST hardware registers live at `$FFFF8000` and up (DMA/ACSI at
  `$FFFF8604`-`$FFFF860D`, MFP at `$FFFFFA01` and up).
- **`stcmd` passes its arguments unquoted** (`$@`), so `stcmd bash -c '…'` breaks: call one tool
  per `stcmd`. It follows `latest`; EPIC-00 STORY-02 pins `1.4.0` (D-05).
- **Hatari loads its saved configuration** (`~/Library/Application Support/Hatari/hatari.cfg`)
  unless `HOME` points elsewhere: a run that must be reproducible sets its own `HOME`.
- **Never read a trace whole.** A Hatari CPU trace reaches hundreds of MB in seconds; use `grep`,
  `head`, `tail` or `sed -n`, and bound traces in time.
- The first pass's tools find the repository through their own location
  (`Path(__file__).parents[2]`), so they break once archived; copy one into `tools/` only when a
  story has verified it.
- `.DS_Store` files are macOS noise; ignore them.

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
checkpoints and the choice of approach (EPIC-03 STORY-01). Do not turn "Diego does it" into a
shot list or a checklist for him.

Evidence comes from this computer: Hatari runs, memory dumps, traces, round trips.
