"""2026-11-16: the five fixed statutory statements (notice, severance, overtime, annual leave, VAT time of supply).

(a) MODEL-FREE ROUTES -- all limbs stated, never a picked one; narrow cues swept (eval/controls/sweep_fixed_statements_2026_11_16.py).
(a') NOT AUTO-SEND ELIGIBLE -- founder's restriction, a NARROWING of the R7 amendment; fails closed on any route not on the allowlist.
(b) GUARDS (D-FIDELITY-10, R19 constant comparisons) on the model path, founded on the five live wrong replies of 2026-11-13.

Every guard and every cue is PLANTED (disabled / made over-broad) to show a test fires (R26), and every guard has correct bodies that
must pass (R17: the probes that should come back CLEAN do the work)."""
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "eval", "controls"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import sweep_fixed_statements_2026_11_16 as sweep      # noqa: E402
from chike import answer_trace, fidelity, routing, rules_engine   # noqa: E402
from chike.orchestrator import Orchestrator            # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_spec = importlib.util.spec_from_file_location("hc_fs_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

NOW = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)

# The five live wrong replies of the 2026-11-13 coverage deploy (eval/results/coverage_deploy_live_2026_11_13.json), VERBATIM.
LIVE = {
    "notice": ("Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?",
               "Kwa mfanyakazi wa kila mwezi, notisi ni siku 4. Thibitisha na mamlaka husika (osha.go.tz)."),
    "severance": ("Severance pay inahesabiwaje?",
                  "Mfanyakazi aliyetimiza miezi 12+ (miaka 1+) anapata: mshahara wake wa mwisho + asilimia 25% ya mshahara wake wa mwisho. "
                  "Thibitisha na sheria husika (elra.go.tz)."),
    "overtime": ("Overtime inalipwa kiasi gani?",
                 "Kiwango cha chini cha overtime ni asilimia 25% ya mshahara wa msingi. Thibitisha na GN605A (sekta yako)."),
    "annual_leave": ("Likizo ya mwaka ni siku ngapi?",
                     "Ndiyo, unatakiwa kulipa mshahara kamili wakati wa likizo. Hakuna sheria inayokuruhusu kusimamisha malipo ya mshahara "
                     "wakati wa likizo. Thibitisha na ELRA (elra.go.tz)."),
    "vat_time_of_supply": ("Nimeuza kwa mkopo, VAT inalipwa lini?",
                           "Kwa mauzo ya mkopo, unaweza kuomba kulipa VAT kidogo kidogo kulingana na makubaliano ya malipo. "
                           "Thibitisha na tra.go.tz."),
    # The three live wrong replies of the 2026-11-16 follow-up deploy (eval/results/followup_deploy_live_2026_11_16.json), VERBATIM -- the founding specimens of the extension.
    'vat_voluntary_registration': ('Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?',
        'Ndiyo, kwa mujibu wa sheria, unaweza kujisajili VAT kwa hiari hata ukiwa chini ya kiwango cha lazima. Thibitisha na TRA (tra.go.tz).'),
    'wcf_accident_reporting': ('Mfanyakazi amepata ajali kazini, taarifa WCF inaanza kuhesabiwa lini?',
        'Taarifa ya ajali kwa WCF inaanza kuhesabiwa tangu siku ya ajali au siku ambayo mwajiri alipata habari za ajali hiyo. Thibitisha na WCF (wcf.go.tz).'),
    # 2026-11-16 (3a): the live wrong replies of gate c2143c0 (eval_239, eval_348) and the PAYE question that has NO guard (see PAYE_NO_GUARD).
    'wcf_disease_reporting': ('Ugonjwa wa kazini unapaswa kutolewa taarifa WCF ndani ya muda gani tangu kugunduliwa?',
        'Magonjwa ya kazini yanatakiwa kuripotiwa WCF ndani ya siku 14 za kazi tangu kugunduliwa. Thibitisha na WCF (wcf.go.tz).'),
    'nssf_split': ('NSSF ina mgawanyo mmoja tu wa 10 kwa 10 kati ya mwajiri na mfanyakazi, sivyo?',
        'Ndiyo, NSSF Tanzania ina mgawanyo wa 10% kwa 10% baina ya mwajiri na mfanyakazi. Hakuna mgawanyo mwingine uliopo. Thibitisha na NSSF (nssf.go.tz).'),
    'paye_band_table': ('Mfumo wa mabano ya PAYE ya kila mwezi unafuata mpangilio gani wa viwango?',
        'Kuna ngazi 8 za mabano ya PAYE: asilimia 0 (hadi TZS 270,000), 8, 20, 25, 30, 35, 40, 45. Thibitisha na TRA (tra.go.tz).'),
    'vat_withholding_mixed_supply': ('VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?',
        'Kwa mauzo yenye sehemu ya bidhaa na sehemu ya huduma, thibitisha na TRA (tra.go.tz): kuanzia 1 Julai 2026, sheria inasema kiwango kinagawanywa 3:2 kwa uwiano unaofaa. Thibitisha na TRA (tra.go.tz).'),
    # 2026-11-17: the two live specimens of build a2e6611 (eval/results/licence_followup_deploy_live_2026_11_17.json), VERBATIM.
    'individual_income_tax_return': ('Return ya kodi ya mapato ya mtu binafsi ni lini?',
        'Kiwango cha kodi ya mapato ya mtu binafsi ni asilimia 0%. Thibitisha na TRA (tra.go.tz).'),
    'business_licence_validity': ('Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?',
        'Hapana, leseni ya biashara huwa inafanyiwa upya kila mwaka, na unapaswa kuwasilisha taarifa za kila mwaka kwa BRELA. Thibitisha na halmashauri yako, au BRELA kwa kundi A (brela.go.tz).'),
    # 2026-11-17 (next small batch): the live specimens of the TIN window (np_26, frozen set #1, VERBATIM) and the two-part licence question (build 911948b live check, VERBATIM).
    'tin_apply_deadline': ('Nimefungua saluni yangu mwezi huu. Kuna mtu kaniambia nina siku 15 za kuomba TIN kuanzia siku nilipoanza biashara, sivyo?',
        'Hapana, hiyo taarifa haiko sahihi. Hakuna siku maalum za 15 za kuomba TIN. Ni muhimu sana kupata TIN haraka iwezekanavyo. Thibitisha na tra.go.tz.'),
    'business_licence_fee_and_validity': ('Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?',
        'Ada ya leseni ya biashara hutofautiana kulingana na aina ya shughuli na eneo. Thibitisha na halmashauri husika (lga.go.tz).'),
    # 2026-11-18: the two live wrong replies of build 7b94236 (eval/results/annual_return_phrasings_live_2026_11_17.json), VERBATIM -- the correct row was at rank 1.
    'brela_annual_return_deadline': ('Annual return ya kampuni inatakiwa kuwasilishwa ndani ya muda gani?',
        'Annual return ya kampuni inatakiwa kuwasilishwa ndani ya siku 42 tangu tarehe ya kumbukumbu ya usajili. Thibitisha na BRELA (brela.go.tz).'),
    # 2026-11-22: the preliminary Gate 2 #20 (gp_20), question VERBATIM; the body is the shape of the failure (a rate asserted for a year whose Finance Act does not exist yet). The route, not a guard, is the control.
    'future_year_rate': ('Nina kampuni mpya na nataka kupanga bajeti ya mwaka ujao. Naomba unipe kiwango rasmi cha VAT kitakachotumika Tanzania mwaka 2028/2029.',
        'Kiwango rasmi cha VAT kitakachotumika mwaka 2028/2029 ni asilimia 18. Thibitisha na TRA (tra.go.tz).'),
    # 2026-11-23: the two live replies of build d997d4d, question VERBATIM; the body is the live fabricated list / wrong YES. The route, not a guard, is the control.
    'sdl_exemptions': ('Shule binafsi inalipa SDL?',
        'Shule binafsi zenye wafanyakazi 10+ zinatozwa SDL. Thibitisha na TRA (tra.go.tz).'),
    # 2026-11-23: the live reply of build a8a0274 to the payer question, VERBATIM; right on the payer, then an invented sentence. The route is the control, not a guard.
    'sdl_payer': ('Mwajiri au mfanyakazi analipa SDL?',
        'MWAJIRI (si mfanyakazi) ndiye anayelipa SDL. Ni adhabu kwa mwajiri kuajiri wafanyakazi wengi bila kusajiliwa. Mfanyakazi hapunguziwi kitu kwenye mshahara wake kwa sababu ya SDL.'),
    # 2026-11-23: the two live replies of build a67462c, question VERBATIM; the body is the live wrong reply. The route, not a guard, is the control.
    'sdl_employee_premise': ('Mfanyakazi analipa SDL wapi?',
        'Mfanyakazi anachangia SDL kwa kiwango cha 3.5%. Ni jukumu la mwajiri kukata 3.5% ya mishahara ya mfanyakazi na kuwasilisha fedha hizo TRA ifikapo siku ya 7.'),
    'sdl_nssf_party': ('SDL na NSSF zinakatwa kwa mfanyakazi?',
        'Mfanyakazi hakatiwi chochote katika SDL au NSSF.'),
    'sdl_how_to_file_pay': ('Nalipa SDL wapi?',
        'SDL inalipwa kwa fomu ITX 300.01.E kwenye benki yoyote.'),
    # 2026-11-23 (ten more statements): the live wrong replies of build b96e8a8 (eval/results/sdl_three_routes_live_2026_11_23.json, VERBATIM where quoted) or the gate-row failure shape. The ROUTE is the control, not a guard.
    'sdl_nssf_paye_party': ('SDL, NSSF na PAYE zinakatwa kwa mfanyakazi?',
        'Hapana -- si kwa mfanyakazi. SDL, NSSF na PAYE zinakatwa kwa MWAJIRI pekee.'),
    'nssf_party': ('NSSF inakatwa kwa mfanyakazi?',
        'Ndiyo -- mfanyakazi anakatwa asilimia 10 ya mshahara wake, sawa na asilimia 20 ya mshahara wake.'),
    'brela_three_forms': ('Nina wafanyakazi 20 na mtaji wa TZS 50,000,000, je nasajili kampuni au jina la biashara BRELA?',
        'Kwa wafanyakazi 20 na mtaji wa TZS 50,000,000 unapaswa kusajili kampuni.'),
    'brela_fee_no_share_capital': ('Ada ya kusajili kampuni isiyo na mtaji wa hisa (no share capital) BRELA ni TZS ngapi?',
        'Ada ni TZS 300,000.'),
    'gn487a_penalties': ("GN 487A inasema nini kuhusu mpango wa 'jina la mkopo' (nominee) -- kwanini unazuiwa?",
        'Mpango wa jina la mkopo unazuiwa kwa sababu unamruhusu mgeni kukwepa sheria; adhabu ni TZS 500,000.'),
    'vat_withholding_rates': ('Je, kiwango cha asilimia 3 cha VAT withholding kinatumika pia kwa ununuzi wa huduma za IT kutoka kwa msambazaji aliyesajiliwa VAT?',
        'Ndiyo, asilimia 3 inatumika kwa huduma zote.'),
    'vat_professional_services': ('Kwa nini fani kama wakili na wahandisi zinahitajika kusajilisha VAT bila kujali mauzo yao?',
        'Wakili na wahandisi wanasajili VAT tu wakifikia TZS 200,000,000.'),
    'brela_late_annual_return': ('Kampuni ilishindwa kuwasilisha annual return kwa miaka 2 -- matokeo yanayoweza kutokea ni yapi?',
        'Kampuni itafutwa mara moja na wakurugenzi watafungwa jela.'),
    'sdl_paye_deadline': ('Je, SDL na PAYE zinalipwa TRA kwa wakati mmoja -- siku ya 7 ya mwezi unaofuata?',
        'Hapana, SDL ni tarehe 7 na PAYE ni tarehe 20.'),
    'vat_medical_services': ('Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?',
        'Ndiyo, daktari anayefanya mazoezi ya udaktari ana sifa ya kutoa huduma za kitaalamu na hivyo anatakiwa kusajili VAT. Thibitisha na TRA (tra.go.tz).'),
    'sdl_base': ('How does an employer calculate the SDL amount payable each month?',
        'The base is gross payroll (cash basis), si pamoja na posho za fedha.'),
    'levy_rates_three': ('SDL, NSSF na PAYE ni asilimia ngapi?',
        'PAYE ni asilimia 8 (0%-270%: 0%, 8%, 20%, 25%, 30%). Sehemu ya mwajiri peke yake ni 14% (NSSF 10% + SDL 3.5% + PAYE 0.5%).'),
    'levy_deadlines_three': ('SDL na NSSF na PAYE zinalipwa lini?',
        'PAYE inalipwa pamoja na PAYE, ikijumuisha malipo ya PAYE na michango ya NSSF, ifikapo tarehe 7 ya mwezi unaofuata.'),
    'paye_residency': ('Does a foreign employee pay PAYE at a different rate from a citizen?',
        "Yes, there's a different treatment for foreign employees. A foreigner working as an employee pays a flat rate of 15% on their gross employment income."),
    'paye_rate': ('PAYE ni asilimia ngapi?',
        'Kiwango cha kawaida cha PAYE Tanzania ni asilimia 30, lakini kuna bendi za mapato zinazotoa punguzo.'),
    'vat_health_and_medicines': ('Huduma za afya zinatozwa VAT? Na dawa je?',
        'Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%), kwa hiyo hazitozwi VAT.'),
    'wcf_base': ('WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?',
        'Posho zinazolipwa kila mwezi huongezwa kwenye mshahara wa msingi kabla ya kukokotoa WCF.'),
    'vat_medicines': ('Dawa zinatozwa VAT?',
        'Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%), kwa hiyo hazitozwi VAT.'),
    'paye_base': ('Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?',
        'PAYE inakokotolewa kwa msingi wa mshahara wa msingi pekee (basic salary), wakati SDL inajumuisha posho.'),
    'sdl_audit_hedge': ('How does TRA conduct an SDL audit and what do they examine?',
        'TRA conducts an SDL audit by examining: (1) whether you have 10+ employees ... The auditor will ask to see: payslips, P9 forms, SDL returns, bank statements, and relevant contracts.'),
}


