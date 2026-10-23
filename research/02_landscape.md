# 領域地圖：邊啲已經做爛，邊啲仍然空白

## 1. 時間線（呢個領域只有 5 年歷史，但 2025–2026 爆得極快）

| 時期 | 代表工作 | 特徵 |
|---|---|---|
| **2021 奠基** | DOC2PPT、D2S | 定義任務、建資料集、seq2seq 生成；無視覺回饋 |
| **2023 評測起步** | PPTC | 開始有標準 benchmark，但只評「操作對不對」 |
| **2025 上半 LLM agent 化** | PPTAgent、AutoPresent、Paper2Poster、PreGenie | 從「生成」轉向「編輯／程式化」；首次認真做評測（PPTEval、PaperQuiz） |
| **2025 下半 多智能體** | SlideBot、SlideGen、SlideTailor、SlideLab | 分工、個人化、受眾；開始報成本 |
| **2026 渲染接地 + 原生編輯** | ReDeck、DeepPresenter、SLIDEFORGE、EditPPT、ACE、SeaSlides | 從「一次生成」轉向「看渲染結果逐步修」；開始處理 .pptx 原生可編輯性 |

**對你嘅意義**：2026 年的前沿已經不是「能不能生成」，而是「**生成完之後點知好唔好、點修**」。你的 project 應該站在這一層，而不是重做一個生成器。

---

## 2. 五條技術路線（你要選一條，唔好混合）

| 路線 | 做法 | 代表 | 優點 | 致命缺點 | 適合你？ |
|---|---|---|---|---|---|
| **A. 端到端學習** | seq2seq / 微調模型直接出 slide 結構 | DOC2PPT、D2S | 學術完整 | 品質已被 LLM 碾壓；要訓練資源 | ❌ |
| **B. 參考 deck 編輯** | 抽取參考 deck 的 schema，生成編輯動作 | PPTAgent、SlideTailor | 視覺一致性好；有現成 repo | 受模板限制；長 deck 誤差累積 | ✅ 做 baseline |
| **C. 程式碼 / IR 生成** | LLM 寫 python-pptx / HTML / Slidev / Typst | AutoPresent、PreGenie、SeaSlides、DeepSlides | 可編輯、可檢查、成本低 | 版面易爆；需要約束 | ✅ **主力** |
| **D. 渲染接地反思** | 每步渲染成圖，用 VLM 看圖再修 | ReDeck、DeepPresenter、ACE | 能修 overflow/重疊 | 延遲與成本高 | ✅ **你的差異化所在** |
| **E. 原生物件編輯** | 直接操作 pptx shape / COM | TalkToYourSlides、SLIDEFORGE、EditPPT | 完全保留可編輯性 | 工程極重；COM 綁 Windows | ⚠️ 只做局部 |

**建議組合**：**C（生成）+ D（檢查與修復）+ 自建度量層**。不要把 E 當主線。

---

## 3. 能力維度 × 飽和度矩陣

| 能力維度 | 有無人做 | 代表工作 | 飽和度 | 你嘅機會 |
|---|---|---|---|---|
| 內容選取與摘要 | 大量 | D2S、DOC2PPT、SlideBot | 🔴 極飽和 | 唔好做 |
| 敘事 / 故事線 | 中等 | ArcDeck、SlideLab、DeepSlide | 🟠 半飽和 | 要用輕量方式做 |
| 版面美學（生成） | 大量 | Design-First、PosterGen、SlideGen | 🔴 極飽和 | 唔好做 |
| 可編輯 .pptx 輸出 | 中等 | SLIDEFORGE、EditPPT、PosterMELD | 🟠 半飽和 | 做「基本可編輯」就夠 |
| 渲染後驗證與修復 | 少數 | ReDeck、DeepPresenter、ACE | 🟢 仍開放 | **可做** |
| **可計算的版面違規指標** | **幾乎無人** | 只有 PosterMELD 的 PRR（海報） | 🟢 **空白** | **★ 最佳切入** |
| 事實接地 / 引用錨點 | 少數 | SlideBot（檢索）、ArcDeck（commitment） | 🟢 仍開放 | **可做** |
| 受眾條件化 | 少數 | SlideLab、X+Slides（只 benchmark） | 🟠 半飽和 | 可做，但要用現成 benchmark |
| **無障礙（對比度／字級／alt text／色盲）** | **完全無人** | — | 🟢 **空白** | **★ 高 novelty** |
| **雙語 / 中文 / 粵語** | **完全無人** | 全部英文 | 🟢 **空白** | **★ 地域優勢** |
| **Speaker notes 品質** | **幾乎無人** | 只有 DeepSlide 沾到 delivery | 🟢 **空白** | **★ 低成本高回報** |
| 成本 / 延遲最佳化 | 少數 | SlideLab（1/4 token）、ACE（省 89%） | 🟠 半飽和 | 做附帶貢獻 |
| 評測方法（自動） | 少數 | PaperQuiz、PPTEval、PRR | 🟠 半飽和 | 可改良 |
| 評測方法（人評） | 極少 | SlideLab（77% 盲測） | 🟢 仍開放 | **做 30–40 人已足夠** |
| 多輪互動修改 | 少數 | ConvDeck、MemSlides、AutoSlideUpdating | 🟠 半飽和 | 做 demo 可以 |

### 讀法

紅色 = 你花 4 個月做出來，評審只會說「已有類似工作」。
綠色 = 你花 2 個月做出來，評審會說「這個角度我沒見過」。

---

## 4. 三個結構性結論（直接影響你嘅選題）

### 結論一：呢個領域的「生成」已經商品化

2026 年，任何人都可以用 GPT/Claude + python-pptx 在一個週末做出「論文轉 PPT」的 demo。
**所以「我做到」不再是貢獻，「我證明到」才是。** 你的分數不會來自系統規模，而來自：
- 你定義了什麼新指標
- 你用什麼 ground truth 驗證它
- 你做了什麼別人不願做的實驗（人評、消融、成本）

### 結論二：所有系統都卡在同一個瓶頸——「唔知自己錯在哪」

ReDeck 講得很白：整份 deck 重寫一次，然後只看一次回饋，**局部錯誤（overflow、重疊、裁切）無法歸因**。
PPTBench 亦指出：模型讀得懂內容，但排不好版面。
**這是整個領域公認的痛點，而且目前只有「修」的方案，沒有「量」的方案。** 這正是你的位置。

### 結論三：設計沒有 ground truth，所以評測必須「多軌」

沒有一個「正確的 deck」。所以你不能只報一個分數。可接受的組合是：
1. **可計算指標**（違規數、PRR、覆蓋率）→ 客觀、可複現
2. **任務導向自動問答**（PaperQuiz 式）→ 測「有沒有傳達到」
3. **相對人評**（pairwise，30–40 人）→ 測「好不好看」

三者有兩者 = B+ 以上；三者齊 = A 區間。

---

## 5. 你唔應該做嘅四件事（避免撞車）

| 不要做 | 原因 |
|---|---|
| 再做一個端到端「論文轉 PPT」系統 | 2026 年已有 15+ 篇，你的版本不會更好 |
| 直接跟 ReDeck / EditPPT / SLIDEFORGE 的技術路線 | 工程門檻高（COM、state graph），單人做不完 |
| 做「多智能體架構」當賣點 | 評審會問「ablation 呢？」，而多 agent 的 ablation 極難做 |
| 用 LLM-as-judge 當唯一評測 | 不可複現、會被質疑；而且這正是你要批評的對象 |
