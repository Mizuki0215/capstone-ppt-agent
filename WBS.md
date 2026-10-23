# DSAI4901 — Work Breakdown Structure

**審核時間**：2026-10-23 (Fri) 16:37 HKT
**用途**：把「20 週 capstone」拆成 30 分鐘 – 3 小時一個 job，每個 job 一個動詞、一個產出、一句驗收。
**原則**：做唔完就再拆，唔准有「寫 methodology」呢類 job。

---

## 0. 拆件規則

| 規則 | 內容 |
|---|---|
| 大小 | 0.3 – 4 h。超過 4 h 即場再拆 |
| 一個 job 一個 artefact | 檔案、數據、段落，唔係「研究一下」 |
| 驗收句 | 寫得出一條可以 check 的條件（有數字或有檔名） |
| 依賴 | 用 job ID 標明，冇依賴就 `—` |
| 標籤 | `S` 環境 · `M` 量度 · `R` 維修 · `C` 控制 · `E` 證據 · `W` 寫作 |
| Buffer | 每個 block 完後預留 20% 空檔，唔排 job |

---

## 1. 現況審核（睇 code，唔睇計劃書）

| 資產 | 實際狀態 | 同舊文件落差 |
|---|---|---|
| `src/parse.py` (151 行) | PyMuPDF 抽 section + figure caption，已可跑 | ✅ 已存在，`CATCHUP_PLAN.md` 話「Stage 1–2 未開始」係錯 |
| `src/compose.py` (208 行) | outline/bullets/notes，deterministic + `--llm` | ✅ |
| `src/render.py` (138 行) | python-pptx 出 deck + speaker notes | ✅ |
| `src/detect.py` (147 行) | **只有 G1 / G2 / G3 / G6** | ❌ G4 contrast、G5 text fit 未寫 |
| `build/detect_v1.json` | DOC2PPT 9 頁：**0 頁 clean、SRR 0.0**；G3 命中 9/9、G6 命中 8/9 | 數字已有，但只 2 份 deck、無 labelling |
| `rulebook.md` v0 | 20 個 `[ ]` / `[?]` 未決 | 呢 20 條就係 P2 的前半 |
| `research/pdfs/` | 42 個檔；**SlideGen、PresentBench 兩篇都有全文** | 所以引用可以即刻補，唔需要再搜 |
| `docs/` | EN + ZH proposal，DOCX + PDF，4 個表 | 2 條引用缺失、4 條 uncited、週次對唔上日曆 |
| 測試 / CI | 冇 unit test、冇 CI | 未建 |
| Held-out 標註集 | 冇 | 未開始 |
| Baseline 對比 | 冇 | 未開始 |
| 人評 | 冇 | 未開始 |

**一句總結**：生成鏈路（parse→compose→render）已通；**量度層缺 2/6 gate、無標註集、無 repair、無 loop、無證據**。proposal 賣的就是那條缺失的鏈，所以 P2 之後全部係真工。

---

## 2. WBS

### P0｜提案交付（10/23 – 11/05，死線 10/29 交 supervisor）— 14.8 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P0.1 | 補 2 條缺失 reference | `build_doc.py` REFS | SlideGen (Liang et al. 2025, arXiv:2512.04529) 與 PresentBench (Chen et al. 2026, arXiv:2603.07244) 可追到正文引用 | 1.0 | — |
| P0.2 | 處置 4 條 uncited reference（PPTBench / X+Slides / PosterMELD / DeepPresenter） | 同上 | 每條要麼在 §2–§3 有引用句，要麼刪 | 1.0 | — |
| P0.3 | 修 Table 4 週次對日曆 | 同上 | 週次與 2026-11-05 / 2027-01-07 / 2027-04-08 三個日子一致 | 1.0 | — |
| P0.4 | Workshop 1 改「TBC (≈9 Nov)」 | 同上 | 唔再斷言 9 Nov | 0.3 | — |
| P0.5 | §7 加一行 brief 指定 stack | 同上 | 出現 PyMuPDF / python-pptx / Streamlit / CodeBuddy | 0.5 | — |
| P0.6 | §8 明寫本文同時係 AI report 的基礎 | 同上 | 一句 | 0.3 | — |
| P0.7 | 重出 EN（DOCX → PDF） | `docs/*.docx` `.pdf` | 6 頁、4 個表、無斷表 | 0.75 | P0.1–6 |
| P0.8 | ZH 同步同一批改動 | `*_ZH.*` | 兩版段落結構一致（63 段 / 4 表） | 1.0 | P0.7 |
| P0.9 | 由頭讀一次 EN | — | 讀完，改動已入 | 1.5 | P0.8 |
| P0.10 | 6 頁 supervisor 問題 deck | `deck/` 新 pptx | brief p9 要求：問題 + 已試方案各一頁 | 2.0 | — |
| P0.11 | Email supervisor | 已寄出的信 | 附 PDF，問 3 件事，**10/29 前** | 0.5 | P0.7, P0.10 |
| P0.12 | git init + 首 commit + 週報模板 | repo + `docs/weekly/` | 由空資料夾到跑起 ≤ 3 command | 1.0 | — |
| P0.13 | 收 feedback → 改 → 11/05 提交 | 系統已提交 | 提交編號 | 4.0 | P0.11 |

