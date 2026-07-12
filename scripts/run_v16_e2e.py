"""End-to-end: run the 6 production spot-check questions through the FULL v16
orchestrator, driven by the REAL v15 model via the raw Modal completion endpoint.

No local GPU needed: retrieval (e5) and the rules engine run locally; only generate()
goes over HTTP to the real fine-tuned model on Modal.

Prereqs:
  1. Deploy the raw endpoint (adds generate_endpoint to the live Modal app):
        modal deploy chike-inference/modal_app.py
  2. Point this at that raw endpoint + the production token:
        set  CHIKE_RAW_ENDPOINT=https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run
        set  CHIKE_MODAL_TOKEN=<MODAL_API_TOKEN value>
     (PowerShell: $env:CHIKE_RAW_ENDPOINT='...'; $env:CHIKE_MODAL_TOKEN='...')
  3. python scripts/run_v16_e2e.py
"""
import os
import sys

# Make `chike` importable when run directly (repo root = parent of scripts/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chike.orchestrator import Orchestrator
from chike.model_abstraction import LocalAdapter

QUESTIONS = [
    'Faini kwa raia wa kigeni anayevunja GN487A ni kiasi gani hasa?',
    'SDL rate Tanzania ni asilimia ngapi?',
    'BRELA annual return ada ni shilingi ngapi?',
    'VAT withholding rate kwenye huduma ni asilimia ngapi?',
    'Naweza kudai input VAT kwenye bidhaa zilizo zero-rated?',
    ('Kampuni yangu ina wafanyakazi 12, mshahara wa jumla wa kila mmoja TZS 600,000. '
     '(1) Ninalipa SDL kiasi gani? (2) Ninalipa NSSF kiasi gani jumla? '
     '(3) Tarehe zote mbili za malipo ni lini?'),
]


def main():
    if not os.environ.get('CHIKE_RAW_ENDPOINT'):
        sys.exit('Set CHIKE_RAW_ENDPOINT and CHIKE_MODAL_TOKEN first (see module docstring).')

    backend = LocalAdapter()               # reads endpoint + token from env
    orch = Orchestrator(backend=backend)   # real e5 retrieval is the default retriever

    for i, q in enumerate(QUESTIONS, 1):
        print('=' * 72)
        print(f'Q{i}: {q}')
        reply = orch.answer(q)
        print(f'[in_scope={reply.in_scope} refused={reply.refused} '
              f'sub_answers={len(reply.sub_answers)}]')
        for j, sa in enumerate(reply.sub_answers, 1):
            tag = f'sub{j} route={sa.sub_question.kind}'
            if sa.needs_clarification:
                tag += ' NEEDS_CLARIFICATION'
            if sa.computation is not None:
                tag += (f' | rules_engine[{sa.computation.computation}] '
                        f'applicable={sa.computation.applicable} '
                        f'amount={sa.computation.amount} working={sa.computation.working!r}')
            if sa.facts:
                tag += f' | retrieved_facts={len(sa.facts)}'
            print('  ' + tag)
        print('--- FINAL v16 REPLY ---')
        print(reply.text)
        print()


if __name__ == '__main__':
    main()
