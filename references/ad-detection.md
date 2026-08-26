# Ad vs Useful — classification guide

The LLM classifies pasted content before saving. This guide is the reference.
Goal: never lose useful information; never store pure ads as if they were knowledge.

## Decision rule

**📢 Ad** if ALL/MOST of:
- Self-promotion is the *core intent* — the piece exists to sell one product/account/service
- "Try it", "Get started free", "DM me", pricing pitch dominates
- Link-dump: a bare URL or one-line link with zero transferable substance
- Vague superlatives ("revolutionary", "game-changing", "the only tool you need")
- No methodology, no data, no reusable steps

**📚 Useful** if ANY of:
- Real methodology / workflow / checklist that transfers to other work
- Concrete data, numbers, benchmarks, comparisons
- A tool is described *with* how to use it and when it beats alternatives
- Policy/regulatory/technical facts (even if the source is a vendor)
- Honest trade-off analysis

**⚖️ Boundary cases** (save with label + provenance):
- Vendor deep-dive with real specs → save, label `useful (vendor source)`
- A tool article that ends with a soft pitch → save the substance, note "ends with promo"
- Marketing comparison table with accurate data → save the data, flag the bias

## Worked examples (2026-08, verified)

| Input | Call | Reason |
|---|---|---|
| Scrnsht Studio "7 principles of App Store screenshots" (ends "we'd love to hear from you") | 📚 useful | 7 principles are transferable methodology; the promo is only the closing |
| "everank.com — try our app ranking tool" (no substance) | 📢 ad | Link-dump, self-promotion core |
| Distribb "SAM.gov registration in 6 steps" (tool ad disguised as guide) | 📢 ad | Core intent = sell the tool; steps are filler |
| Fastic "Nutri ChatBot AI + quiz personalization" (competitor feature page) | 📚 useful | Real feature/positioning data for competitive research |
| "X API now credit-based, Owned Reads $0.001/resource" (official docs) | 📚 useful | Verifiable pricing fact for planning |

## Handling

- Ads: do NOT auto-delete. Save the note with `classification: ad` + one-line reason, or skip if zero insight.
- Useful: save with `classification: useful`, include source_url + channel.
- Unverifiable: label `unverified` and mark confidence in the note.
- Personal info / secrets in pasted content: strip identifiers before saving.
