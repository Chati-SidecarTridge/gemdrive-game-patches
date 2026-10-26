# Iterations

Epics are grouped into iterations via the `iteration: N` frontmatter field; the cockpit groups the
dashboard by it. This file is the narrative: what each iteration sets out to do, the order it is
done in and why, and how it ends. It also holds the hypotheses (`H-NN`) the stories confirm or
refute (D-01).

| Iteration | Theme | Status |
| --- | --- | --- |
| 1 | **Understand and classify**: why Lemmings fails from Hatari's GEMDOS drive, PP's launcher as sources that rebuild it, and every PP adaptation classified with a verdict (D-14) | done (2026-10-15) |
| 2 | **Solutions**: the games that do not run from a GEMDOS drive, ported by the test card's groups, in the order Diego chose at EPIC-03's checkpoint (D-16); Hatari unchanged | in progress |

---

## Where the first pass left off

On 2026-04-23 and 24, before this backlog existed, a first pass worked without a plan, tests or
version control. It left:

- Python unpackers and patchers;
- objdump listings with hand annotations, and notes;
- about 30 unpacked and patched binaries;
- an 800 MB Hatari CPU trace.

It pointed a Hatari GEMDOS drive at this repository's root (`DESKTOP.INF`) and left a patched
build in place of `LEMMINGS/START.TOS`, the original kept as `START.TOS.orig`. Diego decided on
2026-10-11 to start again from scratch, with that work archived (D-01); EPIC-00 STORY-01 moves it
to `_archive/2026-04-first-pass/`.

## Hypotheses

None is a fact here until a story observes it. H-01 to H-06 are the first pass's findings; H-07 is
Diego's guess. H-08 comes from PP's own documentation.

| ID | Hypothesis | Tested by | Verdict |
| --- | --- | --- | --- |
| H-01 | `START.TOS`'s 230-byte text is only a self-extractor. Its data section is a 32-byte record (magic `C3`, sizes, the name `LEMLD2.TOS`) and a custom LZSS stream (not ICE), which unpacks to a GEMDOS program (34,910-byte text, no data, 177 relocations) that the stub relocates and jumps to. | EPIC-02 STORY-02 | **confirmed** (2026-10-11): the header and the stream as described; LEMLD2.TOS unpacked and relocated by `tools/unpack.py` equals Hatari's memory byte for byte on all three setups; match lengths are (c & `$3F`) + 3 and + 4. `src/notes/launcher-formats.md`. |
| H-02 | The `.FIC` files are not catalogues: each is a 32-byte `C3` header plus the same LZSS stream. `LS2DD.FIC` unpacks to code run at `$70000` that loads `psyglogo.img`, `dmalogo.img` and `main`; `D15R_F5.FIC` and `D15R_H5.FIC` unpack to a blob at `$C0100` that performs the file loads. | EPIC-02 STORY-02 | **confirmed, with additions** (2026-10-11): each `.FIC` is the 32-byte `C3` header and the same stream; LS2DD (`$70000`) is patched by LEMLD2's block at `$80100` before it runs, and reads through PP's loader at `$85000` and D15R, not by itself; `D15R_F5` is the Falcon build. `launcher-formats.md`, EPIC-02 STORY-01. |
| H-03 | The loader first looks for a resident PP driver, the long `PPHD` at `_hdv_init - 8`. Without it, it reads sector 0 by itself: raw ACSI DMA registers under TOS 1.x, XBIOS `DMAread` under TOS 2 and later, then the Falcon IDE registers. Every path wants a sector 0 whose words sum to `$1234` (an executable boot sector); failing all, it prints "This prg. requires PP, AHDI or Hddriver hard disk driver". | EPIC-01 STORY-03 | **confirmed, with corrections** (2026-10-11): `$472` is `hdv_bpb`, not `_hdv_init`; the TOS 2.x path takes the device number from `pun_ptr` (`$516`); a good sector 0 is not the end of it, the launcher then continues into D15R. `src/notes/gemdrive-failure.md` §3–4. |
| H-04 | With the `PPHD` check patched out, a run on a Hatari GEMDOS drive stalls in `LS2DD`'s file-load retry loop, suspected to be the lower-case names it asks for (`psyglogo.img`) against upper-case files on a case-sensitive host folder. | EPIC-01 STORY-02 | **refuted** (2026-10-11): no file name is looked up after `Dsetpath("FILES")`, D15R walks the directories by sector; pushed past the gate by hand the stop is TOS's -15 from `Rwabs`; Hatari matches GEMDOS-drive names regardless of case. `gemdrive-failure.md` §4–5. |
| H-05 | The loader hooks `TRAP #1` only for `Malloc` and `Mshrink`, which always get a fixed heap at `$AF100`, and passes every other GEMDOS call to TOS. | EPIC-02 STORY-04 | **confirmed, with a correction** (2026-10-11): the stub exists (`trap1_stub`, text+`$B6C`) and does that, but only while LEMLD2 boots a driver from the disk's boot sector (`boot_driver`, the no-PP-driver path); its pass-on target is written at run time (`trap1_old`), and on a Falcon or TT the area is `$186000`. During the game `TRAP #1` is D15R's own GEMDOS (`trap1`, `$C84A0`) inside TOS's image that `file_io` swaps in. `src/notes/launch-chain.md`. |
| H-06 | Under TOS 2.06 the loader takes the XBIOS path and works through whatever driver is installed. | EPIC-01 STORY-02 | **refuted** (2026-10-11): it takes the XBIOS `DMAread` path, a raw ACSI read on the `PUN_INFO` device; with no driver `pun_ptr` is 0 and the read returns -1. `gemdrive-failure.md` §3. |
| H-07 | **The game fails in GEMDRIVE mode because of the PPera driver embedded in the launcher.** Diego, 2026-10-11. | EPIC-01 STORY-03 | **confirmed in substance, restated** (2026-10-11): the launcher embeds no driver; it requires PP's resident driver (XBRA `PPHD` before `hdv_bpb`), copies and patches it, and its loader D15R reads the FAT volume by sectors through it (`Getbpb`, `Mediach`, `Rwabs`); GEMDRIVE has neither. `gemdrive-failure.md` §1, §4. |
| H-08 | **D15R is PP's GOS**: the GEMDOS 0.15 of TOS 1.04, modded and relocated to high RAM, with the hard-disk driver installed again below it (GOS5 in PP's `GAMEXdoc.html`, which puts the driver and buffers at 700-768 KB and the modded GEMDOS at 768-830 KB). PP's Starglider launcher source (`GamexLSrc3.html`) loads `D15R_NG1.FIC`, "Packed GEMDOS, GOS 1.00". From PP's documents, 2026-10-11. | EPIC-02 STORY-05 | **confirmed, and wider** (2026-10-11): D15R is TOS 1.04 UK in RAM: its GEMDOS (every function), BIOS, XBIOS, floppy driver (`hdv_*` byte for byte), start-up code and data, relocated to `$C0100`, with an image of TOS's RAM at `$D0528`, behind PP's entry points (`file_io`) and his own `TRAP #1` entry; 70.4% of its bytes equal the ROM's or are the same address relocated. `src/notes/disk-layer.md` §1. |

