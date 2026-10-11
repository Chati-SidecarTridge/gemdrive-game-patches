# Iterations

Epics are grouped into iterations via the `iteration: N` frontmatter field; the cockpit groups the
dashboard by it. This file is the narrative: what each iteration sets out to do, the order it is
done in and why, and how it ends. It also holds the hypotheses (`H-NN`) the stories confirm or
refute (D-01).

| Iteration | Theme | Status |
| --- | --- | --- |
| 1 | **GEMDRIVE**: Lemmings launched from Hatari's GEMDOS drive, without changing Hatari; PP's adaptations classified by how they run from a hard disk | planned |

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

## Iteration 1: GEMDRIVE

**Goal:** Lemmings starts and plays from a Hatari GEMDOS drive (GEMDRIVE mode) as an alternative
to a hard-disk image, with Hatari unchanged (C-02). On the way:

- the reason it fails today, shown by runs;
- every PPera launcher program as sources that rebuild into a launcher we can test;
- every game in PP's list of hard-disk adaptations classified by the strategy that runs it from a
  hard disk, in a migration table that says for each game whether it works from a GEMDOS drive
  as it is or needs adapting, and how. PP's site is mirrored first, on 2026-10-11, out of the
  epic order (D-12).

It ends with Diego launching Lemmings in GEMDRIVE mode with the fix (EPIC-04 STORY-05).

### Implementation path

Epic numbers are the execution order. One epic at a time, each on its own `epic-NN-<slug>` branch
(D-07), each ending with a verification story that is Diego's checkpoint. Order set by Diego,
2026-10-11 (D-08, D-10).

| # | Epic | Why at this point |
| --- | --- | --- |
| EPIC-00 | The development environment, the test tools, and Hatari as the test machine | Asked by Diego, 2026-10-11: epic 0, as in the sibling repositories. Every later story is a run of these tools: the clean workspace and git, the pinned toolchain, the round-trip check, the GEMDRIVE and PPDRIVER setups on the ST and STE up to TOS 2.06, and the harness. |
| EPIC-01 | Why the game fails in Hatari's GEMDRIVE mode | First, confirm before building: Diego's guess (H-07) is checked against a working reference booted by PPDRIVER (D-09), and the result is the full list of what GEMDRIVE lacks, which sets EPIC-04's scope. |
| EPIC-02 | The PPera launcher reverse engineered and recompilable, tested with our own build | A fix needs a launcher we can change and test: every stage as sources that reassemble, our own build booting the game like the original, and the disk layer (D15R and the driver it uses) documented. Its signatures feed EPIC-03. |
| EPIC-03 | The ways PP's adaptations run from a hard disk, classified | Asked by Diego, 2026-10-11 (D-10). After EPIC-02, whose unpackers and signatures of Lemmings' launcher are where the survey's signatures start; before EPIC-04, so the approach chosen for Lemmings is weighed against every strategy it might also cover. |
| EPIC-04 | GEMDRIVE mode as an alternative way to launch Lemmings | Last: it needs the list from EPIC-01, the sources from EPIC-02 and the strategies from EPIC-03. The approach is Diego's choice (EPIC-04 STORY-01). |

### Candidates, not yet epics

Kept out of iteration 1 by Diego, 2026-10-11 (D-08, D-10), or found on the way. Each waits for Diego to
choose it into an epic.

- **The reference does not reach the first level in Hatari.** Found in EPIC-01 STORY-01,
  2026-10-11: on the PPDRIVER image, a click on "1 PLAYER" loads `LEVEL020` (bytes verified
  equal to the file; `LEVELDAT` is read earlier, at the title, EPIC-02 STORY-01) and the game then raises an address error at `$2B10`
  (`move.l (a0)+,(a1)+`, `a0 = $3E409` from `($36,a3)`), on ST TOS 1.04 with 1 or 4 MB and on
  STE TOS 2.06 alike. The game's own code, or its interaction with Hatari; not the launcher.
  Needed before EPIC-04 STORY-03 (play), where it would block.

- **Adapting every game that does not work as it is, one generic way at a time.** Diego,
  2026-10-11 (D-10): "implement generic ways in the future (using SidecarTridge GEMDRIVE) to make
  them all running with gemdrive or gemdos in hatari", and "try to adapt all the games that dont
  already work in GEMDOS/GEMDRIVE mode in Hatari". EPIC-03 STORY-05 sketches the ways and names one
  for each game in `migration.csv`; EPIC-04 STORY-01 records which strategies Lemmings' approach
  would also cover. Each way becomes an epic when Diego chooses it.
- **The SidecarTridge's GEMDRIVE** (`../atarist-sidecart-gemdrive`). "GEMDRIVE only for Hatari.
  We will work later on the sidecartridge GEMDRIVE." EPIC-03 notes where it would differ from
  Hatari's.

**Outcome:** _pending._
