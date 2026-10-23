# DSAI4901 Capstone — Topic 2 Slide Agent 追進度計劃（單人版）

**專案**：AI Agent for Presentation Slides Design（論文 PDF → `.pptx` / Markdown）
**執行方式**：**單人獨立完成**（同題目有其他同學各自進行，非同一組）
**Coordinator**：Mr. Chen Xianwei（xianwei.chen@connect.polyu.hk）
**制定日期**：2026-10-18（Sun）｜**修訂**：改為單人 scope

---

## 0. 前提：單人嘅工時預算

假設每週投入 15–20 小時（與其他科目並行），20 週 ≈ **300–400 小時**。
這個預算下，brief 第 6 頁的 7 階段仍然做得完，但**範圍必須收窄**：

| 項目 | 原本（3 人可行） | 單人版 |
|---|---|---|
| 支援論文 | 任意排版 | **只支援單欄學術論文（single-column）** |
| 投影片數 | 12–15 版 | **10–12 版** |
| Template | 多套 adaptive | **2 套**（學術匯報、精簡版） |
| Held-out 測試集 | 12 篇 | **8 篇** |
| Baseline | 2 個 | **2 個（低成本）**：①固定模板人手填 ②純 LLM 一次過生成 |
| Figure 抽取 | 一般化 | 先做 caption-based，失敗則 fallback 為表格化描述 |

> 收窄唔等於交少貨：brief 要求嘅每一項（大綱、bullet、speaker notes、layout、agent loop、評估）一律照做，只是做得深而窄，而非廣而淺。

---

## 1. 現況

按 20 週時程，Stage 1+2 應在第 4 週完結，此刻應在 **Stage 3（大綱／bullet／notes 生成）**。
實際：**Stage 1–2 未開始**。

→ 策略：Stage 1+2 壓縮成 **8 日**（單人，唔可以再壓），第 9 日起進 Stage 3。
→ 硬約束：Proposal 2026-11-05 截止；第 9 頁要求截止前**一星期**交畀 professor 睇 feedback
　 ⇒ **實質死線 = 2026-10-29（Thu）**。

---

## 2. Block A｜2026-10-19（Mon）– 10-21（Wed）｜3 日｜補 Stage 1

目標：把研究空白同評估方法定死，避免一邊寫 code 一邊改 scope。

| # | 任務 | 產出 | 完成定義 |
|---|---|---|---|
| A1 | **深讀 2 篇**：Paper2Poster（Pang et al. 2025）、PPTAgent（2025）；**略讀 2 篇**：AutoPresent、DOC2PPT | `docs/reading.md` | 每篇 5 行：方法／限制／與你嘅差異 |
| A2 | 寫 gap statement（半頁） | `docs/gap.md` | 一句講清「現有系統做唔到 X，所以我做 Y」 |
| A3 | 定 scope 一頁（含上面嘅收窄表） | `docs/scope.md` | 寫明「唔支援」嘅清單，防止日後 scope creep |
| A4 | 收 8 篇 held-out 論文（要有 figure/table 嘅實證論文） | `data/papers/` | 命名一致，先入 3 篇做 spike |
| A5 | Evaluation rubric v0 | `docs/eval.md` | 5 個維度：readability、coverage、design、prompt adherence、cost/latency |

**Deadline：10-21（Wed）晚**

---

## 3. Block B｜2026-10-22（Thu）– 10-26（Mon）｜5 日｜補 Stage 2

目標：打通技術風險最高嘅兩段，拿到「做得到」嘅證據。

| # | 任務 | 產出 | 完成定義 |
|---|---|---|---|
| B1 | Python 3.11 + uv、private Git repo、OpenAI key、**設 cost cap** | 可跑環境 | 由零 clone 到跑起 ≤ 3 command |
| B2 | **PDF parsing spike**：PyMuPDF 切 section、抽 figure+caption、保留 source ref | `src/parse.py` | 3 篇論文，figure 成功率 ≥ 70%，並寫低失敗模式 |
| B3 | **PPTX render spike**：1 template，python-pptx 出 5 種版式（標題／bullet／圖文／雙欄／結語） | `src/render.py` + 範例 .pptx | 檔案開得、無 shape 重疊 |
| B4 | Proposal 骨架 | `docs/proposal.md` | 每個 section 有 heading + 3 句重點 |

