# -*- coding: utf-8 -*-
"""R31 CENSUS: every parameter of every rules-engine function, paired with the extractor that
is supposed to populate it FROM RAW TEXT -- or with the reason it deliberately has none.

WHY THIS EXISTS. R31 has five recorded instances (presumptive/`makadirio`, chike.retrieval's
index contract, corporate `sector`, `partnership_tax_statement` whole-engine, rent-WHT's
subjunctive gate) and every one of them was found AFTER shipping, by measurement or in
production. Each was invisible to the unit tests because the tests call the engine function
directly with the signal already supplied as a keyword argument -- so they prove the BRANCH is
correct and can say nothing about whether the branch is REACHABLE.

R31 asks the question this file answers mechanically: "for every parameter an engine function
accepts, what in routing.py extracts this from question text?" Until now that question was
asked per-engine, by hand, after a defect surfaced. This enumerates it.

THE TWO CHECKS HERE CAN BOTH FAIL, which is the R20 requirement (a census whose assertions are
tautological reports zero remaining work while the gap stays open):

  1. SIGNATURE PARITY. The declared census for each engine must match the LIVE signature
     exactly. Add a parameter to an engine and forget to census it -> this fails. That is the
     arrival point R31 keeps using: a parameter appears, its branch gets unit-tested, and no
     extractor is ever written.
  2. EXTRACTOR EXISTENCE. Every extractor named in the census must be a real callable on the
     module it is attributed to. A renamed or deleted extractor -> this fails, rather than the
     census quietly asserting a wiring that no longer exists (the stale-pin decay shape).

WHAT THIS FILE DOES NOT DO, stated because it is the more important half. A census verifies
WIRING. It cannot show that the extractor FIRES on the phrasings real people use -- that is
exactly what was true of `corporate_sector` before 2026-09-05 (no extractor at all) and of
`asks_rent_withholding` before 2026-09-29 (an extractor that missed every subjunctive form).
Reachability is measured by eval/routing/probe_engine_reachability.py, which starts from a raw
string. This file tells you WHERE to point that harness; it is not a substitute for it.

Usage:  python eval/routing/audit_engine_parameters.py
Exit 0 = census complete and consistent; 1 = a parameter with no census row, a missing
extractor, or an unreviewed absent-extractor parameter.
"""

import inspect
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "engine_parameter_census.json")

from chike import routing, swahili_numbers as swn          # noqa: E402
from chike import rules_engine                             # noqa: E402

# How a parameter is populated. Only these five values are legal.
#   ROUTING      -> a named function in chike.routing reads it from raw text
#   NUMBERS      -> a named function in chike.swahili_numbers reads it from raw text
#   SLOT         -> the model-assisted SlotExtractor (deterministic layer primary), keyed by
#                   REQUIRED_FIELDS for that computation type
#   ENGINE_STATE -> not a user fact at all: a rate constant, a dispatch key, or the clock
#   ABSENT       -> NO extractor exists. Must carry `reviewed` naming the decision.
ROUTING, NUMBERS, SLOT, ENGINE_STATE, ABSENT = (
    "ROUTING", "NUMBERS", "SLOT", "ENGINE_STATE", "ABSENT")

