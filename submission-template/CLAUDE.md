# Competition Project
 
## What This Is
 
An autonomous triage agent for an e-commerce Order Management IT helpdesk, built in ~50 minutes using Claude Code. The agent classifies inbound tickets by category and priority (P1–P4), auto-resolves a defined set of low-complexity issues without human touch, and routes everything else to the correct human queue with full context attached. Domain: Scenario 3 (Agentic Solution).
 
## Tech Stack
 
- Python 3.11
- Anthropic SDK via `AnthropicBedrock` (AWS Bedrock)
- Tool-use agentic loop (Claude claude-3-7-sonnet)
- Structured JSON output for all agent decisions — no free-form text to calling systems
- Model: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`, region `us-east-1`
 
## Project Structure
 
```
agent.py        — agentic loop, pre-flight filters, deterministic router, action executor
tools.py        — tool implementations (mock) + JSON schemas for knowledge_lookup,
                  order_lookup, check_customer, submit_triage_decision
main.py         — demo runner; 8 representative tickets covering happy paths + edge cases
eval.py         — 22-case eval harness; per-dimension scoring across 6 metrics
mandate.md      — SOURCE OF TRUTH: priority framework, autonomous action list, guardrails
architecture.md — component design; section numbers used as stable prompt references
```
 
**Do not reorganize the file structure without updating mandate.md and architecture.md references.**
 
## Conventions
 
**Naming:**
- Tool functions: `verb_noun` snake_case — `order_lookup`, `check_customer`, `knowledge_lookup`
- Queue names: kebab-case — `ops-l1`, `ops-l2`, `fraud-team`, `legal-compliance`, `triage-review`
- Flags: snake_case strings on a list — `injection_suspected`, `legal_complaint`, `fraud_flag_present`
- Priority: always string `"P1"` through `"P4"`, never integer
- Confidence: float 0.0–1.0, two decimal places
 
**Code structure:**
- Pre-flight filters: pure Python, no imports from agent logic, runs before any LLM call
- `route()`: pure function, no side effects, first-match-wins ordered list — independently unit-testable
- `executor_validate()`: returns `(allowed: bool, override_reason: str | None)`
- `ALLOWLIST`: dict of `str → lambda(order, customer) → bool`
- System prompt (`SYSTEM_PROMPT`): module-level constant in `agent.py`, not constructed at runtime
 
**Output format:**
- All agent decisions output via `submit_triage_decision` tool call — never parsed from free-form text
- Every decision writes an audit log record before any action executes
- `reasoning` field: 1–3 sentences; must cite tool results; must name any guardrail triggered
 
**What Claude must never do in this codebase:**
- Combine `order_lookup` and `check_customer` into one tool — tool separation is a deliberate data-exposure boundary
- Put routing logic inside the agentic loop — it belongs in `route()`, called by the executor
- Use free-form string matching for priority or category — enums only, validated against schema
- Trust the LLM's `route_to` suggestion — the deterministic routing table always has final authority
 
## Important Context
 
**The agent is a first-responder, not a resolution system.** It triages, routes, or resolves within a tightly defined allowlist. When in doubt, it routes to a human rather than acts.
 
**Two source-of-truth documents — always reference by section:**
- `mandate.md` — what the agent is authorized to do; do not invent rules not in this document
- `architecture.md` — how it's wired; `§2.2` = pre-flight, `§2.4` = action executor, `§4` = routing table
 
**Domain vocabulary:**
 
| Term | Meaning |
|---|---|
| WISMO | "Where is my order?" — highest-volume ticket type |
| P1–P4 | Priority levels; P1 = critical (1hr SLA), P4 = low (72hr SLA) |
| ops-l1 / ops-l2 | Human queue tiers; l2 is escalation (P1, enterprise, repeat contacts) |
| fraud-team | Specialized queue; any `fraud_flag=true` order routes here immediately |
| auto_resolve | Agent closes ticket with no human touch; re-validated in code by Action Executor |
| triage-review | Catch-all: confidence < 0.70, injection suspected, tool loop cap exceeded |
| cancellation_eligible | Boolean on order object; must be `true` before any cancel auto-action |
| fulfillment_started | Boolean; if `true`, cancellation must route to ops-l2, never auto-resolve |
 
**Auto-resolve allowlist** (6 permitted actions; executor re-validates preconditions in code after LLM decision):
 
| auto_action | Code-enforced precondition |
|---|---|
| `wismo_response` | `order.status is not None` AND customer not fraud-flagged |
| `send_tracking` | `order.tracking_number is not None` AND customer not fraud-flagged |
| `resend_confirmation` | Customer not fraud-flagged |
| `cancel_order` | `cancellation_eligible=true` AND `locked=false` AND customer not fraud-flagged |
| `merge_duplicate` | Always allowed |
| `kb_reply` | Always allowed |
 
**Routing table** (deterministic, first match wins — LLM suggestion is advisory only):
 
| Condition | Queue |
|---|---|
| `category=fraud` OR `order.fraud_flag=true` | `fraud-team` |
| `legal_complaint` flag present | `legal-compliance` |
| `injection_suspected` flag present | `triage-review` |
| `confidence < 0.70` | `triage-review` |
| `priority = P1` | `ops-l2` |
| `customer.open_tickets_48h > 1` | `ops-l2` |
| Cancellation + `fulfillment_started=true` | `ops-l2` |
| Return/refund + `order_total > $500` | `ops-l2` |
| Standard P2/P3 ops (wismo, faq, duplicate, cancellation, invoice) | `ops-l1` |
| Subscription | `ops-l1` |
| Anything else | `triage-review` |
 
**Prompt patterns that worked:**
- Reference by section: `"Implement the pre-flight filter from architecture.md §2.2"` — not re-describing the requirement
- State the constraint first: `"Constraint: the LLM cannot grant itself permission"` before describing the executor function
- "Pure function" framing: explicitly telling Claude a function must have no side effects and be independently testable caused it to suggest extracting `route()` on its own
- Spec translation: giving Claude the full routing table and asking it to encode it as code, not infer routing logic
 
**Known manual corrections made:**
- System prompt: added explicit rule that `submit_triage_decision` cannot be followed by any other tool call (first draft allowed post-submission tool calls)
- `executor_validate()`: confidence check was moved outside the per-action lambda to apply uniformly to all auto-actions
- Threshold resolved to 0.70 everywhere (mandate had 0.75 in one section and 0.70 in another; Claude flagged the conflict and asked before writing)
 
**Current state for day 2:**
- `agent.py`, `tools.py`, `main.py` are working with mock data
- `eval.py` has 22 test cases written but has not been run against the live agent
- All tool implementations in `tools.py` are mock — no live API calls
- To continue: run `eval.py`, fix failures in the system prompt or routing table (not by changing test expectations), then replace mock tool bodies with live OMS/CRM calls using the same return schemas