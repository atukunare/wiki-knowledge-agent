---
name: wiki-knowledge-agent
description: "Turn chat-pasted text/links into a verified, translated, searchable wiki knowledge base. When a user pastes a link or text (in ANY channel — Discord, Slack, CLI, etc.), fetch+verify it, classify it (useful vs ad), translate+summarize it into the target language, save it to the wiki, and optionally alert on time-sensitive information. Also acts as a RAG channel: agents search the wiki for prior knowledge. Use whenever the user pastes content for archiving, asks to save a link/bookmark, asks '알림 있어?', or asks the agent to look up knowledge saved in the wiki."
category: note-taking
triggers:
  - "북마크"
  - "위키에 저장"
  - "링크 저장"
  - "붙여넣기 정리"
  - "인박스"
  - "알림 있어?"
  - "save this link"
  - "bookmark"
  - "wiki"
  - "저장해줘"
---

# Wiki Knowledge Agent

Turn chat-pasted text/links into a **verified, translated, searchable** wiki knowledge base. Works on any agent platform (Hermes, Claude Code, Codex, Cursor) with zero external dependencies beyond `curl` + Python stdlib.

## When to Use

- User pastes a link or text into **any chat channel** and expects it to be captured.
- User says "저장해줘", "링크 저장", "북마크", "save this", "add to wiki".
- User asks "알림 있어?" — read the local alert queue and report.
- An agent needs prior knowledge from the wiki (RAG usage — search `wiki_root`).
- A scheduled job runs the ingest/notify cycle.

## Design Principles

1. **Platform-independent** — works with a single model (no multi-agent setup required) or many.
2. **Zero external dependencies** — `curl` + Python stdlib only. No webhook/app required for core function.
3. **Local-first alerts** — alerts always land in a local file + CLI output. Optional webhook/email/ntfy if configured.
4. **Any-channel input** — a message arriving in any channel is eligible. The onboarding default channel is "the current chat".
5. **LLM does the reasoning** — the scripts fetch/verify/structure; the model classifies ads, translates, and summarizes.

## Configuration

Config file: `~/.config/wiki-knowledge-agent/config.yaml` (default), overridable via `WIKI_AGENT_CONFIG` env var.

Run onboarding to create it interactively:

```bash
python3 scripts/onboarding.py
```

Example config (full reference: `templates/config.example.yaml`):

```yaml
wiki_root: "~/wiki"
target_language: "ko"
translate: true

input:
  sources: ["any"]          # "any" = every channel/CLI; or a specific list e.g. ["discord", "slack"]
  default_channel: "current" # channel used when no preference is set (onboarding default)

notify:
  tier0: true               # always: local file + CLI
  webhook: ""               # optional: Slack/Discord/Telegram webhook URL
  email: ""                 # optional: SMTP DSN
  ntfy_topic: ""            # optional: ntfy.sh topic

alert_on:
  security: true
  account_expiry: true
  project_risk: true
  interest: false
```

### Onboarding flow (interactive questions)

1. **Wiki root path** → default `~/wiki`
2. **Input channels** → choose from known platforms (discord/slack/weixin/telegram/cli…) **or** "any"; if the user doesn't pick, default is **"current chat"** (`default_channel: current`). Content pasted into *other* channels is still judged and saved (never drop input because it arrived in the "wrong" channel).
3. **Target language** → default user's native language (e.g. `ko`).
4. **Alert channel** → if the user has a webhook/email, capture it; otherwise default is the **current chat** (the agent reports alerts in the same conversation). Alerts can be added later anytime: just ask the model "알림 채널 추가해줘" — the LLM updates the config.
5. Write `config.yaml` and print the summary.

## Ingest Workflow (when a message arrives)

```
[input] pasted text or link in any channel
   │
   ▼
1. VERIFY (script: scripts/ingest.py --verify <url-or-file>)
   - Link: curl -s -I -L → HTTP status; 2xx/3xx = valid, 404/410/timeout = dead
   - Text: mark as unverified text
   │
   ▼
2. CLASSIFY (LLM, guided by references/ad-detection.md)
   - 📢 Ad: self-promotion is the core intent, "try it" pitch, link-dump without substance
   - 📚 Useful: real methodology/data/tool with transferable value
   - Output: label + one-line reason
   │
   ▼
3. TRANSLATE + SUMMARIZE (LLM)
   - Foreign content → target_language
   - ≤5-line summary + 3–5 key points
   - If already in target_language, summarize only
   │
   ▼
4. SAVE (script: scripts/ingest.py --save ...)
   - <wiki_root>/knowledge/inbox/YYYY-MM-DD-<topic>.md
   - Frontmatter: date, source_url, source_channel, classification (ad/useful), language
   - Tag: related project or "일반"
   │
   ▼
5. ALERT? (LLM decides against alert_on rules + script: scripts/ingest.py --notify)
   - If alert-worthy → append to <wiki_root>/alerts/notifications.md
     + CLI output "[알림] …" + optional webhook/email
   - Else → silent save; reply "✅ 인박스: <file>"
```

### Ingest script usage

```bash
# Verify a URL (returns HTTP status)
python3 scripts/ingest.py --verify "https://example.com/article"

# Verify a pasted text (saved to temp file first, then verified as content)
python3 scripts/ingest.py --verify-content /tmp/pasted.txt

# Save a structured note (after LLM produced the markdown body)
python3 scripts/ingest.py --save /tmp/note.md --source-url "https://..." --channel "discord" --classification useful --language ko

# Append to the local alert queue
python3 scripts/ingest.py --notify "API key expiring 2026-09-01" --category security

# Read the alert queue (for "알림 있어?")
python3 scripts/ingest.py --alerts
```

## RAG Usage (agents searching the wiki)

- Search knowledge: `search_files(pattern=..., path=<wiki_root>/knowledge)`
- Fast topic mapping: read `<wiki_root>/knowledge-base-map.md` (auto-updated inventory) — topic → file
- Recurring integration: a weekly cron can run the curation flow (see `wiki-inbox-curation` pattern): verify → merge into `knowledge/<topic>.md` → move processed inbox files to `inbox/archive/`.

## Alert Notifications

- **Tier 0 (always)**: append `<wiki_root>/alerts/notifications.md` + print `[알림] …` to stdout.
- **Tier 1 (optional)**: webhook (Slack/Discord/Telegram), email (SMTP), or ntfy.sh topic — only if configured.
- Alerts are *time-sensitive* items: security issues, account/domain expiry, project risk, and (if enabled) user interests.
- To add an alert channel later: user says "알림 채널 추가해줘" → model reads config, asks for the webhook/email, updates config.yaml.

## Pitfalls

- **Never drop input because it came from a "non-default" channel** — judge it and save; the channel is metadata, not a gate.
- **Don't store full verbatim text** — store the distilled note (summary + points), keeping the wiki lean.
- **Verify before trusting** — a 404 after redirects is a dead link; a ~500-byte stub is a bot-block page, not content.
- **Ads are not automatically deleted** — label them 📢 and save only the transferable insight (if any); keep provenance.
- **Personal info / secrets in pasted content** — strip identifiers before saving.
- **Config path** — respect `WIKI_AGENT_CONFIG` env var if set; never hardcode `~/wiki` into scripts.
- **Alert queue growth** — mark items read/archived after reporting (`--alerts --clear` or move to `alerts/archive/`).

## Files

- `scripts/onboarding.py` — interactive config wizard
- `scripts/ingest.py` — verify / save / notify / alerts CLI
- `templates/config.example.yaml` — full config reference
- `references/ad-detection.md` — ad-vs-useful classification rules with worked examples
- `README.md` — public repo docs (EN/KR)
