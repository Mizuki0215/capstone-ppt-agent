# 生成層設計：outline → bullets → speaker notes

狀態：2026-10-23 · 對應 WBS P1b（L1–L13）
一句話：**LLM 只做三件事——選論點、壓縮成 bullet、展開成講稿；其餘（切段、對齊、驗證、排版、gate）全部 deterministic。**

---

## 1. 為什麼一定要 LLM（而唔係再加 heuristic）

現時 `src/compose.py` 是 pure heuristic：抽句子、打分、clip 到 14 字。它跑得通，但輸出有三個結構性毛病，可以直接在 `build/plan.json` 見到：

| 觀察 | 證據 |
|---|---|
| **章節鏡像，不是論證** | 8 個 section → 8 張 slide，第一張叫 `Abstract`。deck 讀起來係論文目錄，唔係 12 分鐘的論證 |
| **bullets 是原句，不是壓縮** | `We propose a hierarchical sequence-to-sequence approach to tackle our task...` — 14 字，但一個字都冇刪，只是截斷 |
| **notes 是模板** | `This slide covers X. Open with: <bullet 0>. Then move to: <bullet 1>.` — 同 bullet 重複，冇轉場，冇時間預算 |

brief p6 第 3 階段本身寫明要用 LLM：「Generate a logical slide outline, concise bullet points and detailed speaker notes **using LLMs**」。所以問題不是「要唔要」，而是**邊一段交畀 LLM、用什麼 contract、怎麼驗**。

---

## 2. 分層決定

| 階段 | 由邊個做 | 為什麼 |
|---|---|---|
| A 切 section / 抽 figure caption | **deterministic**（`parse.py`，已做） | 可重現；換 model 唔應該改到 segmentation |
| B **outline**（邊 8–12 張、每張講什麼、什麼角色） | **LLM ×1 per paper** | 要判斷「哪些是有用的論點」，需要語意理解，規則做唔到 |
| C **claims**（每篇 5–8 條，供 coverage 量度） | LLM ×1，**然後人手凍結** | proposal 已寫明 coverage 要 5–8 claim；凍結後可當標註用 |
| D **bullets**（壓縮到 ≤14 字 ×3–5 條） | **LLM ×1 per slide** | 壓縮即改寫，規則做唔到 |
| E **speaker notes**（講稿） | **LLM ×1 per slide**（同 D 同一個 call） | 要在 bullet 之上展開，且要知下一張講什麼 |
| F 版面 / 渲染 | deterministic（`render.py`） | 已做；不變 |
| G 驗證（grounding + gate） | **deterministic** | 本項目的核心；**唔可以用 LLM 驗 LLM** |

> 關鍵一句：**text layer 生成一次就凍結，之後所有改動只准發生在 layout layer。**
> 因為這份研究要問「inspection 帶來幾多」，如果 repair 同時改文字，就分不到是 inspection 的功勞還是改寫的功勞。W2 的 guardrail（唔准加內容、唔准改數字）就是靠這一條成立。

---

## 3. 三個 LLM 階段的 contract

### B：outline（1 call / paper）

輸入：標題、每節標題 + 首兩句、claims 清單、figure caption 清單。
輸出（strict JSON）：

```json
{"deck_title": "...", "talk_minutes": 12,
 "slides": [
   {"idx": 1, "role": "title|agenda|problem|method|result|figure|conclusion",
    "headline": "一句斷言，不是章節名",
    "source_sections": [3],
    "claim_ids": ["c2"],
    "figure": "Figure 3" | null,
    "budget_sec": 90}
 ]}
```

Prompt 要寫死的三條：
1. **一張 slide 只講一個 claim**；claim 必須來自提供的 `claim_ids`，唔准自創。
2. **headline 唔可以是章節名**（禁 `Abstract` / `Introduction` / `Method(s)` / `Results` / `Related Work`）。
3. 總秒數 = 12 × 60，逐張分配到 `budget_sec`，加起來要剛好。

