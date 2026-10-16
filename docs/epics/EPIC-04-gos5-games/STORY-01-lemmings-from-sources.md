---
id: STORY-01
epic: EPIC-04
title: Lemmings' launcher and GOS through the GEMDOS drive, from the sources
status: done
---

## Goal

Our build of Lemmings' launcher, changed in EPIC-02's sources, starts GOS without PP's driver.
GOS5's file requests go to the `TRAP #1` handler that was there before the launcher. The game
reaches its title from Hatari's GEMDOS drive, and the PPDRIVER reference still runs.

## Tasks

- [x] The launcher's driver checks: with no `PPHD` driver and a GEMDOS drive's `TRAP #1` (a
      cartridge's), GOS is started with no driver copy and no sector-0 read
      (`src/gemdrive/lemld2_gemdrive.s`, `gd_start`). The change lives beside the generated source,
      not in its map: the map gives back PP's bytes.
- [x] GOS5's file requests go to the `TRAP #1` the machine had before the launcher, through
      `gd_forward`. A trace shows which of them Lemmings uses.
- [x] `tools/build_gemdrive.sh` builds it, and from the GEMDOS drive Lemmings reaches its title on
      ST TOS 1.04. Every file it opens is in Hatari's GEMDOS trace, with no `Rwabs` on C:.
- [x] The same build from the PPDRIVER image, the reference.
- [x] `tools/dev/all_harness.sh` still passes, with the new build in it. PP's own launcher is
      unchanged, so its round trips hold.
- [x] The Multidevice's GEMDRIVE (Diego's priority): what its `TRAP #1` handler needs in RAM during
      GOS's calls, and its stack moved out of the game's RAM (`md_move_stack`), checked in Hatari.
- [x] From the Multidevice's GEMDRIVE, on Diego's STE (TOS 1.62, 4 MB), Lemmings reaches its title
      and loads its first level (`PPHD\EPIC04\LEMMINGS\START.TOS` on his card).

## Acceptance

From the GEMDOS drive, on ST TOS 1.04, the rebuilt Lemmings reaches its title, with its file
requests in Hatari's trace. From PPDRIVER it does as before. `all_harness.sh` passes. From the
Multidevice's GEMDRIVE, on Diego's STE, it reaches its title and loads its first level.

## Notes

### The approach (2026-10-15): GOS's code unchanged

S1 as proposed (`hd-strategies.md` §4) changed two things: the launcher's driver checks, and GOS's
`trap1` in each D15R build. Only the first one is needed.

- During `file_io`, GOS swaps in its image of TOS's low RAM, and its `TRAP #1` vector there
  points at GOS's own `trap1`.
- The launcher already writes that image at run time: `reuse_pp_driver` writes the copied
  driver's entries into it at `(1138,a6)`, which is `hdv_bpb`, `$472`, with
  `a6 = ($C07E6) + $C0800`.
- So the launcher can just as well write the image's `TRAP #1` vector, at `($84,a6)`.

`gd_start`, reached from `check_pp_driver` when there is no `PPHD`:

1. It goes on only when the machine's `TRAP #1` points into cartridge ROM (`$FA0000` to
   `$FBFFFF`). Hatari's GEMDOS drive hooks it at `$FA002A`, and the SidecarTridge's GEMDRIVE
   from its ROM too. Anything else takes PP's own path (`no_pp_driver`): a real disk with AHDI
   or HDDriver, and a Falcon, whose exception frames differ.
2. It copies `gd_forward`, 58 bytes, to `$B7180`, where PP's driver copy would go and nothing
   else lives. The machine's `TRAP #1` and GOS's `trap1` go into `gd_forward`'s two slots.
3. It points the image's `TRAP #1` at `$B7180` and copies `_drvbits` into the image, as
   `set_buffers` does, then goes on to `start_d15r`.

`gd_forward` reads the function number from the caller's stack:
- `Dsetpath`, `Fcreate`, `Fopen`, `Fclose`, `Fread`, `Fwrite`, `Fdelete`, `Fseek` and `Dgetpath`
  go to the machine's handler;
- everything else goes to GOS's `trap1`.

`Dsetdrv` stays with GOS: Hatari's hook records the drive and then passes the call on to the
ROM's GEMDOS (`../hatari/src/gemdos.c:1592-1602`), whose RAM the game owns. Hatari keeps the
drive the launcher was started from.

So for every GOS5 game the patch is in `START.TOS` alone: no D15R build changes (STORY-04).

**The build**: `tools/build_gemdrive.sh` copies `src/`, puts `src/gemdrive/lemld2_gemdrive.s`
into the copy of `lemld2.s` before `no_pp_driver`, and sends the `bne.w no_pp_driver` at
`$000330` to `gd_start`. Then it builds the copy with `tools/build_launcher.sh --allow-longer`.
The changed `LEMLD2` packs to 9,146 bytes against PP's 9,106, so `START.TOS` keeps its own
length. The other files are still padded to PP's lengths: the launcher reads a fixed 4,929 bytes
of `LS2DD.FIC`. LS2DD and both D15R builds unpack to PP's bytes, and PP's own build
(`build_launcher.sh` with no option) is unchanged.

