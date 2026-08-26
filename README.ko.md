# Wiki Knowledge Agent

채팅에 붙여넣은 텍스트/링크를 **검증·번역·검색 가능한 위키 지식 베이스**로 바꿔주는 스킬입니다. 모든 에이전트 플랫폼(Hermes, Claude Code, Codex, Cursor)에서 **외부 의존성 없이** 동작합니다 — `curl` + Python 표준 라이브러리만 있으면 됩니다.

- 🔎 **도착 즉시 검증** — 링크 HTTP 상태/리다이렉트 확인, 내용 판별
- 📢 **광고 판별** — 순수 광고와 진짜 유용한 정보를 구분 (자동 삭제 안 함, 출처 보존)
- 🌐 **번역 + 요약** — 내 언어로 (기본: 사용자 모국어)
- 🗂️ **위키에 저장** — 구조화된 메타데이터와 함께 인박스에 보관
- 🔔 **로컬 우선 알림** — 시급한 정보(보안·만료·프로젝트 리스크)는 로컬 큐 + 채팅으로 보고, 필요 시 웹훅/이메일/ntfy도 추가 가능
- 📚 **RAG 준비** — 에이전트가 위키를 지식 채널로 검색, 주제→파일 맵 자동 유지

## 왜 필요한가

사람들은 링크/텍스트를 채팅에 붙여넣고 AI가 기억해주길 기대합니다. 에이전트는 잊지만 위키는 잊지 않습니다. 이 스킬은 에이전트에게 **수집 → 판별 → 번역 → 저장 → 알림**의 반복 가능한 절차를 제공합니다. 플랫폼 무관, SaaS 계정 불필요.

## 요구 사항

- Python 3.9+
- `curl` (링크 검증용)
- SKILL.md 지침을 따를 수 있는 LLM 에이전트

선택: `pyyaml` (config 읽기/쓰기 — 없으면 최소 파서/라이터로 폴백)

## 빠른 시작

```bash
# 1. 클론 또는 스킬 폴더로 복사
#    (에이전트의 skills 디렉토리에 SKILL.md를 넣어도 됨)

# 2. 온보딩 실행 (config 생성)
python3 scripts/onboarding.py
```

### 에이전트별 설치 위치 (스킬 폴더)

| 에이전트 | 설치 위치 | 비고 |
|---------|-----------|------|
| **Claude Code** | `~/.claude/skills/wiki-knowledge-agent/` | 세션 시작 시 자동 인식 |
| **Hermes** | `~/.hermes/profiles/<프로필>/skills/note-taking/wiki-knowledge-agent/` | **다음 세션부터** 인식 |
| **Codex CLI** | 스킬 폴더를 `~/.codex/`에 복사 + `AGENTS.md`에 규칙 추가 | Codex는 스킬 폴더를 자동 스캔하지 않을 수 있음 — AGENTS.md에서 참조 필요 |
| **Cursor** | `~/.cursor/skills/wiki-knowledge-agent/` (또는 프로젝트 `.cursor/rules`) | Cursor 버전별 스킬 폴더 경로 확인 |

Claude Code 설치 예시:

```bash
git clone https://github.com/atukunare/wiki-knowledge-agent.git
mkdir -p ~/.claude/skills/wiki-knowledge-agent
cp -R wiki-knowledge-agent/SKILL.md wiki-knowledge-agent/scripts \
      wiki-knowledge-agent/references wiki-knowledge-agent/templates \
      ~/.claude/skills/wiki-knowledge-agent/
```

### 문제 해결 — "에이전트가 이 스킬 없다고 해요"

- **Hermes / Claude Code / Cursor**: SKILL.md가 위 표의 올바른 스킬 폴더에 있는지 확인하세요. 스킬은 보통 **세션 시작 시** 스캔되므로 설치 후 **세션을 재시작**해야 합니다.
- **Codex CLI**: 일부 버전은 스킬 폴더를 자동 스캔하지 않습니다. `AGENTS.md`에 규칙을 추가하세요:
  ```markdown
  ## 위키 저장
  사용자가 링크/텍스트 저장을 요청하면
  ~/.codex/skills/wiki-knowledge-agent/SKILL.md 의 wiki-knowledge-agent 스킬을 사용한다.
  ```
