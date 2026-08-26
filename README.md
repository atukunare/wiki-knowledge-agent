# Wiki Knowledge Agent

**🌐 [한국어 문서 (Korean README)](README.ko.md)**

Turn chat-pasted text/links into a **verified, translated, searchable** wiki knowledge base. Works on any agent platform (Hermes, Claude Code, Codex, Cursor) with **zero external dependencies** — just `curl` + Python stdlib.

- 🔎 **Verify** links on arrival (HTTP status, redirects) and classify content
- 📢 **Ad detection** — labels pure ads vs. genuinely useful info (no auto-deletion, provenance kept)
- 🌐 **Translate + summarize** into your language (default: the user's native language)
- 🗂️ **Save** to a wiki inbox with structured metadata
- 🔔 **Local-first alerts** — time-sensitive info (security, expiry, project risk) is queued locally and reported in chat; optional webhook/email/ntfy if you add them later
- 📚 **RAG-ready** — agents search the wiki as a knowledge channel, with an auto-maintained topic→file map

## Why

Many people paste links/text into chat and expect the AI to remember them. Agents forget; wikis don't. This skill gives agents a **repeatable procedure** for capturing, judging, translating, storing, and surfacing knowledge — on any platform, with no SaaS account required.

## Requirements

- Python 3.9+
- `curl` (for link verification)
- A model that can follow the SKILL.md instructions (any capable LLM agent)

Optional: `pyyaml` for config read/write (falls back to a minimal parser/writer without it).

## Quickstart

```bash
# 1. Clone / copy this repo into your agent's skills directory
#    (or load SKILL.md into your agent's skill folder)

# 2. Run onboarding to create the config
python3 scripts/onboarding.py
```

Onboarding asks:
1. **Wiki root path** → default `~/wiki`
2. **Input channels** → `any`, or a specific list (discord/slack/…); if you pick nothing, the **current chat** becomes the default — but content pasted into *other* channels is still judged and saved
3. **Target language** → default `ko` (change to your native language)
4. **Alert channel** → optional webhook/email; without one, alerts go to the local queue + current chat. **Add alerts later anytime**: just tell the model *"알림 채널 추가해줘"* — it updates the config.

## Usage

### Ingest (when content arrives in chat)

The model follows SKILL.md: verify → classify → translate/summarize → save → maybe alert.

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

## License

MIT
