# 逐篇分析：賣點 / 做得好 / 做唔好 / 對你嘅啟示

> 分析基於各篇 arXiv 摘要 + 關鍵章節（已下載全文 PDF 於 `pdfs/`）。
> 標記：**賣點**＝佢宣稱嘅核心貢獻；**做得好**＝真正有價值嘅地方；**做唔好**＝你唔應該照抄嘅地方。
> 最後一行「對你嘅啟示」係直接對應你單人 capstone 嘅判斷。

---

## A. 生成主線（論文 → slide deck）

### 01. DOC2PPT — Automatic Presentation Slides Generation from Scientific Documents（2021-01）

- **賣點**：把 document→slide 定義成一個可學習任務；hierarchical seq2seq + 版面預測 + paraphrasing 模組，並釋出約 6K 組配對資料。
- **做得好**：任務定義乾淨，把「摘要、圖文檢索、版面預測」拆成子問題，至今仍是標準拆法；資料集讓後來者有得比。
- **做唔好**：純 seq2seq，無視覺回饋、無可編輯性討論、無 LLM。以今日標準，生成品質遠低於 agent 式系統。
- **對你嘅啟示**：只放在 literature review 做「起點」，**千萬不要當 baseline**（太弱，贏咗都無意義）。

### 02. D2S — Document-to-Slide Generation Via Query-Based Text Summarization（2021-05）

- **賣點**：SciDuet 資料集（NLP/ML 會議論文＋對應 slide）；兩步法：先用 slide 標題檢索相關文字／圖／表，再用 long-form QA 摘要成 bullet。
- **做得好**：「先有大綱、再用大綱反查原文」呢個骨架非常實用；證明 long-form QA 勝過一般摘要。
- **做唔好**：檢索依賴已知 slide 標題；完全冇版面生成；無多模態對齊。
- **對你嘅啟示**：你的 pipeline 可以直接用「outline → per-slide retrieval → 摘要」呢個骨架，但要把檢索換成 embedding + 引用錨點。

### 03. AutoPresent — Designing Structured Visuals from Scratch（2025-01）

- **賣點**：SlidesBench（7k 訓練 / 585 測試，310 個 deck、10 個領域）；benchmark 了「直接出圖」vs「產生程式碼」，結論係程式碼路線品質更高、更可互動修改。
- **做得好**：大規模 benchmark；reference-based 同 reference-free 兩種評測；明確為「程式化生成」背書。
- **做唔好**：以**單張 slide** 為單位，唔處理整份 deck 的敘事與連貫；偏向訓練式微調，zero-shot 新模板表現有限。
- **對你嘅啟示**：「用 python-pptx 產生 slide」係你唯一合理路線，呢篇可以引用嚟 justify。

### 04. PPTAgent — Generating and Evaluating Presentations Beyond Text-to-Slides（2025-01）⭐

- **賣點**：把生成重新定義為**編輯**：先分析參考 deck，抽出 slide 級「功能類型」同「內容 schema」，再起草大綱、逐步產生編輯動作。附 PPTEval（content / design / coherence 三維）。
- **做得好**：視覺一致性天然高（因為沿用參考 deck 的設計）；PPTEval 已成為社群常用指標；**有官方 repo，可以直接跑**。
- **做唔好**：高度依賴參考 deck 的質素與版式；編輯動作空間受模板限制；長 deck 會累積誤差；原本設計偏通用簡報，對「學術論文」場景未必最優。
- **對你嘅啟示**：**這是你第一 baseline**。你必須跑得贏它，或者清楚說明你在哪個維度上不同（例如可量度的版面違規）。

### 05. PreGenie — An Agentic Framework for High-quality Visual Presentation Generation（2025-05）

- **賣點**：走 Slidev（Markdown → 渲染）路線；兩階段：分析＋初版生成 → 審閱＋重生成，用 MLLM 看渲染結果再改。
- **做得好**：用 Markdown 做中間表示，人類可讀可改；review 階段真正看渲染圖，而非只看文字。
- **做唔好**：Slidev 生態與 PowerPoint 不相容，轉 .pptx 會走樣；review 只在整份 deck 層面，無局部歸因。
- **對你嘅啟示**：**中間表示（IR）的選擇是架構第一決策**。選 pptx 原生 → 可編輯但難排版；選 HTML/Markdown → 好排版但要轉檔。你要在 proposal 明確選一邊並講理由。

### 06. SlideBot — A Multi-Agent Framework for Informative, Reliable, Multi-Modal Presentations（2025-11）

