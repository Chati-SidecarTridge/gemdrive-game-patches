# Why Lemmings fails in Hatari's GEMDRIVE mode

Lemmings' hard-disk adaptation does not start from a GEMDOS drive. A GEMDOS drive, such as
Hatari's GEMDRIVE mode, is a host folder served file by file, by name, with no disk sectors
behind it. The Gamex launcher needs a resident hard-disk driver, PPDRIVER, and reads the game by
sectors through it. Without that driver it prints
`This prg. requires PP, AHDI or Hddriver hard disk driver …` and exits.

Found in Hatari 2.6.1 runs on the original files. Run folders are in
`tools/dev/logs/`. `text+` offsets count from the launcher's inner program, LEMLD2. The
GOS5 builds work around the cause, for Lemmings too (`gos5-gemdrive.md`).

## The cause in short

The launcher does not read the game through GEMDOS, the part of TOS that opens files by name. It
looks for PPDRIVER, the hard-disk driver from the 8bitchip.info website, by its XBRA header
`"XBRA" "PPHD"`. The header sits 12 bytes before the routine that `hdv_bpb` (`$472`) points to.
The launcher copies the driver (7,204 bytes) to `$B7180` and rewires it. Then it starts D15R
(`D15R_H5.FIC`, at `$C0100`), the loader that holds GOS. GOS is TOS 1.04's GEMDOS, running from
RAM.

GOS reads the FAT volume by sectors of 1,024 bytes, with BIOS calls on drive C. `Getbpb` returns
the BPB, the table that describes the volume. `Mediach` asks whether the disk changed. `Rwabs`
reads sectors. Hatari's GEMDRIVE has no driver, no BPB and no sectors. So the driver check fails,
the fallback read of sector 0 fails, and the launcher exits.

## 1. The two setups

`tools/dev/make_disks.sh` builds both from a copy of `LEMMINGS/`. Each runs on an ST with TOS
1.04 and STEs with TOS 1.62 and 2.06, all with 1 MB.

- **GEMDRIVE**: `hatari --harddrive <folder>`. A cartridge program at `$FA0000` serves the drive
  through `TRAP #1`. BIOS and XBIOS calls go to the TOS ROM.
- **PPDRIVER**, the reference: a 32 MB ACSI image from `../atari-hd --ppdriver-bootable`. Its
  boot code loads the driver, which stays resident.

## 2. What the reference does

Run `20261011-144024-st-104-ppdriver-first-level`, ST TOS 1.04. The launcher reads its own files
with GEMDOS. After `Dsetpath("FILES")`, every disk access is a BIOS call from D15R. Record numbers
are 1,024-byte logical sectors.

| Rwabs records → buffer | what it is |
| --- | --- |
| 65, 81, 263–264 → `$B1100`–`$B5100` | the root, `LEMMINGS` and `FILES` directories |
| 33 → `$AF100` | FAT copy 2 |
| 387–396 → `$60000`, 397–406 → `$68000` | the two logos, `PSYGLOGO.IMG` and `DMALOGO.IMG` |
| 813–915 → `$A00` | `MAIN` (105,220 bytes) |
| 415–496 → `$10000` | `INTROPAR` (83,362 bytes) |
| 497–575 → `$A00` | `CODE` (80,639 bytes), over `MAIN` |
| 677–680 | `LEVELDAT`, at the title |
| 407–409 → `$41800` | `LEVEL020`, the first level |

Between reads GOS calls `Mediach(2)` 7 to 16 times, and PPDRIVER answers 0.

**Open issue.** The reference does not reach the first level in Hatari. Right after the level
loads, the game raises an address error at `$2B10`. The loader is not to blame: the 3,048 bytes
at `$41800` equal `FILES/LEVEL020` (run `…-click-exc3`).

## 3. Where the GEMDRIVE runs part from the reference

All three GEMDRIVE runs stop at the same check, at text+`$324`:

```
movea.l $472.w,a1              ; hdv_bpb
cmpi.l  #$50504844,-8(a1)      ; "PPHD"
bne.w   text+$482              ; no PPDRIVER: the fallback
```

| setup | `$472` (hdv_bpb) | long at hdv_bpb−8 | `$516` (pun_ptr) | path |
| --- | --- | --- | --- | --- |
| ST 1.04 GEMDRIVE | `$FC173C` (ROM) | `$FFFC4280` | 0 | fallback, raw ACSI |
| ST 1.04 PPDRIVER | `$12960` | `"PPHD"` | `$12FEC` | primary |
| STE 1.62 GEMDRIVE | `$E01914` (ROM) | `$FFFC4280` | 0 | fallback, raw ACSI |
| STE 1.62 PPDRIVER | `$129A4` | `"PPHD"` | `$13030` | primary |
| STE 2.06 GEMDRIVE | `$E05210` (ROM) | `$FFFC4280` | 0 | fallback, XBIOS DMAread |
| STE 2.06 PPDRIVER | `$14DC4` | `"PPHD"` | `$15450` | primary |

With a GEMDOS drive, `hdv_bpb` points to TOS's routine in ROM. With the image, it points to
PPDRIVER.