**Deadline：10-26（Mon）晚**

> B2 / B3 係全項目嘅可行性證據。做成 → proposal 有底氣；做唔成 → 即刻降 scope（例如 figure 一律用表格化描述），唔好拖。

---

## 4. Block C｜2026-10-27（Tue）– 10-29（Thu）｜3 日｜Proposal 完稿並交出

| # | 任務 | 完成定義 |
|---|---|---|
| C1 | 寫 Methodology + 20 週 timeline（對應 brief 第 6 頁 7 階段） | 有 milestone 表，含 interim / final 節點 |
| C2 | 統一 citation 格式、檢查頁數、proofread | 自己由頭讀一次（單人冇人幫你 review，呢步唔可以省） |
| C3 | **10-29（Thu）交畀 professor 睇 feedback** | 已寄出，附「希望 11-02 前收到意見」 |

---

## 5. Block D｜2026-10-30（Fri）– 11-05（Thu）｜改、submit、開 Stage 3

| # | 任務 |
|---|---|
| D1 | 按 feedback 修訂（預留 2 日，唔好排到最後一日） |
| D2 | 11-05（Thu）submit proposal 到系統 |
| D3 | **同步**開 Stage 3：LLM outline + bullet + speaker notes pipeline（唔好等 proposal 交完先開始） |

---

## 6. 單人節奏（最重要嘅一條）

單人最大風險係「無人發現你停咗」。所以強制：

- **每週日 30 分鐘 self-checkpoint**：寫低本週做了什麼、下週做什麼、卡在邊。放 `docs/weekly/`。
- **每月例會帶同一份 master deck**（第 9 頁明文要求，由今日開，用到 final presentation）。
- **每次會議交 <1 頁 meeting notes**（3 點：進度、疑問、下月計劃）。
- 唔好連續兩星期冇 commit — 自己 review commit history 就知進度。

---

## 7. 今晚 30 分鐘就做

1. 開 private Git repo（自己一個都要，commit history 係進度證據）。
2. 開 **master meeting deck**（一份由頭用到 final presentation）。
3. Email Chen Xianwei 一次問清三件事：① scope 收窄到「單欄論文 → 10–12 版」可以嗎；② 同題目同學係各自獨立提交嗎；③ 第一次例會時間。
4. 入 3 篇論文落 `data/papers/` 做 spike。

---

## 8. 風險（單人版）

| 風險 | 為何致命 | 早期動作 |
|---|---|---|
| Figure 抽取質素差 | 直接決定成品顏值，亦係評分重點 | B2 就量成功率；唔得就即轉 fallback |
| PPTX overflow | 靠 LLM 肉眼判斷必然爆版 | Stage 4 用 shape bounding box 程式化 check + render 成圖覆核 |
| API cost / latency 失控 | 評估章節要報 cost 同 latency | B1 設 cost cap，逐次記錄 token 與耗時 |
| **Bus factor = 1** | 冇人接手、冇人 review | 每週 checkpoint + 文件化決策；coordinator 當唯一 reviewer |
| **同題目撞款** | 幾個人做同一題，評分會比較 | 見下節，要有一條明確差異化主線 |

---

## 9. 差異化：你嘅賣點應該擺邊

同題目有其他人做，所以「做到」唔夠，要「唔同」。建議主打**兩點**（其餘做到基本即可）：

1. **可量度嘅 inspection loop**
   brief 第 5 點只寫「inspect and revise」，但冇人會定義點 inspect。
   你若把 overflow / contrast / font-size / bullet 字數 變成**可計算嘅 violation 指標**，
   並報「revision 後 violation 下降幾 %」，呢個就係實驗章節嘅硬通貨。

2. **Speaker notes 品質**
   brief 特別寫「**detailed** speaker notes」，而大部分人會生成一堆同 bullet 重複嘅廢話。
   你若明確要求 notes 係「講稿式、含轉場句、含時間預算（每個 section 幾分鐘）」，
   再加一個 notes 品質嘅人工評分維度，就即刻同其他人分開。

> 這兩點都係低成本、高辨識度，適合單人執行。