---

## Iteration 1: understand and classify

**Goal:** know, from runs, why PP's adaptations do or do not run from a Hatari GEMDOS drive
(GEMDRIVE mode), with Hatari unchanged (C-02), and decide what to do about each one:

- why Lemmings fails, shown by runs (EPIC-01);
- Lemmings' launcher as sources that rebuild it, with the tools and signatures to read PP's other
  launchers (EPIC-02);
- every game in PP's list of hard-disk adaptations classified by the strategy that runs it from a
  hard disk, with one of three verdicts (D-14): **as it is** (it runs from a GEMDOS drive
  unchanged), **fix** (with the solution that would make it run), **not feasible** (with the
  reason); and the solutions proposed, each with the games it covers and its cost (EPIC-03).
  PP's site was mirrored first, on 2026-10-11, out of the epic order (D-12);
- all of it, with the project's documentation, as a website published with the repository
  (EPIC-03 STORY-07), after the repository is cleaned of what cannot be published (D-15).

It ends at EPIC-03's checkpoint, where Diego chooses which solutions become iteration 2's epics,
and in what order.

### Implementation path

Epic numbers are the execution order. One epic at a time, each on its own `epic-NN-<slug>` branch
(D-07), each ending with a verification story that is Diego's checkpoint. Order set by Diego,
2026-10-11 (D-08, D-10, D-14).

