# -*- coding: utf-8 -*-
"""RETRAIN-MEMO EVIDENCE (read-only): what does the CURRENT training export (`datasets/tier1a/sft/train_sft.jsonl`, the bytes that train) say about SDL EXEMPTIONS, the subject of this week's fabricated list, wrong YES for a private school and invented
mining/EPZ exemptions? The population is every row whose question or answer carries SDL beside an exemption word (a LOWER BOUND: R21 -- a different wording is not in it). Each row I READ carries a verdict against the approved statement
(eval/results via chike/rules_engine/fixed_statements.py, VETA Act Cap.82 R.E.2023 s.19 as amended by Finance Acts 2024 and 2026); a row I did not read is listed as UNREAD, never counted as clean (R39: a shorter finding list is not progress).
This does NOT rebuild the export (`rederive_retrain_precondition_2026_10_07.py` regenerates it with `generate_sft.py`, a write; this memo is read-only).

    python eval/controls/sweep_training_sdl_exemptions_2026_11_23.py   ->  eval/results/sweep_training_sdl_exemptions_2026_11_23.json
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402

# Verdicts of rows READ (index into train_sft.jsonl as of the committed export; if the export is regenerated the lookup below re-asserts the question text).
READ = {
    173: ("BORDERLINE", "NGO 'kwa kawaida zinalipa SDL'; only charitable organisations as the Act defines them are exempt, so 'NGO' alone is neither"),
    257: ("WRONG_PROCESS", "says an NGO must apply and obtain TRA confirmation; the exemption is by statutory category or Minister's Gazette notice"),
    400: ("INVENTED", "a formal application to the Commissioner citing EPZ status as a ground; no such route in the Act or the held TRA pages"),
    473: ("OK_HEDGED", "some farming may be exempt, confirm with TRA: consistent with s.19(1)(j)"),
    740: ("OVERBROAD", "'government agencies generally need not pay'; the Act exempts a body WHOLLY financed through Government subvention"),
    797: ("NOT_SDL", "VAT of SEZ companies, out of scope"),
    959: ("OK_HEDGED", "charities may be exempt, confirm with TRA"),
    965: ("UNSUPPORTED", "'EPZ companies usually have an SDL exemption': no held source says so"),
    1227: ("UNSUPPORTED", "lists SDL exemption among SEZ benefits: no held source says so"),
    1367: ("NOT_SDL", "import duty, out of scope"),
    1416: ("UNSUPPORTED", "EPZ may obtain an SDL exemption by TRA approval: no held source says so"),
    1545: ("PARTLY_WRONG", "parastatals 'pay like any other employer unless specially exempted'; the Act exempts those wholly financed through subvention"),
    1836: ("WRONG", "'private schools and colleges may be required to pay SDL if they have 10+ employees': registered educational institutions are exempt (s.19(1)(g)). THE LIVE WRONG REPLY ('Shule binafsi zenye wafanyakazi 10+ zinatozwa SDL') MIRRORS THIS ROW"),
    2041: ("UNSUPPORTED", "'EPZ companies have an SDL exemption': no held source says so"),
    2402: ("NOT_EXEMPTION", "allowance in the SDL base"),
    2444: ("PARTLY_WRONG", "lists SDL among the duties of a PRIVATE SCHOOL ('kama walimu >=10'); registered educational institutions are exempt"),
    2445: ("OK_HEDGED", "charities may be exempt, confirm with TRA"),
    2645: ("PARTLY_WRONG", "private school with 30 staff: 'ungeingia' (you would be in) with 'some education institutions may be exempt'; registered educational institutions are exempt"),
    2753: ("NOT_EXEMPTION", "export profits are taxed; SDL named in passing"),
    2773: ("NOT_SDL", "out-of-scope refusal"),
    2888: ("NOT_SDL", "PAYE of EPZ, out-of-scope refusal"),
    2894: ("OK_HEDGED", "government, embassies, religious and charitable bodies 'usually' exempt: consistent with the list, confirm with TRA"),
    3447: ("UNSUPPORTED", "SEZ company 'may obtain an SDL exemption', confirmed by EPZA: no held source says so"),
    3563: ("OK_HEDGED", "an honest out-of-scope hedge on SEZ"),
    3622: ("OK_HEDGED", "farm workers: some sectors may be exempt, confirm with TRA"),
    3792: ("WRONG_PROCESS", "NGO exemption must be proven to TRA every year, 'no written TRA exemption means SDL remains': invented process; exemption is by statutory category or Gazette"),
    3827: ("NOT_EXEMPTION", "GN487A and tax liability; SDL named in passing"),
}
RX = re.compile(r"(?i)SDL.{0,200}(?:msamaha|samehewa|haitozwi|hawalipi|exempt)|(?:msamaha|samehewa|exempt).{0,200}SDL")


def main():
    with io.open(os.path.join(REPO, "datasets", "tier1a", "sft", "train_sft.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    hit = [i for i, r in enumerate(rows) if RX.search(r["instruction"] + " " + r["output"])]
    out, unread = [], []
    for i in hit:
        if i in READ:
            v, why = READ[i]
            out.append(dict(row=i, verdict=v, why=why, q=rows[i]["instruction"][:160], a=rows[i]["output"][:220]))
        else:
            unread.append(i)
    bad = [o for o in out if o["verdict"] in ("WRONG", "WRONG_PROCESS", "INVENTED", "UNSUPPORTED", "OVERBROAD", "PARTLY_WRONG")]
    art = dict(export_rows=len(rows), matching_rows=len(hit), read=len(out), unread_row_ids=unread, asserting_something_unsupported_or_wrong=len(bad),
               bad_row_ids=[o["row"] for o in bad], rows=out, note="UNREAD rows are NOT clean; the pattern is a lower bound on the population (R21)")
    atomic_artifact.write_json(os.path.join(REPO, "eval", "results", "sweep_training_sdl_exemptions_2026_11_23.json"), art, ensure_ascii=False, indent=1)
    print(f"{len(rows)} export rows; {len(hit)} SDL-exemption rows; {len(out)} read; {len(bad)} wrong/unsupported/overbroad; {len(unread)} UNREAD: {unread}")


if __name__ == "__main__":
    main()
