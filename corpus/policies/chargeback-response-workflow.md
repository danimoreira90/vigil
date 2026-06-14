# Policy — Chargeback Response Workflow

> Synthetic operational playbook. Process steps are illustrative and pending ratification.

## Purpose
Define how Vigil handles an incoming chargeback notification from the acquirer or directly from a network: from receipt to representment decision to Label-store update.

## Step 1 — Intake and triage
- The chargeback is logged with its network reason code (Visa 10.x, MasterCard 4xxx, Amex F/C/R) and tied to the original Transaction.
- The Case is reopened (or created if it never went to `review`) and routed to the chargeback-response analyst queue.

## Step 2 — Evidence gathering
- Pull the Scorer output (Score, reason codes, model version) at the time of the original Transaction.
- Pull authentication evidence (3-D Secure outcome, AVS, CVV).
- Pull fulfillment evidence (delivery confirmation, tracking, signature) where applicable.
- Pull account-history evidence (prior Transactions, prior interactions, prior disputes).

## Step 3 — Representment decision
- If the evidence supports the merchant's position and the chargeback reason code permits representment, prepare the compelling-evidence packet per the network's requirements.
- If the evidence does not support representment, accept the chargeback. Update the Label store: the original Transaction is now a confirmed-fraud Label (for the relevant fraud-flavored reason codes) or a non-fraud dispute (for consumer-dispute reason codes).
- If the reason code is ambiguous (e.g. consumer dispute used as cover for friendly fraud), the analyst's notes guide the Label assignment; mislabeling here teaches the wrong lesson to future Scorer training.

## Step 4 — Feedback loop
- A chargeback on a Transaction that scored low is a Scorer learning opportunity; flag for the Drift monitor.
- A chargeback on a Transaction that scored high but the Decision Engine allowed is a threshold-tuning opportunity; flag for the Rule-review forum.
- A pattern of chargebacks at one merchant feeds the merchant-monitoring queue (see `escalation-thresholds.md`).

## Step 5 — Label-store update
- The final Label assignment is timestamped and tied back to the original Transaction with the reason code and analyst notes.
- The Label store is the training data for the next Scorer iteration; correctness here matters more than speed.

## Out of scope
- Policy on which merchants to accept chargebacks for in bulk (high-volume settlement) is a commercial decision outside this workflow.