| # | Epic | Why at this point |
| --- | --- | --- |
| EPIC-00 | The development environment, the test tools, and Hatari as the test machine | Asked by Diego, 2026-10-11: epic 0, as in the sibling repositories. Every later story is a run of these tools: the clean workspace and git, the pinned toolchain, the round-trip check, the GEMDRIVE and PPDRIVER setups on the ST and STE up to TOS 2.06, and the harness. |
| EPIC-01 | Why the game fails in Hatari's GEMDRIVE mode | First, confirm before building: Diego's guess (H-07) is checked against a working reference booted by PPDRIVER (D-09), and the result is the full list of what GEMDRIVE lacks. |
| EPIC-02 | The PPera launcher reverse engineered and recompilable, tested with our own build | The groundwork for every solution: a launcher we can change and test, the tools to read PP's other launchers (`tools/unpack.py`, `tools/pack.py`, `tools/dev/mksource.py`, the profile probes, the build), the signatures EPIC-03 classifies with, and the disk layer of the GOS strategy (D15R, TOS 1.04 in RAM) understood. |
| EPIC-03 | The ways PP's adaptations run from a hard disk, classified | Asked by Diego, 2026-10-11 (D-10, D-14). After EPIC-02, whose tools and signatures it uses; it decides iteration 2: the verdict for every game and the solutions to build. |

**Outcome** (2026-10-15):
- Lemmings fails from a GEMDOS drive because its launcher needs PP's resident driver and its loader
  reads the disk by sectors (EPIC-01; H-07 confirmed, restated).
- PP's launcher is now sources that rebuild it byte for byte and boot the reference (EPIC-02).
- Of PP's 1,831 adaptations:
  - 1,608 run from a Hatari GEMDOS drive as they are;
  - 212 need a fix, with four solutions proposed;
  - 1 is not feasible;
  - 10 are unsure.
  The verdicts are published as a website, ready for when the repository goes public (EPIC-03).
- Diego tested the verdicts on his machines with the SidecarTridge Multidevice's GEMDRIVE, from a
  test card holding every game. Every game he tried behaved as its folder says (EPIC-03 STORY-08).

## Iteration 2: solutions

**Goal:** the games that do not run from a GEMDOS drive are ported, group by group, with Hatari
unchanged (C-02). The groups are the test card's folders (`tools/survey/sdcard.py`). Each epic has:
- a first test game;
- the build of its fix: each game's start files for a GEMDOS drive, with their originals'
  signatures, which EPIC-09's program installs on a user's copy (D-17);
- its runs on Hatari's three setups;
- Diego's checkpoint, which also covers his Multidevice, from a card (D-16).

### Implementation path

Order set by Diego, 2026-10-15 and 2026-10-16 (D-16, D-17, D-18).

| # | Epic | Why at this point |
| --- | --- | --- |
| EPIC-04 | The GOS5 games from a GEMDOS drive (`FIXGOS5`, 87 games, S1) | Lemmings' own strategy, and the project's aim. Its launcher and GOS are EPIC-02's sources, so S1 is built and tested there first. The reference's first-level error, a candidate until now, is its STORY-02. |
| EPIC-05 | The GOS4 games from a GEMDOS drive (`FIXGOS4`, 117 games, S1) | The largest group. It reuses EPIC-04's builds by signature and adds S1's largest risk: the GEMDOS calls GOS4 games make during play. |
| EPIC-06 | The small fixes (`FIXPLAIN`, `FIXHOLE`, `FIXHAGE`: 8 games, S2 to S4) | Each fix is already shown by a trial (EPIC-03 STORY-06). One epic builds the three. |
| EPIC-07 | The unsure games settled (`UNSURE`, 10 games) | Last of the ports: each needs its cause found first, and their fixes may reuse the earlier epics' work. |
| EPIC-08 | The ports on acsi2stm's GemDrive (<https://github.com/retro16/acsi2stm>) | Asked by Diego (D-18): a check, after the ports, that their builds also work with the other GEMDRIVE, an STM32 on the ACSI port whose driver lives in the ST's RAM. Before the patcher, so that it installs builds that know both. |
| EPIC-09 | The patcher: a user's original start files checked by signature and replaced with our builds | Last (D-17): it installs what EPIC-04 to EPIC-08 built, so it comes when they are done. |

Order since 2026-10-26 (D-22): EPIC-09, the patcher, comes now, with the fixes built by EPIC-04 to
EPIC-06; EPIC-07 and EPIC-08 follow it, and the patcher grows with their fixes.

What was known before these epics were written, as their input:

- **The GOS strategy** (Lemmings' own: a Gamex launcher, PP's resident driver required, D15R, TOS
  1.04 in RAM, reading the game's files by sectors; `src/notes/disk-layer.md`). Its epic would
  start from what was the Lemmings fix (removed by D-14, kept in git history at `7fcff84` as
  `docs/epics/EPIC-04-gemdrive-fix/`): the approach chosen from EPIC-01's dependencies and
  EPIC-02's disk layer (a driver that serves records, a `file_io` that calls the system's GEMDOS,
  or something else); the game booting from a GEMDOS drive to its first level on every setup with
  the PPDRIVER reference still working; a scripted play session (a level to its end, the next one,
  a level of each section entered by number, the music changing) with every file it opens found
  in the trace; a README a user can follow on a fresh copy; Diego's checkpoint. Lemmings is its
  first test game; which games share the strategy is EPIC-03's answer.
- **The SidecarTridge's GEMDRIVE** (`../atarist-sidecart-gemdrive`). "GEMDRIVE only for Hatari.
  We will work later on the sidecartridge GEMDRIVE." EPIC-03 notes where it would differ from
  Hatari's; each solution epic says whether its solution would carry over. Since D-16
  (2026-10-15), Diego's Multidevice is also a test bench at each of iteration 2's checkpoints, from
  a card.

### The solutions EPIC-03 proposes

From EPIC-03 STORY-06 (`src/notes/solutions.md` §4; each "fix" row of
`src/survey/migration.csv` names its solution). 212 games to fix of 1,831; each solution would be
an epic of its own, for Diego to choose and order at EPIC-03's checkpoint (STORY-08).

| | solution | games | first test game | what the epic would build | shown so far |
| --- | --- | --- | --- | --- | --- |
| S1 | GOS reads through the GEMDOS drive | 204 (GOS4 117, GOS5 87) | Lemmings | a patch of each launcher's driver checks and of GOS's GEMDOS entry (13 ST/STE builds of D15R), as tools that change a user's copy; the 204 games run | a proposal: Hatari's hook needs none of TOS's RAM (its source); PP's HAGA reads the same way |
| S2 | a BPB for the GEMDOS drive | 4 (Silmarils: Crystals of Arborea, Targhan, Robinsons Requiem, Storm Master) | Crystals of Arborea | a resident program from `C:\AUTO\` that answers `Getbpb` for the GEMDOS drive | trials: all four play or reach their title |
| S3 | the fastload bit | 3 (Spy vs Spy 2, Strike Force Harrier, Aquanaut) | Spy vs Spy 2 | the bit set in the started program's header | trials: all three |
| S4 | Rody and Mastico 4's `RUNME.TOS` | 1 (Rody and Mastico 2) | itself | instructions only | a trial |

43 of S1's games already run from the GEMDOS drive through another download of PP's (Lemmings'
`LEMMSRD.ZIP`, 2 MB, among them; `solutions.md` §5). One game is not feasible (Great Giana
Sisters STE: it streams its music by sectors itself) and 10 are unsure (§3.6 of the note).

### Candidates, not yet epics

Found on the way. Each waits for Diego to choose it into an epic.

- **The reference does not reach the first level in Hatari** (now EPIC-04 STORY-02). Found in EPIC-01 STORY-01,
  2026-10-11: on the PPDRIVER image, a click on "1 PLAYER" loads `LEVEL020` (bytes verified
  equal to the file; `LEVELDAT` is read earlier, at the title, EPIC-02 STORY-01) and the game then
  raises an address error at `$2B10` (`move.l (a0)+,(a1)+`, `a0 = $3E409` from `($36,a3)`), on ST
  TOS 1.04 with 1 or 4 MB and on STE TOS 2.06 alike. The game's own code (perhaps with PP's
  patches to it, EPIC-02 STORY-04), or its interaction with Hatari; not the launcher. Needed
  before the GOS solution's play session with Lemmings, where it would block.
- **The 10 unsure games** (now EPIC-07). Found in EPIC-03 STORY-05/06: six fail from PPDRIVER too (Lords of
  Doom, Substation, Roger, Zero-5, Spitting Images, Utopos), three only from the GEMDOS drive by
  Diego's look (Super Breakout mono, 9 Lives, Little Puff in Dragonland), and Ice and Fire has
  only floppy images (`solutions.md` §3.6). Each needs its traces read, as S2 and S3's were.
- **Hatari's `Pexec` and the caller's stack.** Found in EPIC-03 STORY-06: Hatari's GEMDOS drive
  clears a started program's free memory before it rewrites the caller's saved `Pexec` call, so a
  caller whose stack lies there ends instead (S3). Not a change here (C-02); a report to Hatari's
  maintainers would leave this Mac, so it waits for Diego (D-15).

**Outcome:** _pending._
