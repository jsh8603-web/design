<!--
======================================================================
이 파일은 두 부분입니다.
  · 윗부분(여기 ~ "✂ CUT HERE" 줄): 설계 의도/배경 설명. 로컬에서 읽고 이해하는 용도.
  · 아랫부분("---" YAML frontmatter부터 끝까지): 실제 SKILL.md.

로컬에서 스킬로 쓸 때:  "✂ CUT HERE" 아래의 `---` 줄부터 파일 끝까지를 복사해
  analytical-slide-coauthoring/SKILL.md 로 저장하면 됩니다. 윗부분은 버리세요.
  (frontmatter `---` 위의 모든 줄을 지우면 곧바로 유효한 스킬 파일입니다.)
======================================================================
-->

# 설계 의도 — 읽고 나서 아래 스킬만 떼어 쓰세요

## 1. 원본 대비 무엇을 바꿨나 (요청 3가지)

**(1) 로컬 Claude Code화.**
claude.ai 수동 경로(원본 §12.2 Approach B)와 커넥터 안내 멘트를 제거. 전부 파일
기반(`create_file`/`str_replace`) + 서브에이전트 기반으로 재구성. 사내망 현실(프록시/SSL,
npm·PyPI 차단)을 명시해, 소스에 못 닿으면 추정치로 메우지 말고 추출본을 요청하게 했고,
검증 코드는 stdlib만 쓰도록 못 박음.

**(2) "처음 한 번 MD" 방식.**
시작 시 `00-brief.md` 한 장을 만들고 거기서 방향을 잡음(메타/근거맵/정치적 맥락/검증
원장). 항목별 채팅 심문은 폐기. → §10.

  ⚠️ 단, 슬라이드 단위 *규율* 자체는 없애지 않고 "동기 채팅 → 파일+자율 실행"으로 옮김.
  "브리프 쓰고 일괄 생성"은 액션 타이틀이 주제 라벨로 무너지고 고스트덱이 깨지므로 금지.
  대신 Claude가 고스트덱 테스트/스타일/전체 재독을 *스스로* 돌리고 브리프에 기록만 함.

**(3) 환각 방지 검증 게이트(§13) 추가 — 이 어댑테이션의 핵심.**
주장을 internal(사내 DB) / external(회계·재무·세무 지식) / derived(파생 계산) 로 분류해
각각 다른 검사:
  · internal → 인용 추출본에 대한 NLI 함의 검사(RAGAS faithfulness, ≥0.9). 검증
    서브에이전트는 *주장+소스만* 보고 덱 서사는 안 봄(CoVe 디커플링 원리).
  · external → RARR 루프(검증질문→1차 권위 소스 국세청/한국회계기준원/IFRS→합의 게이트
    →모순 시에만 수정·재인용).
  · derived → LLM이 아니라 *코드*로 결정론적 재계산(분산·증감률·마진·환산·크로스풋).
    재무 덱이 깨지는 지점이라 LLM 판단에서 분리.
출구 산출물 = 검증 원장. `unsupported` 0건, `needs-human` 전부 사용자에게 라우팅(AIS 기준).

참고한 방법(스킬 §13에 출처째 기재 — 나중에 감사 가능):
  · RAGAS faithfulness — Es et al. 2023, `explodinggradients/ragas`
  · Chain-of-Verification(CoVe) — Dhuliawala et al., Meta 2023, arXiv:2309.11495
  · RARR — Gao et al., ACL 2023, `anthonywchen/RARR`
  · AIS(Attributable to Identified Sources) — Rashkin et al. 2023

## 2. "처음 한 번" 의도는 지켜졌나 — 예 (이번 수정으로 더 충실해짐)

설계 목표 = **초기 상호작용 1회(브리프) → 이후 자율 빌드.**
브리프 이후 사용자에게 돌아오는 경우는 두 가지뿐:
  · (필수) `needs-human` 검증 항목 — 소스가 안 닿거나 외부 사실을 권위 출처가 못 풀 때.
    지어낼 수 없으니 물어볼 수밖에 없음.
  · (필수) 마지막 핸드오프 리포트 — 협상 게이트가 아니라 요약+검증 원장 보고.
고스트덱·스타일·전체 재독은 Claude가 자체 수행하고 브리프에 기록만 함. 사용자만 아는
지식이 없으면 못 푸는 진짜 분기일 때만 조건부로 물음. → 스킬 §11.0 / §10.4.

