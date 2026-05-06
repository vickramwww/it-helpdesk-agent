# Judging Prompt for Proctors

Use this prompt to have Claude evaluate team submissions. Feed it all team submissions at once for comparative ranking.

---

## The Prompt

```
You are the judge for a Claude Code competition. Teams had 70 minutes to pick a scenario (Code Modernization, Data & Analytics, or Agentic Solution) and complete as many of 5 progressive challenges as possible using Claude Code.

Each team submitted 3 files:
- README.md — describes what they built, challenge status, decisions, and how they used Claude Code
- CLAUDE.md — the context file they used to teach Claude about their project
- presentation.html — a self-contained HTML summary

Evaluate each team across these 5 categories on a 1-10 scale with justification:

1. **Most Production-Ready (1-10)**: Could this be handed to an ops team? Look for: runbooks, error handling, tests, realistic architecture, deployment thinking.

2. **Best Architecture (1-10)**: Are the design decisions clear and well-reasoned? Look for: decomposition thinking, service boundaries, data ownership, trade-off analysis.

3. **Best Claude Code Usage (1-10)**: Did they use Claude Code effectively? Look for: quality of CLAUDE.md (specific conventions, domain context, evolving instructions), creative tool use, evidence of iterative prompting.

4. **Most Complete (1-10)**: How far did they get through the 5 challenges with quality intact? Partial but honest > complete but shallow.

5. **Best Presentation (1-10)**: Does the presentation.html tell a clear story? Can you understand what they built without reading the code?

For each team, provide:
- Scores (1-10) for each category
- A 2-sentence summary of their strongest quality
- One thing they could improve

Then rank all teams by total score and declare:
- Overall Winner (highest total)
- Category winners (best in each of the 5 categories)

Here are the submissions:

[PASTE TEAM SUBMISSIONS HERE]
```

---

## How to Use

1. When time is called, collect all team zip files
2. Unzip each one
3. Copy the contents of each team's README.md, CLAUDE.md, and presentation.html
4. Paste them all into Claude (claude.ai or Claude Code) with the prompt above
5. Claude will score and rank the teams
6. Announce the winners

**Tip:** If there are more than 5 teams, you may need to batch them (Claude can handle a lot of context, but very large submissions may need splitting).
