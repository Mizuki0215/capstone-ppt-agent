# 選段設計：requirement → 規則表 → claim 級 1/0

狀態：2026-10-23 · 對應 WBS P1c（Q1–Q5）· 實作在 `src/schema.py`（38 個測試）

---

## 0. 三個修正，全部接受

| 你提出的 | 為什麼對 | 落在哪裡 |
|---|---|---|
| **① 逐節 prompt 只准抽取，唔准寫故事** | 每節各自出 slide，次序就等於論文次序，正是 Gap 3 批評的目錄式 deck | 分成 extraction（逐節）與 composition（全域）兩層 |
| **② 1/0 要落到 claim 層，而且有分級** | results 一節內有主結果與附帶結果，整節 1/0 太粗；5 分鐘不是「有／無」而是「幾多」 | `Claim.importance ∈ {1,2,3}` + 兩段式決定（section 開關 → importance 門檻） |
| **③ 1/0 唔好交畀 LLM** | LLM 只留在邊界，中間可重現 | LLM 一次出 requirement 表；1/0 由 `TABLE` + `HARD_ON` + `CUTOFF` 決定 |

**①的補充（重要）**：「只准根據自己嗰節」只適用於**抽取與 evidence**，不適用於 outline。
理由就是你自己講的：result 那張要知道 problem 講了什麼。所以 grounding 是 **evidence id 的性質**（`sec3:s12` 指向一個可檢查的位置），不是「文字來自哪個窗口」。

**②的補充**：兩個階段各有自己的規則 id —— `table:12:method`（呢一節要唔要）與 `importance:cut2`（呢條 claim 要唔要）。分開記錄，才答得到「是選段錯，還是選 claim 錯」。

---

## 1. 固定詞彙（已實作）

論文標題五花八門，先對應到 10 類：`motivation · problem · background · related_work · method · setup · results · analysis · limitations · conclusion`。

`section_type()` 接受編號前綴（`3.2.1 Problem Formulation` → `method`）；**對應不到的 section 返 `None`，不可以帶 claim** —— 冇規則就唔應該有長度，唔可以靜靜當 0 或 1。

## 2. 規則表與優先次序

```
5 分鐘          12 分鐘
background   0      1
related      0      0
setup        0      0
analysis     0      1
limitations  0      1
method       1      1
results      1      1   ← 硬性
conclusion   1      1   ← 硬性
```

決定次序（寫入 `decide()` 的 docstring，因為次序本身是設計）：

1. **硬性**：results / conclusion 永遠保留
2. **must_exclude**：明確要求剔除的類型
3. **must_include**：明確要求保留（可繞過 importance 門檻）
4. **規則表**：section 類型 × talk 長度
5. **importance**：通過前四關後，短 talk 只留 importance ≥ 3

`Requirement` 在構造時就驗證：duration 只准 `5/10/12/15/20`，audience 只准 `expert/general`，未知 key 直接報錯，**矛盾要求報錯**（include ∩ exclude），**要求剔除 results 報錯**。即 `from_dict()` 是 fail-closed，唔會「猜」。

## 3. 我加的三點

### (a) retention 與 coverage 要分開兩個數

你講「coverage 要對住被選中的論點計，否則虛低」——對，但如果只報一個數，會變成另一個方向的虛高：5 分鐘 talk 剔走一半論文，coverage 仍然 100%。

```
retention = 保留的 claim / 標註的 claim     （這篇論文被講了多少）
coverage  = 進入 deck 的 claim / 保留的 claim（保留的內容有沒有真的做出來）
```

`accounting()` 一次出兩個數，並且拒絕 `kept ⊄ annotated`、`deck ⊄ kept`。報告的表格用兩欄，唔好合併。

### (b) 規則表本身是慣例，要 sweep

12 分鐘那欄的 `background=1`、`analysis=1` 冇證據支持，同 G6 的 140 字一樣是 convention。所以**同一條紀律**：報告兩個版本（寬鬆 = analysis/limitations 都留；嚴格 = 只留主結果），結論要在兩版都成立。這就把它從「我拍的數」變成「掃描過的範圍」。

### (c) `DEFAULT_REQ` 凍結

`DEFAULT_REQ = Requirement(12, "expert")` 而家是 module constant。**所有實驗臂（A0/A1/A2、PPTAgent、naive）都用同一個 requirement**，否則比較不公平；adaptive request 只出現在 demo。這一條要寫入 pre-registration（P5.1）。

---

## 4. 對評估的影響（你提防的地方，我同意）

| 影響 | 處理 |
|---|---|
| coverage 定義 | 用上面兩個數，唔好混 |
| 公平性 | 主實驗固定 12 分鐘 / expert；adaptive 只做 demo |
| 會不會變主線 | 唔會：貢獻仍然是量度 + repair（C1–C3）。這個功能放「系統特色」與 demo，唔入 RQ |

---

## 5. 已完成 / 未完成

| | |
|---|---|
| ✅ `src/schema.py` | Requirement / Claim / SectionType / TABLE / HARD_ON / CUTOFF / decide() / accounting() |
| ✅ `tests/test_schema.py` | 38 個測試：對照表、fail-closed、硬性規則、優先次序、determinism、兩個 coverage 數 |
| ⬜ Q3 | 自由文字 → requirement 表（LLM 一次）+ 失敗回退（1.5 h） |
| ⬜ Q4 | 接上 claim 抽取 → select → outline（2.0 h） |
| ⬜ Q5 | 寬鬆／嚴格兩版規則表掃描（1.5 h） |
