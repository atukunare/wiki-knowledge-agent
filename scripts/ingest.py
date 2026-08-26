#!/usr/bin/env python3
"""
wiki-knowledge-agent — ingest CLI

Fetch/verify links, save structured notes, manage the local alert queue.
Pure stdlib (curl invoked via subprocess for link checks).

Usage:
  python3 scripts/ingest.py --verify <url>
  python3 scripts/ingest.py --verify-content <file>
  python3 scripts/ingest.py --save <note.md> [--source-url URL] [--channel NAME]
         [--classification ad|useful] [--language ko]
  python3 scripts/ingest.py --notify "message" [--category security|account_expiry|project_risk|interest]
  python3 scripts/ingest.py --alerts [--clear]
  python3 scripts/ingest.py --status
"""
import argparse
import datetime
import os
import pathlib
import subprocess
import sys
import urllib.parse

CONFIG_ENV = "WIKI_AGENT_CONFIG"
DEFAULT_CONFIG = pathlib.Path.home() / ".config" / "wiki-knowledge-agent" / "config.yaml"


def load_config() -> dict:
    path = pathlib.Path(os.environ.get(CONFIG_ENV, DEFAULT_CONFIG))
    if not path.exists():
        return {}
    try:
        import yaml  # noqa
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except ImportError:
        # minimal key:value parser for the fallback format
        data = {}
        section = None
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith(":") and not line.startswith("  "):
                section = line[:-1]
                data[section] = {}
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip('"')
                if section:
                    data[section][k] = v
                else:
                    data[k] = v
        return data


def wiki_root(config: dict) -> pathlib.Path:
    raw = config.get("wiki_root") or "~/wiki"
    return pathlib.Path(os.path.expanduser(raw))


