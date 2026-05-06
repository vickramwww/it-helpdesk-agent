# Scenario 3 — Agentic Solution

## "The Intake"

Somewhere in the business, inbound is drowning a human. Requests arrive through four different channels, get hand-triaged into a dozen internal teams, and the average time-to-first-response is measured in hours that nobody is proud of. Someone senior wants an agent. Someone in Legal wants to know what could possibly go wrong. Both are right.

You have **50 minutes** to build an intelligent triage agent. You pick the domain, the tools, the guardrails. The only constraint: the agent has to make a *real decision* — classify something, route it somewhere, take an action — not just chat.

**This scenario connects directly to Session 3** — you're building the same tool_use / agentic loop pattern, but for a real problem.

---

## Pick Your Intake (or invent your own)

| Domain | What's flooding in | What the agent decides |
|---|---|---|
| **Professional services** | Emails, Slack, web forms, one partner who still faxes | Which of 12 internal teams owns this |
| **IT helpdesk** | Tickets, chat, "urgent" emails to the CIO | P1 vs. P4, which queue, auto-resolve the password resets |
| **Insurance claims** | PDFs, photos, voicemail transcripts | Fast-track, investigate, or deny — and why |
| **Code review** | PRs across 30 repos | Auto-approve the trivials, flag the scary ones, assign a human |
| **Compliance / KYC** | Onboarding docs, sanctions-list hits | Clear, escalate, or request-more-info |
| **Sales lead routing** | Form fills, inbound email, conference badge scans | Which rep, which tier, is this even real |

---

## The 5 Challenges

With 50 minutes, aim for 3 done well. The mandate and architecture are as important as the code.

### Challenge 1: The Mandate (10 min)
*(PM role)* Define the agent's job. What it decides alone. What it escalates. What it must never touch. One page. Legal reads this.

**Prompt idea:** *"Help me define the mandate for a [domain] triage agent. Include: what it can decide autonomously, what requires human approval, explicit guardrails (what it must NEVER do), and escalation criteria with specific triggers."*

### Challenge 2: The Bones (10 min)
*(Architect role)* Agent architecture. Tools, state, guardrails. A diagram someone can argue with. How does routing work? Where does context come from?

**Prompt idea:** *"Design the architecture for our triage agent. Define: the tools it needs (with input/output schemas), the routing logic, the escalation flow, and how it stores/retrieves context. Create an architecture diagram."*

### Challenge 3: The Triage (15 min)
*(Developer role)* Build the core agent using the Claude API (via AWS Bedrock). Ingest a request, classify it, enrich it with context, route it. Log the reasoning — not just the answer.

**Prompt idea:** *"Build a Python triage agent using AnthropicBedrock. It should: accept a request as input, classify it into our categories, decide whether to handle automatically or escalate, and return a structured response with classification, confidence, recommended action, and reasoning."*

### Challenge 4: The Hands (10 min)
*(Developer role)* Give it tools. At minimum: a knowledge lookup and a system-of-record check. The agent decides when to use them.

**Prompt idea:** *"Add two tools to our triage agent: 1) knowledge_lookup — searches a FAQ (create mock FAQ data for our domain), and 2) check_status — looks up a record in our system (create mock data). The agent should use these when classifying and routing."*

### Challenge 5: The Test (5 min)
*(Tester role)* Build an eval set with 10+ test cases. Happy paths, edge cases, and adversarial cases (requests that try to bypass guardrails).

**Prompt idea:** *"Create an automated eval harness for our triage agent with 10+ test cases. Include: happy paths (clear classification), edge cases (ambiguous requests), adversarial cases (attempts to bypass guardrails). Check classification accuracy, routing, and guardrail compliance. Print a scorecard."*

---

## Tips
- **The mandate (Challenge 1) is what separates a demo from a product** — take it seriously
- Use CLAUDE.md to teach Claude your domain's terminology and routing rules
- The eval set (Challenge 5) is where you show quality thinking — edge cases matter more than happy paths
- Log the agent's reasoning, not just its decisions — judges want to see the thinking
- If you have time, show what happens when the agent encounters something outside its mandate