驗收（deterministic，唔問 LLM）：
- 8 ≤ 張數 ≤ 12
- 冇 headline 撞禁字表
- 每個 `claim_id` 都真係存在
- `sum(budget_sec) == 720 ± 30`
- 至少 1 張 `result`、剛好 1 張 `conclusion`

### D+E：bullets + notes（1 call / slide）

輸出：

```json
{"bullets": [{"text": "...", "evidence": "sec3:s12", "kind": "claim|number|method"}],
 "notes": "...", "est_sec": 90}
```

Prompt 注入的硬約束（同 gate 對齊，唔好靠事後修）：
- bullets 3–5 條、每條 ≤14 字、全張 ≤140 字（= G6 的 content 上限）
- 唔准有 citation 標記（`(Author, 2025)`）
- **原句的數字要原樣保留**，唔准出現原文冇的數字
- notes 120–200 字、必須包含：① 一句唔可以照抄 bullet 的開場；② 一句轉場（`Next / Moving on / To sum up`）；③ 一句時間提示（`about 90 seconds`）
- 每條 bullet 要帶 `evidence`（`sec<idx>:s<句子號>`），做 grounding 的把手

### 兩段式 notes

先一個 call 出 bullets + notes；跑完 notes 指標，**只有不合格的 slide 才發第二次 call 補 notes**（唔重做 bullets）。原因：notes 要長，跟 bullets 同一個 call 出，模型會偏向短。

---

## 4. 驗證：唔靠 LLM 驗 LLM

| # | 檢查 | 方法 | 抓什麼 |
|---|---|---|---|
| V1 | **數字接地** | 抽出輸出所有 `\d+(\.\d+)?%?`，逐個在該 slide 的 `source_sections` 原文找；找唔到 = fail | 幻覺數字（LLM 最危險的失敗） |
| V2 | **evidence id 存在** | 每個 `sec:s` 都要在 `deck.json` 對得上 | 假 grounding |
| V3 | **長度** | 字數 / bullet 數，直接數 | 超 G6 |
| V4 | **notes 品質** | wpm = 字數 / est_sec；轉場 regex；同 bullets 的 Jaccard < 0.5 | 講稿變 bullet 回聲 |
| V5 | **禁字** | headline 唔可以等於章節名 | 目錄式 deck |

**V1 同時解決咗 brief p6 第 5 階段的要求**：brief 寫「check factual support and layout overflow」，而 proposal 現時只覆蓋 overflow。V1 是一個**機械可判**的 factual-support 檢查（數字有冇出現在原文），唔需要判斷 claim 對唔對——所以它唔會撞 proposal 第 6 節「claim correctness 唔在範圍」的界線。這一點要寫入 proposal 的 §7，因為 reviewer 一定會問「brief 的 factual support 你點做」。

---

## 5. 成本、cache、可重現

| 項目 | 數 |
|---|---|
| 每篇 calls | 1 (outline) + 10 (slides) ≈ 11 |
| 每篇 tokens | ≈ 8k in / 2.5k out |
| 8 篇總計 | ≈ 64k in / 20k out |
| 成本（gpt-4o-mini 級） | **≈ US$0.02** |
| 成本（旗艦級） | ≈ US$0.4 |

→ **成本不是約束**，所以唔需要為省錢犧牲品質。真正的約束是**可重現**：

1. **cache 以內容為 key**：`sha256(model_id, prompt_version, paper_sha, stage, slide_idx)` → `build/llm/<key>.json`，同時記 tokens / 成本 / 時間。
2. **`--offline` 只讀 cache**：ablation 重跑幾十次都零成本、零漂移。
3. **model id 寫入結果**：論文報告要寫明用邊個版本，因為 provider 會靜靜更新。
4. **temperature 0**（或 provider 支援的 seed），prompt 有版本號 `p1`、`p2`…，改 prompt 即係新 cache namespace。

現時 `llm_rewrite()` 有三個問題要換掉：per-slide rewrite 冇大綱（每張各自為政）、冇 cache（重跑就再付錢且結果會變）、出錯 `break` 會令後面全部 slide 靜靜退回 heuristic。