def verify_url(url: str, timeout: int = 15) -> dict:
    """Return HTTP status + final URL. Uses curl -s -I -L."""
    try:
        proc = subprocess.run(
            ["curl", "-s", "-I", "-L", "--connect-timeout", "8", "--max-time", str(timeout), "-o", "/dev/null",
             "-w", "%{http_code}\t%{url_effective}", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        out = proc.stdout.strip()
        if "\t" in out:
            code, final = out.split("\t", 1)
            return {"status": int(code), "final_url": final, "valid": 200 <= int(code) < 400}
        return {"status": None, "final_url": url, "valid": False, "error": "no output"}
    except subprocess.TimeoutExpired:
        return {"status": None, "final_url": url, "valid": False, "error": "timeout"}
    except FileNotFoundError:
        return {"status": None, "final_url": url, "valid": False, "error": "curl not found"}


def slugify(topic: str, max_len: int = 40) -> str:
    safe = []
    for ch in topic.lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in " _-":
            safe.append("-")
    s = "".join(safe).strip("-")
    return s[:max_len] or "note"


def save_note(config: dict, note_path: pathlib.Path, source_url: str = "", channel: str = "",
              classification: str = "", language: str = "") -> pathlib.Path:
    """Copy a prepared note into <wiki_root>/knowledge/inbox/YYYY-MM-DD-<topic>.md"""
    root = wiki_root(config)
    inbox = root / "knowledge" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    body = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
    topic = slugify(pathlib.Path(note_path).stem)
    today = datetime.date.today().isoformat()
    dest = inbox / f"{today}-{topic}.md"

    header = []
    if source_url:
        header.append(f"source_url: {source_url}")
    if channel:
        header.append(f"channel: {channel}")
    if classification:
        header.append(f"classification: {classification}")
    if language:
        header.append(f"language: {language}")
    if header:
        body = "---\n" + "\n".join(header) + "\n---\n\n" + body

    dest.write_text(body, encoding="utf-8")
    return dest


def notify(config: dict, message: str, category: str = "general") -> None:
    """Append to local alert queue + print CLI output. Optional webhook post."""
    root = wiki_root(config)
    alerts_dir = root / "alerts"
    alerts_dir.mkdir(parents=True, exist_ok=True)
    queue = alerts_dir / "notifications.md"

    now = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    with open(queue, "a", encoding="utf-8") as f:
        f.write(f"- [{now}] ({category}) {message}\n")
    print(f"[알림] ({category}) {message}")

    webhook = (config.get("notify") or {}).get("webhook")
    if webhook:
        try:
            import json
            import urllib.request
            payload = json.dumps({"text": f"[{category}] {message}"}).encode("utf-8")
            req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10):
                pass
        except Exception as e:  # webhook failure must not break the flow
            print(f"  (webhook failed: {e})")


def alerts(config: dict, clear: bool = False) -> None:
    root = wiki_root(config)
    queue = root / "alerts" / "notifications.md"
    if not queue.exists():
        print("(알림 없음)")
        return
    content = queue.read_text(encoding="utf-8").strip()
    if not content:
        print("(알림 없음)")
        return
    print(content)
    if clear:
        archive = root / "alerts" / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        stamp = datetime.date.today().isoformat()
        queue.replace(archive / f"notifications-{stamp}.md")
        print(f"\n(cleared → alerts/archive/notifications-{stamp}.md)")


def status(config: dict) -> None:
    root = wiki_root(config)
    inbox = root / "knowledge" / "inbox"
    alerts_q = root / "alerts" / "notifications.md"
    print(f"wiki_root          : {root}")
    print(f"input sources      : {(config.get('input') or {}).get('sources', ['any'])}")
    print(f"target language    : {config.get('target_language', 'ko')}")
    print(f"inbox files        : {sum(1 for _ in inbox.glob('*.md')) if inbox.exists() else 0}")
    print(f"alert queue        : {alerts_q.exists()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="wiki-knowledge-agent ingest CLI")
    parser.add_argument("--verify", metavar="URL", help="verify a URL with curl")
    parser.add_argument("--verify-content", metavar="FILE", help="verify pasted text file (content check)")
    parser.add_argument("--save", metavar="NOTE.md", help="save a prepared note to the inbox")
    parser.add_argument("--source-url", default="", help="source URL for --save")
    parser.add_argument("--channel", default="", help="source channel for --save")
    parser.add_argument("--classification", default="", choices=["", "ad", "useful", "unverified"], help="ad/useful label")
    parser.add_argument("--language", default="", help="note language")
    parser.add_argument("--notify", metavar="MESSAGE", help="append to local alert queue")
    parser.add_argument("--category", default="general", help="alert category")
    parser.add_argument("--alerts", action="store_true", help="print alert queue")
    parser.add_argument("--clear", action="store_true", help="with --alerts: archive queue")
    parser.add_argument("--status", action="store_true", help="print config status")
    args = parser.parse_args()

    config = load_config()

    if args.verify:
        result = verify_url(args.verify)
        if result.get("valid"):
            print(f"✅ {result['status']} → {result['final_url']}")
        else:
            print(f"❌ {result.get('status') or 'error'} (final: {result.get('final_url')}) {result.get('error', '')}")
        return

    if args.verify_content:
        path = pathlib.Path(args.verify_content)
        if not path.exists():
            print("❌ file not found")
            sys.exit(1)
        size = path.stat().st_size
        preview = path.read_text(encoding="utf-8", errors="ignore")[:300].replace("\n", " ")
        print(f"content: {size} bytes")
        print(f"preview: {preview}")
        print("→ classification/translation is done by the LLM (references/ad-detection.md)")
        return

    if args.save:
        dest = save_note(config, pathlib.Path(args.save), args.source_url, args.channel,
                         args.classification, args.language)
        print(f"✅ 인박스: {dest}")
        return

    if args.notify:
        notify(config, args.notify, args.category)
        return

    if args.alerts:
        alerts(config, args.clear)
        return

    if args.status:
        status(config)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
