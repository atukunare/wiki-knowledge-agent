#!/usr/bin/env python3
"""
wiki-knowledge-agent — onboarding wizard

Creates ~/.config/wiki-knowledge-agent/config.yaml interactively.
Questions:
  1. Wiki root path
  2. Input channels (any / specific list; default = current chat)
  3. Target language
  4. Alert channel (webhook/email optional; default = current chat)

Usage:
    python3 scripts/onboarding.py
"""
import os
import sys
import pathlib
import yaml  # optional; falls back to a simple writer if missing

DEFAULT_CONFIG_DIR = pathlib.Path.home() / ".config" / "wiki-knowledge-agent"
DEFAULT_CONFIG = DEFAULT_CONFIG_DIR / "config.yaml"

KNOWN_PLATFORMS = ["discord", "slack", "weixin", "telegram", "whatsapp", "cli", "web"]


def ask(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{question}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[onboarding aborted]")
        sys.exit(1)
    return val if val else default


def parse_sources(raw: str) -> list:
    raw = raw.strip().lower()
    if not raw or raw in ("any", "*", "all"):
        return ["any"]
    return [p.strip() for p in raw.replace(",", " ").split() if p.strip()]


def write_config_yaml(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml  # noqa
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    except ImportError:
        # Minimal YAML writer fallback (flat + nested dicts)
        lines = []
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"{k}:")
                for k2, v2 in v.items():
                    lines.append(f"  {k2}: {yaml_scalar(v2)}")
            else:
                lines.append(f"{k}: {yaml_scalar(v)}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def yaml_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(str(x) for x in v) + "]"
    if isinstance(v, str):
        if v == "":
            return '""'
        return v
    return str(v)


def main() -> None:
    print("=" * 60)
    print(" wiki-knowledge-agent — onboarding")
    print(" Creates a config file. Defaults are shown in [brackets].")
    print(" Press Enter to accept a default.")
    print("=" * 60)

    # 1. wiki root
    wiki_root = ask("Wiki root path", "~/wiki")
    wiki_root = os.path.expanduser(wiki_root)

    # 2. input channels
    print("\nInput channels — where pasted content may come from.")
    print(f"  Known platforms: {', '.join(KNOWN_PLATFORMS)}")
    print("  'any' = every channel/CLI. If you pick nothing, default = the current chat.")
    src_raw = ask("Input sources (comma/space separated, or 'any')", "any")
    sources = parse_sources(src_raw)

    # 3. target language
    lang = ask("Target language for translation (e.g. ko, en, ja, zh)", "ko")

    # 4. alert channel
    print("\nAlert notifications — time-sensitive info (security, expiry, risk).")
    print("  No external app required: alerts always save locally + print in the chat.")
    webhook = ask("Optional webhook URL (Slack/Discord/Telegram; empty = skip)", "")
    email = ask("Optional email/SMTP DSN (empty = skip)", "")
    ntfy = ask("Optional ntfy topic (empty = skip)", "")

    config = {
        "wiki_root": wiki_root,
        "target_language": lang,
        "translate": True,
        "input": {
            "sources": sources,
            "default_channel": "current",  # onboarding default = this chat
        },
        "notify": {
            "tier0": True,
            "webhook": webhook,
            "email": email,
            "ntfy_topic": ntfy,
        },
        "alert_on": {
            "security": True,
            "account_expiry": True,
            "project_risk": True,
            "interest": False,
        },
    }

    write_config_yaml(DEFAULT_CONFIG, config)

    print("\n" + "=" * 60)
    print(f"✅ Config written to: {DEFAULT_CONFIG}")
    print("=" * 60)
    print("Summary:")
    print(f"  wiki_root       : {wiki_root}")
    print(f"  input sources   : {sources}")
    print(f"  default channel : current (this chat)")
    print(f"  target language : {lang}")
    print(f"  notify          : tier0=always | webhook={webhook or 'none'} | email={email or 'none'} | ntfy={ntfy or 'none'}")
    print("\nTo change anything later, edit the config or ask your model:")
    print('  e.g. "알림 채널 추가해줘" → the model updates config.yaml.')
    print("To re-run: python3 scripts/onboarding.py")


if __name__ == "__main__":
    main()
