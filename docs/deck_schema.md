# deck.json — 一份「可以直接再生成」的簡報資料結構

狀態：2026-10-23 · 實作在 `src/deck.py`（15 個測試）· 對應 WBS P1b L3–L7

---

## 0. 一句話

**簡報不是一張圖，而是一組「可追溯的斷言」。** 每一句 bullet 都要指回一條 claim，每一條 claim 都要指回論文某一行。沒有這條鏈，就談不上「驗證」。

## 1. 研究：四個系統的 intermediate representation

| 系統 | 它的 IR | 存了什麼 | 缺什麼（對我們而言） |
|---|---|---|---|
| **Doc2PPT**（2110.11796） | 階層式：section plan → slides | 章節大綱、每頁要點 | 沒有 claim→原文的連結，無法驗證 |
| **PPTAgent**（2501.03936） | slide 叢集 + **content schema** | 每類 slide 的「元素類型 + 內容組織」 | schema 是學來的模板，不是可審核的資料 |
| **ReDeck**（2609.00194） | 狀態元組 `st = (d_t, r_t, C_t)` | deck 表示、渲染幾何、診斷 | 三者混在 agent 狀態裡，沒有落成檔案 |
| **SLIDEFORGE**（2609.03109） | structured artifact | 可原生編輯的物件 | 定義了「成功」的六個準則，但無 claim 層 |
| Marp / Slidev | Markdown → AST | 純文字 + 少量版面提示 | 冇幾何座標，算不到 gate |

ReDeck 那個三元組是整個設計的起點：**表示（寫什麼）、幾何（放在哪）、診斷（哪裡壞了）是三件不同的事，應該分三個檔案。**

- <https://deepwiki.com/marp-team/marp/1.1-core-components>
- <https://deepwiki.com/slidevjs/slidev/3-markdown-processing-system>

## 2. 三個檔案，三個責任

```
deck.json     ← 寫什麼      claims · headlines · bullets · notes     （文字層，凍結）
layout.json   ← 放在哪      每個 shape 的 x/y/w/h、字級、顏色          （版面層，可修）
metrics.json  ← 哪裡壞了    每個 gate 的違規、SRR、deck-ready          （量度層，只讀）
```

**為什麼一定要分開**：repair loop 只准寫 `layout.json`，不准碰 `deck.json`。
如果它可以兩邊都改，那麼「loop 令 deck 變好了」就分不清是**排版修好了**還是**文字改好了** —— 而 A2 − A1 就是這份論文的主結果。分檔就是這條紀律的執行機制，不是整潔癖。

## 3. deck.json 的欄位

### 3.1 deck 層

| 欄位 | 型 | 說明 |
|---|---|---|
| `schema_version` | str | `"1.0"`；日後 migration 用 |
| `title` | str | 論文標題（不是 deck 標題） |
| `requirement` | obj | 這次的要求：`duration_min`、`audience`、`focus`、`must_include`、`must_exclude`。**凍結後不可改**，因為所有實驗臂要同一個要求 |
| `claims[]` | list | 見 3.2 |
| `figures[]` | list | 見 3.3 |
| `slides[]` | list | 見 3.4 |
| `meta` | obj | source path/sha、pages、generator version、model id、prompt version、created_at |
| `metrics` | obj | 量度結果（由 `metrics.json` 匯入，方便單檔傳遞） |
| `human_edits[]` | list | 見 §7 |

### 3.2 claim（選段的結果，`src/schema.py` 產生）

```json
{"claim_id": "c3", "section_type": "results", "importance": 3,
 "text": "PPTAGENT outperforms baselines by 12 points on content quality",
 "evidence": "sec5:s2",
 "selected": true, "rule": "table:12:results", "why": "kept in a 12 min talk"}
```

`rule` 與 `why` 是**審核用的欄位**，不是裝飾：任何一條 claim 為何被保留或被剔走，都可以指回一條規則（`table:12:results`、`importance:cut2`、`hard:results`、`req:include`、`req:exclude`）。

### 3.3 figure

```json
{"figure_id": "f2", "page": 2, "kind": "figure",
 "caption": "Figure 2: Overview of the PPTAGENT workflow...",
 "image": "build/figures/PPTAgent_2501.03936/p02_01_figure.png",
 "bbox": [71.2, 68.5, 524.0, 300.2], "area": 106256}
```

### 3.4 slide

```json
{"index": 2, "role": "result", "section_type": "results",
 "headline": "A shared workflow beats per-slide generation",
 "claim_ids": ["c3"],
 "bullets": [{"text": "12 points higher content score than baselines",
              "claim_id": "c3", "importance": 3}],
 "notes": {"text": "Open with the gap...", "target_sec": 90,
           "transition": "That gap is why we measure rather than judge."},
 "figure_id": "f2", "budget_sec": 90, "origin": "llm"}
```

四個關鍵選擇：

1. **`role` 與 `section_type` 分開**。`role` 是這張 slide 在**敘事**中的功能（problem / method / result / conclusion），`section_type` 是它取材自論文的**哪一類章節**。同一張 result slide 可以取材自 experiments；分開之後，G3/G6 可以用 role 設下限，而選段用 section_type 判 1/0。
2. **`headline` 是斷言，不是章節名**。`"Evaluation"` 不合格，`"A shared workflow beats per-slide generation"` 合格 —— 這條規則由 outline 階段驗證（禁字表）。
3. **bullet 必帶 `claim_id`**。這是 V2 檢查的把手：對不上就是假的接地。
4. **`notes.transition` 獨立成欄**。講稿最常失敗的地方是「每張各自精采，但連起來跳」。把轉場句變成一個必填欄位，它就不能被略過。