# ---------------------------------------------------------------------------------------------
# THE CENSUS. Every row was read off the orchestrator CALL SITE, not off a comment (R26: three
# checks in the 2026-08-24 audit matched the comment explaining why a defect was removed).
# `site` is the orchestrator line that makes the call.
# ---------------------------------------------------------------------------------------------
CENSUS = {
    "compute_sdl": {
        "route": "sdl", "site": "orchestrator.py:422/467 rules_engine.compute",
        "params": {
            "gross_monthly_payroll": (SLOT, "SlotExtractor + swn.parse_payroll_groups"),
            "employee_count": (SLOT, "SlotExtractor + swn.parse_payroll_groups"),
        }},
    "sdl_applies": {
        "route": "sdl", "site": "orchestrator.py:673 rules_engine.applicability",
        "params": {
            "employee_count": (SLOT, "SlotExtractor via APPLICABILITY_REQUIRED_FIELDS"),
        }},
    "sdl_by_month": {
        "route": "sdl", "site": "orchestrator.py:382",
        "params": {
            "periods": (NUMBERS, "swn.parse_month_headcounts"),
            "gross_monthly_payroll": (NUMBERS, "swn.sole_plausible_amount"),
        }},
    "compute_nssf": {
        "route": "nssf", "site": "orchestrator.py:422/467 rules_engine.compute",
        "params": {
            "gross_monthly_payroll": (SLOT, "SlotExtractor + swn.parse_payroll_groups"),
            "party": (ROUTING, "routing.nssf_party"),
            "employer_rate": (ENGINE_STATE, "rates.py constant, not a user fact"),
            "employee_rate": (ENGINE_STATE, "rates.py constant, not a user fact"),
        }},
    "nssf_applies": {
        "route": "nssf", "site": "orchestrator.py:673", "params": {}},
    "compute_paye": {
        "route": "paye", "site": "orchestrator.py:467 rules_engine.compute",
        "params": {
            "monthly_salary": (SLOT, "SlotExtractor"),
            "resident": (ROUTING, "routing.paye_resident (+ paye_residency_unclear veto)"),
        }},
    "compute_paye_each": {
        "route": "paye", "site": "orchestrator.py:411",
        "params": {
            "salaries": (NUMBERS, "swn.parse_individual_salaries"),
            "resident": (ROUTING, "routing.paye_resident"),
        }},
    "compute_wcf": {
        "route": "wcf", "site": "orchestrator.py:422/467",
        "params": {
            "gross_monthly_payroll": (SLOT, "SlotExtractor + swn.parse_payroll_groups"),
        }},
    "wcf_applies": {
        "route": "wcf", "site": "orchestrator.py:673", "params": {}},
    "compare_to_floor": {
        "route": "minimum_wage", "site": "orchestrator.py:536",
        "params": {
            "paid": (NUMBERS, "swn.sole_plausible_amount"),
            "sector_no": (ENGINE_STATE, "wage_schedule.resolve(sq.text) -- reads raw text"),
            "sub": (ENGINE_STATE, "wage_schedule.resolve(sq.text) -- reads raw text"),
            "period": (ROUTING, "routing.wage_period"),
            "frame": (ROUTING, "routing.wage_question_frame"),
        }},
    "sector_rates_statement": {
        "route": "minimum_wage", "site": "orchestrator.py:534",
        "params": {
            "sector_no": (ENGINE_STATE, "wage_schedule.resolve(sq.text)"),
            "paid": (NUMBERS, "swn.sole_plausible_amount"),
            "period": (ROUTING, "routing.wage_period"),
        }},
    "vat_registration": {
        "route": "vat_registration", "site": "orchestrator.py:558",
        "params": {
            "turnover": (NUMBERS, "swn.sole_plausible_amount"),
            "period": (ROUTING, "routing.turnover_period"),
        }},
    "efd_required": {
        "route": "efd_requirement", "site": "orchestrator.py:572",
        "params": {
            "vat_registered": (ROUTING, "routing.states_vat_registered"),
        }},
    "compute_presumptive": {
        "route": "presumptive", "site": "orchestrator.py:590/608",
        "params": {
            "annual_turnover": (NUMBERS, "swn.sole_plausible_amount"),
            "keeps_records": (ROUTING, "routing.keeps_records"),
            "excluded_service": (ROUTING, "routing.states_excluded_service"),
            "new_business_exemption_granted": (ABSENT, None),
        }},
    "corporate_tax_rate_statement": {
        "route": "corporate_tax", "site": "orchestrator.py:620",
        "params": {
            "is_dse_listed": (ROUTING, "routing.is_dse_listed"),
            "meets_public_float": (ROUTING,
                                   "routing.dse_public_float_percent -> _dse_float_verdict"),
            "loss_years": (ROUTING, "routing.corporate_loss_years"),
            "sector": (ROUTING, "routing.corporate_sector"),
            "today": (ENGINE_STATE, "the clock (R32) -- not a user fact"),
        }},
    "partnership_tax_statement": {
        "route": "partnership_tax", "site": "orchestrator.py:640",
        "params": {
            "partner_is_individual": (ABSENT, None),
        }},
    "rent_wht_statement": {
        "route": "rent_wht", "site": "orchestrator.py:653",
        "params": {
            "letting_is_commercial": (ROUTING, "routing.rent_letting_is_commercial"),
            "payer_is_withholding_agent": (ABSENT, None),
        }},
    "levy_rate_statement": {
        "route": "sdl|nssf|paye|wcf", "site": "orchestrator.py:398",
        "params": {
            "computation_type": (ENGINE_STATE, "the route itself"),
            "amount": (NUMBERS, "swn.sole_plausible_amount"),
        }},
    "reject_base": {
        "route": "any levy", "site": "orchestrator.py:441",
        "params": {
            "computation_type": (ENGINE_STATE, "the route itself"),
            "stated_amount": (NUMBERS, "swn.rejectable_base_amount"),
            "invite": (ENGINE_STATE, "copy switch, not a user fact"),
        }},
}

