# 35 篇文獻索引

篩選流程：arXiv 12 組查詢 → 367 篇候選 → 關鍵詞相關度篩選 69 篇 → 精選 **30 篇 PPT/Slide Agent + 5 篇 PPT 教育應用**。

所有 GitHub 連結均由論文 PDF 內文抽取，並用 HTTP 逐一驗證存在（2026-10-18）。

> 幾點說明：
> - `gh_status` 標明係「作者 repo」定「未見公開碼」。文中引用嘅第三方工具（marker、PptxGenJS、playwright 等）唔算作者 repo，已剔除。
> - 全部為 arXiv 預印本；peer-review 狀態未逐一核實，引用時請自行確認版本。


## 生成主線（18 篇）

| # | 名稱 | 年月 | 標題 | arXiv | GitHub | 開源狀態 |
|---|---|---|---|---|---|---|
| 1 | **PPTAgent** | 2025-01 | PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides | [2501.03936](https://arxiv.org/abs/2501.03936) | https://github.com/icip-cas/PPTAgent | ✅ 作者 repo |
| 3 | **AutoPresent** | 2025-01 | AutoPresent: Designing Structured Visuals from Scratch | [2501.00912](https://arxiv.org/abs/2501.00912) | https://github.com/para-lost/AutoPresent | ✅ 作者 repo |
| 4 | **DOC2PPT** | 2021-01 | DOC2PPT: Automatic Presentation Slides Generation from Scientific Documents | [2101.11796](https://arxiv.org/abs/2101.11796) | — | — 未見公開碼 |
| 5 | **D2S** | 2021-05 | D2S: Document-to-Slide Generation Via Query-Based Text Summarization | [2105.03664](https://arxiv.org/abs/2105.03664) | https://github.com/IBM/document2slides | ✅ 作者 repo |
| 6 | **SlideBot** | 2025-11 | SlideBot: A Multi-Agent Framework for Generating Informative, Reliable, Multi-Modal Presentations | [2511.09804](https://arxiv.org/abs/2511.09804) | — | — 未見公開碼 |
| 7 | **PreGenie** | 2025-05 | PreGenie: An Agentic Framework for High-quality Visual Presentation Generation | [2505.21660](https://arxiv.org/abs/2505.21660) | — | — 未見公開碼 |
| 8 | **SlideGen** | 2025-12 | SlideGen: Collaborative Multimodal Agents for Scientific Slide Generation | [2512.04529](https://arxiv.org/abs/2512.04529) | — | — 未見公開碼 |
| 9 | **DeepPresenter** | 2026-02 | DeepPresenter: Environment-Grounded Reflection for Agentic Presentation Generation | [2602.22839](https://arxiv.org/abs/2602.22839) | — | ⚠️ 同組前作 PPTAgent 有 repo，本篇無獨立 repo |
| 10 | **ReDeck** | 2026-08 | ReDeck: Step-Level Render-Grounded Refinement for Document-to-Slide Generation | [2609.00194](https://arxiv.org/abs/2609.00194) | https://github.com/microsoft/ReDeck | ✅ 作者 repo |
| 11 | **SlideTailor** | 2025-12 | SlideTailor: Personalized Presentation Slide Generation for Scientific Papers | [2512.20292](https://arxiv.org/abs/2512.20292) | https://github.com/nusnlp/SlideTailor | ✅ 作者 repo |
| 12 | **ConvDeck** | 2026-08 | ConvDeck: Conversational Paper-to-Slide Generation via Stage-Specific User Feedback | [2609.00226](https://arxiv.org/abs/2609.00226) | https://github.com/RehgLab/ConvDeck | ✅ 作者 repo |
| 13 | **ArcDeck** | 2026-04 | Narrative-Driven Paper-to-Slide Generation via ArcDeck | [2604.11969](https://arxiv.org/abs/2604.11969) | https://github.com/RehgLab/ArcDeck | ✅ 作者 repo |
| 14 | **MemSlides** | 2026-06 | MemSlides: A Hierarchical Memory Driven Agent Framework for Personalized Slide Generation with Multi-turn Local Revision | [2606.17162](https://arxiv.org/abs/2606.17162) | — | — 未見公開碼 |
| 15 | **SlideLab** | 2026-09 | SlideLab: Audience-Centered Scientific Slide Generation and Evaluation | [2609.30294](https://arxiv.org/abs/2609.30294) | — | — 未見公開碼 |
| 16 | **SeaSlides** | 2026-08 | SeaSlides: Semantic Abstraction Layer for Agentic Slide Generation | [2608.03298](https://arxiv.org/abs/2608.03298) | — | — 未見公開碼 |
| 17 | **DesignFirstCodeLater** | 2026-04 | Design First, Code Later: Aesthetically Pleasing Template-Free Slides Generation | [2605.26451](https://arxiv.org/abs/2605.26451) | https://github.com/sxswz213/DeepSlides | ✅ 作者 repo（DeepSlides） |
| 18 | **Textual2VisualSelfVerify** | 2025-02 | Textual-to-Visual Iterative Self-Verification for Slide Generation | [2502.15412](https://arxiv.org/abs/2502.15412) | — | — 未見公開碼 |
| 19 | **DeepSlide** | 2026-04 | DeepSlide: From Artifacts to Presentation Delivery | [2605.15202](https://arxiv.org/abs/2605.15202) | https://github.com/PUITAR/DeepSlide | ✅ 作者 repo |

## 編輯/原生PPTX（5 篇）

| # | 名稱 | 年月 | 標題 | arXiv | GitHub | 開源狀態 |
|---|---|---|---|---|---|---|
| 20 | **SLIDEFORGE** | 2026-09 | SLIDEFORGE: An LLM Agent for Controllable Editing of Slides as Structured Artifacts | [2609.03109](https://arxiv.org/abs/2609.03109) | https://github.com/UIUC-MONET/SLIDEFORGE | ✅ 作者 repo |
| 21 | **EditPPT** | 2026-06 | EditPPT: Faithful Long-Deck Slide Editing via Structured Tool-Using Multi-Agent with Dual-Modal Validators | [2608.20381](https://arxiv.org/abs/2608.20381) | — | — 未見公開碼 |
| 22 | **ACE** | 2026-08 | ACE: A Self-Correcting Agentic Canvas Editor for Multi-Slide Presentation Automation | [2608.24103](https://arxiv.org/abs/2608.24103) | https://github.com/BloomBerry/agentic-canvas-editor | ✅ 作者 repo |
| 23 | **TalkToYourSlides** | 2025-05 | Talk to Your Slides: High-Efficiency Slide Editing via Language-Driven Structured Data Manipulation | [2505.11604](https://arxiv.org/abs/2505.11604) | — | — 未見公開碼 |
| 24 | **AutoSlideUpdating** | 2026-04 | Automatic Slide Updating with User-Defined Dynamic Templates and Natural Language Instructions | [2604.17894](https://arxiv.org/abs/2604.17894) | https://github.com/XiaoZhou2024/SlideAgent | ✅ 作者 repo |

## 海報生成（3 篇）

| # | 名稱 | 年月 | 標題 | arXiv | GitHub | 開源狀態 |
|---|---|---|---|---|---|---|
| 2 | **Paper2Poster** | 2025-05 | Paper2Poster: Towards Multimodal Poster Automation from Scientific Papers | [2505.21497](https://arxiv.org/abs/2505.21497) | https://github.com/Paper2Poster/Paper2Poster | ✅ 作者 repo |
| 25 | **PosterGen** | 2025-08 | PosterGen: Aesthetic-Aware Multi-Modal Paper-to-Poster Generation via Multi-Agent LLMs | [2508.17188](https://arxiv.org/abs/2508.17188) | https://github.com/Y-Research-SBU/PosterGen | ✅ 作者 repo |
| 26 | **PosterMELD** | 2026-08 | PosterMELD: Multi-Agent Paper-to-Poster Generation for Controllable Design Diversity with Editable Print-Ready Outputs | [2608.02218](https://arxiv.org/abs/2608.02218) | — | — 未見公開碼 |

## 評測基準（4 篇）

| # | 名稱 | 年月 | 標題 | arXiv | GitHub | 開源狀態 |
|---|---|---|---|---|---|---|
| 27 | **PPTC** | 2023-11 | PPTC Benchmark: Evaluating Large Language Models for PowerPoint Task Completion | [2311.01767](https://arxiv.org/abs/2311.01767) | https://github.com/gydpku/PPTC | ✅ 作者 repo |
| 28 | **PPTBench-Layout** | 2025-12 | PPTBench: Towards Holistic Evaluation of Large Language Models for PowerPoint Layout and Design Understanding | [2512.02624](https://arxiv.org/abs/2512.02624) | https://github.com/Gastronomicluna/PPTBench-Eval | ✅ 作者 repo（評測碼） |
| 29 | **PresentBench** | 2026-03 | PresentBench: A Fine-Grained Rubric-Based Benchmark for Slide Generation | [2603.07244](https://arxiv.org/abs/2603.07244) | — | — 未見公開碼 |
| 30 | **X-Slides** | 2026-06 | X+Slides: Benchmarking Audience-Conditioned Slide Generation | [2606.19256](https://arxiv.org/abs/2606.19256) | https://github.com/OpenDataBox/X-SlidesBench | ✅ 作者 repo（benchmark） |

## 教育應用（5 篇）

| # | 名稱 | 年月 | 標題 | arXiv | GitHub | 開源狀態 |
|---|---|---|---|---|---|---|
| 31 | **Slide2Text** | 2025-03 | Slide2Text: Leveraging LLMs for Personalized Textbook Generation from PowerPoint Presentations | [2503.17710](https://arxiv.org/abs/2503.17710) | — | — 未見公開碼 |
| 32 | **AISSA** | 2026-05 | AISSA: Implementation and Deployment of an AI-based Student Slides Analysis tool for Academic Presentations | [2605.04729](https://arxiv.org/abs/2605.04729) | — | — 未見公開碼 |
| 33 | **SlideDeckQA** | 2026-05 | Slide Deck Q&A Quality Assurance App: A Multi-Stage Pipeline for Pedagogical Question Generation | [2605.26428](https://arxiv.org/abs/2605.26428) | https://github.com/blinding2submit/slidesqaqa | ✅ 作者 repo（匿名投稿） |
| 34 | **ScriptToSlide** | 2026-03 | Script-to-Slide Grounding: Grounding Script Sentences to Slide Objects for Automatic Instructional Video Generation | [2603.16931](https://arxiv.org/abs/2603.16931) | — | — 未見公開碼 |
| 35 | **AI-VideoLectures** | 2025-10 | Transforming Higher Education with AI-Powered Video Lectures | [2511.20660](https://arxiv.org/abs/2511.20660) | — | — 未見公開碼 |

## 一句話賣點總表

| # | 名稱 | 賣點 |
|---|---|---|
| 1 | PPTAgent | 把生成變成「編輯既有 slide」：先抽參考 deck 的 slide 功能類型＋內容 schema，再產生編輯動作；附 PPTEval 三維評測 |
| 2 | Paper2Poster | 首個 poster 生成 benchmark + 四維指標（視覺對齊／文字連貫／整體美感／PaperQuiz 內容傳達） |
| 3 | AutoPresent | SlidesBench（7k 訓練 / 585 測試）；證明「程式化生成」比「直接出圖」更可控、可編輯 |
| 4 | DOC2PPT | 開創 document-to-slide 任務；hierarchical seq2seq + 版面預測，釋出 6K 配對資料 |
| 5 | D2S | 首個大規模 paper–slide 配對資料集 SciDuet；用 slide 標題反查內容再長問答摘要成 bullet |
| 6 | SlideBot | 教育場景多智能體：retrieval 提升可靠性 + 程式碼生成提升可自訂性，強調 informativeness/reliability/practicality |
| 7 | PreGenie | 走 Slidev（Markdown→渲染）路線，兩階段 analyze→generate→review→regenerate，用 MLLM 做視覺檢視 |
| 8 | SlideGen | 協作式 VLM 多智能體：敘事規劃／多模態 grounding／版面構成三線分工，主打視覺平衡同敘事流 |
| 9 | DeepPresenter | 以「渲染後的 slide 狀態」做環境接地反思，取代只憑 reasoning trace 自我反省；可自主 plan/render/revise |
| 10 | ReDeck | 把修訂拆成原子編輯動作，每步之後即刻渲染取觀測（one edit, one observation），解決 overflow/overlap/clipping 難歸因 |
| 11 | SlideTailor | 只需一組「論文–slide 範例 + 視覺模板」隱式表達偏好，唔需要用戶寫長段偏好文字 |
| 12 | ConvDeck | 把對話式回饋分散到 pipeline 各階段（stage-specific loops），唔係等整份 deck 出完先改 |
| 13 | ArcDeck | 用篇章結構（discourse tree）+ global commitment document 做敘事重建，另出 ArcBench |
| 14 | MemSlides | 分層記憶（user profile / working / tool memory）支撐跨任務個人化同多輪局部修訂 |
| 15 | SlideLab | 受眾中心 + 訓練免調整；報 77% 盲測偏好、token 用量約為最強開源 baseline 的 1/4；附 ConfArena 評測 |
| 16 | SeaSlides | 語意抽象層：模型只寫結構化內容，模板負責版面／樣式／渲染，避免直接寫座標或 SVG |
| 17 | DesignFirstCodeLater | 「先設計、後寫碼」：把版面設計同實作解耦，無模板；附 SlideDesign 資料集 + 多智能體 RL |
| 18 | Textual2VisualSelfVerify | 把缺頁生成拆成內容生成 + 版面生成；用 LLM Reviewer + Refiner 做文字→視覺自我驗證 |
| 19 | DeepSlide | 從「產出 deck」延伸到「交付演講」：時間預算敘事規劃、slide–script 對齊、排練支援 |
| 20 | SLIDEFORGE | Deck State Graph 串起視覺分解／原生 pptx 物件結構／知覺組織，保持可編輯性做可控編輯 |
| 21 | EditPPT | 把編輯化約為受限的 tool-selection，經 PowerPoint COM 做 shape 級操作；雙模態驗證 + DeckEdit-Bench |
| 22 | ACE | 分層 scene-graph（98 個工具）＋內容感知 router（省約 89% input token）＋無 ground-truth 的 IF judge 自我修正 |
| 23 | TalkToYourSlides | 改走底層物件模型而非螢幕像素，文字類／批次編輯又快又準，保留樣式 |
| 24 | AutoSlideUpdating | 定義 BYO-template 的動態更新任務，出 DynaSlide（20,036 組三元組），支援用戶自帶模板 |
| 25 | PosterGen | 模擬專業設計師流程的四智能體（Parser/Curator/Layout/Stylist），重視美學原則 |
| 26 | PosterMELD | 模板條件化 + 容量感知 slot + 確定性 gate 與 VLM 覆核；輸出可編輯 PPTX/PNG，報 Print-Ready Rate |
| 27 | PPTC | 279 個多輪 session 的 PowerPoint 任務完成 benchmark，用 PPTX-Match 直接對檔案評分 |
| 28 | PPTBench-Layout | 958 個 PPTX、4,439 樣本，測 Detection/Understanding/Modification/Generation，專攻版面理解 |
| 29 | PresentBench | 細粒度 rubric 式評測，針對「整體印象式打分」太粗的問題 |
| 30 | X-Slides | 受眾條件化評測：113 主題、7 場景、8,133 條 source-grounded probe，按受眾加權 |
| 31 | Slide2Text | PPT → 個人化教材：OCR 抽內容、重整結構、生成解釋／練習／參考 |
| 32 | AISSA | 課堂規模的簡報 slide 自動評分與回饋：rubric 驅動 + 學習分析儀表板 |
| 33 | SlideDeckQA | 由 PDF slides 抽文字＋渲染圖，四階段 LLM pipeline 生成教學問題，deck 級去重 |
| 34 | ScriptToSlide | 定義 script→slide object grounding 任務，為教學影片自動加視覺效果鋪路（F1 0.924） |
| 35 | AI-VideoLectures | Gemini 寫稿 + Polly 配音 + PowerPoint 組影片的半自動教學影片工作流 |