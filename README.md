# Unity NAI · GPT Skills

Claude Code에서 게임 아트를 뽑을 때 쓰는 공용 스킬 두 개. 프로젝트에 묶이지 않게 일반화해 둠.

| 스킬 | 하는 일 |
|---|---|
| `nai-image` | NovelAI Diffusion V5로 일러스트 · 배경 · 소품 · 스프라이트 생성. 투명 PNG, 캐릭터별 캡션, 타일링 지원 |
| `codex-art-request` | 로컬 Codex 앱(GPT 이미지)으로 UI · VFX · 스프라이트를 목업 → 분절 두 단계로 받아 옴 |

## 설치 (새 PC / 노트북)

1. 이 저장소를 사용자 스킬 폴더에 받음.
   - `~/.claude/skills`가 비어 있으면 그 자리에 바로 clone:
     ```
     git clone https://github.com/SkylightStudio07/Unity-NAI-GPT-Skills.git "%USERPROFILE%\.claude\skills"
     ```
   - 이미 다른 스킬이 있으면 아무 데나 clone한 뒤 `nai-image`, `codex-art-request` 폴더만 `~/.claude/skills/`로 복사함.
   - 한 프로젝트에서만 쓸 거면 그 프로젝트의 `.claude/skills/`에 넣어도 됨.
2. Python 3와 Pillow 설치: `pip install pillow`
3. Claude Code를 다시 열면 스킬 목록에 두 개가 보임.

## 인증 (저장소에 절대 넣지 않음)

- **NAI:** Windows 사용자 환경 변수 `NAI_API_KEY`에 NovelAI 토큰을 등록함 (시스템 속성 → 환경 변수 → 사용자 변수). 채팅에 붙여 넣지 않음.
- **GPT (Codex):** Codex 앱을 설치하고 로그인함. 스크립트는 앱 안의 `codex.exe`를 자동으로 찾음.
- 확인:
  ```
  python -I ~/.claude/skills/codex-art-request/scripts/run_codex_art.py --check
  python -I ~/.claude/skills/nai-image/scripts/nai_gen.py --prompt "no humans, game asset, wooden crate" --name test --dry-run
  ```

## 새 프로젝트에서 NAI 쓰기

프로젝트 루트에 `Art Prompts/` 폴더를 만들고 아래 파일을 둠 (자세한 형식은 `nai-image/SKILL.md`).

- `[Base Prompts].txt`: 모든 프롬프트 뒤에 붙는 공통 화풍 (작가 · 품질 태그)
- `[Negative Prompts].txt`: 네거티브
- `[Props] 01_Name.txt` 등: `## 1. 제목 (16:9)` / `### 1-A. 항목` 섹션 하나가 프롬프트 하나 → 키 `01:1-A`

화풍은 첫날 몇 장 뽑아 보고 `[Base Prompts].txt`에 고정해 두는 게 좋음. 그 뒤로는 에셋마다 화풍 단어를 따로 넣지 않음.

## 지키는 것

- 토큰 · `~/.codex/auth.json`은 읽지도 출력하지도 않음.
- NAI는 무료 범위(≤1024×1024, ≤28 step, 1장씩)만 씀. 넘으면 스크립트가 경고함.
- 실존 IP · 실존 인물 태그 금지.
- 생성물 폴더(`_nai_out/`)와 Codex 작업 파일(`_codex_*.txt`, `Working/`, `.py` · `.cjs` · `.ps1`)은 게임 프로젝트에 커밋하지 않음.