# ---------------------------------------------------------------------------------------------
# ABSENT parameters need an explicit, reviewed decision. An unreviewed ABSENT fails the run --
# that is the whole point, because "parameter with no extractor" is R31's signature and the
# difference between a documented refusal to guess and an unnoticed gap is the review, not the
# absence. `defect` marks the ones that are NOT by design.
# ---------------------------------------------------------------------------------------------
ABSENT_REVIEW = {
    ("rent_wht_statement", "payer_is_withholding_agent"): {
        "verdict": "BY_DESIGN",
        "why": "Whether a payer is a withholding agent is a fact about their own tax status "
               "that no question states. Inferring it is how ext_43 went wrong (a small "
               "individual trader renting a village house told he must withhold). None states "
               "BOTH limbs and refuses to decide. R19 Guard-B: a derived quantity with no "
               "extractor must not be computed.",
        "guarded_by": "tests/test_rent_wht.py asserts NO such extractor exists",
    },
    ("compute_presumptive", "new_business_exemption_granted"): {
        "verdict": "BY_DESIGN",
        "why": "FA2026 s.27(a)(ii)-(iii) turns on whether the COMMISSIONER HAS GRANTED an "
               "application (para 2(4) -- not self-executing). No question states that, and "
               "asserting TZS 0 without it would be as wrong as ignoring a real possibility "
               "of TZS 0. None computes the ordinary band figure -- still the correct "
               "fallback -- and appends _NEW_BUSINESS_NOTE stating the exemption's possible "
               "applicability explicitly. Documented in presumptive.py's own module docstring.",
        "guarded_by": "NOTHING ASSERTS THE ABSENCE. Unlike payer_is_withholding_agent there is "
                      "no test forbidding a future extractor, so a later reader could add one "
                      "believing it an improvement. Recorded as a gap in the GUARD, not in the "
                      "design.",
    },
    ("partnership_tax_statement", "partner_is_individual"): {
        "verdict": "DEFECT",
        "why": "R31 exactly. The parameter narrows the EXPLANATION (an individual partner's "
               "share falls under the individual progressive bands, not a flat corporate "
               "rate), it is not a never-guess hazard, and the orchestrator calls "
               "partnership_tax_statement() with NO arguments at all -- so the branch is "
               "unreachable from every possible question. ext_06 was authored specifically to "
               "exercise it ('tests the partner_is_individual refinement, not just the bare "
               "refusal') and was adjudicated PARTIAL on 2026-09-23 with the note 'The "
               "partner_is_individual refinement is not exercised.' The gate row already "
               "records the cost.",
        "guarded_by": None,
    },
}


def _module_of(attribution):
    """Which module a census extractor string is attributed to."""
    if attribution is None:
        return None
    if attribution.startswith("routing."):
        return routing
    if attribution.startswith("swn."):
        return swn
    return None


