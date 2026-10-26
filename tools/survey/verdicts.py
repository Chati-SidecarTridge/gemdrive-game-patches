#!/usr/bin/env python3
"""Every game's verdict, into src/survey/migration.csv.

Usage: verdicts.py

For every game of migration.csv: its run from Hatari's GEMDOS drive on ST TOS 1.04, or on STE TOS
1.62 for a game made for the STE (its name says STE) (tools/dev/builds/survey/runs.tsv, run_all.py),
its run from a PPDRIVER image, the working reference, when it has one, Diego's answer, if he
gave one (src/survey/review.tsv, review.py; Diego, 2026-10-11: "if i dont check any button, it means
i trust your guess"), and what a game's own trace showed when it was looked into
(src/survey/findings.tsv, with the evidence). Writes the columns verdict, run, reason (as it
is, fix, not feasible, unsure) and by (whose verdict: "trace", "Diego", "ppdriver" or "run"):

  a finding                       its verdict and reason
  Diego's OK                      as it is
  Diego's Broken, GOS4/GOS5       fix (the launcher's driver checks, src/notes/recognising-modes.md)
  Diego's Broken, otherwise       unsure: broken in its run, the cause still to find (and what the
                                  PPDRIVER run did)
  Diego's Not sure, or a proposal other than "as it is", with a PPDRIVER run:
    the same from PPDRIVER        as it is: the drive changes nothing (Hatari does the same with PP's
                                  driver: a halt, a quit, a file missing from PP's archive)
    PPDRIVER runs it              fix: the GEMDOS drive breaks it, the cause to find
    otherwise                     unsure
  without a PPDRIVER run          Diego's Not sure: unsure; run_all.py's proposal ("broken": unsure)

An answer stands while the run that counts is the one Diego answered on, or ends as it did (the same
proposal, by today's rules); one given on a run since replaced by a run that ends otherwise (another
program, more RAM, a run that started in time) gives way to the new run's proposal, and the game is
listed in tools/dev/builds/survey/stale.txt, which review.py shows again as not reviewed.

A run that reads C: by sectors (BIOS Rwabs, Getbpb over and over) sets the access column to
"sectors" where classify.py found no such access in the programs' code.

Every "fix" gets its solution (src/notes/solutions.md) from src/survey/solutions.tsv
(a row number, or a strategy, and the solution), and the game's other downloads that run as it is
from the GEMDOS drive (tools/dev/builds/survey/runs-other.tsv, run_other.py).

Prints the counts, the access corrected, and the findings that contradict an answer of Diego's.
Standard library only.
"""

from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all  # noqa: E402
import run_other  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SURVEY = REPO / "tools" / "dev" / "builds" / "survey"
GOS = ("Gamex + GOS4", "Gamex + GOS5")


def kind(reason: str) -> str:
    """A reason without its details: "the CPU halted", "the program quit to the desktop", "not found"."""
    return re.split(r" after | \(|:", reason)[0]


def compared(run: dict, ref: dict) -> tuple[str, str]:
    """The verdict from a game's GEMDOS-drive run and its PPDRIVER run. On PPDRIVER a program's own
    sector reads on C: are answered: they do not count against it there."""
    said = run["reason"] or run["proposal"]
    ref_ok = ref["proposal"] == "as it is" or ref["reason"].endswith("sector reads on C:")
    if ref["proposal"] == run["proposal"] and (run["proposal"] == "as it is" or kind(ref["reason"]) == kind(run["reason"])):
        return "as it is", f"the same from PPDRIVER ({said}): the drive changes nothing"
    if ref_ok and run["proposal"] != "as it is":
        return "fix", f"runs from PPDRIVER, not from the GEMDOS drive: {said}"
    return "unsure", f"{said}; from PPDRIVER: {ref['reason'] or ref['proposal']}"


def standing(answer: dict, run: dict, archive: Path) -> bool:
    """Does Diego's answer stand for the run that counts now?"""
    if not run or answer["run"] == run["run"]:
        return True
    old = SURVEY / "runs" / answer["run"]
    return old.is_dir() and run_all.analyse(old, run["strategy"], archive)["proposal"] == run["proposal"]


