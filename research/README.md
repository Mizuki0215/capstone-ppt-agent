# PPT Agent 文獻包 — 給 DSAI4901 Capstone 用

**建立日期**：2026-10-18
**用途**：Topic 2「AI Agent for Presentation Slides Design」單人 capstone 的選題與定位依據

---

## 這個資料夾有什麼

| 檔案 | 內容 | 幾時睇 |
|---|---|---|
| `README.md` | 本檔：導航 + 核心結論 | 現在 |
| `papers_index.md` | 35 篇總表（分類、arXiv、GitHub、開源狀態、一句話賣點） | 先掃一次 |
| `papers_index.csv` | 同上，Excel/pandas 可讀 | 做文獻表時用 |
| `01_paper_analysis.md` | **逐篇分析**：賣點 / 做得好 / 做唔好 / 對你嘅啟示 | 必讀 |
| `02_landscape.md` | 領域地圖：時間線、五條技術路線、飽和度矩陣 | 寫 literature review 時用 |
| `03_A_grade_directions.md` | **教授視角評分表 + 10 個方向 + 最推薦 5 個** | 決定題目時用 |
| `04_action_plan.md` | 由 10-19 到 4-08 的具體行動計劃 | 決定「聽日做咩」時用 |
| `pdfs/` | 35 篇全文 PDF（檔名 = 名稱_arXivID.pdf） | 精讀時用 |

---

## 篩選流程（可寫入報告的方法章節）

```
arXiv 12 組查詢（slide / PPT / poster / presentation / deck …）
        ↓ 367 篇候選
關鍵詞相關度篩選（排除 presentation attack、無關 poster 等）
        ↓ 69 篇
人工篩選（與 paper→slide 任務直接相關）
        ↓
30 篇 PPT/Slide Agent  +  5 篇 PPT×教育/演示
```

GitHub 連結全部由論文 PDF 內文抽取，並用 HTTP 逐一驗證存在；文中引用的第三方工具（marker、PptxGenJS、playwright 等）已剔除，只保留作者自己的 repo。

---

## 四個核心結論（如果只讀一段，讀這裡）

### 1. 「生成」已經飽和，「測量」仍然空白

2025–2026 有 20+ 篇系統論文，但真正定義「什麼叫好」的只有少數：
- Paper2Poster 的 **PaperQuiz**（用答題測內容傳達）
- PosterMELD 的 **Print-Ready Rate**（用四道 gate 測可用性）
- PresentBench 的細粒度 rubric

**你的機會在測量層，不在生成層。**

### 2. 全領域的共同痛點：系統不知道自己在哪裡壞了

- **ReDeck**（微軟, 2026-08）明說：整份 deck 重寫、只看一次回饋，導致 overflow / 重疊 / 裁切**無法歸因**。
- **PPTBench**（2025-12）用 958 個真實 PPTX 證明：模型讀得懂內容，但**排不好版面**。

但 ReDeck 只做「修」，**沒有人定義「量」**。這就是你的切入位。

### 3. 無障礙與非英文場景 = 實證到的空白

我對 35 篇全文做了關鍵詞掃描：

| 關鍵詞 | 命中篇數 |
|---|---|
| `WCAG` | **0** |
| `colorblind` | 1（附帶提及） |
| `alt text` | 3（非核心） |
| `speaker notes` | 5（全部附帶提及，無一篇當研究對象） |

→ 沒有任何一篇把「無障礙」或「非英文」當成研究問題。

### 4. 你的護城河不是 code

AI 兩日可以寫出一個 renderer，評審也知道。
真正屬於你、AI 不能代做的只有三樣：
**人手標註的 ground truth、實驗設計、問題選擇。**

---

## 建議的題目（一句話版）

> **「現有系統能生成好看的 deck，但不知道自己哪裡壞了。本項目提出一套可計算的版面違規指標，嵌入生成—檢查—修復迴圈，並用 150 版人手標註與 30 人 pairwise 評測驗證其有效性。」**

主線：SlideQC（版面違規度量 + 修復）
副線：Speaker Notes 2.0（時間預算 + 轉場 + 口語化）
Stretch：Accessibility-First（WCAG 約束）

詳細見 `03_A_grade_directions.md` 第六節。

---

## 使用建議

1. **今日**：讀 `03_A_grade_directions.md` 的第一、五、六節（15 分鐘），決定方向。
2. **明日**：讀 `01_paper_analysis.md` 的 04 / 15 / 24 / 26 / 28（PPTAgent、ReDeck、Paper2Poster、PosterMELD、PPTBench）。
3. **星期三前**：照 `04_action_plan.md` 第 1 節執行，10-29 交 proposal 給 professor。

---

## 注意事項

- 全部 35 篇都是 **arXiv 預印本**，peer-review 狀態未逐一核實；引用前請確認最新版本。
- 部分論文（如 `blinding2submit/slidesqaqa`）使用匿名 repo，屬正常投稿做法。
- 374 MB PDF；如只需摘要，可只看 `papers_index.md`。