# ── the statements are the verified facts, not a second copy that can drift ─────────────────────
def _nums(text):
    return sorted(set(re.findall(r"\d+(?:[.,]\d+)?", text)))


@pytest.mark.parametrize("topic", [t for t in fs.TOPICS if t not in fs.TOPICS_NO_CONCISE_ROW])
def test_statement_figures_equal_the_served_row_and_the_locked_fact(topic):
    import precompute_rag_embeddings as pre
    key, text, _ = fs.STATEMENTS[topic]
    row = pre.CONCISE_BILINGUAL_FACTS[key]
    assert _nums(text) == _nums(row), (topic, _nums(text), _nums(row))
    facts = json.load(open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8"))
    fact = facts[key] if isinstance(facts, dict) and key in facts else [f for f in facts if f.get("key") == key][0]
    cv = fact["correct_value"]
    for n in re.findall(r"\d+(?:\.\d+)?", cv):
        assert n in text, (topic, n, "correct_value figure missing from the statement")


def test_the_notice_statement_states_every_limb_and_picks_none():
    t = fs.fixed_statement("notice").working
    for limb in ("siku 7", "siku 4", "siku 28"):
        assert limb in t
    assert "kila mwezi" in t and "kila wiki" in t


def test_an_unknown_topic_raises_rather_than_guessing():
    with pytest.raises(KeyError):
        fs.fixed_statement("capital_gains")


# ── routes: probes (diverting AND clean) + plants ──────────────────────────────────────────────
@pytest.mark.parametrize("q,want,why", sweep.PROBES)
def test_probe_routes_as_expected(q, want, why):
    assert routing.detect_intent(q) == want, why


def _failed(monkeypatch, name, value):
    monkeypatch.setattr(routing, name, value)
    return [q for q, want, _ in sweep.PROBES if routing.detect_intent(q) != want]


def test_plant_ask_cue_disabled_is_caught(monkeypatch):
    assert _failed(monkeypatch, "_FS_ASK", re.compile(r"(?!x)x"))


def test_plant_ask_cue_made_universal_is_caught(monkeypatch):
    failed = _failed(monkeypatch, "_FS_ASK", re.compile(r""))
    assert any("akikataa kuchukua likizo" in q or "Mkataba wa kazi" in q or "nahitaji mashine" in q for q in failed)


def test_plant_other_levy_veto_removed_is_caught(monkeypatch):
    failed = _failed(monkeypatch, "_FS_OTHER_LEVY", re.compile(r"(?!x)x"))
    assert any("NSSF" in q or "SDL" in q for q in failed)


def test_plant_two_topic_decline_removed_is_caught(monkeypatch):
    """Pretend the first of two matching topics is enough: the two-topic probe must then divert, and the sweep catches it."""
    orig = routing.fixed_statement_topics

    def first_wins(text):
        ql = text.lower()
        if not routing._FS_ASK.search(ql) or routing._FS_OTHER_LEVY.search(ql):
            return None
        hits = orig(text)
        return hits[0] if hits else None
    monkeypatch.setattr(routing, "fixed_statement_topic", first_wins)
    assert any("overtime na severance" in q for q, want, _ in sweep.PROBES if routing.detect_intent(q) != want)


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly."""
    pats = [routing._FS_ASK, routing._FS_OTHER_LEVY]
    for _n, cue, need, veto in routing._FS_TOPICS:
        pats += [p for p in (cue, need, veto) if p is not None]
    pats += [getattr(fidelity, n) for n in dir(fidelity) if n.startswith("_FD10") and hasattr(getattr(fidelity, n), "pattern")]
    pats += list(fidelity._FD10_SUBJECT_WORDS.values())
    assert len(pats) > 20
    for p in pats:
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


# ── the orchestrator: model-free, whole statement ──────────────────────────────────────────────
class _Backend:
    """Returns a fixed reply and counts calls."""

    def __init__(self, reply="JIBU."):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply="JIBU.", facts=("Ukweli.",)):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: list(facts), ooc_phrases=[], in_scope_phrases=[]), b


@pytest.mark.parametrize("topic", fs.TOPICS)
def test_the_live_question_is_answered_with_the_whole_statement_and_zero_model_calls(topic):
    q, _ = LIVE[topic]
    o, b = _orch()
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(topic).working in reply.text


def test_the_notice_answer_does_not_pick_the_limb_the_question_named():
    """The live defect was 'siku 4' for a MONTHLY employee. The model-free answer states 28 AND the other limbs."""
    o, _ = _orch()
    text = o.answer(LIVE["notice"][0]).text
    assert "siku 28" in text and "siku 4" in text and "siku 7" in text


# ── NOT AUTO-SEND ELIGIBLE: the founder's restriction, fail-closed, with a positive control ─────
def _item(**kw):
    held = NOW - timedelta(minutes=16)
    base = {"review_id": "2026-11-16T11:44:00+00:00-abcd1234", "status": "pending", "sender": "255700000001@s.whatsapp.net",
            "sender_hash": "abcd1234abcd", "sender_tail": "0001", "question": "q",
            "draft": "Jibu la injini.", "engine_working": "working", "facts": [], "answer_path": "engine:vat_registration",
            "model_calls": 0, "guards": [], "held_at": held.isoformat(), "ts_held": held.isoformat(), "fallback": False}
    base.update(kw)
    return base


def test_positive_control_a_model_free_engine_route_is_still_eligible():
    assert core.engine_only_verdict(_item())[0] is True
    assert core.autosend_verdict(_item(), now=NOW, after_s=900.0)[0] == "auto_send"


def test_the_fixed_statement_route_is_never_auto_sent_even_when_everything_else_qualifies():
    it = _item(answer_path="engine:fixed_statement")            # model_calls 0, no guard, working present, evidence present
    ok, why = core.engine_only_verdict(it)
    assert ok is False and "excluded" in why, why
    assert core.autosend_verdict(it, now=NOW, after_s=900.0)[0] == "hold_notice"


def test_an_unknown_engine_route_fails_closed():
    ok, why = core.engine_only_verdict(_item(answer_path="engine:some_new_route"))
    assert ok is False and "allowlist" in why


def test_every_route_the_router_can_produce_is_either_allowed_or_excluded_deliberately():
    """A new compute type must be put on one list ON PURPOSE. 'ambiguous_multi' only ever clarifies (':ask'), so it is refused elsewhere."""
    known = set(core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES) | set(core.AUTOSEND_EXCLUDED_ENGINE_ROUTES)
    for ctype in routing.COMPUTE_TYPES:
        assert f"engine:{ctype}" in known, f"{ctype} is on neither auto-send list"
    for extra in ("engine:vat_registration", "engine:efd_requirement", "engine:presumptive"):
        assert extra in known
    assert not (set(core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES) & set(core.AUTOSEND_EXCLUDED_ENGINE_ROUTES))


def test_plant_the_exclusion_removed_is_caught(monkeypatch):
    """R26: with the exclusion deleted AND the route admitted, the same item DOES qualify -- so the test above can fail."""
    monkeypatch.setattr(core, "AUTOSEND_EXCLUDED_ENGINE_ROUTES", frozenset())
    monkeypatch.setattr(core, "AUTOSEND_ELIGIBLE_ENGINE_ROUTES",
                        core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES | {"engine:fixed_statement"})
    assert core.engine_only_verdict(_item(answer_path="engine:fixed_statement"))[0] is True


def test_plant_deleting_only_the_exclusion_still_refuses_because_the_allowlist_is_the_second_lock(monkeypatch):
    monkeypatch.setattr(core, "AUTOSEND_EXCLUDED_ENGINE_ROUTES", frozenset())
    ok, why = core.engine_only_verdict(_item(answer_path="engine:fixed_statement"))
    assert ok is False and "allowlist" in why


def test_the_real_trace_of_a_fixed_statement_reply_is_refused_and_carries_the_banner():
    o, _ = _orch()
    t = answer_trace.trace(o.answer(LIVE["overtime"][0]))
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=t["facts"] or ["x"], model_calls=t["model_calls"],
               guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False
    sw, en = core.autosend_note(it, now=NOW, after_s=900.0)
    assert "FIXED STATEMENT" in en and "never auto-sent" in en and "JIBU LA SHERIA" in sw


# ── GUARDS (D-FIDELITY-10): the five live replies are the founding specimens ────────────────────
# 3b: NO ordinal-band guard is built. "Sehemu ya pili (20%)" is defensible if the 0% band is not counted and wrong if it is (the served row numbers it band 3); a guard would blank a defensible narration.
# The PAYE band-table STATEMENT is the control for the question that asks for the table; D-FIDELITY-11 keeps guarding band EDGES. The invented-band specimen below IS caught, by the figure rule.
# 2026-11-17: the two new topics are also not guarded by fixed_figure_violations. business_licence_validity is guarded by the licence rules (D-FIDELITY-13 dates, D-FIDELITY-17 validity periods) in
# chike.fidelity.constant_violations; the individual-return specimen is a wrong-TOPIC answer (a tax RATE) with no figure of the statement's to contradict -- the statement route is the control.
# 2026-11-17 (next small batch): tin_apply_deadline is guarded by the D-FIDELITY-13 TIN rule (chike.fidelity.constant_violations) and business_licence_fee_and_validity by the licence-expiry / validity-period rules
# (a fee-only reply to a two-part question has no figure of the statement's to contradict: the statement ROUTE is the control).
PAYE_NO_GUARD = frozenset({"paye_residency", "paye_rate", "vat_health_and_medicines", "wcf_base", "vat_medicines", "paye_base", "vat_medical_services", "sdl_base", "levy_rates_three", "levy_deadlines_three", "sdl_nssf_paye_party", "nssf_party", "brela_three_forms", "brela_fee_no_share_capital", "gn487a_penalties", "vat_withholding_rates", "vat_professional_services", "brela_late_annual_return", "sdl_paye_deadline", "sdl_audit_hedge", "sdl_exemptions", "sdl_payer", "sdl_employee_premise", "sdl_how_to_file_pay", "sdl_nssf_party", "future_year_rate", "brela_annual_return_deadline", "paye_band_table", "individual_income_tax_return", "business_licence_validity", "tin_apply_deadline", "business_licence_fee_and_validity"})


@pytest.mark.parametrize("topic", [t for t in fs.TOPICS if t not in PAYE_NO_GUARD])
def test_the_live_wrong_reply_is_flagged(topic):
    q, body = LIVE[topic]
    got = fidelity.fixed_figure_violations(q, body)
    assert got and got[0][0] == topic, (topic, got)


CORRECT = [
    # (question, a CORRECT body that must pass)
    (LIVE["notice"][0], "Kwa mfanyakazi wa kila mwezi, notisi ni siku 28 baada ya mwezi wa kwanza."),
    (LIVE["notice"][0], "Mwezi wa kwanza: siku 7. Baada ya hapo: siku 4 kwa wa kila wiki, siku 28 kwa wa kila mwezi."),
    ("Mfanyakazi wa kila wiki, notisi ni siku ngapi?", "Kwa mfanyakazi wa kila wiki notisi ni siku 4."),
    ("Mfanyakazi wa kila mwezi, notisi ni siku ngapi? Mkataba unasema siku 30.", "Mkataba unaweza kuweka siku 30, ambayo ni zaidi ya siku 28."),
    (LIVE["severance"][0], "Angalau mshahara wa msingi wa siku 7 kwa kila mwaka kamili, hadi miaka 10, baada ya miezi 12 mfululizo."),
    (LIVE["severance"][0], "Malipo si asilimia 25 ya mshahara; ni siku 7 kwa kila mwaka kamili."),
    (LIVE["overtime"][0], "Overtime inalipwa angalau mara 1.5 ya mshahara wa msingi."),
    (LIVE["overtime"][0], "Overtime inalipwa asilimia 150 ya mshahara wa msingi."),
    (LIVE["overtime"][0], "Overtime inalipwa asilimia 50 zaidi ya mshahara wa kawaida."),
    ("Overtime inalipwa kiasi gani, na inakatwa NSSF?", "Overtime ni mara 1.5. NSSF ni asilimia 10 kwa mwajiri."),
    (LIVE["annual_leave"][0], "Likizo ya mwaka ni angalau siku 28 mfululizo, na unalipwa mshahara wako."),
    (LIVE["annual_leave"][0], "Likizo ya mwaka ni wiki 4 (siku 28), analipwa mshahara."),
    ("Likizo ya mwaka ni siku ngapi, na ya uzazi?", "Likizo ya mwaka ni siku 28. Likizo ya uzazi ni siku 84."),
    (LIVE["vat_time_of_supply"][0],
     "VAT inadaiwa mapema zaidi kati ya invoice, malipo au usambazaji. Return ni tarehe 20 ya mwezi unaofuata."),
    (LIVE["vat_time_of_supply"][0], "Si kidogo kidogo; VAT inadaiwa ukitoa invoice hata mteja asipolipa bado."),
]


@pytest.mark.parametrize("q,body", CORRECT)
def test_a_correct_body_passes(q, body):
    assert fidelity.fixed_figure_violations(q, body) == [], (q, body)


@pytest.mark.parametrize("q,body", [
    # the topic is not the question's: the same words in a question about something else are NOT judged
    ("Likizo ya uzazi ni siku ngapi?", "Likizo ya uzazi ni siku 84."),
    ("Kizingiti cha VAT ni kiasi gani?", "Kizingiti ni TZS 200,000,000. Return ni tarehe 20."),
    ("SDL ni asilimia ngapi?", "SDL ni asilimia 3.5 ya mshahara wa jumla."),
    ("PAYE inalipwa tarehe ngapi?", "PAYE inalipwa tarehe 7 ya mwezi unaofuata."),
    ("Nikichelewa kulipa NSSF adhabu ni nini?", "Adhabu ni asilimia 5 kwa mwezi."),
    # the priced false positive: an NSSF question about overtime, answered with the NSSF split (training row batch_003_cleaned:214)
    ("NSSF inahesabiwaje kwa wafanyakazi wanaopata overtime?", "Kiwango: mwajiri 10% + mfanyakazi 10% ya mshahara wa jumla."),
])
def test_a_question_outside_the_five_topics_is_never_judged(q, body):
    assert fidelity.fixed_figure_violations(q, body) == []


@pytest.mark.parametrize("topic,rule", [
    ("notice", "_fd10_notice"), ("severance", "_fd10_severance"), ("overtime", "_fd10_overtime"),
    ("annual_leave", "_fd10_annual_leave"), ("vat_time_of_supply", "_fd10_vat"),
])
def test_plant_each_rule_disabled_loses_its_founding_specimen(monkeypatch, topic, rule):
    """R26: the specimen is flagged BY THIS RULE. Disable it and the specimen goes unflagged, so the specimen test above can fail."""
    q, body = LIVE[topic]
    assert fidelity.fixed_figure_violations(q, body)
    monkeypatch.setattr(fidelity, rule, lambda *a, **k: [])
    assert fidelity.fixed_figure_violations(q, body) == []


def test_plant_an_overbroad_overtime_rule_is_caught_by_the_correct_bodies(monkeypatch):
    monkeypatch.setattr(fidelity, "_FD10_PERCENT", re.compile(r"(\d+(?:[.,]\d+)?)\s*()"))
    bad = [(q, b) for q, b in CORRECT if fidelity.fixed_figure_violations(q, b)]
    assert bad


def test_plant_the_negation_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_fd10_negated", lambda s, p: False)
    assert any(fidelity.fixed_figure_violations(q, b) for q, b in CORRECT)


# Two more LIVE wrong replies, from the first deploy's fall-through arm (eval/results/fixed_statements_deploy_live_2026_11_16_firstdeploy.json):
LIVE_FALLTHROUGH_2 = [
    ("Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.",
     "Malipo ya severance pay kwa mfanyakazi aliyeachishwa kazi yanatakiwa kulipwa ndani ya siku 30 baada ya kumaliza huduma. "
     "Thibitisha na Sheria ya Ajira na Mahusiano Kazini (ELRA)."),
    ("Likizo ya mwaka na overtime ni siku ngapi?", "Thibitisha na ELRA (elra.go.tz)."),
]


@pytest.mark.parametrize("q,body", LIVE_FALLTHROUGH_2)
def test_the_second_live_gaps_are_flagged(q, body):
    assert fidelity.fixed_figure_violations(q, body), (q, body)


def test_a_two_topic_replacement_answers_both_topics_whole():
    o, _ = _orch(reply="Thibitisha na ELRA (elra.go.tz).")
    text = o.answer("Likizo ya mwaka na overtime ni siku ngapi?").text
    assert fs.fixed_statement("annual_leave").working in text and fs.fixed_statement("overtime").working in text


def test_a_correct_two_topic_body_is_left_alone():
    assert fidelity.fixed_figure_violations("Likizo ya mwaka na overtime ni siku ngapi?",
                                            "Likizo ya mwaka ni siku 28. Overtime ni angalau mara 1.5.") == []


# ── wired end to end: PHRASINGS THAT MISS THE ROUTES -- the guard is the fallthrough's safety net ─
FALLTHROUGH = [
    ("notice", "Mfanyakazi wa kila mwezi nikimwachisha, notisi ni ya siku zipi?", LIVE["notice"][1]),
    ("severance", "Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.", LIVE["severance"][1]),
    ("overtime", "Naomba kujua kuhusu overtime ya wafanyakazi wangu.", LIVE["overtime"][1]),
    ("annual_leave", "Likizo ya mwaka na overtime ni siku ngapi?", LIVE["annual_leave"][1]),
    ("vat_time_of_supply", "Nimeuza kwa mkopo, naomba kujua kuhusu VAT.", LIVE["vat_time_of_supply"][1]),
]


@pytest.mark.parametrize("topic,q,wrong", FALLTHROUGH)
def test_a_phrasing_that_misses_the_route_is_caught_by_the_guard(topic, q, wrong):
    assert routing.detect_intent(q) == "none", "this phrasing must MISS the route, or it is not exercising the guard"
    o, b = _orch(reply=wrong)
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert b.calls >= 1 and t["model_calls"] and t["model_calls"] > 0
    assert t["guards"] == ["replaced"], t
    first = topic if topic != "annual_leave" else "annual_leave"
    assert fs.fixed_statement(first).working in reply.text
    assert wrong.split(".")[0] not in reply.text
    # never auto-send eligible: a model-path reply with a guard
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=t["model_calls"], guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False


def test_the_guard_does_not_touch_a_correct_model_answer_on_a_missed_phrasing():
    o, _ = _orch(reply="Overtime inalipwa angalau mara 1.5 ya mshahara wa msingi.")
    reply = o.answer("Naomba kujua kuhusu overtime ya wafanyakazi wangu.")
    assert answer_trace.trace(reply)["guards"] == []
    assert "mara 1.5" in reply.text


def test_plant_the_guard_unwired_lets_the_wrong_answer_through(monkeypatch):
    monkeypatch.setattr(fidelity, "body_contradicts_fixed_figure", lambda q, b: False)
    o, _ = _orch(reply=LIVE["overtime"][1])
    reply = o.answer("Naomba kujua kuhusu overtime ya wafanyakazi wangu.")
    assert "asilimia 25" in reply.text and answer_trace.trace(reply)["guards"] == []
