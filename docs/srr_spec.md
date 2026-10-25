# SRR：形式定義（v0.1）

狀態：2026-10-25 · 對應 WBS P2.17a · 實作時以此為準

---

## 0. 為什麼要寫這份東西

投影片上的一句話「可判斷的檢查之中，通過的比例」在口頭答辯撐得住，但在論文裡撐不住 ——
審稿人會問三個問題：**分母是什麼、平均是怎麼平均的、判斷不到算不算**。
以下逐項釘死。

## 1. 符號

| 符號 | 意思 |
|---|---|
| `G` | 六條規則，`G = {G1..G6}`, `n = 6` |
| `S` | 一份 deck 的所有 slide |
| `r(s)` | slide `s` 的角色（title / content / figure / conclusion …） |
| `θ` | 門檻向量，`θ_g(r)` 是 gate `g` 在角色 `r` 的門檻 |
| `C_{s,g}` | slide `s` 上 gate `g` 的**檢查實例**集合（每個形狀、每個 run、每一對重疊） |
| `v(c) ∈ {pass, fail, na, unknown}` | 單一檢查的判定 |

**檢查實例（check instance）** 是這份定義的基本單位，不是「一張 slide × 一個 gate」。
理由：一頁有 6 個字的 textbox 和一個 9pt 的 textbox，G3 應該算兩次，不是一次。

## 2. 可判斷集與通過集

```
J_{s,g} = |{ c ∈ C_{s,g} : v(c) ∈ {pass, fail} }|      # 判斷得到的
P_{s,g} = |{ c ∈ C_{s,g} : v(c) = pass }|              # 其中通過的
```

`na`（不適用）與 `unknown`（可適用但算不出）**都不入分母**，但兩者分開記錄：

| 判定 | 例子 | 入分母？ | 記錄 |
|---|---|---|---|
| `pass` | 字級 24pt ≥ 下限 18 | 是 | value, threshold |
| `fail` | 字級 9pt < 18 | 是 | value, threshold, shape id |
| `na` | 一頁只有一個 textbox，G2 沒有「成對」可比較 | 否 | reason code `no_pair` |
| `unknown` | 背景是圖片，G4 算不出有效背景色 | 否 | reason code `image_background` |

## 3. Deck 層面：兩個平均，主指標只有一個

```
SRR      = Σ_{s∈S} Σ_{g∈G} P_{s,g}  /  Σ_{s∈S} Σ_{g∈G} J_{s,g}        (check-level, micro)
SRR_slide = (1/|S|) Σ_{s∈S} ( Σ_g P_{s,g} / Σ_g J_{s,g} )             (slide-level, macro)
```

**主指標是 `SRR`（check-level micro）**，理由：

1. 它與「每個檢查權重相等」這句話一致 —— 每張 slide 的權重取決於它有多少檢查，而不是一張 2 個檢查的標題頁與 6 個檢查的內容頁同權。
2. `J_{s,g} = 0` 時不需要特例（該頁自然貢獻 0/0，不影響總和）；macro 版本則要處理「0 個檢查」的除零。
3. 它對「多一頁」不敏感，只對「多一個違規」敏感 —— 這正是我們想要的。

`SRR_slide` **仍然要報**，因為它答的是另一個問題：「有幾多頁是乾淨的」。兩者不可互相取代。

**逐 gate 分解（這是本論文的貢獻，不是附錄）：**

```
SRR_g = Σ_s P_{s,g} / Σ_s J_{s,g}          for each g
```

沒有 `SRR_g`，就答不到「哪一類缺陷對修復有反應」—— 而那正是 A2 − A1 要拆開的東西。

## 4. 掃描，不是擬合

門檻不是一個數，是一個範圍：

```
SRR(θ)  where θ ∈ Θ = Π_g [lo_g, hi_g]
```

例如 `θ_G3(content) ∈ [14, 22] pt`、`θ_G2 ∈ [2%, 10%]`。

