<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Paid model calls: grants, counters, guard rails

The budget is the owner's. No paid model call (OpenRouter or any other provider) is made
without a grant he recorded himself, and every call is counted.

## Rules

1. **Ask first.** Whoever prepares a run (a spike, a reading campaign, even one test call)
   asks the owner with the scope, the model, the number of calls and an estimated cost.
2. **The owner grants.** `uv run tm budget grant --scope <scope> --usd <amount> --note "<his
   words>"` asks for confirmation on the terminal; there is no flag to skip it.
3. **The code refuses without room.** Every call goes through `tm.budget.Ledger.call(scope,
   estimate, model)`: it raises before the request when the estimate exceeds what is left,
   reserves the estimate, records the actual cost (the provider's `usage.cost`), and charges
   the estimate when a call fails or forgets to record.
4. **Count.** `uv run tm budget status` shows granted, spent, reserved and left per scope.
   The ledger (`TM_MODEL_LEDGER`, default `.local/model-ledger.jsonl`) is append-only and
   machine-local.
5. **Keys stay secret.** Keys live in `.env` (ignored) or the environment only. They are never
   printed, logged, committed or written to the ledger, which refuses notes that look like a
   credential. Tools read `.env` line by line for the variable they need, never whole.

## A second lock, outside the code

Set a credit limit on the key itself in the provider's dashboard (OpenRouter: *Keys → Edit
→ Credit limit*), equal to the sum of the grants. The ledger protects against our mistakes;
the provider's limit protects against everything else.
