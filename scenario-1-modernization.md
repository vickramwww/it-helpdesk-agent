# Scenario 1 — Code Modernization

## "The Monolith"

It works — mostly — but the people who built it are gone, the docs are a folder of outdated Word files, and the board just approved "modernization" without defining what that means.

You have **50 minutes** to prove modernization is possible without a big-bang rewrite. You pick the language, the era, the architecture, the decomposition strategy. The only rule: generate something ugly enough that fixing it is interesting.

---

## Pick Your Legacy (or invent your own)

| Flavor | What Claude generates for you |
|---|---|
| **PHP 5 monolith** | `index.php`, SQL strings concatenated inline, sessions in globals |
| **Enterprise Java 2010** | Spring XML config, `AbstractSingletonProxyFactoryBean`, WAR on WebLogic |
| **Stored-proc architecture** | 40 T-SQL procs that *are* the business logic, app is a thin shell |
| **Early Node callback hell** | Express 3, callbacks 6 deep, logic in Mongoose pre-save hooks |
| **Rails 2 majestic monolith** | Fat models, `lib/` doing unspeakable things, cron + rake jobs |
| **Python Django all-in-one** | One `views.py` with 3000 lines, raw SQL, no tests, circular imports |

**Pick a domain** (or invent one):
- E-commerce platform (orders, inventory, payments, users)
- Hospital management (patients, appointments, billing, pharmacy)
- University portal (courses, grades, enrollment, faculty)
- Fleet management (vehicles, drivers, routes, maintenance)

**Modernize toward:** Strangler fig, containerize-and-ship, event-driven, API facade, serverless extraction, DB-first split. Your call.

---

## The 5 Challenges

With 50 minutes, aim for 3 done well. Nobody finishes all five — that's the point.

### Challenge 1: The Stories (10 min)
*(PM role)* Write 5-8 user stories for the three most important business capabilities in this system. You decide what they are. Acceptance criteria that a tester could actually execute.

**Prompt idea:** *"Help me write user stories for modernizing a [domain] monolith. Each story should have a title, description, and acceptance criteria."*

### Challenge 2: The Patient (10 min)
*(Architect role)* Generate the legacy monolith. 4-6 modules, shared database, at least two circular dependencies, one God class. Make it realistic — including the parts that make you wince.

**Prompt idea:** *"Generate a realistic legacy [language] [domain] monolith. 4-6 modules that share state, a single database, tight coupling, some technical debt — hardcoded values, no tests, inconsistent naming. Make it ugly enough to be interesting."*

### Challenge 3: The Map (10 min)
*(Architect role)* Produce a decomposition plan. Name the seams. Rank the services by extraction risk. Show the dependency graph.

**Prompt idea:** *"Analyze this monolith and create a service decomposition plan. Identify bounded contexts, data ownership, and the safest extraction order. Use [strangler fig / your strategy]."*

### Challenge 4: The Cut (15 min)
*(Developer role)* Extract your first service. Clean API contract. The monolith still works with the service extracted. Prove both.

**Prompt idea:** *"Extract the [chosen module] into a standalone service with a REST API. Add tests. The monolith should call the new service's API instead of the old internal module."*

### Challenge 5: The Weekend (5 min)
*(Ops role)* Write the cutover runbook. Steps, rollback triggers, the 3am decision tree. The one ops will actually follow.

**Prompt idea:** *"Write a production cutover runbook for migrating from the monolith's [module] to the new service. Include health checks, traffic shifting, monitoring, and rollback procedures."*

---

## Tips
- **Start your CLAUDE.md** with the domain, language, era, and your modernization strategy
- Don't try to build a perfect microservice — show the *thinking* behind the decomposition
- The runbook is where you show production-readiness
- The uglier the legacy code, the more impressive the modernization