### The runs (2026-10-15)

`tools/dev/expect/gemdrive-first-level.exp`: the launcher's own opens, then GOS's `Fopen` of
`psyglogo.img`, `IntroPar`, `CODE` and `leveldat`, the title, a click on "1 PLAYER", and
`level020`.

| setup | disk | result | run |
|---|---|---|---|
| ST TOS 1.04 | GEMDOS drive | PASS 10/10, title, `level020` loaded | `tools/dev/logs/20261015-141013-st-104-gemdrive-gemdrive-gos` |
| STE TOS 1.62 | GEMDOS drive | PASS 10/10 | `20261015-141136-ste-162-gemdrive-gemdrive-gos` |
| STE TOS 2.06 | GEMDOS drive | PASS 10/10 | `20261015-141138-ste-206-gemdrive-gemdrive-gos` |
| ST TOS 1.04 | PPDRIVER | PASS 13/13 (`reference-first-level.exp`, PP's driver as before) | `20261015-141134-st-104-ppdriver-gemdrive-build-ref` |

- **From the GEMDOS drive there is no `Rwabs` at all.** The only `Getbpb` calls are the ROM's at
  boot, for drive A.
- GOS's requests reach Hatari from `file_io` (PC `$C0162` to `$C0254`): one `Dsetpath`
  (`\LEMMINGS\FILES`), then `Fopen`, `Fseek`, `Fread` and `Fclose` for each file (9 of each on
  the STEs).
- **After `level020` loads, the game stops with an address error at `$2B10`, reading `$3E409`.**
  That is the reference's own stop in Hatari (STORY-02), seen in the same place from PPDRIVER.
  Lemmings now gets exactly as far from the GEMDOS drive as from PP's driver.
- **On ST TOS 1.04 only**, the loader's first call passes a non-name. GOS asks for
  `Fopen("T,…")`, which fails, and the game goes on. On the reference, that call carries `"FORM…"`,
  which the loader skips (`launch-chain.md`). The bytes at `a0` differ between setups; for STORY-02.
- LS2DD asks for `dmalogo.imgg`, which GEMDOS cuts to 8.3, as GOS's own GEMDOS did.

**`all_harness.sh`** has a new check, 5b: `build_gemdrive.sh`, then `gemdrive-first-level.exp` on
ST TOS 1.04 from the GEMDOS drive. Run with it: 0 failures, the new check PASS 10/10 to
`level020`, PP's own build still its bytes and 13/13 from PPDRIVER, `LEMMINGS/` unchanged (711 s;
Docker had just been started, and its steps ran about three times slower than usual).


### The Multidevice's GEMDRIVE (2026-10-15)

Diego's priority is the Multidevice, not Hatari. Its GEMDRIVE (`../md-drives-emulator`, v1.2.0,
`target/atarist/src/gemdrive.s`) is ROM code that, unlike Hatari's hook, uses the ST's RAM during a
call. `src/probes/epic04/multidevice_probe.py` logs, at each call `gd_forward` hands on, what it
would find (STE TOS 1.62, 4 MB, `tools/dev/logs/20261015-162922-ste-162-gemdrive-multidevice`):

- **In GOS's image, all valid.** `_sysbase` is `$C0800`, GOS's copy of TOS 1.04's header, whose
  `os_run` gives the basepage `$D64DA` (`get_run_basepage`, for Fopen). `_dskbufp` points into GOS's
  RAM at `$Dxxxx`: the 20 bytes Fread keeps at `+$100`, and the wait code `send_sync` copies there,
  land in GOS's buffer. `_longframe` is 0.
- **The current drive is C:.** For Dsetpath, and Fopen with no drive letter, GEMDRIVE asks Dgetdrv
  through `TRAP #1`, which `gd_forward` gives to GOS: GOS's basepage says drive 2 from `tos_paths`'
  first `Dsetdrv(2)` on.
- **Its stack is in the game's RAM.** From v1.2.0 GEMDRIVE runs the calls it serves on a 1 KB stack
  it Mallocs at boot, at `_membot`: `$A892` on TOS 1.62, or `$13094` with the ACSI emulation's
  34 KB reservation below it. Filled with ILLEGAL at every call (`--stack`), those two places
  stop the game before `IntroPar` (`20261015-163227-ste-162-gemdrive-multidevice-stack`).