(직전 버전엔 체크포인트가 4개 있었음. 의도대로 1회+필수 접점으로 줄였음.)

## 3. 파일 구성 결정

원본도 SKILL.md 단일 파일이라(36K, 부속 파일 없음) 단일 파일이 정상 구조. 요청대로
템플릿(브리프 §10.2, 스캐폴드 §11.3)과 검증 원장(§13.6)은 *별도 파일로 빼지 않고* 스킬
본문에 인라인으로 둠.

  · derived 재계산 스크립트(`verify.py`)는 의도적으로 코드를 안 박았음 — 받을 추출본
    포맷(쿼리결과 JSON/CSV/셀참조)과 원장 스키마가 사세훈 님 환경에 묶여 있어서. §13.4는
    "코드로 결정론적 재계산(stdlib)"이라는 *방법*으로 두고, 실제 스크립트는 그 포맷이
    정해지면 작성하는 게 맞음. 포맷 알려주면 인라인 코드블록으로 추가해 드림.

======================================================================
✂ CUT HERE — 아래 `---` 줄부터 파일 끝까지가 SKILL.md 입니다. 이 줄 위는 모두 잘라내세요.
======================================================================

---
name: analytical-slide-coauthoring
description: Builds analytical and business-reporting slide content (FP&A board packs, variance/forecast reviews, exec briefings, research updates, defenses) with action titles, one-job-per-slide structure, exhibit discipline, and a source-grounded verification gate that catches hallucinated numbers and unsupported claims. Optimized for local Claude Code — file-driven, with a single upfront brief and then an autonomous build instead of per-item questioning; multi-session advice and reader testing run as subagents. Most evidence comes from internal company data (internal DB extracts); some claims rest on external accounting/finance/tax facts, and both are verified before the deck ships. Trigger on requests for slides, decks, presentations, board packs, briefings — keywords include "slides", "deck", "presentation", "보고", "보고서", "발표자료", "슬라이드", "덱".
---

# Analytical Slide Co-Authoring (Local / Claude Code)

Produces slide body text + speaker notes in markdown, ready for handoff to a design/PPTX step. Two backbones run together:

1. **Content discipline** (§1–§9) — what makes a slide carry its weight. Domain-general; do not skip even in freeform mode.
2. **A file-driven, single-pass workflow** (§10–§15) — adapted for local Claude Code: one upfront brief markdown file holds direction, the deck is then built into a file autonomously, and grounding/verification + reader testing run as decoupled subagents.

**Language:** converse with the user in Korean unless they switch. Keep the deck file in whatever language the deck is delivered in.

---

## 0. Why this version differs from synchronous co-authoring

A chat-turn-per-item workflow exists to do two jobs. They are not the same and are ported differently:

- **Context transfer** — closing the gap between what the user knows and what Claude knows. Here, *front-load it into a brief file* (§10) the user can edit async. Strictly better than dribbling questions for a power user.
- **Quality gating** — the slide-by-slide loop is the *mechanism* that forces action titles instead of topic labels (the ghost-deck test, §2). This cannot be replaced by "write brief → batch-generate the deck": batch output reliably collapses titles into topic labels and breaks the ghost deck.

So gating is **moved, not removed**: Claude builds outline-first → slide-by-slide *into the deck file autonomously*, and pauses only at a small set of checkpoints (§11.0). No per-bullet interrogation; the discipline survives. When in doubt, write the reasoning and open questions into the brief file and keep going — surface a checkpoint only at a real decision fork.

---

## 1. Argument Structure

### Lead with the question or claim
State the central question, recommendation, or claim explicitly — by slide 2–3 at the latest. The audience needs it to evaluate everything after. Do not bury it.

### Pick one narrative spine and hold it
- **SCR (Situation / Complication / Resolution)** — what was true → what broke or changed → what you found / recommend. Default for variance reviews and analytical memos.
- **Funnel + Answer** — broad context → specific gap → approach → key findings → implications. Default for research updates and defenses.
- **Answer First** — lead with the conclusion, then support it. Default for senior, time-pressured audiences: board packs, exec briefings, grant panels.

### One argument per deck
Resist presenting the whole analysis. Choose the claim you can make convincingly in the time available. Everything else is appendix.

### Each slide has exactly one job
If a slide does two things, split it.