- **賣點**：教育場景三支柱：informativeness（深度內容）、reliability（外部檢索）、practicality（程式碼生成可自訂）。
- **做得好**：少數把「可靠性」寫進架構的系統；模組化清晰，容易借用。
- **做唔好**：限於教育場景；未見大規模人評；多模組 → 成本與延遲高。
- **對你嘅啟示**：「可靠性 / grounding」係一個可以量化嘅切入點（見方向 D2）。

### 07. SlideGen — Collaborative Multimodal Agents for Scientific Slide Generation（2025-12）

- **賣點**：協作式 VLM 多智能體：敘事規劃、多模態 grounding、版面構成三線分工；主張現有方法只做文字選取，忽略視覺平衡與敘事流。
- **做得好**：把「版面」當一等公民；明確處理圖、公式、表格的整合。
- **做唔好**：多 agent 協調成本高；未見公開碼，難以複現。
- **對你嘅啟示**：分工架構可以參考，但單人専案要控制在 2–3 個 agent，否則 debug 成本會吃掉全部時間。

### 08. SlideTailor — Personalized Presentation Slide Generation for Scientific Papers（2025-12）

- **賣點**：用「一組論文–slide 範例 + 一個視覺模板」隱式表達用戶偏好，唔需要寫長段偏好文字。
- **做得好**：輸入門檻低，貼近真實用戶行為；有 repo。
- **做唔好**：冷啟動問題（用戶要有範例）；偏好對齊的效果難以客觀量化。
- **對你嘅啟示**：個人化方向可以做 demo，但**評測會非常難寫**，單人不建議做主線。

### 09. ArcDeck — Narrative-Driven Paper-to-Slide Generation（2026-04）

- **賣點**：把 paper→slide 當成「敘事重建」：先建 discourse tree 與 global commitment document，再用角色化 agent 迭代批判與修訂；附 ArcBench。
- **做得好**：少數認真處理「故事線」而非逐段摘要的工作；有 benchmark 支撐。
- **做唔好**：discourse parsing 的誤差會一路傳播；計算成本高。
- **對你嘅啟示**：「敘事」係上位概念，你可以用更輕量的方式實現（claim–evidence 對齊），效果相近但成本低得多。

### 10. MemSlides — Hierarchical Memory Driven Agent Framework（2026-06）

- **賣點**：三層記憶（user profile / working / tool memory）＋ scoped slide-local revision，支撐跨任務個人化與多輪局部修改。
- **做得好**：把「記住用戶偏好」同「精準局部改」分開處理，工程上務實。
- **做唔好**：記憶會膨脹；個人化評測同樣難。
- **對你嘅啟示**：如果你打算支援多輪修改，**記憶結構要第一日就定**，之後改很痛。

### 11. SlideLab — Audience-Centered Scientific Slide Generation and Evaluation（2026-09）⭐

- **賣點**：training-free 多 agent；先規劃敘事，再建 deck 並迭代精修；附 ConfArena（模擬會議室與觀眾）。報稱盲測中 77% 論文被偏好於開源與商業系統，且 token 用量約為最強開源 baseline 的 1/4。
- **做得好**：**有真人偏好研究**（說服力最強）；有成本意識；把「受眾」變成評測維度。
- **做唔好**：未見公開碼；ConfArena 用 LLM 模擬觀眾，與真人仍有落差。
- **對你嘅啟示**：**「人評 + 成本數字」是 A grade 的標準配備**。你不需要贏它，但你的實驗章節要有同等規格。

### 12. SeaSlides — Semantic Abstraction Layer for Agentic Slide Generation（2026-08）

- **賣點**：模型只寫「結構化內容」（可重用元件 + 能力模組），版面、樣式、渲染由模板負責；分別在 HTML 與 Typst 實作。
- **做得好**：解決「叫 LLM 寫座標」的脆弱性；能處理公式、程式碼、資料圖表等特殊物件。
- **做唔好**：受組件庫能力限制；抽象層設計本身要花大量工程。
- **對你嘅啟示**：**限制模型輸出空間 = 提升穩定性**。這與 EditPPT 的 tool-selection 思路一致，是你應該抄的核心原則。

### 13. Design First, Code Later / DeepSlides（2026-04）

- **賣點**：先做 slide-page 設計、後寫實作，解耦 design 與 implementation，無預設模板；附 SlideDesign 資料集與多智能體 RL。
- **做得好**：無模板仍能產出有設計感的版面；資料集有價值。
- **做唔好**：RL 訓練成本高，單人幾乎不可能複現；美學評測主觀。
- **對你嘅啟示**：概念可借（先 layout 決策、後渲染），但**唔好跟 RL**。

### 14. DeepPresenter — Environment-Grounded Reflection（2026-02）

