# Contributing to Wiki Knowledge Agent

Thanks for considering a contribution! This project is intentionally **small and lightweight** — please keep that spirit in mind.

## What this project is

A platform-independent agent skill that turns chat-pasted text/links into a verified, translated, searchable wiki knowledge base. Zero external dependencies (curl + Python stdlib), local-first alerts, and LLM-driven reasoning in the workflow steps.

## Ways to contribute

- **Report a bug** — open an issue with a minimal reproduction
- **Suggest a feature** — open an issue describing the use case (not just the feature)
- **Improve docs** — README, SKILL.md, references, Korean/English parity
- **Fix bugs / add tests** — PRs welcome

## Before opening a PR

1. Keep the **zero-dependency principle**: only `curl` + Python stdlib. No npm, no pip packages.
2. Keep it **light**: this skill refuses feature creep. If a change needs a lot of new code, it probably belongs in your agent's native capabilities instead.
3. SKILL.md is the agent-facing contract — changes to the workflow must update SKILL.md.
4. If you change scripts, run them:
   ```bash
   python3 scripts/ingest.py --verify https://example.com
   python3 scripts/ingest.py --alerts
   ```
5. Update README.md and README.ko.md together (they must stay in sync).

## Code style

- Python 3.9+, stdlib only
- Follow the existing style (simple, readable, minimal comments)
- No external service dependencies in the core scripts

## Questions

Open an issue — no need to ask permission first.
