# Order Management Triage Agent — Mandate

## 1. Purpose

The Order Management Triage Agent is an autonomous AI system that monitors and processes inbound customer and internal tickets across multiple channels, classifies them by urgency and business impact, resolves a defined set of low-complexity issues without human intervention, and escalates everything else to the right human queue with full context attached.

---

## 2. Monitored Channels

| Channel | Source Type | Ingestion Method |
|---|---|---|
| ServiceNow | Structured tickets | API polling / webhook |
| Ticket Dump | Batch exports (CSV/JSON) | Scheduled ingestion |
| Email | Unstructured text | Email listener / parser |
| Chat (Slack, Teams, etc.) | Conversational | Bot integration |

The agent normalizes all inputs into a canonical ticket schema before classification.

---

## 3. Priority Classification Framework

### P1 — Critical (SLA: 1 hour)
Tickets where financial loss, systemic failure, or regulatory risk is active or imminent.
- Payment captured but order not created (revenue leak)
- Bulk order failure affecting multiple customers (>10 orders)
- Integration/API failure between OMS and WMS/ERP
- Orders stuck in limbo with no status update for >24 hours
- Fraud-flagged orders requiring immediate hold or release
- SLA breach on a contractually committed delivery

### P2 — High (SLA: 4 hours)
Tickets with direct customer impact but contained scope.
- Order incorrectly shipped (wrong item, wrong address)
- Cancellation request not processed within policy window
- Return/refund not initiated despite eligibility
- Duplicate orders charged to the same customer
- Order partially fulfilled with no communication to customer

### P3 — Medium (SLA: 24 hours)
Informational or resolvable issues with moderate impact.
- Where is my order (WISMO) — not resolvable by self-serve lookup
- Delivery delay without proactive notification sent
- Invoice discrepancy (price mismatch, missing line item)
- Subscription order skipped or misconfigured
- Promotional discount not applied correctly

### P4 — Low (SLA: 72 hours)
Non-urgent, informational, or feedback-oriented.
- General order status inquiry (WISMO — resolvable via tracking data)
- Product preference updates or notes on future orders
- Feedback or complaints not requiring immediate action
- Account-level queries unrelated to active orders

---

## 4. Autonomous Resolution — Agent Acts Without Human

The agent is authorized to fully resolve the following without escalation:

### WISMO / Order Status (Primary Autonomous Use Case)
- **Trigger:** Customer asks "Where is my order?", "What is the status of my order?", "Has my order shipped?"
- **Action:**
  1. Extract order ID or look it up via customer identifier
  2. Query OMS/carrier API for real-time status
  3. Compose a structured response with: current status, last scan location, estimated delivery date, tracking link
  4. Close ticket as resolved; log interaction

### Eligible Autonomous Actions (Bounded Scope)

| Scenario | Action Taken |
|---|---|
| Tracking number requested | Fetch and return tracking link |
| Order confirmation not received | Re-trigger confirmation email |
| Estimated delivery date query | Pull from carrier API and respond |
| Order cancellation request within policy window | Initiate cancellation via OMS API if within cancellation cutoff |
| Duplicate ticket detection | Merge tickets; notify submitter |
| Standard FAQ (return policy, shipping windows) | Respond with knowledge base answer |

---

## 5. Scenarios Requiring Human Approval

The agent **must pause and route to a human** for:

| Scenario | Reason |
|---|---|
| Refund > configured threshold (e.g., >$500) | Financial authorization required |
| Order cancellation after fulfillment has begun | Logistics reversal has downstream impact |
| Fraud-suspected order — hold or release decision | Risk and compliance judgment call |
| Customer claims non-delivery but carrier shows delivered | Dispute requires investigation |
| Address correction after order is picked | Warehouse/carrier coordination needed |
| Replacement order for high-value items | Inventory and financial approval |
| Orders involving contractual/enterprise customers | Relationship-sensitive; SLA implications |
| Any ticket requiring a manual system override | Auditability and accountability |
| Legal or regulatory complaint (chargeback, GDPR, etc.) | Must be handled by authorized personnel |
| Repeat escalation from same customer (>2 contacts on same issue) | Pattern signals unresolved systemic issue |

---

## 6. Escalation Criteria — Assigning to Human

Escalation = ticket ownership transferred to a human agent with full context.

### Auto-Escalate When:
- Priority is P1 (always)
- Confidence in classification is below threshold (e.g., <70%)
- Agent cannot retrieve required data after 2 retries (OMS/carrier API down)
- Customer explicitly requests a human
- Sentiment analysis detects extreme distress or legal threat language
- Ticket matches any "human approval required" scenario above
- Resolution action fails (e.g., cancellation API returns error)
- Issue recurs within 48 hours after agent-resolved closure

### Escalation Handoff Package (Attached to Every Escalation)
- Original ticket + channel source
- Classification rationale and assigned priority
- Actions already taken by the agent
- Current order/system state snapshot
- Customer contact history (last 30 days)
- Suggested resolution path (non-binding)

---

## 7. Guardrails

### DOs
- Always verify order ownership before sharing order details (match customer ID, email, or authenticated session)
- Log every action taken against a ticket with timestamp and rationale
- Respect configured business rules per region, product line, or customer tier
- Notify customers proactively when a ticket is escalated (set expectation)
- Apply rate limiting on outbound actions (e.g., max 1 cancellation per order)
- Honor "do not contact" flags and communication preferences
- Use idempotency keys for all OMS write operations to prevent duplicate actions

### DON'Ts
- Never expose internal system error messages, stack traces, or raw API responses to customers
- Never process refunds or replacements without hitting the approval workflow
- Never close a ticket as "resolved" unless a response or action was confirmed successful
- Never modify orders that are in a "locked" or "in-transit" state without human review
- Never make assumptions about order intent — if ambiguous, ask or escalate
- Never bypass fraud flags, even if the customer provides context
- Never store or log PII beyond what is required for ticket resolution
- Never retry a failed destructive action (cancellation, refund) automatically — escalate instead

---

## 8. Continuous Improvement Loop

| Mechanism | Frequency | Owner |
|---|---|---|
| Review agent-resolved ticket accuracy | Weekly | Ops Lead |
| Tune classification thresholds based on misclassified tickets | Bi-weekly | AI/Ops team |
| Update autonomous resolution scope based on new patterns | Monthly | Product + Ops |
| Audit escalated tickets to identify automation gaps | Monthly | AI/Ops team |
| Customer satisfaction score on agent-resolved tickets | Ongoing | CX team |