**`md_move_stack`** (Diego's idea: the code is in ROM, only the buffers move): when the machine's
`TRAP #1` carries the XBRA id `SDGD`, `gd_start` sends GEMDRIVE `CMD_SET_SHARED_VAR`
(`SHARED_VARIABLE_STACK`, `$B7100`), what its `gemdrive_start` sends for the stack it Mallocs.
The protocol is `send_sync`'s, run from the launcher's RAM, five tries. `$B7100` is the top of
PP's GEMDOS buffers (`$AF100`-`$B70FF`), which nothing uses on this path. If the RP does not hold
the new value afterwards, the launcher takes PP's own path and shows his message.

| check (STE TOS 1.62, 4 MB) | result | run |
|---|---|---|
| 1 KB of ILLEGAL at `$B6D00` at every call | PASS 10/10; nothing else ever writes there | `20261015-164007-ste-162-gemdrive-multidevice-stack` |
| `SDGD` and the RP's answer faked in the debugger | sends `$0487 $000C`, the token, `$0016 $0000 $7100 $000B`, checksum `$DE60`, as `send_sync`; PASS 10/10 | `20261015-164232-ste-162-gemdrive-fake-md` |
| `SDGD` faked, no answer | about 15 s, then PP's "This prg. requires PP, AHDI or Hddriver" | `20261015-164335-ste-162-gemdrive-fake-md-silent` |
| from `C:\EPIC04\LEMMINGS\` | PASS 10/10: GOS's path is `\EPIC04\LEMMINGS\FILES`, from `Dgetpath` | `20261015-164535-ste-162-gemdrive-deep` |

Firmware before v1.2.0 serves calls on the caller's stack (GOS's), and its variable 22 is unused.
The build is on Diego's card as `PPHD\EPIC04\LEMMINGS\`.

**The first run on the STE (TOS 1.62, 4 MB): three bombs**, with garbage over the top half of the
screen while the Psygnosis logo shows. The cause is a name, not RAM:

- After `psyglogo.img`, LS2DD asks GOS for `"dmalogo.imgg"` (to `$68000`). TOS's GEMDOS reads a
  name as 8.3 and drops the fourth character; so does Hatari's drive. GEMDRIVE hands the name to
  FatFS as it comes (`getLocalFullPathname`, `rp/src/gemdrive.c:614`): no such file, -33.
- `file_io` takes the error cleanly (it skips the read and returns it). The logo at `$68000` is
  never loaded, and the intro shows and decodes whatever is there.
- `src/probes/epic04/md_emulate.py` makes Hatari do what GEMDRIVE does in RAM at every call (its
  stack at `$B7100`, the nested `Dgetdrv` into GOS, ILLEGAL over the `$114` bytes at `_dskbufp`,
  a busy loop for an SD card's latency): the game still runs to `level020`
  (`20261015-170753-ste-162-gemdrive-mdemu-stack-dgetdrv-dskbuf-delay40000`, and its check
  `20261015-171029-ste-162-gemdrive-mdemu-check`: ten nested `Dgetdrv` reach GOS's `trap1` on the
  stack at `$B70BC`; `_dskbufp` is `$D1D44`, in GOS's RAM). What it does in RAM is not the cause.

**The fix: `gd_forward` cuts names to 8.3.** For Dsetpath, Fcreate, Fopen and Fdelete, it copies
the name to `gd_name` (after itself, at `$B7180` and up, where PP's driver copy would go) with
each part cut to 8 characters and its extension to 3, as GEMDOS reads it, and the call names the
copy. `gemdrive-first-level.exp` now expects `Fopen("dmalogo.img")`.

| check | result | run |
|---|---|---|
| STE TOS 1.62, 4 MB | PASS 11/11; GOS's names: `psyglogo.img`, `dmalogo.img`, `main`, `IntroPar`, `CODE`, `leveldat`, `level020` | `20261015-171549-ste-162-gemdrive-gemdrive-83` |
| ST TOS 1.04 | PASS 11/11 (the first name is still garbage, cut to 8.3, and fails harmlessly) | `20261015-171626-st-104-gemdrive-gemdrive-83` |
| STE TOS 2.06 | PASS 11/11 | `20261015-171727-ste-206-gemdrive-gemdrive-83` |
| STE TOS 1.62, 4 MB, GEMDRIVE's RAM use emulated | PASS 11/11 | `20261015-172448-ste-162-gemdrive-mdemu-stack-dgetdrv-dskbuf-delay40000` |

The new `START.TOS` is on the card (only it changed).

GEMDRIVE taking names as GEMDOS does fixes this for every program. At Diego's request, branch
`fix/gemdos-8-3-names` of `../md-drives-emulator` (`6aeece3`, local, in the worktree
`../md-drives-emulator-gemdos83`, for his review): `getLocalFullPathname` (Fopen, Fcreate, Fdelete,
Fattrib, Frename, Dcreate, Ddelete) takes the 8.3 form when the name as it came is not on the card
and that form is. Its cut passes ten cases on the host, and the firmware builds, release and
debug, with no warnings. Not flashed or run on the hardware.

**On Diego's STE (TOS 1.62, 4 MB), from the Multidevice's GEMDRIVE (2026-10-15): it works.** The
title, the first level and play, and space during the intro (STORY-02's `gd_quiet`, the build of
`START.TOS` `27c534e8…`). Diego: "it works great".