def main() -> int:
    path = REPO / "src" / "survey" / "migration.csv"
    games = list(csv.DictReader(path.open()))
    runs, ste, ppdriver = {}, {}, {}
    for r in csv.DictReader((SURVEY / "runs.tsv").open(), delimiter="\t"):
        if r["disk"] == "gemdrive" and r["setup"] in ("st-104", "ste-162"):
            (runs if r["setup"] == "st-104" else ste)[r["row"]] = r
        elif r["disk"] == "ppdriver" and r["setup"] == "st-104":
            ppdriver[r["row"]] = r
    findings = {f["row"]: f for f in csv.DictReader((REPO / "src" / "survey" / "findings.tsv").open(), delimiter="\t")}
    answers = {}
    review = REPO / "src" / "survey" / "review.tsv"
    if review.exists():
        for a in csv.DictReader(review.open(), delimiter="\t"):
            answers[a["row"]] = a  # the last answer counts
    stale = []
    for g in games:
        run, answer, finding = runs.get(g["row"], {}), answers.get(g["row"]), findings.get(g["row"])
        ref = ppdriver.get(g["row"])
        if re.search(r"\bSTE\b", g["name"]) and g["row"] in ste:
            run = ste[g["row"]]
        g["run"] = run.get("run", "")
        # a run that reads C: by sectors corrects classify.py's access, found in the programs' code
        # (Crystals of Arborea's START.PRG: no sector-access signature, Getbpb(2) in a loop when run)
        if re.search(r"sector reads on C:|boot block", run.get("reason", "")) and g["access"] not in ("sectors", "registers"):
            g["access"], g["evidence"] = "sectors", g["evidence"] + "; run: " + run["reason"]
            print(f"  access corrected: {g['row']} {g['name']}: sectors ({run['reason']})")
        if answer and not standing(answer, run, SURVEY / "games" / Path(g["download"]).with_suffix("")):
            stale.append(g["row"])
            answer = None
        if finding:
            g["by"], g["verdict"], g["reason"] = "trace", finding["verdict"], finding["reason"]
            if answer and (answer["verdict"] == "ok") != (finding["verdict"] == "as it is"):
                print(f"  finding against Diego's {answer['verdict']}: {g['row']} {g['name']}: {finding['verdict']}")
        elif answer and answer["verdict"] in ("ok", "broken"):
            g["by"] = "Diego"
            note = f" ({answer['note']})" if answer["note"] else ""
            if answer["verdict"] == "ok":
                g["verdict"], g["reason"] = "as it is", "works in its run" + note
            elif g["strategy"] in GOS:
                g["verdict"], g["reason"] = "fix", "the launcher's driver checks stop it" + note
            else:
                g["verdict"], g["reason"] = "unsure", "broken in its run, the cause still to find" + note
                if ref:
                    g["reason"] += f"; from PPDRIVER: {ref['reason'] or ref['proposal']}"
        elif ref and run and (answer or run["proposal"] != "as it is"):
            g["by"] = "ppdriver"
            g["verdict"], g["reason"] = compared(run, ref)
            if answer and g["verdict"] == "unsure":
                g["by"], g["reason"] = "Diego", "Diego is not sure; " + g["reason"]
        elif answer:
            g["by"], g["verdict"] = "Diego", "unsure"
            g["reason"] = "Diego is not sure" + (f" ({answer['note']})" if answer["note"] else "")
        elif run:
            g["by"] = "run"
            proposal = run.get("proposal", "")
            g["verdict"] = "unsure" if proposal == "broken" else proposal
            g["reason"] = ("broken in its run, the cause still to find: " if proposal == "broken" else "") + run.get("reason", "")
        else:
            g["by"], g["verdict"], g["reason"] = "", "unsure", "not run"
    solutions = {s["match"]: s["solution"]
                 for s in csv.DictReader((REPO / "src" / "survey" / "solutions.tsv").open(), delimiter="\t")}
    others = collections.defaultdict(list)
    if (SURVEY / "runs-other.tsv").exists():
        for r in csv.DictReader((SURVEY / "runs-other.tsv").open(), delimiter="\t"):
            if r["disk"] == "gemdrive" and r["proposal"] == "as it is":
                folder = "".join(f" in C:\\{f}" for f in run_other.FOLDERS.get(r["download"], ()))
                others[r["row"]].append(f"{r['download']} ({r['strategy']}) runs as it is{folder}")
    for g in games:
        fix = g["verdict"] == "fix"
        g["solution"] = "; or ".join(filter(None, [solutions.get(g["row"]) or solutions.get(g["strategy"], "")]
                                             + others[g["row"]])) if fix else ""
        if fix and not g["solution"]:
            print(f"  no solution: {g['row']} {g['name']}")
    fields = list(games[0].keys())
    if "by" not in fields:
        fields.insert(fields.index("reason") + 1, "by")
    with path.open("w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(games)
    (SURVEY / "stale.txt").write_text("".join(f"{row}\n" for row in stale))
    print(f"{path.relative_to(REPO)}: {len(games)} games; {len(stale)} answers given on a run since replaced")
    print("  verdicts:", dict(collections.Counter(g["verdict"] for g in games)))
    print("  by:", dict(collections.Counter(g["by"] for g in games)))
    by_strategy = collections.defaultdict(collections.Counter)
    for g in games:
        by_strategy[g["strategy"]][g["verdict"]] += 1
    for s, c in sorted(by_strategy.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {s:18} {sum(c.values()):5}  {dict(c)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
