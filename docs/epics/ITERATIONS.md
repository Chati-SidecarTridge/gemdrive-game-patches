# Iterations

Epics are grouped into iterations via the `iteration: N` frontmatter field; the cockpit groups the
dashboard by it. This file is the narrative: what each iteration sets out to do, the order it is
done in and why, and how it ends. It also holds the hypotheses (`H-NN`) the stories confirm or
refute (D-01).

| Iteration | Theme | Status |
| --- | --- | --- |
| 1 | **GEMDRIVE**: Lemmings launched from Hatari's GEMDOS drive, without changing Hatari | planned |

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
Diego's guess.

| ID | Hypothesis | Tested by | Verdict |
| --- | --- | --- | --- |
| H-01 | `START.TOS`'s 230-byte text is only a self-extractor. Its data section is a 32-byte record (magic `C3`, sizes, the name `LEMLD2.TOS`) and a custom LZSS stream (not ICE), which unpacks to a GEMDOS program (34,910-byte text, no data, 177 relocations) that the stub relocates and jumps to. | EPIC-02 STORY-02 | open |
| H-02 | The `.FIC` files are not catalogues: each is a 32-byte `C3` header plus the same LZSS stream. `LS2DD.FIC` unpacks to code run at `$70000` that loads `psyglogo.img`, `dmalogo.img` and `main`; `D15R_F5.FIC` and `D15R_H5.FIC` unpack to a blob at `$C0100` that performs the file loads. | EPIC-02 STORY-02 | open |
| H-03 | The loader first looks for a resident PP driver, the long `PPHD` at `_hdv_init - 8`. Without it, it reads sector 0 by itself: raw ACSI DMA registers under TOS 1.x, XBIOS `DMAread` under TOS 2 and later, then the Falcon IDE registers. Every path wants a sector 0 whose words sum to `$1234` (an executable boot sector); failing all, it prints "This prg. requires PP, AHDI or Hddriver hard disk driver". | EPIC-01 STORY-03 | **confirmed, with corrections** (2026-10-11): `$472` is `hdv_bpb`, not `_hdv_init`; the TOS 2.x path takes the device number from `pun_ptr` (`$516`); a good sector 0 is not the end of it, the launcher then continues into D15R. `src/notes/gemdrive-failure.md` §3–4. |
| H-04 | With the `PPHD` check patched out, a run on a Hatari GEMDOS drive stalls in `LS2DD`'s file-load retry loop, suspected to be the lower-case names it asks for (`psyglogo.img`) against upper-case files on a case-sensitive host folder. | EPIC-01 STORY-02 | **refuted** (2026-10-11): no file name is looked up after `Dsetpath("FILES")`, D15R walks the directories by sector; pushed past the gate by hand the stop is TOS's -15 from `Rwabs`; Hatari matches GEMDOS-drive names regardless of case. `gemdrive-failure.md` §4–5. |
| H-05 | The loader hooks `TRAP #1` only for `Malloc` and `Mshrink`, which always get a fixed heap at `$AF100`, and passes every other GEMDOS call to TOS. | EPIC-02 STORY-04 | open; seen in EPIC-01: by the first `Rwabs`, `$84` points to D15R's handler at `$C84A0`, which returns 0 for GEMDOS 1–11 and saves context for the rest (`gemdrive-failure.md` §3) |
| H-06 | Under TOS 2.06 the loader takes the XBIOS path and works through whatever driver is installed. | EPIC-01 STORY-02 | **refuted** (2026-10-11): it takes the XBIOS `DMAread` path, a raw ACSI read on the `PUN_INFO` device; with no driver `pun_ptr` is 0 and the read returns -1. `gemdrive-failure.md` §3. |
| H-07 | **The game fails in GEMDRIVE mode because of the PPera driver embedded in the launcher.** Diego, 2026-10-11. | EPIC-01 STORY-03 | **confirmed in substance, restated** (2026-10-11): the launcher embeds no driver; it requires PP's resident driver (XBRA `PPHD` before `hdv_bpb`), copies and patches it, and its loader D15R reads the FAT volume by sectors through it (`Getbpb`, `Mediach`, `Rwabs`); GEMDRIVE has neither. `gemdrive-failure.md` §1, §4. |

---

## Iteration 1: GEMDRIVE

**Goal:** Lemmings starts and plays from a Hatari GEMDOS drive (GEMDRIVE mode) as an alternative
to a hard-disk image, with Hatari unchanged (C-02). On the way:

- the reason it fails today, shown by runs;
- every PPera launcher program as sources that rebuild into a launcher we can test.

It ends with Diego launching Lemmings in GEMDRIVE mode with the fix (EPIC-03 STORY-05).

### Implementation path

Epic numbers are the execution order. One epic at a time, each on its own `epic-NN-<slug>` branch
(D-07), each ending with a verification story that is Diego's checkpoint. Order set by Diego,
2026-10-11 (D-08).

| # | Epic | Why at this point |
| --- | --- | --- |
| EPIC-00 | The development environment, the test tools, and Hatari as the test machine | Asked by Diego, 2026-10-11: epic 0, as in the sibling repositories. Every later story is a run of these tools: the clean workspace and git, the pinned toolchain, the round-trip check, the GEMDRIVE and PPDRIVER setups on the ST and STE up to TOS 2.06, and the harness. |
| EPIC-01 | Why the game fails in Hatari's GEMDRIVE mode | First, confirm before building: Diego's guess (H-07) is checked against a working reference booted by PPDRIVER (D-09), and the result is the full list of what GEMDRIVE lacks, which sets EPIC-03's scope. |
| EPIC-02 | The PPera launcher reverse engineered and recompilable, tested with our own build | A fix needs a launcher we can change and test: every stage as sources that reassemble, our own build booting the game like the original, and the PPera driver's interface documented. |
| EPIC-03 | GEMDRIVE mode as an alternative way to launch Lemmings | Last: it needs the list from EPIC-01 and the sources from EPIC-02. The approach is Diego's choice (EPIC-03 STORY-01). |

### Candidates, not yet epics

Kept out of iteration 1 by Diego, 2026-10-11 (D-08), or found on the way. Each waits for Diego to
choose it into an epic.

- **The reference does not reach the first level in Hatari.** Found in EPIC-01 STORY-01,
  2026-10-11: on the PPDRIVER image, a click on "1 PLAYER" loads `LEVELDAT` and `LEVEL020`
  (bytes verified equal to the file) and the game then raises an address error at `$2B10`
  (`move.l (a0)+,(a1)+`, `a0 = $3E409` from `($36,a3)`), on ST TOS 1.04 with 1 or 4 MB and on
  STE TOS 2.06 alike. The game's own code, or its interaction with Hatari; not the launcher.
  Needed before EPIC-03 STORY-03 (play), where it would block.

- **Other PPera games.** "Only Lemmings by now." EPIC-03 STORY-01 records whether the chosen
  approach would carry over to other games that use PPera's launchers and drivers.
- **The SidecarTridge's GEMDRIVE** (`../atarist-sidecart-gemdrive`). "GEMDRIVE only for Hatari.
  We will work later on the sidecartridge GEMDRIVE."

**Outcome:** _pending._