### Flow test
Read the slide titles in order. Each should make the next feel like a natural consequence. A slide that could appear anywhere without loss is misplaced or dispensable.

---

## 2. Action Titles — the most important rule

Every content-slide title is a complete sentence stating the takeaway (the "so what"), not a topic label.

| Topic label (wrong) | Action title (right) |
|---|---|
| Q3 Results | Q3 revenue beat guidance by 4%, driven by B2B renewals |
| Variance Analysis | Marketing overspend is concentrated in one paid-search campaign |
| Methodology | RD exploits a sharp funding threshold for clean identification |
| Forecast | FY rolling forecast now lands 2% below plan on softer Q4 demand |
| Headcount | Backfill lag, not attrition, explains the open-role buildup |

**Ghost deck test:** read only the action titles in sequence. They must tell the complete argument. If they don't, the logic is broken — fix titles / restructure before building bodies.

Title length: 1–2 lines. If more is needed, the point isn't sharp yet. Render at 24–28 pt bold in design.

---

## 3. Exhibit Discipline

- **One exhibit per slide** — one chart, table, diagram, or equation block. Two charts usually means two slides (or one combined comparison).
- **Every exhibit earns its place** — cover the exhibit and read the title: does it still make sense? Cover the title and read the exhibit: is the takeaway obvious? If a chart needs no title to land, fix the annotation or the title.
- **Annotate the finding on the exhibit** — call-out arrow, shaded region, a text box ("↑ 23% vs. plan"), or a focal-series color. Do not make the audience hunt.
- **Self-sufficient slide test** — readable without narration, because it will be circulated as PDF. If not, add an annotation.
- **Figure left, interpretation right** — evidence first, reading second.
- **Graphs over tables for trends/comparisons**; reserve tables for exact values that must be compared precisely.
- **Rebuild figures** at presentation resolution (axis labels ≥16 pt); don't paste from a PDF.
- **Don't include what you won't discuss** — if it's in, discuss it; else appendix.
- **`Visual hint` field** — every exhibit slide carries a one-line design brief: chart type, axes, what's annotated, what's de-emphasized. e.g. `bar: Q1–Q4 actual vs. plan, Q3 bar in accent, plan as dashed line`.

---

## 4. Text Discipline

- **≤ ~40 words of body per slide.** More means the slide does too much, or the material is appendix/handout.
- **Bullets are orientation cues, not paragraphs.** One idea each; 3–5 per slide; >5 is a warning.
- **Telegraphic is fine.** "Intervention cut cost 23% (p<0.01)" beats a full sentence. Body font 20 pt floor.
- **Bold/italics sparingly** — key term on first use, inline labels ("Note:", "Limitation:"), the focal finding. Not decoration.
- **Speaker notes are not a reprint of the body.** They hold: (1) context the body couldn't fit, (2) the transition to the next slide, (3) the anticipated question + how to handle it, (4) optionally a verbatim phrase for delicate framing. 3–6 sentences, written as spoken.

---

## 5. Citations and Source Tags

This is where grounding starts; §13 enforces it.

- **Tag every non-trivial number while drafting.** In the deck markdown, each quantitative claim carries an inline machine-resolvable tag:
  - Internal: `[src: <query_id|table.view|file p.X|cell Sheet!B12> @ <as_of_date>]`
  - External: `[src: <authority>, <doc/standard>, <section>, <retrieved_date>]`
  - Unknown: `[Source needed]` — must be resolved before completion.