- **賣點**：用「渲染後的 slide 狀態」做反思依據，取代只看 reasoning trace 的自我反省；能自主 plan / render / revise，跳出固定 workflow。
- **做得好**：指出 self-reflection 的根本問題（模型看不到自己產出的東西）；long-horizon 精修。
- **做唔好**：迭代次數多 → 成本與延遲；本篇無獨立 repo（同組前作 PPTAgent 有）。
- **對你嘅啟示**：「看渲染圖再修」是你**可以直接實作且能量化**的核心機制，成本可控（用 VLM 只看關鍵版）。

### 15. ReDeck — Step-Level Render-Grounded Refinement（2026-08）⭐

- **賣點**：把修訂拆成原子編輯動作，每步之後即刻渲染取觀測（one edit, one observation）；多粒度回饋平衡局部修復與全域品質。
- **做得好**：精準解決 overflow / overlap / clipping / off-canvas **難以歸因**的問題；微軟開源。
- **做唔好**：每步都渲染 → 延遲高；需要可靠的 renderer（LibreOffice 轉圖）。
- **對你嘅啟示**：**呢篇同你嘅方向最貼近**。它做「修」，但**冇定義一套可計算的違規指標**——呢個空缺就係你的切入位。

### 16. ConvDeck — Conversational Paper-to-Slide Generation（2026-08）

- **賣點**：把對話式回饋分散到 pipeline 各階段（stage-specific loops），用戶可在中途介入，而非等整份 deck 出完。
- **做得好**：正視「生成是迭代的」這個本質；有 repo。
- **做唔好**：需要人機互動實驗，樣本量難做大；結果高度依賴用戶質素。
- **對你嘅啟示**：互動式適合做 demo / 展示亮點，但**不適合做你唯一的貢獻**（評測不可控）。

### 17. Textual-to-Visual Iterative Self-Verification（2025-02）

- **賣點**：把「補齊缺頁」拆成內容生成 + 版面生成；用 LLM Reviewer + Refiner 做文字→視覺的自我驗證。
- **做得好**：意識到「文字 layout 描述」與「視覺結果」之間有鴻溝。
- **做唔好**：**全靠 LLM 主觀判斷，冇任何可計算指標**——這是最大的方法論弱點。
- **對你嘅啟示**：**這篇正好是你的反面教材**。「讓 LLM 說版面好不好」= 不可量度、不可複現。你要做的是把它變成數字。

### 18. DeepSlide — From Artifacts to Presentation Delivery（2026-04）

- **賣點**：從「產出 deck」延伸到「交付演講」：時間預算的邏輯鏈規劃、slide–script 對齊、注意力增強、排練支援。
- **做得好**：首次把 delivery（節奏、敘事、準備）納入系統；有 dual-scoreboard benchmark。
- **做唔好**：系統龐大、模組多；排練/語音部分評測困難。
- **對你嘅啟示**：**speaker notes + 時間預算** 係一個「大系統做唔細、細系統做得好」的空隙，非常適合單人。

---

## B. 編輯與原生 PPTX

### 19. Talk to Your Slides — Language-Driven Structured Data Manipulation（2025-05）

- **賣點**：不走螢幕像素，直接操作底層物件模型；文字類、批次編輯又快又準，樣式保真。
- **做得好**：效率與精確度遠勝 GUI agent；分層架構處理複雜指令。
- **做唔好**：只做編輯、不做生成；需要結構化輸入（現成 pptx）。
- **對你嘅啟示**：若要「保留可編輯性」，**物件模型是唯一正路**；這也決定了你的輸出格式應該是 .pptx。

### 20. SLIDEFORGE — Controllable Editing of Slides as Structured Artifacts（2026-09）

- **賣點**：Deck State Graph 串起視覺分解、原生 pptx 物件結構、知覺組織；支援 theme-preserving 重建與渲染狀態驗證。
- **做得好**：正視「agent 只看得懂 screenshot、改完就爛版」的現實；保留人類可理解的元件。
- **做唔好**：建圖成本高；複雜 deck 容易失敗。
- **對你嘅啟示**：工程門檻太高，**單人唔建議主攻**；但「state graph」概念可簡化借用。

### 21. EditPPT — Faithful Long-Deck Slide Editing（2026-06）

- **賣點**：把編輯化約為受限的 tool-selection 問題，經 PowerPoint COM 做 shape 級操作；雙模態驗證器；附 DeckEdit-Bench。
- **做得好**：限制 action space → 穩定性高；COM 保證 PowerPoint 語意正確；長 deck 有針對設計。
- **做唔好**：**依賴 Windows + Office COM**（macOS 開發者直接出局）；長 deck 仍有累積誤差。
- **對你嘅啟示**：⚠️ 如果你在 Mac 上開發，**這條路線直接排除**。環境風險要在 proposal 前確認。

