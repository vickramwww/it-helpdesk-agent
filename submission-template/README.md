# Order Management IT Helpdesk Triage Agent
 
**Built in ~50 minutes using Claude Code**
 
---
 
## 1. What We Built
 
An autonomous triage agent for an e-commerce Order Management IT helpdesk. The agent ingests inbound tickets from ServiceNow, email, chat, and batch exports; normalizes them into a canonical schema; classifies by category and priority (P1–P4); and either resolves the ticket autonomously or routes it to the correct human queue with full context attached. It handles WISMO lookups, FAQ replies, eligible cancellations, and duplicate merges without human touch. Everything else — fraud holds, high-value refunds, post-fulfillment cancellations, legal threats, enterprise accounts — routes to a human.
 
---
 
## 2. Challenge Status
 
| Block | Status | Notes |
|---|---|---|
| **1 — Define Mandate** | Complete | `mandate.md` — full priority framework (P1–P4), autonomous action list, escalation table, hard guardrails |
| **2 — Design Architecture** | Complete | `architecture.md` — full Mermaid system diagram, component specs, routing table, pre-flight filters, action executor |
| **3 — Build Triage Logic** | Complete | `agent.py` — agentic loop with tool use, pre-flight filter, deterministic router, allowlist executor, system prompt encodes all mandate rules |
| **4 — Add Custom Tools** | Complete | `tools.py` — `knowledge_lookup`, `order_lookup`, `check_customer`, `submit_triage_decision` with mock data; `main.py` runs 8 representative demo tickets |
| **5 — Build Eval Set** | Complete | `eval.py` — 22 test cases spanning P1–P4, auto-resolve paths, hard guardrails, and adversarial inputs; per-dimension scoring across 6 metrics |
 
---
 
## 3. Architecture Overview
 
```
Inbound (ServiceNow · Email · Chat · Ticket Dump)
  │
  ▼
Intake Adapter — normalizes all sources to canonical Ticket schema
  │
  ▼
Pre-flight Filters (pure Python, no LLM)
  — PII / size cap (8192 char truncation)
  — Injection pattern detection (regex)
  — Legal threat keyword scan
  — Distress signal flag
  │
  ├─ Hard fail (injection confirmed) ──────────────────▶ triage-review
  │
  ▼
Triage Agent (Claude claude-3-7-sonnet via AWS Bedrock)
  — Agentic loop, up to 5 tool rounds
  — Calls: knowledge_lookup / order_lookup / check_customer
  — Terminates with exactly one: submit_triage_decision
  │
  ├─ action = auto_resolve ──▶ Action Executor (re-validates allowlist in code)
  │                                    │
  │                                    ├─ Allowed ──▶ Act + Audit Log
  │                                    └─ Blocked ──▶ Route to ops-l1 + Audit Log
  │
  └─ action = route ─────────▶ Deterministic Router (category + priority + flags)
                                        │
                          ┌─────────────┼──────────────────┐──────────────┐
                          ▼             ▼                  ▼              ▼
                       ops-l1        ops-l2          fraud-team   legal-compliance
                    (P3/P4 ops)   (P1, enterprise,  (fraud_flag)  (legal/GDPR)
                                   repeat esc.)
                                        │
                                   triage-review
                                (low confidence,
                                 injection suspected)
```
 
**Queues:**
- `ops-l1` — Standard P2/P3 ops: wrong shipments, invoice issues, standard cancellations, subscriptions
- `ops-l2` — P1 critical and escalations: bulk failures, integration outages, enterprise accounts, repeat contacts
- `fraud-team` — Any order with `fraud_flag=true`
- `legal-compliance` — Legal threats, chargebacks, GDPR mentions
- `triage-review` — Low confidence (<0.70), injection suspected, tool loop exhausted
 
---
 
## 4. Tools Built
 
| Tool | What It Does | Preconditions / Guardrails |
|---|---|---|
| `knowledge_lookup` | Keyword + similarity search over FAQ/policy articles; returns top 3 matches with relevance scores | None — safe read; no side effects |
| `order_lookup` | Fetches order status, tracking number, carrier, fulfillment state, fraud flag, and order total from OMS | Requires `order_id` + `customer_id`; verifies customer ownership before returning data — returns `security_flag` on mismatch |
| `check_customer` | Returns customer tier, fraud flag, open ticket count in last 48h, and recent issue categories | None — read-only; used to detect repeat escalation and enterprise status |
| `submit_triage_decision` | Structured terminal output: category, priority, confidence, action, auto_action, route_to, guardrail_triggered, reasoning, customer_response | Must be called exactly once; LLM cannot call any tool after it; Action Executor re-validates all `auto_resolve` decisions against code-level allowlist |
 
**Action Executor allowlist** (what `auto_resolve` permits, validated in code after LLM decision):
 
| auto_action | Precondition checked in code |
|---|---|
| `wismo_response` | Order status is not null AND customer not fraud-flagged |
| `send_tracking` | Tracking number present AND customer not fraud-flagged |
| `resend_confirmation` | Customer not fraud-flagged |
| `cancel_order` | `cancellation_eligible=true` AND `locked=false` AND customer not fraud-flagged |
| `merge_duplicate` | Always allowed |
| `kb_reply` | Always allowed |
 
---
 
## 5. Key Decisions
 
- **Pre-flight filters run before the LLM, in plain Python.** Injection detection, legal keyword scanning, and size capping happen deterministically upstream. The alternative — giving the agent a `check_injection` tool — was rejected because ticket content could potentially influence the LLM's decision to call it. Code-level rules can't be argued past.
 