- **Cite on the slide** — small muted font (12–14 pt) at the bottom, consistent format throughout.
- **As-of date is mandatory for internal data.** Internal figures are bitemporal; a number with no as-of date is unverifiable. (Matches the user's event-sourced data discipline.)
- **Oral attribution** for external sources: "K-IFRS 1116 requires…" before the parenthetical flashes.
- **References slide** before the appendix lists every cited source.

---

## 6. Deck Architecture

Pick the variant by deck type; both keep the required slots.

### Variant A — Analytical / Business report (board pack, variance review, exec briefing)
1. **Title** — title framed as a statement or question, owner, audience/forum, as-of period, date.
2. **Bottom line up front (BLUF)** — the recommendation/headline in one slide, if Answer-First.
3. **Context / what changed** — why this matters now (Situation + Complication).
4. **The question or decision** — stated explicitly, its own slide.
5. **Findings** — one finding per slide, exhibit + annotated takeaway.
6. **Implications / recommendation** — interpret; connect to the decision; name the main risk/limitation and pre-empt it.
7. **Conclusions / asks** — 2–4 bullets; stays on screen during discussion; do NOT follow with "Thank You".
8. **References** — all sources.
9. **Appendix** — pre-built Q&A slides, robustness/sensitivity, supporting tables, derivations. Label each.

### Variant B — Research / academic (update, seminar, defense)
Title → Motivation/Context (1–2) → Research Question (own slide) → Methods (1–2; only what's needed to evaluate findings) → Results (one finding/slide) → Discussion/Implications (limitation pre-empted) → Conclusions (survives Q&A) → References → Appendix.

In both: the **decision/question gets its own slide**, the **conclusions slide survives Q&A**, and a **References slide always exists**.

---

## 7. Timing and Slot Management

- **Max one slide per minute.** 10-min ≈ 8–10 content slides; 15-min ≈ 12–14; 20-min ≈ 15–18; 45-min seminar ≈ 30–40. Title/references excluded.
- **Rehearse to finish 1–2 min under.** Going over at a board or conference is a real misstep.
- **Know what to cut** — mark skippable slides; protect the question, the key finding, the conclusion. Context/methods compress first.
- **Q&A prep** — pre-build appendix slides for the 3–5 likeliest questions ("why not method X?", "is the sample/period representative?", "what about the endogeneity / one-off?", "how does this reconcile to the GL?").
- **End on conclusions**, on screen, and invite: "Questions or feedback?"

---

## 8. International & Accessibility

- International audiences: avoid idioms and local humor; define every acronym on first use; plain sentence structure.
- Accessibility: 20 pt body / 24 pt+ titles; high contrast; never color alone (use labels/patterns/shapes); alt text on figures if circulated as PDF.

---

## 9. Common Mistakes

| Mistake | Fix |
|---|---|
| Topic-label titles | Action title: complete sentence, states takeaway |
| Presenting the whole analysis | One argument; rest to appendix |
| Reading slides aloud | Slides carry evidence; presenter carries argument |
| Evidence without a "so what" | Annotate the finding on the exhibit |
| Untagged numbers | Every number gets a `[src: …]` with as-of date |
| Body < 20 pt | Remove content until it fits at 20 pt |
| Slides you won't discuss | Appendix |
| Over time | Rehearse under; know what to cut |
| Ending on "Thank You" | End on conclusions; it survives Q&A |
| Burying the decision/question | Its own slide, slides 2–3 |
| No references slide | Always include one |
| Number that "looks right" but is recomputed wrong | Deterministic recompute, §13.4 |

---

## 10. Stage 1 — The Brief (one file, front-loaded)

Instead of interrogating the user turn-by-turn, create **one brief file first** and drive direction through it.

### 10.1 Create the brief
`create_file` at `slides/<deck-slug>/00-brief.md` (or working dir). Tell the user: "I've created the brief file; fill what you can — bullet fragments are fine — and I'll work the rest." The brief holds direction, the data-source map, and (later) the verification ledger. It is the async substitute for clarifying questions.

### 10.2 Brief template
```markdown
# Brief — <deck title>

## Meta
- Type: <board pack / variance review / exec briefing / research update / defense / other>
- Audience: <seniority, prior knowledge, decision authority>
- Desired impact: <what they should DO or BELIEVE after>
- Time slot: <minutes>  → slide cap per §7
- Setting: <live / pre-read / async share / hybrid>
- One-sentence thesis: <the single sentence they must remember>
- Narrative spine: <SCR / Funnel+Answer / Answer-First>

## Evidence base
- Internal sources: <DBs, query IDs, tables/views, dashboards, file paths, as-of dates>
- External sources: <standards/regulations/market data: K-IFRS/IFRS, 국세청/NTS, 한국회계기준원, etc.>
- Access path: <how Claude reads each — MCP/connector, exported extract, pasted, or subagent-fetched>

## Constraints & politics
- Required sections / template / brand:
- Forbidden topics / sensitivities:
- Who is skeptical / who must be convinced:
- Past versions that failed and why:
- Q&A risks — toughest expected questions:

## Open questions (Claude fills as it works)
-

## Decisions log (append-only)
-

## Verification ledger (populated in Stage 3)
| Slide | Claim | Class (internal/external/derived) | Source tag | Check method | Status |
|---|---|---|---|---|---|
```

### 10.3 Reading source material
- If sources are reachable via connector/MCP (Drive, internal DB tools): read them and record what was learned in the brief's *Decisions log*. Confirm with the user before running expensive or write-capable calls.
- If not reachable (corporate network blocks, proxy/SSL): say so plainly and ask the user to paste an extract or run their export and drop the file in. Do not invent the data.
- Track gaps in *Open questions* as they arise; do not let them accumulate.

### 10.4 Exit — the single elicitation pass
The brief is sufficient when Claude can reason about trade-offs and edge cases without re-asking basics. Show the filled brief (or summarize the diffs), confirm thesis + spine + slide cap in one round, then proceed to autonomous build. This is the one scheduled user interaction; everything after is autonomous except the cases in §11.0.

---

## 11. Stage 2 — Outline, then build into the deck file

### 11.0 When Claude pauses for the user
The design target is **one upfront interaction** — the brief (§10) — then an autonomous build. After the brief, Claude returns to the user only in these cases:
- **Mandatory:** `needs-human` verification items (§13) — a number whose source isn't reachable, or an external fact no authority resolves. These cannot be invented, so they must be routed to the user.
- **Mandatory:** the final handoff report (§15) — a summary + the verification ledger; a report, not a gate to negotiate.
- **Conditional only:** a genuine fork Claude cannot resolve from the brief — two defensible deck structures, a finding that contradicts an earlier slide, or a self-run ghost-deck test (§11.2) that fails and can't be fixed without knowledge only the user has. No fork → no interruption.

Claude self-runs the ghost-deck test, the style choice, and the full-deck re-read autonomously and records the calls in the brief's *Decisions log* instead of asking. It does **not** re-interrogate the user item-by-item. The brief is the single elicitation pass.

### 11.1 Choose the spine
Confirm the spine from the brief (default by type per §1/§6).

### 11.2 Ghost-deck outline — the critical step (self-run)
Generate the whole deck as **action titles only** — no body, no notes. Apply the ghost-deck test (§2) yourself: read the titles in sequence and confirm they tell the complete argument. Cross-check against the required architecture (§6): decision/question slide, conclusions-that-survive-Q&A, references slide. Verify slide count vs. the §7 cap. Write the outline into `slides/<slug>/deck.md` as titles + empty scaffolds and log the structure choice in the brief. Surface to the user only if the ghost deck won't hold without knowledge you don't have (a missing logical link only they can supply) — otherwise proceed to building.

### 11.3 Scaffold
Each slide in `deck.md`:
```
## Slide N: [Action Title]
**Key message**: [1 sentence — takeaway restated]
**Body**: [3–5 bullets, ≤40 words]
**Visual hint**: [chart type, axes, annotation, de-emphasis]
**Sources**: [src tags for every number; as-of date for internal]
**Speaker notes**: [3–6 sentences: context / transition / Q&A]
```
Placeholders read `[To be written]`.

### 11.4 Build order
Draft the highest-uncertainty slide first — usually the **core finding / recommendation**. Then supporting evidence → context/motivation → title + summary last.

### 11.5 Per-slide loop (run autonomously; `str_replace` into the file)
For each slide:
1. Decide the single takeaway. If it's doing two things, split it and update the outline.
2. Draft body per §2–§5: action title, one annotated exhibit, ≤40 words, every number tagged `[src: …]`. Where a number is *derived*, write the formula in the Sources line so §13.4 can recompute it (e.g., `variance = actual − plan = 12.3 − 11.8`).
3. Draft speaker notes per §4 (not a body reprint).
4. Log any assumption or missing input as a `[Source needed]` tag and a line in the brief's *Open questions*. Never paper over a gap with a plausible number — an unfilled tag is required, not optional.
5. Never reprint the whole deck in chat; point to the file.

Do **not** batch-generate all slides in one shot — that breaks the action-title discipline. Building into the file one slide at a time is the autonomous equivalent of the synchronous loop.

### 11.6 Near-complete re-read (self-run)
At ~full draft, re-read the whole deck yourself and check: ghost deck still holds; no contradiction/redundancy; every slide carries weight; no `[Source needed]` left untracked; speaker notes don't repeat bodies; slide count within budget. Apply surgical `str_replace` fixes directly. Then move to Stage 3. No user pause unless a contradiction needs a decision only the user can make.

---

## 12. Multi-session advice via subagents (replaces parallel chat sessions)

When a structural or analytical call is genuinely uncertain (which spine, whether a finding is load-bearing, whether a robustness concern is fatal), spawn a **fresh subagent** with only the relevant slice — not the whole build context — and ask for an independent read. This is the local equivalent of the user's cross-model advisory sessions. Decoupling matters for the same reason it does in CoVe (§13.2): an advisor that sees your rationale tends to ratify it. Summarize the subagent's take, then decide. Use the user's existing harness/Task primitives if available; otherwise a single Task subagent per question.

---

## 13. Stage 3 — Grounding & Verification (the hallucination gate)

**Goal:** before the deck ships, every claim is either grounded in an identified, independently checkable source, revised to match the source, or flagged for the human. Nothing ships `unsupported`. This is the load-bearing addition for internal-data reporting.

The design composes four established methods. Cite them in the build log so the approach is auditable:
- **RAGAS faithfulness** (Es et al., 2023; `explodinggradients/ragas`) — decompose output into atomic claims, NLI-check each against its cited source, score = supported/total; treat ≥0.9 as grounded.
- **Chain-of-Verification / CoVe** (Dhuliawala et al., Meta, 2023; arXiv 2309.11495) — verification questions answered **decoupled from the draft**, so the verifier can't copy the draft's error. → run verifiers as subagents that see only claim + source.
- **RARR** (Gao et al., ACL 2023; `anthonywchen/RARR`) — *retrieve → agreement-gate → revise only if contradicted → attach citation*. Used for external facts.
- **AIS — Attributable to Identified Sources** (Rashkin et al., 2023) — the acceptance bar: a claim is OK only if verifiable against an independent source document.

Classify each claim into **internal** (from the company DB), **external** (accounting/finance/tax knowledge), or **derived** (computed from other numbers). Each class has its own check.

### 13.1 Extract atomic claims (subagent)
Run an extractor subagent over the deck: decompose each slide into atomic, pronoun-free claims (RAGAS statement decomposition). Output a claim list keyed by slide. Over-splitting is safer than missing a claim.

### 13.2 Internal claims — entailment against the cited extract (decoupled subagent)
For each internal claim, hand a **grounding subagent** *only* the claim text and the cited source extract (the actual query result / cell / row at the stated as-of date) — **not** the deck narrative or the drafting rationale. The subagent returns `entailed / contradicted / unsupported` + a one-line rationale. This decoupling is the CoVe principle: a verifier with the draft's reasoning rationalizes the draft's mistake.
- If the source extract isn't available, the claim is `unsupported` → it cannot be the verifier's job to find the data; flag for the human to supply the extract.
- Slide faithfulness = supported claims / total. Below ~0.9 → the slide goes back to §11.5.

### 13.3 External claims — RARR retrieve-and-revise (subagent)
For each external claim (a tax rate, a K-IFRS/IFRS treatment, a statutory threshold, a market figure):
1. Generate verification questions that interrogate the claim.
2. Retrieve from an **authoritative primary source** — 국세청(NTS)/홈택스, 한국회계기준원, IFRS Foundation, the relevant statute/standard text — via web or a curated internal KB. Prefer primary over aggregators/blogs.
3. **Agreement gate:** does the evidence contradict the claim? If no, attach the citation and stop. If yes, **revise the claim to match the evidence**, then re-tag.
4. If no authoritative source resolves it, mark `needs-human` — do not let an unresolved external fact ship.

Caution (from deep-research-agent citation studies): more retrieval ≠ more reliable citation. A few authoritative sources beat a pile of weak ones; always confirm the retrieved source actually says what the citation claims, not merely that it exists.

### 13.4 Derived numbers — deterministic recompute (code, not an LLM)
Arithmetic is where finance decks break, and an LLM judge is the wrong tool. For every derived figure, recompute it **in code** from its inputs (the formula recorded in the Sources line, §11.5):
- variances, growth %, margins, run-rates, totals, weighted averages, FX conversions, reconciliations.
- Keep it dependency-free (stdlib arithmetic) so it runs inside the corporate network with no `pip install`.
- Recomputed ≠ stated → fix the number, then re-run §13.2 on it. Cross-foot tables (rows and columns sum to stated totals).

### 13.5 Self-consistency sweep (subagent)
One subagent reads the full deck for *internal* contradictions: the same metric stated two ways, a number on slide 7 that conflicts with slide 3, an as-of date mismatch, an undefined acronym, a claim in the conclusion not supported by any findings slide.

### 13.6 The verification ledger is the exit artifact
Populate the brief's ledger: every claim → class → source tag → check method → status (`grounded / revised / unsupported / needs-human`). **Exit condition:** no row is `unsupported`; every `needs-human` has been routed to the user with the exact question; every derived number passed recompute; self-consistency is clean. Routing `needs-human` items is the one mandatory mid-build user contact (§11.0); resolve them, then move to reader testing.

---

## 14. Stage 4 — Reader Testing (subagents)

Test whether the deck works for someone who wasn't in the room — critical because it ships as PDF without the presenter.

1. **Audience questions** — generate 5–10 realistic Q&A questions for this deck.
2. **Answer test** — for each, a subagent with *only the deck markdown* answers; record right/wrong/uncertain.
3. **Ghost-deck reconstruction** — a fresh subagent gets only the action titles in order and reconstructs the argument. If it can't, the ghost deck is broken → fix titles (§2) before anything else.
4. **Self-sufficient slide** — a subagent gets one slide at a time, no speaker notes, and states the takeaway. Each must read solo (§3).
5. **Ambiguity sweep** — a subagent flags ambiguity, false assumptions, undefined acronyms, contradictions.

Summarize what each subagent got right/wrong. For each issue, fix the responsible slide(s) via §11.5 surgical edits; re-test only the changed slides plus any whose context shifted. **Exit:** subagents reliably identify the main argument, answer audience questions correctly, stop surfacing new gaps, and reconstruct the ghost deck cleanly.

---

## 15. Final Review & Handoff

Reader testing passing means *near* done, not done. Before completion:

1. **User ownership** — recommend the user do a final read-through. The verification ledger covers grounded claims, but the user owns the deck and must confirm judgment calls Claude can't (materiality, framing, what to disclose).
2. **Read aloud at pace** — speaking the notes verbatim catches timing and phrasing no subagent catches; ~1 min/content slide.
3. **Ledger audit** — confirm zero `unsupported`, zero unresolved `[Source needed]`, all `needs-human` closed.
4. **Fact spot-check** — names, dates, links, as-of periods, statistical interpretations; refinement can introduce subtle errors.
5. **Structure** — ends on conclusions (not "Thank You"/blank); references slide present; 2–3 appendix slides for the toughest Q&A.
6. **Impact check** — does it actually drive the audience to the intended decision/belief from the brief?

### 15.1 Completion
- **Build log** — keep this session (and the subagent verifications) linked in the deck folder. If the deck is challenged later, the log shows how the argument was assembled, what was verified and how, and what alternatives were considered.
- **Versioning** — `deck-v1.md`, `deck-v2.md`; freeze v1 before any major restructure.
- **Update from reality** — after the actual presentation, fold in what the audience really asked.
- **Design handoff** — the markdown + `Visual hint` fields are the design brief; hand off to the PPTX/design step.

---

## 16. Operating notes for local Claude Code

- **Files, not chat dumps.** `create_file` for the brief and deck scaffold; `str_replace` for every per-slide edit; confirm the file path after edits; never reprint the whole deck inline.
- **Brainstorming stays in chat or the brief's scratch area — not in `deck.md`.** The deck file contains only the deck.
- **Subagents are the unit of independent judgment.** Verification (§13), advice (§12), and reader testing (§14) all run as subagents precisely because they must be decoupled from the build context. If the user's harness/Team primitives are available, use them; otherwise one Task subagent per job.
- **Network reality.** When a source or package isn't reachable (corporate proxy/SSL, npm/PyPI blocks), say so and ask for an extract or a vendored path; keep verification code stdlib-only. Never substitute a guessed number for an unreachable source.
- **One elicitation pass, then autonomy.** The brief (§10) is the single scheduled user interaction. After it, build and log; return to the user only for `needs-human` verification items and the final handoff, plus genuine forks (§11.0). Do not re-interrogate.
- **The §13 gate is non-negotiable even in freeform mode.** A user can skip the brief or the per-slide checkpoints; they cannot skip grounding for a deck built on internal numbers.
