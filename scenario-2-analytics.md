# Scenario 2 — Data & Analytics

## "The Dashboard Nobody Trusts"

Somewhere in the business there are 40 dashboards across three BI tools. Executives make decisions by gut because the numbers never match. One metric — the one everyone says is *the* metric — is calculated four different ways depending on who you ask. A new VP wants one number, one definition, defended in a room full of people who each think their version is right.

You have **50 minutes** to define the metric precisely, build the single source of truth, and create a unified dashboard. You pick the domain, the metric, the stack, and how deep into data science you want to go. The only rule: the disagreement has to be *plausible* — pick a metric where reasonable people could genuinely calculate it differently.

---

## Pick Your Domain (or invent your own)

| Domain | The contested metric | Why nobody agrees |
|---|---|---|
| **Manufacturing** | OEE (Overall Equipment Effectiveness) | Does planned maintenance count as downtime? Startup scrap? |
| **SaaS / subscription** | Churn | Logo vs. revenue churn. Does a downgrade count? When does the clock start? |
| **E-commerce / retail** | Customer Lifetime Value | Which margin? Which discount rate? Cohort vs. predictive? |
| **Logistics / delivery** | On-Time Delivery | Promised date vs. revised date. Partial shipments. Whose clock? |
| **Fintech / lending** | Default rate | 30/60/90 days past due? Principal only? After recoveries? |
| **Healthcare ops** | Bed utilization | Midnight census vs. hourly. Does observation count? |
| **Ad tech / media** | Attribution / conversion | Last-touch vs. multi-touch. Which lookback window? |

---

## The 5 Challenges

With 50 minutes, aim for 3 done well. Go dashboard-heavy or go model-heavy — your call.

### Challenge 1: The Definition (10 min)
*(Architect role)* Define the metric once. Document every assumption, every edge case, every "what counts." This is your semantic layer's first citizen. Also document 3 common ways organizations calculate it wrong.

**Prompt idea:** *"Help me write a precise metric definition for [metric] in [domain]. Include the exact formula, inclusion/exclusion rules, time window, edge cases (partial periods, refunds, transfers), and document 3 common miscalculations."*

### Challenge 2: The Mess (10 min)
*(Data Engineer role)* Generate plausible raw data. Include realistic noise: gaps, mislabeled categories, that one source system reporting in the wrong timezone. The ugliness is the point.

**Prompt idea:** *"Generate a realistic [domain] dataset in CSV format. At least 500 rows with timestamps, categories, amounts, statuses. Add realistic noise — missing values, edge cases (partial refunds, status changes), records that different metric definitions would treat differently."*

### Challenge 3: The Engine (10 min)
*(Developer role)* Build the metric calculation. As code, with testable functions. Not a SQL view buried in a BI tool. It should handle all the edge cases from Challenge 1.

**Prompt idea:** *"Build a Python script that calculates [metric] from the generated data. Handle all edge cases from our definition. Log any records it can't classify. Output the result with breakdown by [category]."*

### Challenge 4: The One (15 min)
*(Developer role)* One dashboard that replaces the 40. Working HTML prototype with charts. Drill-down from top-level to the thing an operator actually fixes.

**Prompt idea:** *"Create a self-contained HTML dashboard showing our [metric] results. Include: headline number, trend over time (chart), breakdown by [category], and a section showing how our calculation differs from the 'wrong' versions. Use Chart.js from CDN. Dark theme."*

### Challenge 5: The Watchdog (5 min)
*(Data Science role)* Anomaly detection. When the metric moves in a way that's statistically weird, flag it before someone asks.

**Prompt idea:** *"Add anomaly detection to our metric calculation. Flag when the metric moves >2 standard deviations from a 30-day rolling average. Add flagged periods to the dashboard with explanations."*

---

## Tips
- **The definition (Challenge 1) is the foundation** — spend time getting it right. Everything else builds on it.
- Show the "wrong" calculations alongside yours — that's what wins the room
- The dashboard is your presentation piece — make it look professional
- If you have data scientists on the team, go deep on anomaly detection