- **그래도 못 찾으면?** 폴더 이름이 스킬 이름(`wiki-knowledge-agent`)과 일치하는지, `SKILL.md`가 폴더 바로 아래(중첩 없이) 있는지 확인하세요. 그 다음 온보딩 재실행(`python3 scripts/onboarding.py`) 후 `~/.config/wiki-knowledge-agent/config.yaml` 생성 여부를 확인하세요.
- 스크립트는 에이전트가 찾지 못해도 터미널에서 직접 실행할 수 있습니다: `python3 scripts/ingest.py --verify <url>` — *분류/번역* 단계만 SKILL.md를 읽은 LLM이 필요합니다.

온보딩 질문 4가지:
1. **위키 루트 경로** → 기본 `~/wiki`
2. **입력 채널** → `any` 또는 특정 목록(discord/slack/…); 선택하지 않으면 **현재 채팅창**이 기본 — 다른 채널에 실수로 붙여넣어도 **판단해서 저장**
3. **번역 언어** → 기본 `ko` (모국어로 변경)
4. **알림 채널** → 선택: 웹훅/이메일; 없으면 로컬 큐 + 현재 채팅창으로. **나중에 언제든 추가 가능**: 모델에게 *"알림 채널 추가해줘"* 라고 말하면 config를 업데이트합니다.

## 사용법

### 수집 (채팅에 내용이 도착하면)

모델이 SKILL.md를 따라: 검증 → 판별 → 번역/요약 → 저장 → (필요시) 알림.

스크립트 보조:

```bash
# URL 검증
python3 scripts/ingest.py --verify "https://example.com/article"
# ✅ 200 → https://example.com/article

# 준비된 노트 저장
python3 scripts/ingest.py --save /tmp/note.md \
  --source-url "https://..." --channel discord --classification useful --language ko
# ✅ 인박스: ~/wiki/knowledge/inbox/2026-08-26-example.md

# 알림 큐
python3 scripts/ingest.py --notify "API 키 2026-09-01 만료" --category account_expiry
python3 scripts/ingest.py --alerts            # 읽기
python3 scripts/ingest.py --alerts --clear    # 보관
```

### 저장 구조 (wiki_root 기준)

```
<wiki_root>/
├── knowledge/
│   ├── inbox/YYYY-MM-DD-<topic>.md   ← 수집 노트 (원문 아닌 요약)
│   └── <topic>.md                    ← 통합 지식
├── alerts/
│   ├── notifications.md              ← Tier-0 알림 큐
│   └── archive/                      ← 처리된 알림
└── knowledge-base-map.md             ← RAG 인벤토리 (주제 → 파일)
```

### RAG (에이전트가 위키를 지식 채널로 활용)

- 검색: `search_files(pattern=..., path=<wiki_root>/knowledge)`
- 빠른 매핑: `knowledge-base-map.md` 읽기
- 선택: 주간 크론 — 인박스 검증 → `knowledge/<topic>.md` 통합 → 처리된 파일 보관

## 설정

`~/.config/wiki-knowledge-agent/config.yaml` (`WIKI_AGENT_CONFIG` 환경변수로 오버라이드).

전체 레퍼런스: [`templates/config.example.yaml`](templates/config.example.yaml)

```yaml
wiki_root: "~/wiki"
target_language: "ko"
translate: true
input:
  sources: ["any"]            # 또는 ["discord", "slack", ...]
  default_channel: "current"
notify:
  tier0: true                 # 항상 켜짐
  webhook: ""                 # 선택
  email: ""                   # 선택
  ntfy_topic: ""              # 선택
alert_on:
  security: true
  account_expiry: true
  project_risk: true
  interest: false
```

## 문서

- [SKILL.md](SKILL.md) — 에이전트용 절차 (에이전트에 로드)
- [references/ad-detection.md](references/ad-detection.md) — 광고 vs 유용 정보 판별 가이드 (실전 예시)
- [templates/config.example.yaml](templates/config.example.yaml) — 전체 설정 레퍼런스
- [README.md](README.md) — English

## 라이선스

MIT