---

## 6. 三臂設計（呢個係 ablation 的地基）

| 臂 | 生成 | 驗證 | 用來答 |
|---|---|---|---|
| **A0 naive** | 1 個 call：paper → 整個 deck JSON | 唔用 | baseline；亦係區辨效度最低的一組 |
| **A1 staged** | B → D+E，cache 凍結 | 量度但**唔修** | A1 − A0 = staged pipeline + renderer 的貢獻 |
| **A2 staged + loop** | 同 A1（文字完全一樣） | 量度**並修 layout** | A2 − A1 = **inspection 的貢獻（本項目的主結果）** |

A1 同 A2 的文字必須 byte-identical，否則 A2−A1 唔乾淨。做法：A2 讀 A1 的 cache，只跑 repair。這一點寫落 `docs/ablation.md`（P5.2）之前就要在 code 上成立。

---

## 7. 新增 job（WBS P1b）

| ID | Job | 驗收 | h |
|---|---|---|---|
| L1 | cache 層 + prompt 版本號 | 同一輸入重跑 0 call、byte-identical 輸出 | 2.5 |
| L2 | provider client（retry / timeout / 成本記錄） | 一次 429 會 retry 而唔會 crash | 2.0 |
| L3 | outline 階段 + JSON schema | 8 篇全部出得到合法 JSON | 3.0 |
| L4 | outline 驗證（5 條） | 5 條各有 unit test | 1.5 |
| L5 | bullets 階段 + 約束注入 | 違反約束的輸出會被 flag 而唔會靜靜過 | 2.5 |
| L6 | **grounding 檢查 V1 / V2** | 人手塞一個假數字，V1 一定抓到 | 2.5 |
| L7 | notes 階段 + 轉場 / 時間提示 | 8 篇 × 每張都有 3 個要素 | 2.0 |
| L8 | notes 指標 V4 + 失敗分類 | 出一個失敗原因統計 | 1.5 |
| L9 | 兩段式 notes 重試 | 不合格的 slide 只重發 notes | 1.0 |
| L10 | **A0 naive 臂**（1 call 全 deck） | 8 篇出得到 deck | 1.5 |
| L11 | `--offline` replay | 斷網都跑得完 8 篇 | 1.0 |
| L12 | 8 篇正式跑 + 品質檢視表 | 每篇 1 張表：V1–V5 結果 | 2.0 |
| L13 | prompt 迭代 3 輪（人手評） | 3 個版本有分數 | 3.0 |
| | **合計** | | **26.0 h** |

WBS 更新：P1.7（notes schema）併入 L7，故 P1 由 12 個 job 變 11 個、23.5 h 變 21.5 h；總工時 184.3 → **208.3 h**（+20% = 250 h），仍然在 300–400 h 預算內。

---

## 8. 要你決定的一件事

**用邊個 model / provider？** 三個選擇，成本差別唔大（全部 < US$1），所以要揀的是**可重現性**：

| 選擇 | 好處 | 代價 |
|---|---|---|
| OpenAI `gpt-4o-mini`（現時 `compose.py` 寫死的就是這個） | 便宜、JSON mode 穩、文獻對照多 | provider 會更新版本；要記錄 snapshot id |
| OpenAI 旗艦（`gpt-5` 級） | bullet 壓縮品質最好 | 貴 20 倍（仍然 < US$1）；生成慢 |
| DeepSeek | 最便宜、香港latency 低 | JSON mode 穩定性要自己驗 |

建議：**主用 `gpt-4o-mini` 級，另抽 5 張 slide 用旗艦做一次「品質上界」對照**——報告可以講「我們用便宜模型，唔係靠大模型堆品質」，對 reviewer 來講更有說服力。

另外要確認：**你有冇 OpenAI API key？** 現時環境冇 `OPENAI_API_KEY`；`api.openai.com` 通（401 = 通，只欠 key）。冇 key 的話 L1–L2 照做（cache 同 client 可以 mock），L3 之後就卡住。
