# Changelog

## v1.0.0 (2026-10-26)

The first release. Every Atari ST hard-disk adaptation on the 8bitchip.info website's list, 1,831
games, started from a GEMDOS drive and given a verdict; the fixes for the games that do not run as
they are; and a page that patches a game's own download in the browser.

### Get it

The release is the website's "Patch a game" page, <https://gemdrive.sidecartridge.com/>. Give it
a game's ZIP exactly as downloaded from the 8bitchip.info website, and it says whether the game runs
from GEMDOS and GEMDRIVE as it is, or patches the ZIP and gives it back. No file of the games is
published: the page rebuilds the fixed file from your own copy and checks it against this project's
build.

### What it does

- **Every game classified**: its strategy, its run in Hatari's GEMDOS drive, its verdict. 1,608
  run as they are, 212 need a fix, 1 is not feasible, 10 are unsure. The catalogue on the website
  has them all, with each game's last screen.
- **The GOS games**: the start programs of the 87 GOS5 and 117 GOS4 games are rebuilt so that GOS
  reads its files through GEMDOS and GEMDRIVE by name. 85 GOS5 games and all 117 GOS4 games run.
- **Eight games with a small fix**: `GDBPB.PRG` for the four Silmarils games, the fastload bit for
  Spy vs Spy 2, Strike Force Harrier and Aquanaut, and a start program for Rody and Mastico 2.
  Seven of the eight run.
- **The patcher**: every archive of the list known by its SHA-256; 208 games patched in the
  browser, byte for byte this project's builds; a second download asked for when a fix needs one.
- **Tested twice**: every fix in Hatari, on an ST with TOS 1.04 and an STE with TOS 1.62 and 2.06,
  and on real machines with the SidecarTridge Multi-device's GEMDRIVE.

### Known limits

- Awesome and Prison refuse a cartridge in the port, which both GEMDOS drives need.
- Aquanaut reboots on the Multi-device: it runs only where a bare TOS 1.04 loads it.
- Storm Master needs any floppy in drive A at its credits.
- The 10 unsure games, and Great Giana Sisters STE, are not fixed.