### P1｜基礎加固（W3–4，11/09 – 11/22）— 23.5 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P1.1 | 凍結 `deck.json` / `plan.json` schema | `docs/contract.md` | 3 支 script 只讀 contract 內欄位 | 1.5 | — |
| P1.2 | 8 篇 held-out 跑 parse，記 failure mode | `docs/parse_report.md` | 8 篇成功率 + 失敗分類 | 2.5 | P1.1 |
| P1.3 | figure 抽取成功率 | 同上 | caption→bbox 對得上 ≥ 70% | 2.0 | P1.2 |
| P1.4 | table 轉文字 fallback | `src/parse.py` | figure 失敗時有替代 | 2.0 | P1.3 |
| P1.5 | parse 單元測試（3 fixture） | `tests/` | `pytest -q` 綠 | 2.0 | P1.2 |
| P1.6 | claim 抽取（每篇 5–8 條） | `src/claims.py` | 8 篇各出 5–8 條，可人手改 | 3.0 | P1.2 |
| P1.7 | speaker notes schema：轉場句 + 每節時間預算 | `src/compose.py` | notes 含 transition + 秒數 | 2.0 | — |
| P1.8 | 第二套 template（minimal） | `src/render.py` | `--template minimal` 出到 deck | 2.5 | — |
| P1.9 | 圖片 contain 唔拉伸 | 同上 | aspect ratio 誤差 < 1% | 1.5 | — |
| P1.10 | 鎖 13.333×7.5 / 16:9 | 同上 | 每份 deck 都有 assertion | 0.5 | — |
| P1.11 | `run.sh` 8 篇全通 + 記 latency/cost | `out/ledger.csv` | 8 行，無 crash | 2.0 | P1.2–10 |
| P1.12 | baseline A：固定模板人手填 | `baseline/A/` | 1 篇示範 + 流程文件 | 2.0 | — |

### P2｜W1 量度（W5–7，11/23 – 12/13）— 41.5 h

**前半：把 rulebook 由 v0 凍結成 v1（20 條決定）**

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P2.1 | G1 4 條決定（full-bleed / 被遮 / group / 零面積） | `rulebook.md` | 每條由 `[ ]` 變 `[x]` | 1.0 | — |
| P2.2 | G2 5 條（背景形狀 / panel / 疊標題 / 旋轉 / 字壓圖） | 同上 | 同上 | 1.0 | — |
| P2.3 | G3 5 條（角色下限 / 表格 / chart 遞歸 / autofit） | 同上 | 同上 | 1.0 | — |
| P2.4 | G4 4 條（有效背景 / 漸層圖 / theme 色 / 連結色） | 同上 | 同上 | 2.0 | — |
| P2.5 | G5 5 條（字體代入 / 斷行誤差 / CJK / autofit） | 同上 | 同上 | 2.0 | — |
| P2.6 | G6 5 條（空格 / bullet 記號 / 標題算唔算 / CJK / 表格） | 同上 | 同上 | 1.5 | — |
| P2.7 | 跨切面 4 條（pt 單位 / gate 次序 / 多重違規 / 雙標註） | 同上 | 同上 | 1.0 | — |

