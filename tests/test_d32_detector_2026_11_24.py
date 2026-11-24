"""D-FIDELITY-32 DETECTOR (medicines called zero-rated). NOT WIRED: no replacement copy until the founder approves the medicines_vat_exempt text. Planted both ways (R26): specimens flag, controls (negation, contrast clause, export, exempt wording) stay clean."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chike import fidelity  # noqa: E402

FLAG = ["Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).", "Kwa mfano, vifaa tiba (zero-rated) na dawa vinaweza kudai input VAT.", "Medicines are zero-rated in Tanzania."]
CLEAN = ["Dawa si zero-rated; ni msamaha wa VAT.", "Mauzo ya nje ni zero-rated; dawa ni msamaha.", "Dawa zinazouzwa nje ya nchi ni zero-rated.", "Mauzo ya nje yana tozo 0%.", "Dawa zimesamehewa VAT.", "Medicine is exempt, not zero-rated."]


@pytest.mark.parametrize("t", FLAG)
def test_specimen_flags(t):
    assert fidelity.medicines_called_zero_rated("", t)


@pytest.mark.parametrize("t", CLEAN)
def test_control_is_clean(t):
    assert not fidelity.medicines_called_zero_rated("", t)


def test_not_wired_yet():
    """Wiring is a separate, founder-approved step; this pins that the detector is not already in the served guard list."""
    import inspect
    assert "medicines_called_zero_rated" not in inspect.getsource(fidelity.body_contradicts_d16)
    from chike import clarification
    assert "medicines_zero_rated" not in clarification.CONSTANT_RESTATEMENTS
