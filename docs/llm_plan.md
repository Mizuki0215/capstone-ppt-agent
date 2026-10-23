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

---

## 9. 為什麼不是 model training

（2026-10-23 決策記錄。若 reviewer 問「為什麼不用學習式方法」，答案就是這一節。）

「train model」在這個題目下可以指三件完全不同的事，要分開判斷：

| 想 train 什麼 | 需要什麼 | 對這份論文的影響 |
|---|---|---|
| **① 生成器**（fine-tune LLM 由 paper 出 deck） | ≥1,000 對 (paper, deck)；GPU；數週調參與評估 | 直接對撞同題其他同學的主線（brief 的 Topic 2 本身），而**完全答不到**本研究問的問題 |
| **② 學習式 detector**（由 slide 圖判斷有無缺陷） | 大量標註圖；正是 SlideAudit 做過的事（2,400 張、付費標註員） | 會摧毁本研究的核心主張：deterministic、可審核、reference-free |
| **③ 學習式 repair policy**（RL / imitation） | 編輯軌跡（PPTArena 有 1,300 條人手編輯） | 有趣，但係另一個 project；單人 20 週做唔完 |

### 三個決定性理由

**1. 論文的主張與「學習式判斷」互斥。**
proposal §5 寫得很白：「these are arithmetic, not judgements. A rule can be audited; a model's opinion cannot.」整份 proposal 相對 PPTPilot 的差異化，就是「deterministic 而唔係 VLM judge」。若把 detector 換成訓練出來的模型，就變回自己批評的那個東西——reviewer 會即時指出。

**2. 標註預算只能驗證，不能訓練。**
本項目的標註是 110 張、兩位標註者獨立、計 per-class κ。這個數量：
- **足夠**驗證一個 deterministic detector 的 precision/recall（每個 gate 約 18 張）
- **远远不夠**訓練任何 detector（110 張 × 6 類，未計類別不平衡）

而 proposal §6 已經用同一個邏輯講過閾值：40 張校準 slide 支撐不起 6 個 fit 出來的閾值。**訓練比 fit 閾值需要更多數據**，所以同一條理由更強地否決 training。

**3. 訓練一個更好的生成器，會令本研究的問題更難答，而不是更容易。**
研究問題是因果的：「量度本身帶來幾多改善？」若生成器同時在變，A2 − A1 就不再乾淨。把生成器固定住（用現成 API、cache 凍結），反而是**實驗設計的需要**，不是偷懶。

### 成本對照（單人 250 h 預算）

| 路線 | 額外工時 | 額外風險 | 答到研究問題？ |
|---|---|---|---|
| 用 API + cache（本計劃） | 0（已計入 L1–L13） | provider 更新版本（用 snapshot id 記錄） | ✅ |
| Fine-tune 生成器 | +60–80 h | 數據對齊、評估成本、與他人撞題 | ❌ |
| 訓練 detector | +40 h | 110 張樣本訓練必失敗 | ❌（且摧毁主張） |

### 如果你仍然想有「學習」成分：有一個便宜且加分的做法

不是取代 deterministic detector，而是**用它做對照組**，證明 deterministic 在這個任務上更值得信：

| ID | Job | 驗收 | h |
|---|---|---|---|
| S1 | 由 P3.10 的 110 張 slide 渲染 PNG | 110 張齊 | 1.0 |
| S2 | 抽特徵（尺寸、面積佔比、字數、色差） | 特徵表 110 × N | 1.5 |
| S3 | 訓練 logistic regression / 小 CNN，5-fold CV | per-gate F1 | 2.0 |
| S4 | 同 deterministic detector 比 per-gate F1 + 樣本效率曲線 | 一張圖：F1 vs 訓練樣本數 | 1.0 |
| S5 | 寫入報告「為何選 deterministic」 | 半頁 + 圖 | 0.5 |
| | **合計** | | **6.0 h** |

這 6 小時做的是**辯護**，不是取代：它用數據回答「你為什麼不用 ML」，而唔是用 ML 去回答一個唔需要 ML 的問題。要就加入 WBS 做 S-block（總工時 208.3 → 214.3 h）。

---

## 10. claims：LLM 直讀，不用 RAG（決策記錄 2026-10-23）

問題：抽 claim 這一步，直接讓 LLM 讀該節，還是先做檢索再餵給它（RAG）？

**決定：直讀。不建 vector store，不用 embedding，不做檢索。**

### 為什麼

| 理由 | 數字 |
|---|---|
| **要檢索的語料本來就塞得入 context** | 一節 ≈ 300–800 tokens；8 頁論文全文 ≈ 4–6k tokens。RAG 解決的是「context 裝不下」，這裡沒有這個問題 |
| **RAG 會為文字層加入新的機率成分** | 檢索可能漏掉關鍵句 → claim 少了 → 下游 outline/coverage 全部受影響。而 A2 − A1 要乾淨，文字層的變數愈少愈好 |
| **接地不是靠檢索，是靠事後的確定性錨定** | claim 回來之後用 token overlap 對回原文句，得 `sec3:s12`；對不上就丟（fail closed）。檢索只改變「模型看到什麼」，不保證「它講得對」——V1 數字檢查才是保證 |
| **每個零件都要 sweep** | chunk size、embedding model、k 三個新參數 = 三個新掃描維度。20 週單人項目，不值得為一個不存在的問題加三個旋鈕 |

### 真正要的三個機制（看起來像 RAG，其實不是）

1. **結構化切塊**：`parse.py` 已按 section 切好。太長的 section 按 paragraph 做 map-reduce（map 逐段抽、reduce 合併去重），切法由結構決定，不是相似度。
2. **事後錨定**：claim → 最相近原文句（token overlap），產生 evidence id。這是**歸因**，不是檢索。
3. **跨節連結**：同一 claim 在 abstract 出現、在 results 有數據支撐，用同一套 overlap join 連起來。同樣不需要向量。

### 什麼情況才值得回頭用 RAG（目前全部在 scope 外）

- 處理 100 頁以上的論文或整本書 —— 那時 context 真的裝不下。
- 要判斷「這篇論文與既有文獻是否一致」—— 屬於 claim correctness，proposal 第 6 節已列為 scope 外。
- 想用類似 annotated claim 做 few-shot exemplar 檢索 —— 可以做，但必須當成**一個 swept variant** 報告，不可以入主線。

### 成本

直讀：0 額外工時（L5 本來就是這樣）。
RAG：+8 h（索引、檢索、評估）+ 一個新掃描維度 + 一個新失敗模式（檢索漏）。

> 一句總結：**這裡的瓶頸是「講得對不對」，不是「看不看得到」。看得見的問題不存在，所以不需要檢索；對不對的問題用確定性檢查解決，所以也不需要檢索。**