**後半：實作（G4、G5 係長桿）**

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P2.8 | G1 實作（旋轉 bbox + group） | `src/gates/g1.py` | 對 detect_v1 的 2 份 deck 結果不變 | 2.0 | P2.1 |
| P2.9 | G2 實作（AABB + 旋轉多邊形） | `g2.py` | 同上 | 2.5 | P2.2 |
| P2.10 | G3 實作（role minima + theme 繼承） | `g3.py` | 同上 | 2.0 | P2.3 |
| P2.11 | **G4 顏色解析**（theme→RGB、z-order 有效背景） | `g4.py` | 每個 run 都解得到一個背景色或 `unknown` | 4.0 | P2.4 |
| P2.12 | G4 WCAG ratio + 已知色對 unit test | `tests/test_contrast.py` | #767676 on #FFF = 4.54 | 1.5 | P2.11 |
| P2.13 | G4 漸層/圖片背景 fallback | `g4.py` | 標 `unknown` 而唔係亂報 | 3.0 | P2.11 |
| P2.14 | **G5 font metrics + wrap estimator** | `g5.py` | 給定字串與框寬，出高度（pt） | 4.0 | P2.5 |
| P2.15 | G5 對 LibreOffice 實渲染驗誤差 | `docs/g5_validation.md` | 20 頁，高度相對誤差中位數 < 15% | 3.0 | P2.14 |
| P2.16 | G6 role-aware density | `g6.py` | title slide 與 content slide 用唔同上限 | 2.0 | P2.6 |
| P2.17 | SRR 定義 + 實作 | `src/srr.py` | 對 2 份 deck 出一個 0–1 數 | 2.0 | P2.8–16 |
| P2.18 | deck-ready + CLI v2 + JSON schema + regression fixture | `detect.py` v2 | `--json` 有 schema 版號 | 2.0 | P2.17 |
| P2.19 | 建區辨效度語料（人手 deck / PPTAgent / naive） | `data/validity/` | 3 組，每組 ≥ 5 份 | 2.0 | P2.18 |
| P2.20 | **跑區辨效度，寫結果** | `docs/validity_1.md` | 三組 SRR 排序，附圖 | 2.0 | P2.19 |

> **P2.20 係 GO/NO-GO**：人手 deck 唔係最高分 → 修 gate 定義，唔准開 P4。

### P3｜W2 維修（W8–11，12/14 – 01/17）— 28.0 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P3.1 | repair action 清單（cheapest-first） | `docs/repair.md` | 每類違規 1–3 個動作，有理由 | 1.5 | P2.7 |
| P3.2 | guardrail：唔准加內容／改數字 | `src/guard.py` | 對 50 個 repair 全部擋得住 | 2.0 | P3.1 |
| P3.3 | G1 repair（nudge + clamp + group） | `repair/g1.py` | 修完 G1 = 0 | 2.0 | P3.2 |
| P3.4 | G3 repair（升到角色下限，再跑 G5） | `repair/g3.py` | 修完 G3 = 0 且無新 G5 | 1.5 | P3.2 |
| P3.5 | G6 repair（拆頁 / 縮 bullet） | `repair/g6.py` | 修完 G6 = 0，頁數可增 | 3.0 | P3.2 |
| P3.6 | G2 repair（grid search 空位） | `repair/g2.py` | 修完 G2 = 0 | 2.5 | P3.2 |
| P3.7 | G4 repair（加深字色 / 加背板） | `repair/g4.py` | 修完 G4 = 0 | 2.0 | P3.2 |
| P3.8 | G5 repair（減字或擴框） | `repair/g5.py` | 修完 G5 = 0 | 2.0 | P3.2 |
| P3.9 | action log + 每類 repair 成本 | `out/actions.csv` | 每動作記 gate、耗時、ΔSRR | 1.5 | P3.3–8 |
| P3.10 | 110 頁測試集組裝 | `data/test110/` | 110 頁 + provenance 表 | 4.0 | P2.18 |
| P3.11 | 標註 pass 1（兩人獨立） | `data/labels_a.json` | 兩份獨立檔 | 4.0 | P3.10 |
| P3.12 | adjudication + per-class agreement | `docs/agreement.md` | 每類 Cohen's κ | 2.0 | P3.11 |