- **The Action Executor re-validates allowlist preconditions after the LLM decision.** The LLM does not have final authority on whether an auto-resolve is permitted. The executor re-checks `cancellation_eligible`, `locked`, `fraud_flag`, and confidence floor in code. This means a hallucinated or manipulated `auto_action` cannot slip through.
 
- **`order_lookup` and `check_customer` are separate tools.** The agent only pulls customer history when it needs it (e.g., repeat escalation pattern check). On a simple WISMO ticket, customer history is never fetched. This limits data exposure on low-risk tickets.
 
- **The router is deterministic, not LLM-driven.** Given `(category, priority, flags, order_state, customer_tier)`, the routing table produces a queue with no LLM involvement. The LLM's suggested `route_to` is advisory; the executor uses the deterministic table. This makes routing auditable and testable independently of model behavior.
 
- **Confidence floor at 0.70.** Below that threshold, the agent routes to `triage-review` regardless of its category/priority assignment. The tradeoff: more tickets to `triage-review` than strictly necessary, but no auto-resolves on uncertain classifications. Given that auto-resolve has real-world side effects (cancellations, confirmations), we accepted the false-positive escalation rate.
 
---
 
## 6. Guardrails & Escalation Logic
 
**The agent will never autonomously:**
- Issue or authorize any refund — it can only route to a human
- Cancel an order if fulfillment has started or the order is locked
- Take any action on a fraud-flagged order or customer
- Act on a ticket from an enterprise-tier customer
- Take action when `confidence < 0.70`
- Close, resolve, or modify a P1 ticket
- Respond to a ticket flagged as a legal complaint, chargeback, or GDPR request
- Take action on a ticket containing prompt injection patterns — route to `triage-review` immediately
 
**Specific escalation triggers (first match wins in the routing table):**
 
| Condition | Queue |
|---|---|
| `category=fraud` OR `order.fraud_flag=true` | `fraud-team` |
| `legal_complaint` flag present | `legal-compliance` |
| `injection_suspected` flag present | `triage-review` |
| `confidence < 0.70` | `triage-review` |
| `priority = P1` | `ops-l2` |
| `customer.open_tickets_48h > 1` | `ops-l2` (repeat escalation signal) |
| Cancellation requested + `fulfillment_started=true` | `ops-l2` |
| Return/refund + `order_total > $500` | `ops-l2` |
| Standard P2/P3 ops categories | `ops-l1` |
| Anything else | `triage-review` |
 
Every decision — including auto-resolves — writes a structured audit log with ticket ID, classification, confidence, action taken, tools called, guardrails triggered, and reasoning. This log is intended to be the record Legal reads.
 
---
 
## 7. How We Used Claude Code
 
**Context engineering came first.** We wrote `mandate.md` and `architecture.md` as the first two artifacts — not as documentation but as source of truth that Claude Code would reference throughout. This meant every subsequent prompt could be grounded: "implement the routing table from architecture.md §4" rather than re-explaining domain logic each time.
 
**Specific examples of what worked:**
 
- *"Implement the pre-flight filter from architecture.md §2.2 — it must run before any LLM call, pure Python, no tools."* — Claude correctly scoped it as deterministic code and matched the injection patterns to the guardrails in the mandate.
 
- *"Write the system prompt encoding all priority, category, autonomous action, and guardrail rules from mandate.md. The agent must call submit_triage_decision exactly once as its terminal action."* — The resulting system prompt is dense and structured; Claude flagged a conflict between two guardrail conditions and proposed a resolution before writing it.
 
- *"Add executor_validate() — it re-checks allowlist preconditions in code after the LLM returns auto_resolve. The LLM's decision is not final."* — Claude immediately understood the security motivation and implemented the lambda-based allowlist pattern correctly.
 
- *"Write eval.py with 22 test cases covering the full priority matrix, all autonomous paths, all hard guardrails, and adversarial inputs. Score on 6 dimensions."* — Generated a complete harness with dataclass-based test models and per-dimension scoring in one pass.
 
**What surprised us:** Claude Code proactively pointed out that splitting the routing logic into a pure function (`route()`) would make it independently testable without running the full agentic loop — a structural improvement we hadn't asked for but immediately adopted. It also caught that the original system prompt used inconsistent threshold values (0.70 vs 0.75) between the routing rule and the guardrail section, and asked which was authoritative before writing.
 
---
 
## 8. What We'd Do With More Time
 
- **Live integrations.** All tools are mock implementations. Real `order_lookup` and `check_customer` would connect to an actual OMS and CRM API. The schemas are already defined.
 
- **Run the eval harness and iterate.** `eval.py` is written but untested against the live agent on all 22 cases. We'd run it, find the failures, and tighten the system prompt or routing table accordingly.
 
- **Channel-specific normalization.** The intake adapter currently assumes clean structured input. Email parsing (headers, quoted replies, attachment detection) and ServiceNow webhook normalization are not implemented.
 
- **Confidence calibration.** The 0.70 threshold was set by judgment. With eval results we'd tune it per-category — fraud and legal probably warrant a higher floor; simple WISMO queries could tolerate lower.
 
- **Human-in-the-loop feedback loop.** The audit log feeds a weekly digest placeholder. We'd build an actual feedback loop where human queue decisions (overrides, corrections) flow back to improve routing accuracy over time.
 
- **Rate limiting and queue backpressure.** No throttling exists on the agentic loop. Under load, uncontrolled parallelism could exhaust Bedrock quota or cascade tool failures.