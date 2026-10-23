# 基於以上分析，你實際上要做啲咩

> 前提：單人、20 週、每週 15–20 小時、AI 可以幫你寫大部分 code。
> 結論先講：**你要做的不是一個更好的 PPT 生成器，而是一個「能證明 PPT 好在哪裡」的量測系統。**

---

## 0. 三個要即刻做的決定（唔做呢三個，之後全部白做）

| # | 決定 | 建議 | 幾時要定 |
|---|---|---|---|
| 1 | **定位** | 主線 = D1 SlideQC（可計算違規指標 + 修復迴圈）；副線 = D3 Speaker Notes | 10-20 前 |
| 2 | **Baseline** | ①PPTAgent（有官方 repo，直接跑）②Naive single-pass（一次 LLM 出大綱 → 一次渲染，無檢查） | 10-26 前 |
| 3 | **評測三軌** | ①違規指標（自動）②PaperQuiz 式問答（自動）③30 人 pairwise（人評） | 11-05 寫入 proposal |

**為什麼 baseline 一定是這兩個**：PPTAgent 是領域公認最強的可複現系統；naive single-pass 則證明「你的檢查迴圈有用」。少了 naive baseline，你無法歸因功勞。

---

## 1. 即刻 10 日（10-19 → 10-29）：補進度 + 出 proposal

| 日期 | 做什麼 | 產出 |
|---|---|---|
| 10-19（一） | 讀完本資料夾 `01_paper_analysis.md` 的 04/15/24/26/28 五篇（PPTAgent、ReDeck、Paper2Poster、PosterMELD、PPTBench） | 一頁筆記：你的 gap 一句話 |
| 10-20（二） | 寫死 scope：單欄英文論文、10–12 版、2 套模板、8 篇 held-out | `scope.md` |
| 10-21（三） | 收 8 篇論文（要有圖表）；定義 6 類違規的**操作型定義** | `data/papers/`、`violations.md` |
| 10-22（四） | 環境：Python + uv + repo + API key + cost cap | 可跑環境 |
| 10-23（五） | PDF parsing spike（PyMuPDF 切 section、抽 figure+caption） | `parse.py`，3 篇成功率 |
| 10-24（六） | python-pptx render spike（5 種版式） | `render.py` + 範例 pptx |
| 10-25（日） | **寫 violation detector 的第一個**（overflow：bbox 超出 slide 邊界） | `slideqc/overflow.py`，能在 spike 上跑 |
| 10-26（一） | 跑通 PPTAgent baseline（照官方 README） | baseline 輸出 3 份 deck |
| 10-27（二） | Proposal：problem / gap / method 三節 | `proposal.md` 初稿 |
| 10-28（三） | Proposal：timeline / evaluation / risk 三節 + 全文 proofread | 完整 draft |
| 10-29（四） | **交畀 professor 睇 feedback** | 已寄出 |

> **關鍵**：10-25 就寫出第一個 detector，是為了讓你在 10-29 交 proposal 時，手上有真實數字（「我在 3 篇論文上測到平均 4.7 個 overflow」），而不是空話。這一句話會讓 proposal 看起來像已經開始了。

---

## 2. 11 月：把量測系統做成型

| 週 | 任務 | 里程碑 |
|---|---|---|
| 11-02 週 | 收 professor feedback、改 proposal、11-05 submit | Proposal 完成 |
| 11-09 週 | 完成 6 個 violation detector（overflow / overlap / off-canvas / 對比度 / 字級 / 圖文碰撞） | `slideqc` v0.1 |
| 11-16 週 | Stage 3：outline → bullet → notes pipeline | 端到端可出 10 版 |
| 11-23 週 | **開始人手標註**：150 版 slide 的違規 ground truth | 完成 50 版 |
| 11-30 週 | 修復迴圈 v1（偵測 → 修 → 再偵測） | 違規數下降初步數字 |

**11 月的唯一目標**：讓「違規指標」從概念變成有 precision/recall 的工具。

---

## 3. 12 月：模板、標註、初步實驗