def main():
    failures, rows = [], []

    for fn_name, entry in sorted(CENSUS.items()):
        fn = getattr(rules_engine, fn_name, None)
        if fn is None:
            failures.append(f"{fn_name}: not exported from chike.rules_engine")
            continue
        live = [p for p in inspect.signature(fn).parameters]
        declared = list(entry["params"])

        # CHECK 1 -- signature parity. Can fail: add an engine parameter, forget the census.
        missing = [p for p in live if p not in declared]
        extra = [p for p in declared if p not in live]
        if missing:
            failures.append(
                f"{fn_name}: LIVE PARAMETERS WITH NO CENSUS ROW: {missing}. This is R31's "
                f"arrival point -- census them and name the extractor, or mark ABSENT with a "
                f"reviewed decision.")
        if extra:
            failures.append(f"{fn_name}: census names parameters the signature does not "
                            f"have: {extra}")

        for pname in declared:
            kind, attribution = entry["params"][pname]
            row = {"engine": fn_name, "route": entry["route"], "site": entry["site"],
                   "parameter": pname, "kind": kind, "extractor": attribution,
                   "in_live_signature": pname in live}

            # CHECK 2 -- extractor existence. Can fail: rename or delete an extractor.
            mod = _module_of(attribution)
            if mod is not None:
                attr = attribution.split(".", 1)[1].split()[0].split("(")[0]
                if not callable(getattr(mod, attr, None)):
                    failures.append(f"{fn_name}.{pname}: census names "
                                    f"{attribution!r} but {mod.__name__}.{attr} is not a "
                                    f"callable")
                row["extractor_exists"] = callable(getattr(mod, attr, None))

            if kind == ABSENT:
                review = ABSENT_REVIEW.get((fn_name, pname))
                if review is None:
                    failures.append(
                        f"{fn_name}.{pname}: ABSENT with NO reviewed decision. A parameter "
                        f"with no extractor is either a documented refusal to guess or an "
                        f"unnoticed R31 gap, and only the review distinguishes them.")
                else:
                    row.update(review)
            rows.append(row)

    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    absent_defects = [f"{r['engine']}.{r['parameter']}" for r in rows
                      if r["kind"] == ABSENT and r.get("verdict") == "DEFECT"]

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/routing/audit_engine_parameters.py",
        "what_this_measures": (
            "WIRING: for every parameter of every rules-engine function, whether a named "
            "extractor reads it from raw question text, and for every parameter with none, "
            "whether that absence carries a reviewed decision."),
        "what_it_cannot_show": (
            "REACHABILITY. A census proves an extractor is wired, never that it fires on the "
            "phrasings real people use. corporate_sector had no extractor at all for four "
            "days while its branches were unit-tested; asks_rent_withholding HAD an extractor "
            "that missed every object-marked subjunctive form. Both are census-clean states. "
            "eval/routing/probe_engine_reachability.py is the measurement; this file only "
            "says where to point it."),
        "why_this_population": (
            "Every engine function exported by chike.rules_engine, which is the complete set "
            "of deterministic answers the system can give. R31's instances were all in this "
            "population and all found one at a time, after shipping."),
        "totals": {"engines": len(CENSUS), "parameters": len(rows), "by_kind": by_kind,
                   "absent_by_design": sum(1 for r in rows if r.get("verdict") == "BY_DESIGN"),
                   "absent_defects": absent_defects},
        "rows": rows,
        "failures": failures,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    for r in rows:
        mark = {"ABSENT": "!!"}.get(r["kind"], "  ")
        note = ""
        if r["kind"] == ABSENT:
            note = f"  <- {r.get('verdict', 'UNREVIEWED')}"
        print(f"{mark} {r['engine']:30} {r['parameter']:32} {r['kind']:12}"
              f"{r['extractor'] or '(none)'}{note}")

    print()
    print(f"engines: {len(CENSUS)} | parameters: {len(rows)} | {by_kind}")
    print(f"ABSENT extractors: by design "
          f"{sum(1 for r in rows if r.get('verdict') == 'BY_DESIGN')} | "
          f"DEFECT {len(absent_defects)} {absent_defects}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