**結論的接受條件**：一個比較（例如 A2 > A1）只有在 `∀θ ∈ Θ` 都成立時才寫進論文。
否則報「在 θ 的哪一段成立、哪一段不成立」。這是「swept, not fitted」的形式版本。

## 5. Deck-ready：避開那個陷阱

前一版草案寫成 `∀s: |J_s| = |G| ∧ |P_s| = |G|`，這在實際資料上**永遠是 0**：
任何一份 deck 都有標題頁（G2 沒有成對的文字框）、都會有圖片背景（G4 unknown）。這條定義會令指標失去用途。

正確的寫法分兩層：

```
DeckReady = 1   iff   (∀s,g: P_{s,g} = J_{s,g})        # 沒有任何 fail
                 and  (∀g: Σ_s J_{s,g} ≥ 1)             # 每條 gate 至少被行使過一次
```

白話：
1. **冇任何違規**（不是「大部分通過」）；
2. **每條 gate 至少在某處真的判斷過** —— 標題頁不需要 G6，但整份 deck 要有某一頁被 G6 檢查過。

這條不需要任何新的自由參數（沒有「X% N/A 就不計分」這種拍出來的數），而且標題頁不再拖死整份 deck。

另外報三個診斷量，唔改 DeckReady 的定義：

```
fail_free    = 1 iff ∀s,g: P_{s,g} = J_{s,g}              # 忽略可判斷性，只看有沒有 fail
decidability = Σ_{s,g} J_{s,g} / (|S| · |G|)              # 六條規則平均被行使了多少
n_unknown    = 記錄數量，按 reason code 分組
```

`decidability` 低就是老實話：這份 deck 有幾多東西我們其實量不到。這比假裝全部量到更有價值。

## 6. N/A 的紀律（每一條 gate 都要有前置條件）

「判斷不到」不可以由程式隨意決定，每條 gate 都要有一個**寫得出來的前置條件**：

| Gate | 可判斷的必要條件 | `na` 的理由 | `unknown` 的理由 |
|---|---|---|---|
| G1 出界 | 至少一個有面積的形狀 | `empty_slide` | — |
| G2 重疊 | 至少兩個有文字的形狀 | `fewer_than_two_text_shapes` | — |
| G3 字級 | 至少一個 run 帶明確字級 | `no_explicit_size` | `theme_size_unresolved` |
| G4 對比 | 有效背景色可解析 | `no_text` | `image_background`, `gradient_background` |
| G5 溢出 | 有高度可量的 text frame | `autofit_shape`（另記警告） | `font_missing` |
| G6 密度 | 該頁有文字 | `no_text` | — |

規則：**`na` 由前置條件決定，`unknown` 由解析失敗決定，兩者都必須帶 reason code。**
沒有 reason code 的「判斷不到」一律當 `null` 處理，並在報告中列為缺陷。

## 7. 兩件仍然要交待人判斷的事

1. **`unknown` 比例高時怎麼辦** —— 不是降低標準，而是改進解析（例如漸層取中位色，標記為估算）。若 `decidability < 0.8`，該 deck 的 SRR 要附註，不可與其他 deck 直接比。
2. **G3/G6 的門檻本身是慣例** —— 所以它們一定要在 `Θ` 裡掃描；G1（0 pt）與 G4（WCAG）沒有自由參數，可以直接用。

## 8. 用現有資料演示一次

`out/PPTAgent_2501.03936.pptx`：9 頁、4 條 gate 已實作、33 個違規。

- slide-level（現行程式）：`clean_slides / slides = 0/9 = 0.00`
- check-level（本 spec）：分母 ≈ 9 × 4 = 36 個檢查（G1/G2 每頁各 1 次、G3/G6 依實例數），通過 ≈ 3 → **SRR ≈ 0.08**

兩個數都真，答的問題不同：`0.00` 是「有幾多頁完全乾淨」，`0.08` 是「逐個檢查計，通過率幾多」。
論文寫 `SRR`，圖表可以兩個都放。
