# Evidence rule for expanding auto-send to more routes (approved in principle 2026-11-26)

Today only model-free engine answers on `handler_core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES` may send after 15 minutes unreviewed, prefixed as an unchecked
automated calculation. `engine:fixed_statement` is excluded by name (`AUTOSEND_EXCLUDED_ENGINE_ROUTES`, 2026-11-16). This is the rule for letting a
route in. "Approved in principle" means the shape is agreed; each threshold is ratified when the first route qualifies.

A route (one `answer_path`) qualifies only when ALL hold, measured from the per-route review report (item D) over a single window:

1. **Volume and spread:** at least **60** reviewed instances, from at least **8 distinct non-test participants**, within the last 60 days. Zero defects
   in 60 puts the 95% upper bound on the defect rate near 5%. Fewer than 8 participants means one person's repeated question is the whole sample.
2. **Zero** edits, withholds and reviewer retries on the route in the window, and **zero misroutes** (an edit or withhold whose reason code is
   "wrong topic"; the review form needs that reason code first).
3. **Content version fixed:** the route's statement text and engine version hash is unchanged for the whole window. Any change to it resets the count.
4. **Review depth:** reviews decided faster than a minimum dwell (set from the measured median `decision_latency_s`) do not count. Skimming makes the
   evidence worthless (the R7 void-list item about review becoming skimming).
5. **Recorded sign-off:** the founder names the route in writing; the change is an allowlist edit in code, with a test and a positive control, as for 2c.
6. **Automatic demotion:** any later edit, withhold or misroute on an auto-sent route removes it from auto-send until it re-earns the evidence. A
   tunable kill switch exists and is exercised in a test.

Never eligible, however good the evidence: any route whose reply contains model-written text (`model_calls > 0`), any guard firing, a fact,
clarification, refusal or fallback path. Those stay under the 2026-11-13 amendment's void list.

Prerequisites (built with D): per-route approve-unchanged / edited / rejected counts, an edit-reason code list including "wrong topic", and the
content hash recorded on each stored item.