### 22. ACE — Self-Correcting Agentic Canvas Editor（2026-08）

- **賣點**：分層 scene-graph（98 個工具）＋ 內容感知 router（平均省約 89% input token）＋ 無 ground-truth 的 instruction-following judge 自我修正。
- **做得好**：**正面處理「設計沒有唯一正確答案」**——所以用 IF judge 而非 diff；成本控制有實測數字。
- **做唔好**：工具太多 → 選擇困難；judge 本身可能帶偏見。
- **對你嘅啟示**：「設計無 ground truth」是你必須在報告中正面回答的問題。建議用**相對比較（pairwise 人評）**而非絕對分。

### 23. Automatic Slide Updating with Dynamic Templates（2026-04）

- **賣點**：定義 BYO-template 的「自然語言指令動態更新」任務；DynaSlide 20,036 組（原 slide、指令、目標 slide）三元組。
- **做得好**：貼近真實商業需求；資料規模大、有外部 DB grounding。
- **做唔好**：限於數據報表類版面；需要外部資料庫。
- **對你嘅啟示**：「更新既有 deck」是被低估的方向；DynaSlide 的標註格式值得借用（instruction → edit triple）。

---

## C. 海報生成（方法可移植到 slide）

### 24. Paper2Poster — Multimodal Poster Automation（2025-05）⭐

- **賣點**：首個 poster 生成 benchmark + 四維指標：(i) 與人設計海報的視覺語意對齊、(ii) 文字連貫、(iii) VLM-as-judge 的六項美學與資訊準則、(iv) **PaperQuiz**——用 VLM 答題測試海報是否真的傳達到論文核心。
- **做得好**：**PaperQuiz 是最聰明的自動評測設計**：不問「好不好看」，而問「讀者能不能從成品回答論文問題」。
- **做唔好**：poster 是單頁，slide 是多頁（有敘事與節奏問題）；解析成本高。
- **對你嘅啟示**：**PaperQuiz 直接搬得去 slide**：每份 deck 生成 10 條論文理解題，用 VLM 只看 deck 作答，正確率 = 內容傳達度。這是你最容易實作、又最有說服力的自動指標。

### 25. PosterGen — Aesthetic-Aware Multi-Agent（2025-08）

- **賣點**：模擬專業設計師流程的四智能體：Parser/Curator（內容與故事板）、Layout（空間配置）、Stylist（美學）。
- **做得好**：把「美學」明確拆成可執行步驟；pipeline 清晰。
- **做唔好**：美學難以量化；四 agent 成本高。
- **對你嘅啟示**：流程可參考，但**不要學它的評測方式**。

### 26. PosterMELD — Controllable Design Diversity with Editable Outputs（2026-08）

- **賣點**：模板條件化 + 容量感知 slot（先確保內容寫得落）+ 確定性 gate（幾何、可讀性、資產完整、明顯事實錯誤）+ VLM 覆核；輸出可編輯 PPTX/PNG；定義 **Print-Ready Rate (PRR)**。
- **做得好**：**PRR 是一個極實用的工程指標**：把「成品能不能用」變成可數的比例；而且輸出可編輯。
- **做唔好**：模板限制設計自由度；621 篇的評估規模單人難複製。
- **對你嘅啟示**：**PRR 就是你要做的東西的 slide 版**。把它改成「Deck-Ready Rate」，你就有一個現成的、有文獻背書的指標框架。

---

## D. 評測與基準

### 27. PPTC Benchmark — PowerPoint Task Completion（2023-11）

- **賣點**：279 個多輪 session，涵蓋數百條多模態指令；用 PPTX-Match 直接對「產出檔案」評分，而非對 API 序列。
- **做得好**：以檔案為準的評分方式，容許不同實作路徑；是 PPT 領域最早的標準 benchmark。
- **做唔好**：評的是「操作是否正確」，不是「內容/設計好不好」。
- **對你嘅啟示**：若你做編輯功能，可用它做 sanity check；但**不要用它當主評測**（不評品質）。

### 28. PPTBench — Holistic Evaluation of PowerPoint Layout and Design Understanding（2025-12）⭐

- **賣點**：958 個 PPTX、4,439 樣本，四類任務（Detection / Understanding / Modification / Generation），專門測版面理解。
- **做得好**：**揭示了一個關鍵落差：模型讀得懂內容，但排不好版面**。這句話本身就是你的 problem statement。
- **做唔好**：偏「理解與修改」，較少評生成美感。
- **對你嘅啟示**：你的 proposal 可以直接引用這個 gap，並用可計算的版面指標去補它。

