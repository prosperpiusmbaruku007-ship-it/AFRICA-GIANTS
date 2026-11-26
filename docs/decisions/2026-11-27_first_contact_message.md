# The first-contact message: ONE message for every new number (founder amendment to the R7 disclosure reading, 2026-11-27)

## What changed
| | before | now |
|---|---|---|
| a NEW number sends a greeting | the disclosure, then the welcome (two messages) | **one** message: the first-contact message |
| a NEW number sends a question | the disclosure, then the normal answer flow | the first-contact message, then the normal answer flow |
| an EXISTING number (already told) | the returning-user welcome on a greeting | **unchanged** |
| the number was deleted (FUTA) | treated as new again | unchanged: new again, so it gets the first-contact message again |

The text is the founder's, in `handler_core.FIRST_CONTACT_TEXT` (pinned verbatim in `tests/test_first_contact.py`). `DISCLOSURE_TEXT` is now an alias of it, so every path that sent "the message
once" sends this. The V1 disclosure is kept only as the never-sent constant `LEGACY_DISCLOSURE_TEXT_V1`, so the limb check can show nothing was lost.

## Every limb of the V1 disclosure is carried (pinned, limb by limb, in `tests/test_first_contact.py`)
| limb | V1 wording | first-contact wording |
|---|---|---|
| what Chike is | msaidizi wa maswali ya kodi na sheria za biashara | msaidizi (AI) wa Africa Giants |
| early-stage / supervised pilot | jaribio linalosimamiwa | hatua za mwanzo |
| a person reads most answers | yanasomwa na mtu | husomwa na mtu |
| latency is real | wakati mwingine saa kadhaa | wakati mwingine saa kadhaa |
| guidance, not formal legal advice | si ushauri rasmi wa kisheria | si ushauri rasmi wa kisheria |
| confirm with TRA / the authority | thibitisha na TRA au mamlaka husika | thibitisha na TRA au mamlaka husika |
| no unnecessary personal data | taarifa binafsi zisizo za lazima | taarifa binafsi zisizo za lazima |
| no passwords / bank numbers | nywila, namba za benki | nywila, namba za benki |
| messages help improve Chike | kuiboresha Chike | kuiboresha Chike |
| (new) how to delete records | | tuma FUTA |

**The one wording change to know about:** the literal words "jaribio linalosimamiwa" (a supervised test) no longer appear. The supervision limb is carried by "Chike yuko katika hatua za mwanzo"
together with "husomwa na mtu". The founder chose this wording; the amendment records it so it is not a quiet edit. A limb check fails if any pinned phrase is removed (planted in the tests).

## Decisions made while building it (the founder can reverse any of them)
1. **A greeting from a new number that already has a question pending** still gets the "your answer is still being prepared" notice after the first-contact message: the notice carries separate information.
2. **A clean send failure** releases the claim and the greeting falls back to the returning-user welcome, so the participant is not left in silence; the next message is still treated as a first contact.
3. **`DISCLOSURE=off`** still switches the whole mechanism off: a greeting then gets the welcome as before.
4. The message is a fixed text: the model is never called for it.

## Rollback
Set `DISCLOSURE_TEXT` back to `LEGACY_DISCLOSURE_TEXT_V1` and remove the greeting-first branch in `greet_and_send`; both are one-line changes, and the tests that pin the new behaviour will say exactly which to update.