## 4. 不變量（`Deck.validate()` 強制）

| # | 規則 | 為什麼 |
|---|---|---|
| 1 | 每個 `bullet.claim_id` 必須是**已選中**的 claim | 防止講了被剔走的內容 |
| 2 | `bullet.claim_id` 必須在該 slide 的 `claim_ids` 內 | 防止引用沒有列在這頁的 claim |
| 3 | `figure_id` 必須存在 | 防止指向空氣（就是我們之前那個「有 caption 冇圖」的 bug） |
| 4 | `Σ budget_sec ≈ duration_min × 60`（±30s） | 防止 12 分鐘的 talk 排了 20 分鐘的內容 |
| 5 | `role ∈ ROLES`、`origin ∈ ORIGINS` | 下游依賴這些值做決策 |
| 6 | claim_id / figure_id 不重複 | 引用必須唯一 |
| 7 | ≥3 張 slide | 少於 3 張就不是一場 talk |

`validate()` 回傳**全部**錯誤而不是第一個 —— 因為一次修完比逐個撞牆快。

## 5. 「唔同 part 用唔同 prompt」

十種 `section_type` 各有一個 spec（`src/deck.py: PROMPT`），四個欄位：

| 欄位 | 作用 |
|---|---|
| `goal` | 這一頁要令觀眾得到什麼 |
| `bullets` | 幾條（results 允許多，conclusion 只准 2–3） |
| `shape` | 論證的形狀（results：每條帶一個數字；analysis：一條一個對照） |
| `forbid` | 這一類最常見的錯（results 不准報新數字；limitations 不准防衛式語氣） |

例：

```
results    goal=the headline number and what it means
           shape=each bullet carries a number that appears in the evidence
           forbid=no new numbers, no rounding up, no interpretation beyond the data
limitations goal=one honest boundary
           forbid=no defensive framing, no promises about future work
```

**十個 prompt 由一個 `build_prompt()` 產生**，不准手寫。理由：手寫十個就一定有十個版本漂移，而你要在論文裡聲稱「所有 slide 用同一套約束」。

## 6. 要求 → prompt 的接口（唔離題的機制）

「唔同人有唔同要求」= 同一個 `Requirement` 表（§3.1）。它由三步保證唔離題：

```
Requirement（凍結）
   ├─ ① 選段：規則表決定邊啲 claim 入（可審核，不靠模型）
   ├─ ② 生成：build_prompt() 只餵該頁自己的 claim 文字（allow-list）
   └─ ③ 驗證：V1 數字必須出現在 evidence；V2 bullet 必須對得回 claim
```

**「smooth」同「on-topic」是兩個相反的力，所以分兩層做：**

- **smooth（連貫）** 來自 **outline 這一層**：它看得到全部被選中的 claim，負責排序、轉場、時間分配。
- **on-topic（不離題）** 來自 **生成這一層**：它只看得到自己那一頁的 claim，模型沒有機會偏離。

這兩層就是 `plan_selection.md` 裡「抽取 / 組合」的同一招。**看得全的地方不寫字，寫字的地方看不全。**

## 7. 編輯模型：直接改，還是指令？（你問的第 4 條）

**答案：兩者都要，但分層。**

| 改法 | 動哪個檔 | 何時允許 | 後果 |
|---|---|---|---|
| **A. 給指令**「第 3 頁簡單一點」 | `deck.json` | 隨時 | 文字層 v+1；該頁 `origin="human"`；重跑 V1/V2 |
| **B. 直接改版面**（拖、縮、換色） | `layout.json` | 隨時 | 幾何改變，重跑 gate；`origin` 不變 |
| **C. 直接改文字**（在 PowerPoint 裡打字） | `deck.json` | 允許，但要記錄 | 同 A，且 `human_edits` 記 `kind="direct"` |

**為什麼唔可以只准 A**：真實用戶一定會直接打字，禁止只會令工具沒人用。
**為什麼唔可以只准 B**：直接改字會令「這份 deck 由系統生成並驗證」這句話失效，而論文的主張依賴它。

所以規則寫死在 `record_edit()`：

- 改 `layout` 層不准碰文字欄位（`headline`/`bullet`/`notes`）→ 直接報錯
- 改 `deck` 層的文字 → 該頁 `origin` 變 `human`，並記錄 before/after
- **主實驗只用 `origin` 全部是 `llm` 的 deck**；有人手改字的 deck 只入 demo，不入 ablation

這條界線同時保護了兩件事：產品的可用性（人可以改），和實驗的有效性（A2 − A1 乾淨）。

**不支援**：改 claim registry。那等於改「論文說了什麼」，屬於作者的工作，不是工具的。

## 8. 落地狀態

| 項目 | 狀態 |
|---|---|
| `src/deck.py`：Deck / Slide / Bullet / Notes / Figure + `validate()` | ✅ 完成，15 個測試 |
| `PROMPT`：10 個 section_type 的 spec | ✅ 完成 |
| `build_prompt()`：要求 + evidence allow-list + 禁止項 | ✅ 完成 |
| `record_edit()`：三種改法 + provenance | ✅ 完成 |
| 由 `plan.json` 遷移成 `deck.json` | ⬜ 下一步（L5 接線時一併做） |
| `layout.json` / `metrics.json` 落檔 | ⬜ L8（與 P2 的 gate 一齊做） |
| 人評介面（改完之後重跑 gate） | ⬜ P6 demo |