| 週 | 任務 | 里程碑 |
|---|---|---|
| 12-07 週 | 2 套模板 + 版面演算法（約束式：先算容量再放內容） | 5 種版式穩定 |
| 12-14 週 | 標註完成 150 版（目標 κ ≥ 0.7） | ground truth 完成 |
| 12-21 週 | 初步實驗：8 篇 × 3 條件（naive / PPTAgent / 你的系統） | 第一版結果表 |
| 12-28 週 | 寫 interim report 初稿 | 6–8 頁 |

**12 月的唯一目標**：interim 要有「真實數據」，不是進度報告。

---

## 4. 1 月–2 月：主實驗 + 人評

| 期間 | 任務 |
|---|---|
| 01-04 週 | **01-07 交 interim report** |
| 01-11 週 | Speaker notes 模組（時間預算 + 轉場 + 口語化） |
| 01-18 週 | 消融實驗：逐個關掉 detector，看違規率變化 |
| 01-25 週 | PaperQuiz 式自動問答評測（每份 deck 10 題） |
| 02-01 週 | **人評招募**（30 人，同學 + 朋友，pairwise 比較） |
| 02-08 週 | 人評執行（每人 30 分鐘，2 份 deck 比較） |
| 02-15 週 | 統計分析（Wilcoxon signed-rank、Cohen's κ） |
| 02-22 週 | 主實驗完成，鎖定結果 |

---

## 5. 3 月–4 月：寫作與交付

| 期間 | 任務 |
|---|---|
| 03-01 週 | 結果章節 + 圖表（每張圖只講一件事） |
| 03-08 週 | 討論與限制（老實寫：你的系統在雙欄論文會失敗） |
| 03-15 週 | 全文整合、proofread |
| 03-22 週 | 給 professor 看最終稿（截止前一週） |
| 03-29 週 | Turnitin + AI Report + 格式檢查 |
| **04-08** | **交 Final Report + Turnitin + AI Report** |
| 04-09 → 04-21 | Presentation（用同一份 master deck 更新） |

---

## 6. 你要维持的三張表（從第一日開始記）

| 表 | 欄位 | 為什麼 |
|---|---|---|
| `runs.csv` | run_id, paper, config, model, tokens_in/out, cost_usd, latency_s, violations_before/after | 成本與延遲章節的唯一來源 |
| `human_eval.csv` | rater_id, paper, pair(A/B), winner, 三維分數, 時間 | 人評可複現 |
| `claims.csv` | bullet_id, paper_span, support_label, annotator | 事實性分析 |

**唔記這三張表，你 4 月會重跑一次所有實驗。** 這是親眼見過最常見的 capstone 死法。

---

## 7. 預算估算

| 項目 | 估算 | 備註 |
|---|---|---|
| LLM API（8 篇 × 3 條件 × 約 40 call） | US$15–40 | 用 flash/mini 級模型即可；PPTAgent baseline 較貴 |
| VLM 檢查（每版一張圖） | US$10–25 | 只檢查關鍵版可再省 |
| 人評酬勞（30 人 × 30 分鐘） | HK$0–1,500 | 同學互評可省；有酬勞則樣本質素更好 |
| **總計** | **約 HK$500–3,000** | 記得在 proposal 寫明 |

---

## 8. 每週節奏（單人防線）

- **週日 30 分鐘**：更新 `docs/weekly/W##.md`（做了什麼 / 下週做什麼 / 卡在哪）
- **每月例會**：帶同一份 master deck，只加不減
- **每次會議後**：<1 頁 meeting notes（3 點）
- **每兩週**：跑一次完整 pipeline，確保沒有壞掉

---

## 9. 最後：如果只記得一句話

> **你的分數不取決於你生成幾好看的 PPT，而取決於你能不能說清楚「這份 PPT 好在哪裡、壞在哪裡、你怎麼知道」。**

這就是 D1（違規指標）+ D3（講稿品質）的組合能夠拿到 A 的原因：它們把一個主觀的設計問題，變成兩個可量度的工程問題。
