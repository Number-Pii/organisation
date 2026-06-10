# Number Pii Writing Standard

> **Binding contract, loaded on demand.** Versioned with `CLAUDE.md` (see its `_Version:` line).
> Before producing any substantial prose deliverable (documentation, specifications,
> architecture documents, reports, proposals, marketing copy, client communications,
> knowledge-base articles, plans, README files), you MUST read this file in full and
> apply it. It carries the same binding force as `CLAUDE.md`. The short rules in the
> Writing Style standard of `CLAUDE.md` always apply, even when this file is not loaded.
> Owner: Head of Content & SEO (`Teams/05-Growth-Marketing/Head-Content-SEO.md`).

## Core Directive

Produce writing that is indistinguishable from the work of a highly skilled human writer. Every piece must be natural, engaging, persuasive, professional, context-aware, and appropriate to its audience. If a sentence sounds like a language model wrote it, rewrite the sentence.

## Readability Standards

- Target a Flesch Reading Ease score of 30 to 40 for professional and technical audiences. For consumer-facing marketing copy, aim for 50 to 65. Check with `python3 scripts/check_writing.py <file>`.
- Vary sentence length deliberately. Follow a long, clause-heavy sentence with a short one. Short lands harder.
- Build natural rhythm and pacing; read the piece aloud (or simulate doing so) and fix anything you stumble over.
- Keep sentence logic tight: one idea per sentence, each sentence earning its place.
- Never open three sentences in a row the same way, and avoid leaning on any single opener across a document.

## Vocabulary Standards

- Use diverse vocabulary; if a notable word appears twice in two paragraphs, replace one occurrence.
- Avoid clichés and stock metaphors.
- Prefer precise verbs over adverb-propped weak ones: "sprint" beats "run very quickly".
- Cut filler: phrases that survive deletion without changing meaning should be deleted.
- Match terminology to the audience. Spell out concepts for general readers; use exact technical terms, without apology or padding, for expert readers.
- Use the words on the Use Sparingly list only when nothing more specific exists.

## Structural Standards

- Vary paragraph length. A one-sentence paragraph is a legitimate tool.
- Use lists only when they genuinely improve clarity (steps, options, reference data). Default to prose; never convert an argument into bullets.
- **No em dashes (—) and no en dashes (–).** Use commas, semicolons, colons, or periods. Write ranges with "to", or a plain hyphen in compact numeric ranges such as 1-3.
- Strongly favour active voice. Use passive voice only when the actor is genuinely unknown or irrelevant.
- Maintain a clear information hierarchy: the reader should be able to skim headings and topic sentences and still leave with the argument.

## AI Pattern Avoidance

### Banned phrases

These are hard failures. `scripts/check_writing.py` reads this list directly from the block below and flags any occurrence (case-insensitive). The Head of Content & SEO maintains the list; additions and removals go through a normal PR.

<!-- BANNED-PHRASES:START -->
- `delve`
- `dive into`
- `deep dive`
- `unpack`
- `leverage`
- `harness`
- `unlock`
- `unleash`
- `empower`
- `elevate`
- `supercharge`
- `seamless`
- `seamlessly`
- `robust`
- `cutting-edge`
- `state-of-the-art`
- `game-changer`
- `game-changing`
- `revolutionary`
- `groundbreaking`
- `transformative`
- `best-in-class`
- `world-class`
- `in today's fast-paced`
- `in today's digital age`
- `ever-evolving`
- `digital landscape`
- `the landscape of`
- `navigate the complexities`
- `it's important to note`
- `it is important to note`
- `it's worth noting`
- `it is worth noting`
- `needless to say`
- `it goes without saying`
- `in conclusion`
- `a testament to`
- `underscores the importance`
- `crucial role`
- `pivotal role`
- `holistic`
- `synergy`
- `paradigm shift`
- `low-hanging fruit`
- `move the needle`
- `utilize`
- `utilise`
- `in order to`
- `due to the fact that`
- `at the end of the day`
- `when it comes to`
- `the world of`
- `a wide range of`
- `a myriad of`
- `plethora`
- `look no further`
- `rest assured`
- `take it to the next level`
- `embark on a journey`
- `rich tapestry`
- `tapestry`
- `beacon`
- `in the realm of`
- `foster a`
- `boasts`
<!-- BANNED-PHRASES:END -->

### Use sparingly

Legitimate words that signal machine writing when they recur: comprehensive, furthermore, moreover, additionally, significantly, essentially, basically, simply, very, really, streamline, ensure. One use per document is fine; a pattern is not.

### Banned patterns

These need judgement rather than string matching. Reviewers check for them; the validator catches the mechanical cases.

- Generic introductions and conclusions: opening with a definition of the topic, closing with a summary that restates every section.
- Formulaic transition chains: paragraphs that each begin with a connective (Furthermore... Moreover... Additionally...).
- The "not just X, it's Y" construction and its variants.
- Rule-of-three overuse: three parallel items in sentence after sentence.
- Identical sentence openers in sequence (the validator fails three or more in a row).
- Excessive hedging: stacked qualifiers like "arguably", "perhaps", "to some extent" diluting every claim.
- Symmetric paragraphs: every paragraph the same length with the same internal shape.

## Document-Type Calibration

| Type | Audience | Tone | Flesch target | Review required |
|---|---|---|---|---|
| Technical (specs, architecture, runbooks) | Engineers | Precise, direct, no sales language | 30 to 40 | Lead engineer |
| Product (briefs, user stories, release notes) | Mixed internal | Plain, concrete, outcome-focused | 35 to 50 | PM or lead |
| Consultancy (reports, assessments, roadmaps) | Client executives | Authoritative, evidence-led, persuasive | 30 to 40 | Senior Content Strategist |
| Marketing (web copy, campaigns, social) | Prospects, general | Engaging, benefit-led, human | 50 to 65 | Senior Content Strategist |
| Internal (handover notes, memos, SOPs) | Team members | Brief, factual, skimmable | 35 to 55 | Self-check |

The same core directive applies to all five types; only tone, readability target, and review depth change.

## Governance

- **Ownership:** the Head of Content & SEO owns this standard, maintains the banned-phrases list, and arbitrates style questions.
- **Editorial review:** the Senior Content Strategist reviews client-facing and marketing deliverables before delivery, per the table above and the project's quality gates.
- **Approval:** the producing role self-checks first (validator plus a read-through against the Banned Patterns list). Department leads sign off per the project's `doc/workflow.md` gates. The founders hold final authority, as on everything.
- **Escalation:** a deliverable that fails validation or editorial review is blocked, returned to the producing role with the scorecard findings, fixed, and re-checked. Disputes about the standard itself go to the Head of Content & SEO, then the founders.

## Compliance Loop

1. Draft the deliverable with this standard loaded.
2. Run `python3 scripts/check_writing.py <file>`; fix every FAIL, weigh every WARN.
3. Re-read once against the Banned Patterns list; automation cannot catch all of them.
4. Pass the deliverable through the review level required by its document type and the project's classification level quality gates.
5. Record editorial sign-off in the department handover notes when the gates require it.

The validator's scorecard is the compliance measurement. Repeated failure patterns feed back into this file: when a new AI-signalling phrase shows up in rejected work, the Head of Content & SEO adds it to the banned list.

<!-- CACHE_BOUNDARY -->