**The fallback.** On TOS 1.x the launcher reads sector 0 itself, through the ACSI DMA registers.
With no ACSI device the read times out, and the error exit prints the message. On TOS 2.x it
calls XBIOS `DMAread` on the device named in `PUN_INFO`, the table a hard-disk driver installs at
`pun_ptr`. With no driver, `pun_ptr` is 0, `DMAread` returns -1 and the same exit follows.

**What the launcher does with PPDRIVER.** It copies 7,204 bytes from the XBRA header (`$12954`)
to `$B7180`: the driver's code, data and variables. Then it:

- points the copy's three "old vector" slots and its vector table at D15R (copy offsets `+$9`,
  `+$3F`, `+$43B`, `+$495..+$49D`), so the driver chains to D15R instead of TOS;
- rewrites the driver's BPB and buffer pointers (`+$771..+$78B`), so its buffers sit at
  `$AF100`–`$B5100`;
- installs the copy's entries in `$472`, `$476` and `$47E` (`$B718C`, `$B71C2`, `$B75BE`), sets
  `$47A` to `$C1F3E` (D15R) and clears `pun_ptr`.

By the first `Rwabs`, `TRAP #1` points to D15R's handler at `$C84A0`.

## 4. The embedded driver

The launcher carries no driver of its own. It requires PPDRIVER, resident, and reuses it:
copied, relocated and patched at fixed offsets.

Answering the disk by hand from the debugger only reveals the next missing piece (ST TOS 1.04,
GEMDRIVE):

| answered by hand | what happened next |
| --- | --- |
| nothing | the error message |
| sector 0 = the image's PPDRIVER boot sector | the launcher goes into D15R. TOS returns 0 for `Getbpb(2)`, and the run crashes |
| + `Getbpb(2)` = PPDRIVER's BPB | TOS returns -15 (unknown device) for `Rwabs`, and the run crashes |
| + `Mediach(2)` = 0, `Rwabs` 65 and 81 from the image | D15R restores a context it never saved, and Hatari halts |

The fallback never initialises D15R, so nothing past the last stop works without the real driver.

PPDRIVER's BPB for the image, as `Getbpb(2)` returns it on the reference: recsiz 1024, clsiz 2,
clsizb 2048, rdlen 16, fsiz 32, fatrec 33, datrec 81, numcl 16343, bflags 1.

## 5. Everything GEMDRIVE lacks

In the order the launcher needs them:

1. **A resident driver with the `PPHD` header before `hdv_bpb`**, laid out like PPDRIVER. The
   launcher patches its copy at `+$9`, `+$3F`, `+$43B`, `+$495..+$49D` and `+$771..+$78B`.
2. Failing that, **a boot sector 0 that can be read raw**. Even then D15R is not initialised.
3. **BIOS `Getbpb(2)`** returning PPDRIVER's BPB (§4).
4. **BIOS `Mediach(2)`** returning 0 before each read.
5. **BIOS `Rwabs` on drive 2**, serving the whole FAT volume.
6. **Fixed memory**: the driver copy at `$B7180`, its buffers at `$AF100`–`$B5100`, D15R at
   `$C0100`, LS2DD at `$70000`, `MAIN` and `CODE` at `$A00`.
7. **`TRAP #1`** for D15R from the first `Rwabs` on. Hatari's GEMDOS drive hooks it too, so a fix
   must live with both, as the GOS5 builds do.

The case of file names plays no part. GOS walks the directories itself, and Hatari ignores case
on a GEMDOS drive.

## 6. The first look's guesses

A first look at the launcher, in April 2024, left guesses about the cause.

- Without a resident PPDRIVER, the loader reads sector 0 itself: confirmed (§3).
- With the `PPHD` check patched out, the run stalls on lower-case file names: refuted. It stops
  on `Rwabs` returning -15 (§4).
- The loader hooks `TRAP #1` only for `Malloc` and `Mshrink`: not at the first `Rwabs`, when
  D15R's handler owns it (§3).
- On TOS 2.06 the loader works through whatever driver is installed: refuted. It needs
  `PUN_INFO` and an ACSI device (§3).
- The copy of PPDRIVER embedded in the launcher causes the failure (the starting guess):
  confirmed in substance. The driver is required and resident, not embedded (§4).
- `START.TOS` only unpacks the rest, and the `.FIC` files are packed code: consistent with the
  runs (`launcher-formats.md`).

## 7. Evidence and tools

- The reference: run `20261011-144024-st-104-ppdriver-first-level`, script
  `tools/dev/expect/reference-first-level.exp`, BPB in run `…-ppdriver-bpb`.
- The check and the fallbacks: runs `20261011-141008-st-104-gemdrive-gate`,
  `20261011-141116-ste-206-gemdrive-gate` and the other `…-gate` runs, from
  `src/probes/gemdrive-failure/gate_probe.py <setup> <disk>`. `read_probe.py <run>` prints a run's chain.
- The driver copy: runs `…-st-104-ppdriver-gate` and `…-drv`.
- The answers by hand: `src/probes/gemdrive-failure/fallback_probe.py` and `serve_rwabs.py`, runs
  `…-gemdrive-fallback` and `…-gemdrive-serve-02`.
