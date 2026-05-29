# PLANSO - Junior AI Engineer - Take-Home Assignment

## Overview

intelli-site is Planso's site analysis product for architects and AEC professionals. At its core, it answers questions about specific sites — grounded in real data — so that a professional can make better decisions faster.

This take-home asks you to build a small version of that core. You are given a corpus of real data and asked to build a system that answers questions about specific sites, grounded in that data.

**Time budget:** We expect this to take roughly two days of focused work. Please don't spend more than that — an honest, well-reasoned partial submission is more useful to us than an over-engineered one.

---

## The Corpus

You are given two types of data in the `corpus/` directory.

### Prose documents (`corpus/zoning/`)

Ten excerpts from the **NYC Zoning Resolution** — the actual legal text governing land use and building bulk in New York City. These are publicly available municipal documents published by the NYC Department of City Planning.

Each document covers a specific regulation: floor area ratios, yard requirements, permitted obstructions, environmental designations, and rules of interpretation. Read them. They are the kind of text intelli-site has to reason over.

You will notice that:
- Some documents cross-reference other documents (e.g. "except as provided in Section 23-341"). Those referenced documents may or may not be present in the corpus.
- Some documents carry a vintage label. Pay attention to these.
- The corpus does not cover every possible question an architect might ask. That is intentional.

### Structured data (`corpus/structured/site_records.csv`)

Five site records, one row per BBL (Borough-Block-Lot — the unique identifier for NYC properties). Each record contains the site's zoning district, flood zone designation, (E) designation status, and demographic data for the surrounding census tract.

A copy of **NYC MapPLUTO (v25v4)** is also included at `corpus/structured/pluto_25v4.csv`. It covers all NYC tax lots with zoning, building, and lot attributes and can be used to enrich site lookups. The five test BBLs are fully defined in `site_records.csv` — MapPLUTO is supplementary.

---

## The Task

Build a system that takes two inputs:
1. A **BBL** identifying which site is being queried (from the structured data)
2. A **natural language question** about that site

And produces a response that is **grounded in the corpus**.

Examples of the kinds of questions the system should handle:

- *"What is the maximum floor area ratio for this site?"*
- *"Is a rear yard required, and how deep must it be?"*
- *"Can I place an air conditioning unit in the rear yard?"*
- *"Does this site have any environmental flags I should know about?"*
- *"What is the population density of the surrounding area?"*
- *"What was the maximum floor area ratio for this site's zoning district five years ago?"*

These are not the exact test questions. They are illustrative of the range and type.

---

## What We Care About

**Grounding and honesty over speed.** The system should:
- Cite which document or data field it is drawing from
- Refuse to answer — clearly and specifically — when the corpus does not support an answer
- Surface conflicts or vintage issues when they are relevant to the answer
- Distinguish between "the corpus doesn't cover this" and "the answer is clearly X"

**Retrieval quality.** How you chunk, embed, index, and retrieve the prose documents matters. You will be asked to defend every decision you made.

**The routing decision.** Some questions are best answered by the structured data. Some require reasoning over prose. Some require both. The system should handle this correctly — or at minimum, you should be able to explain exactly where and why it falls short.

We deliberately have not specified:
- How to chunk the documents
- What embedding model to use
- What retrieval method to use
- What the similarity threshold should be
- What the output format should be
- Whether to use an agent loop, a single retrieve-then-reason pass, or something else

These are your decisions. Make them and defend them.

---

## Deliverables

**1. Working code**

A runnable system. A CLI or a thin API is fine — no frontend required.

Your `README.md` (this file will be replaced by your own) must contain:
- How to install and run
- How to run your own eval (see below)
- Any environment variables required (API keys etc.)

Use whatever stack you are comfortable with. Python is preferred given our backend, but not required.

**One non-negotiable output requirement:** for every query, the system must log or return which documents it retrieved and their similarity scores, alongside the final answer. Format is up to you — a structured JSON field, a printed trace, anything readable. This is not optional. A system we cannot inspect is a system we cannot trust, and retrieval transparency is part of the job.

**2. A reasoning document** (`reasoning.md`)

One to two pages covering:

- **Chunking strategy** — how did you split the documents, and why? What did you consider and reject?
- **Retrieval design** — what method did you use (dense, sparse, hybrid)? What threshold or cutoff did you use, and how did you choose it?
- **Routing logic** — how does the system decide whether a question should go to the structured data, the prose retrieval, or both?
- **Failure handling** — how does the system behave when retrieval fails or the corpus has no answer? What does "I don't know" look like in your system?
- **What you would build next** — if you had one more week, what is the single most important thing you would fix or add, and why?

The reasoning document is as important as the code. We will read it before we look at the code.

**3. An eval script** (`eval.py` or equivalent)

A script that runs a set of test cases against your system and reports a score or structured output. Your eval must include:
- At least 8 question/expected-behavior pairs
- At least 2 cases where the correct answer is "the corpus does not support this question" (abstention)
- At least 1 case involving a vintage or version conflict
- At least 1 case where the answer requires following a cross-reference between documents

The eval doesn't need to be perfect — but it needs to test the hard behaviors, not just easy lookups. We will run your eval script ourselves.

---

## Submission

Send a zip of the repository (or a GitHub link) to careers@planso.co within 48 hours of receiving this brief.

Include your `reasoning.md` at the root of the repo.

---

## A Note on Honesty

The product we are building is used by professionals making real decisions about real buildings. When intelli-site does not know something, it should say so — clearly, specifically, and in a way that points the professional toward where to look next. A confident wrong answer is worse than no answer.

That principle should be visible in the system you build.

---

*Questions about the assignment to be emailed to careers@planso.co.*