### P4｜W3 控制（W12–14，01/18 – 02/07）— 14 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P4.1 | loop skeleton | `src/loop.py` | 一輪 measure→repair→measure 跑得完 | 2.0 | P3.9 |
| P4.2 | greedy + 終止條件 + 震盪防護 | 同上 | 唔會無限循環 | 2.5 | P4.1 |
| P4.3 | budget-aware（ΔSRR per $ / per s） | 同上 | 出 budget 曲線 | 3.0 | P4.2 |
| P4.4 | controller on/off 開關 | 同上 | `--no-inspect` 出唔同 SRR | 1.5 | P4.2 |
| P4.5 | 掃描 runner（120/140/160 等） | `src/sweep.py` | 一次跑完一組 | 2.0 | P2.18 |
| P4.6 | 凍結掃描 + calibration 報告 | `docs/calibration.md` | 結論在整段掃描值域都成立 | 1.5 | P4.5 |
| P4.7 | 首次 SRR 對比表 | `docs/srr_compare.md` | 5 個系統 × 6 gate | 1.5 | P4.3 |

### P5｜W4 證據（W15–18，02/08 – 03/07）— 24.5 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P5.1 | 預註冊收斂效度假設 | `docs/prereg.md` | 有日期、有方向、有 alpha | 1.0 | — |
| P5.2 | ablation 設計（off / on / random-repair） | `docs/ablation.md` | 三臂各評乜寫清 | 1.0 | P4.4 |
| P5.3 | 跑 ablation 8 篇 × 3 臂 | `out/ablation.csv` | 24 行完整 | 4.0 | P5.2 |
| P5.4 | 統計：paired test、effect size、per-class 歸因 | `docs/stats.md` | 每個 gate 一個 Δ + CI | 3.0 | P5.3 |
| P5.5 | 人評 protocol + 同意書 | `docs/study.md` | 20 人可行 | 2.0 | — |
| P5.6 | 招 20 位參與者 | 已確認名單 | ≥ 20 | 2.0 | P5.5 |
| P5.7 | 跑 session | `out/human.csv` | 每人 ≥ 20 對比較 | 6.0 | P5.6 |
| P5.8 | coverage 標註（5–8 claim × 8 篇） | `data/claims.json` | 8 篇齊 | 4.0 | P1.6 |
| P5.9 | cost/latency ledger | `out/ledger.csv` | 每個系統每篇一行 | 1.5 | P4.7 |

### P6｜報告與示範（W19–22，03/08 – 04/08）— 38 h

| ID | Job | 產出 | 驗收 | h | Dep |
|---|---|---|---|---|---|
| P6.1 | Interim 大綱 | `docs/interim_outline.md` | 節標題 + 每節一句 | 1.0 | — |
| P6.2 | Interim 初稿 | `Interim_Report.docx` | 20–25 頁 | 7.0 | P6.1, P2.20 |
| P6.3 | Interim 校對 + 01/07 提交 | 已提交 | 提交編號 | 2.0 | P6.2 |
| P6.4 | master deck 每月更新（5 次） | `deck/master.pptx` | 每次例會前更新 | 5.0 | — |
| P6.5 | Final report 五節 | `Final_Report.docx` | 對應 5 個章 | 12.0 | P5.4, P5.7 |
| P6.6 | Turnitin + AI report / log | 兩份 | 兩份都交 | 2.0 | P6.5 |
| P6.7 | Streamlit demo（upload / preview / download） | `app.py` | 上傳 PDF 出可下載 pptx | 4.0 | P4.3 |
| P6.8 | Presentation deck + 排練 | `deck/final.pptx` | 15 分鐘講得完 | 5.0 | P6.6 |

---

## 3. 日曆（同 proposal Table 4 對過）

| 期間 | 主要 block | 硬節點 |
|---|---|---|
| 10/23 Fri – 10/29 Thu | P0.1–P0.11 | **10/29 交 supervisor**（brief p9：死線前一星期） |
| 10/30 – 11/04 | P0.13 buffer + P1.1–1.3 | 等 feedback，唔好排滿 |
| 11/05 Thu | 提交 | **Proposal due** |
| 11/09 – 11/22 (W3–4) | P1 完成、P2.1–P2.7 | W5 開始做 gate 實現 |
| 11/23 – 12/13 (W5–7) | P2.8–P2.20 | **12/13 區辨效度 GO/NO-GO** |
| 12/14 – 01/17 (W8–11) | P3 主體；**12 月中起並行 P6.1–6.3** | **01/07 Interim** |
| 01/18 – 02/07 (W12–14) | P4 + P3.10–3.12 標註 | 掃描凍結 |
| 02/08 – 03/07 (W15–18) | P5 全部 | 人評完 |
| 03/08 – 04/08 (W19–22) | P6.5–6.8 | **04/08 Final + 04/09–21 簡報** |