### 29. PresentBench — Fine-Grained Rubric-Based Benchmark（2026-03）

- **賣點**：針對「整體印象式打分太粗」的問題，設計細粒度、可驗證的 rubric 來評真實場景的 slide 生成。
- **做得好**：把評測從 holistic 推向 rubric；方向正確。
- **做唔好**：rubric 設計本身帶主觀性；未見公開碼。
- **對你嘅啟示**：**自建 rubric 並公開 = 一個便宜又有份量的 contribution**。

### 30. X+Slides — Benchmarking Audience-Conditioned Slide Generation（2026-06）

- **賣點**：113 個主題、7 種場景、8,133 條 source-grounded probe；按受眾（專家 vs 決策者）給不同權重，報四個互補指標。
- **做得好**：把「對象是誰」變成可計算的變量；probe 由源文件接地，不是憑空生成。
- **做唔好**：只評內容覆蓋與深度，不評視覺。
- **對你嘅啟示**：若你做受眾版本，可直接用它報數，**省下大半評測設計成本**。

---

## E. PPT × 教育 / 演示

### 31. Slide2Text — Personalized Textbook Generation from PowerPoint（2025-03）

- **賣點**：把 PPT 反向變成個人化教材：OCR 抽內容 → 重整結構 → 生成解釋、練習、參考。
- **做得好**：反向應用（slide → 教材）少見；OCR + 結構化流程完整。
- **做唔好**：單作者短文；**完全沒有評測**，只有功能描述。
- **對你嘅啟示**：只能當「應用場景」引用，不能當方法參考。

### 32. AISSA — AI-based Student Slides Analysis Tool（2026-05）

- **賣點**：rubric 驅動的自動評分與回饋系統，配合學習分析儀表板；已在課堂部署。
- **做得好**：**rubric 由教師定義 → 可解釋、可爭辯**；有真實部署與使用者。
- **做唔好**：只評分不生成；依賴 LLM judge，未見與人類評分的一致性分析。
- **對你嘅啟示**：若你想碰教育場景，**rubric 化 + 與人類評分對齊（Cohen's κ）** 是唯一可辯護的做法。

### 33. Slide Deck Q&A Quality Assurance（2026-05）

- **賣點**：由 PDF slides 抽文字與渲染圖，四階段 LLM pipeline（window planning → deck synthesis → slide annotation → reconciliation）生成教學問題，並在 deck 層面去重。
- **做得好**：**正視「重點分散在跨 slide」的問題**；有工程細節（question budget、reconciliation）。
- **做唔好**：系統描述型論文，評測有限。
- **對你嘅啟示**：「deck 級一致性」是一個好角度——多數系統逐頁生成，忽略整體節奏。

### 34. Script-to-Slide Grounding（2026-03）

- **賣點**：定義 script 句子 → slide 物件的 grounding 任務，為教學影片自動加視覺效果鋪路；文字物件上 F1 = 0.924。
- **做得好**：**任務定義窄而清楚，指標明確**——這正是好論文的模板。
- **做唔好**：只做文字物件，範圍窄。
- **對你嘅啟示**：**把題目縮窄到一個可量度的任務**，比做一個大而全的系統更容易拿高分。

### 35. Transforming Higher Education with AI-Powered Video Lectures（2025-10）

- **賣點**：Gemini 寫稿 + Amazon Polly 配音 + PowerPoint 組装的半自動教學影片工作流；有兩門課的 pilot study。
- **做得好**：實務工作流完整，考慮了教學意圖與同步。
- **做唔好**：本質是工程報告，**沒有基準比較、沒有量化評估**。
- **對你嘅啟示**：**反面示範**——只講「我做了什麼」而沒有「我證明了什麼」，在 capstone 一定拿不到 A。

---

## 總結：三條跨論文的教訓

1. **「生成」已飽和，「測量」仍空白**。2025–2026 有 20+ 篇系統論文，但真正定義「什麼叫好」的只有少數幾篇（Paper2Poster 的 PaperQuiz、PosterMELD 的 PRR、PresentBench 的 rubric）。**你的機會在測量層。**
2. **限制模型輸出空間 = 穩定性**。SeaSlides（語意抽象層）、EditPPT（tool-selection）、ACE（98 工具 + router）都在做同一件事：不讓 LLM 自由發揮。這是你架構設計的第一原則。
3. **設計沒有 ground truth**。所以評測必須靠 (a) 可計算的違規指標、(b) 相對比較的人評、(c) 任務導向的自動問答（PaperQuiz 式）。三者至少要有兩者。
