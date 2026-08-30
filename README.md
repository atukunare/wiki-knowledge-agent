# Wiki Knowledge Agent

**🌐 [한국어 문서 (Korean README)](README.ko.md)**

> ## 🧠 Your AI forgets. A wiki doesn't.
>
> **Wiki Knowledge Agent** turns chat-pasted text and links into a **verified, translated, searchable** wiki knowledge base — a persistent brain for any agent. Works on Claude Code, Codex, Cursor, and Hermes with **zero external dependencies**.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Zero deps](https://img.shields.io/badge/dependencies-zero-orange.svg)]()

---

## Why this exists

You paste a link into chat and expect your AI to remember it. **Agents forget — wikis don't.**

OpenHuman and other big harnesses build entire apps to solve this. This skill solves the *essential* part in ~50KB: a repeatable procedure any agent can follow, on any platform, with nothing to install beyond `curl` + Python.

## What it does — 3 moves

| | Move | What happens |
|---|------|--------------|
| 🔎 | **Verify** | Links are checked on arrival (HTTP status, redirects). Ads are separated from genuinely useful content. |
| 🌐 | **Remember** | Content is translated & summarized into your language, then saved to your wiki as a distilled note. |
| 🔔 | **Nudge** | Time-sensitive items (security, expiry, project risk) land in a local alert queue — plus it offers to remind you before holidays, birthdays, and deadlines. |

## Demo — a real flow

```
You:  "save this Chuseok gift list for me"  (paste a gift-guide link)

Agent (before saving):
  📌 This looks useful for our project — you can use it as material for social content.
  📅 Chuseok (9/29) is less than a month away, would you like me to remind you a week before?
You:  "sure"

Result:
  ✅ Saved to wiki/knowledge/inbox/2026-08-26-chuseok-gifts.md
  📅 Reminder registered — your agent (or its native scheduler) nudges you on 9/22
```

The save never waits on the feedback — the note is stored instantly, the offer is a bonus.

## Why zero dependencies matters

- **No npm install, no pip install, no SaaS account.** Just clone, copy the folder, and run one onboarding command.
- Works with a **single model** or a fleet of agents — no multi-agent setup required.
- Alerts are **local-first**: no webhook, no email app? You still get the alert in your chat. Add Slack/Discord/Telegram/ntfy later, anytime.

## Quickstart

```bash
# 1. Clone
git clone https://github.com/atukunare/wiki-knowledge-agent.git

# 2. Onboarding (4 questions, defaults are fine)
cd wiki-knowledge-agent
python3 scripts/onboarding.py

# 3. Use it — paste any link/text into chat and say "save this"
```

### Install per agent (skill folder locations)

| Agent | Install location | Notes |
|-------|------------------|-------|
| **Claude Code** | `~/.claude/skills/wiki-knowledge-agent/` | Auto-detected on session start |
| **Hermes** | `~/.hermes/profiles/<profile>/skills/note-taking/wiki-knowledge-agent/` | Recognized from the *next* session |
| **Codex CLI** | Add a rule to your `AGENTS.md` pointing at the skill, plus copy the folder under `~/.codex/` | Codex may not auto-scan skill folders — reference it in AGENTS.md |
| **Cursor** | `~/.cursor/skills/wiki-knowledge-agent/` (or project `.cursor/rules`) | Check your Cursor version's skill folder path |

### Troubleshooting — "the agent says it doesn't have this skill"

- **Hermes / Claude Code / Cursor**: verify the SKILL.md is inside the correct skills folder (paths above). Skills are usually scanned at session start — **restart the session** after installing.
- **Codex CLI**: it does not auto-scan skill folders in all versions. Add a line to `AGENTS.md`:
  ```markdown
  ## Wiki saves
  Use the wiki-knowledge-agent skill at ~/.codex/skills/wiki-knowledge-agent/SKILL.md
  when the user asks to save/archive a link or text.
  ```
- **Still not found?** Check the folder name matches the skill name (`wiki-knowledge-agent`), and that `SKILL.md` sits directly in that folder (not nested). Then re-run onboarding (`python3 scripts/onboarding.py`) and confirm `~/.config/wiki-knowledge-agent/config.yaml` exists.
- The scripts themselves don't need the agent to find them — you can also call `python3 scripts/ingest.py --verify <url>` directly from a terminal; only the *classification/translation* step requires an LLM that has read SKILL.md.

## Usage

### Ingest (when content arrives in chat)

The model follows SKILL.md: verify → classify → pre-save feedback → translate/summarize → save → maybe alert.

Script helpers:

```bash
# Verify a URL
python3 scripts/ingest.py --verify "https://example.com/article"
# ✅ 200 → https://example.com/article

# Save a prepared note
python3 scripts/ingest.py --save /tmp/note.md \
  --source-url "https://..." --channel discord --classification useful --language ko
# ✅ 인박스: ~/wiki/knowledge/inbox/2026-08-26-example.md

# Alert queue
python3 scripts/ingest.py --notify "API key expiring 2026-09-01" --category account_expiry
python3 scripts/ingest.py --alerts            # read
python3 scripts/ingest.py --alerts --clear    # archive
```

### Storage layout (under wiki_root)

```
<wiki_root>/
├── knowledge/
│   ├── inbox/YYYY-MM-DD-<topic>.md   ← collected notes (distilled, not verbatim)
│   └── <topic>.md                    ← integrated knowledge
├── alerts/
│   ├── notifications.md              ← Tier-0 alert queue
│   └── archive/                      ← cleared alerts
└── knowledge-base-map.md             ← RAG inventory (topic → file)
```

### RAG (agents using the wiki as a knowledge channel)

- Search: `search_files(pattern=..., path=<wiki_root>/knowledge)`
- Fast mapping: read `knowledge-base-map.md`
- Optional weekly cron: verify inbox → merge into `knowledge/<topic>.md` → archive processed files

## Configuration

`~/.config/wiki-knowledge-agent/config.yaml` (override with `WIKI_AGENT_CONFIG`).

Full reference: [`templates/config.example.yaml`](templates/config.example.yaml)

```yaml
wiki_root: "~/wiki"
target_language: "ko"
translate: true
input:
  sources: ["any"]            # or ["discord", "slack", ...]
  default_channel: "current"
notify:
  tier0: true                 # always on
  webhook: ""                 # optional
  email: ""                   # optional
  ntfy_topic: ""              # optional
alert_on:
  security: true
  account_expiry: true
  project_risk: true
  interest: false
```

## Docs

- [SKILL.md](SKILL.md) — the agent-facing procedure (load this into your agent)
- [references/ad-detection.md](references/ad-detection.md) — ad-vs-useful classification guide with worked examples
- [templates/config.example.yaml](templates/config.example.yaml) — full config reference

## Community

- Report bugs / request features: [Issues](https://github.com/atukunare/wiki-knowledge-agent/issues)
- Discussions: [GitHub Discussions](https://github.com/atukunare/wiki-knowledge-agent/discussions)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Grok Bot (X) — community template

Want this skill as an X-based AI teammate? A community Grok Bot template called **Ywiky** follows the same procedure (verify → label ad/useful → one-line context → summarize → save):

- **Bot link:** https://x.ai/bot/ODzi9HX2HOreEdk2cBCNG
- **How to use:** install Grok Bot (desktop/iOS), open the link, click "Add to Grok Bot", then paste links/text into the chat.

> Note: Grok Bot is a remote X agent — it keeps its own memory space and can't read your local `~/wiki` files. For a local-file wiki, use the skill folder install above. To make your own bot, create one in the Grok Bot app and paste the procedure from [SKILL.md](SKILL.md) into its description.

## License

MIT