**兩個撞期發現，寫 proposal 前要處理：**

1. **Table 4 的週次唔係一個一致日曆。** 11/05 → 04/08 實際係 **22 週**，唔係 20 週；而且用同一套 W 編號，interim 01/07 會落在 W11，唔係表上寫的 W12–14。要麼改 W1–W22，要麼加一行 `W21–22 contingency`，唔好留住一個對唔上的編號。
2. **Interim（01/07）在 P3 未完之前。** 即係 interim 只可以報 W1 量度 + 區辨效度 + 初步 repair 個案，**唔可能有 ablation 結果**。章節結構要照此寫，否則 12 月一定趕唔切。

---

## 4. 關鍵路徑

```
P0.7/P0.8 ─► P0.11 (10/29) ─► P0.13 (11/05)
P2.1–P2.7 (rulebook 凍結)
   └─► P2.8–P2.16 (六個 gate；G4 + G5 共 15.5 h 係長桿)
          └─► P2.17–P2.18 (SRR)
                 └─► P2.19–P2.20 ──[GO/NO-GO]──► P3.1 ─► P3.2 ─► P3.3–P3.8
                        └─► P3.10–P3.12 ─► P4.1–P4.7 ─► P5.2–P5.4 ─► P6.5
```

**長桿風險**：G5（font metrics + wrap）同 G4（theme 色解析）合共 15.5 h，係全項目最容易超時的兩件。
**降級方案**（寫入 risk）：G5 驗證誤差 > 25% → 改為只報 `autofit` 警告，唔計入 SRR；G4 image 背景 → 一律 `unknown` 唔計。呢個降級要**在 12/13 之前決定**，唔好拖到 1 月。

---

## 5. 工時總表

| Block | 期間 | 計劃工時 | +20% buffer |
|---|---|---|---|
| P0 提案 | 10/23 – 11/05 | 14.8 h | 17.8 |
| P1 基礎 | W3–4 | 23.5 h | 28.2 |
| P2 量度 | W5–7 | 41.5 h | 49.8 |
| P3 維修 | W8–11 | 28.0 h | 33.6 |
| P4 控制 | W12–14 | 14.0 h | 16.8 |
| P5 證據 | W15–18 | 24.5 h | 29.4 |
| P6 報告 | W19–22 | 38.0 h | 45.6 |
| **總計** | 22 週 | **184.3 h** | **221.2 h** |

`CATCHUP_PLAN.md` 假設 15–20 h/週 × 20 週 = 300–400 h。計劃用 221 h，**剩 79–179 h 係 buffer**，剛好覆蓋 figure 抽取重做同人評超時 —— 所以呢個 profile 係緊但有餘，唔需要再收窄 scope。

---

## 6. 今日（10/23）就開始的三個 job

1. **P0.1**（1.0 h）補 SlideGen + PresentBench 兩條 reference — 兩篇 PDF 已在 `research/pdfs/`，首頁 metadata 已核實。
2. **P0.2**（1.0 h）四條 uncited reference：每條加一句引用或刪。
3. **P0.3**（1.0 h）Table 4 週次改為一致日曆。

三個加埋約 3 h，今晚做完，P0.7 明日就可以重出 PDF，10/29 交 supervisor 就唔會趕。

---

## 7. 只有你可以決定的事（會擋住 P2 / P5）

| # | 問題 | 點解要現在答 |
|---|---|---|
| D1 | **單人定小組？** brief p5 列三位同學，`CATCHUP_PLAN.md` 寫單人 | 決定 P0.11 問 supervisor 的第一條，亦決定 scope 收窄表要唔要入 proposal |
| D2 | **人手 deck 從邊嚟？** P2.19 要靠「人手做的 deck」做區辨效度的上界 | 冇語料就冇 GO/NO-GO；DECKBench 有 1,200 張 slide、PPTAgent 有 released decks，要現在確認可唔可以取得 |
| D3 | **G6 留唔留？** proposal 自己講 G6 係 convention、冇證據 | 若 reviewer 追問，要有答案：留（因為 sweep 過、可分解）定降為 warning |
