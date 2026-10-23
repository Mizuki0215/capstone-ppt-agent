from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

INK = RGBColor(0x10, 0x23, 0x3A)
GREY = RGBColor(0x5A, 0x6B, 0x7C)

doc = Document()

# ---- page + base styles ----
for sec in doc.sections:
    sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.4)
    sec.left_margin = Cm(2.6); sec.right_margin = Cm(2.6)

normal = doc.styles["Normal"]
normal.font.name = "Helvetica Neue"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(7)
normal.paragraph_format.line_spacing = 1.22
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "PingFang HK")

def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = "Helvetica Neue"
        r.font.color.rgb = INK
        r.font.size = Pt(14 if level == 1 else 11.5)
    h.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    h.paragraph_format.space_after = Pt(5)
    return h

def para(text, italic=False, size=10.5, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic
    r.font.size = Pt(size)
    if color is not None:
        r.font.color.rgb = color
    return p

def bullet(text):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
    return p

def caption(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True; r.font.size = Pt(8.5); r.font.color.rgb = GREY
    p.paragraph_format.space_before = Pt(2)
    return p

def table(headers, rows, widths, cap=None):
    if cap:
        cp = caption(cap)
        cp.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h); r.bold = True; r.font.size = Pt(8.8)
    for row in rows:
        cells = t.add_row().cells
        for i, c in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(c); r.font.size = Pt(8.6)
            p.paragraph_format.space_after = Pt(1)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True
    for cell in t.rows[-1].cells:
        for p in cell.paragraphs:
            p.paragraph_format.keep_with_next = False
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ============================ TITLE ============================
t = doc.add_paragraph()
r = t.add_run("從生成，到可驗證")
r.bold = True; r.font.size = Pt(22); r.font.color.rgb = INK
t.paragraph_format.space_after = Pt(2)

st = doc.add_paragraph()
r = st.add_run("以可量度的版面可用性，作為論文轉簡報的控制訊號")
r.font.size = Pt(11.5); r.font.color.rgb = GREY; r.italic = True
st.paragraph_format.space_after = Pt(10)

meta = doc.add_paragraph()
r = meta.add_run("CHAN Yee Tung  ·  DSAI4901 Capstone  ·  指導老師：Dr. Jibin Wu  ·  2026 年 10 月")
r.font.size = Pt(9); r.font.color.rgb = GREY
meta.paragraph_format.space_after = Pt(4)

hr = doc.add_paragraph()
hr.paragraph_format.space_after = Pt(6)
pPr = hr._p.get_or_add_pPr()
from docx.oxml import OxmlElement
pBdr = OxmlElement("w:pBdr")
bottom = OxmlElement("w:bottom")
bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
bottom.set(qn("w:space"), "1"); bottom.set(qn("w:color"), "C08A2E")
pBdr.append(bottom); pPr.append(pBdr)

# ---------------- 1 ----------------
heading("1. 背景")
para("一場會議演講只有十至十五分鐘，要講完一篇佔八頁的論文。所以 deck 不是論文的摘要，而是把論文壓縮成一條觀眾能即時跟上的論證。"
     "這個壓縮過程很慢：作者要決定留什麼、為每個論點找回那張圖，再把兩者放進一頁仍然能在房間後排看得清的版面。")
para("語言模型現在一分鐘內就能從一篇論文產生一份看起來合理的 deck。本項目的起點不是它們能不能做，而是結果能不能用——以及系統自己知不知。")
para("第二個問題之所以重要，是因為失敗並不細微。文字框跑出邊界、兩個元素重疊、caption 壓在深色背景上、一頁塞了二百五十字："
     "這些都是機械性失敗，投影的一刻就看得見。而這些正是語言模型看不見的失敗，因為它從不渲染自己寫的東西。")

# ---------------- 2 ----------------
heading("2. 現時的做法")
para("這個領域的工作大致分成兩類，旁邊長出一套評測文獻。")
para("生成。PPTAgent 把做 deck 視為編輯而非撰寫：分析參考簡報、抽出 slide 層級的 schema、輸出編輯動作。SlideGen、SlideLab、ArcDeck "
     "加上敘事規劃與多模態接地。這些系統產出的 deck 有說服力，在盲測偏好上可與商業工具競爭。")
para("修復。ReDeck 把修訂拆成原子編輯動作，每步之後取回 renderer 的觀測。PPTPilot（隨 PPTArena 提出）跑 plan–edit–check 迴圈，"
     "由視覺語言模型判斷結果。SLIDEFORGE 把 slide 保持為結構化物件，令編輯不破壞原生可編輯性。")
para("評測。SlideAudit（UIST '25）提供 27 類版面缺陷的分類法，涵蓋 2,400 張已標註 slide。DECKBench（KDD '26）以參考 deck 作比對，"
     "用相似度指標加 LLM judge 評分。PresentBench 用細緻的 rubric 評生成品質。")

table(["工作", "提供什麼", "仍未解決"],
      [["PPTAgent, SlideGen, SlideLab", "強生成器；敘事規劃", "輸出是否可用；局部失敗"],
       ["ReDeck, PPTPilot, SLIDEFORGE", "帶渲染回饋的修復迴圈", "哪些修復有用、有多少用"],
       ["SlideAudit", "缺陷分類法；2,400 張標註", "無迴圈；基於圖像；無逐類修復分析"],
       ["DECKBench", "對照參考 deck 的評分", "需要目標 deck；只排名，不驅動"]],
      [4.0, 5.4, 5.9], cap="表 1. 各部分工作提供了什麼，又留下了什麼。")

# ---------------- 3 ----------------
heading("3. 好在哪裡，差在哪裡")
para("三件事真的解決了。Deck 看起來像真：版面穩定、風格一致。輸出的可編輯性提升，因為工作已進入 .pptx 物件層。"
     "評測亦由整體打分成熟到任務式量度——只用成品答問題，或用明確準則判斷可用性。")
para("四件事仍未解決。")
bullet("歸因缺失。ReDeck 與 PPTPilot 都跑修復迴圈，但都沒有報「哪一類缺陷對修復有反應、哪一類沒有」。deck 層面升十分，只告訴我們迴圈有用，沒告訴我們用在哪裡。")
bullet("量度是事後的。SlideAudit 與 DECKBench 評的是已完成的作品。生成之後才到的分數，無法指揮生成。")
bullet("工具需要參考或標註。DECKBench 要目標 deck；SlideAudit 要人手標註圖像。兩者都無法在執行時對任意 .pptx 計算。")
bullet("閾值是慣例。用來判斷一頁是否太密的數字——六個 bullet、三十字、24pt——被廣泛重複，卻少有證據，第 6 節會說明。")

# ---------------- 4 ----------------
heading("4. 我們對文獻的判讀")
para("合起來看，這個領域很會做 deck，也很會在事後打分，但沒有把兩者接上。工具來得太遲，真的用得著的時候又不可分解。")
para("這就是本項目處理的缺口。它刻意窄：不是又一個生成器，不是新分類法，而是一層可以在生成期間計算的量度，以及研究這個量度值多少。")

# ---------------- 5 ----------------
heading("5. 為何值得做")
para("第一，這些失敗是機械性的，可以用確定性方法判定。形狀有沒有超出 slide、兩個文字框有沒有相交、一對顏色有沒有達到對比要求："
     "這些是算術，不是判斷。規則可以審核；模型的意見不可以。")
para("第二，可用性是前提。一頁讀不到的 deck，無論內容選得多好都是失敗。在讀不到的頁上改進內容，不會令演講更好。")
para("第三，結果可以轉移。如果量度無需參考、又在物件模型上計算，就可以套用到任何系統產生的任何 deck——包括本項目用來比較的 baseline。"
     "這令比較公平，也令成果可重用。")

# ---------------- 6 ----------------
heading("6. 慣例，不是證據")
para("業界不缺規則。例如 IEEE NMDC 的作者指引寫明「不要使用小於 24 point 的字級」，文字頁「不多於 30 字、不多於 6 行」。"
     "建議清楚、廣為跟隨，而且完全沒有引用證據。文中沒有任何研究支持；其他會議給的數字又不一樣。")
para("而這些規則之間彼此矛盾。六六法則允許每行六字、共六行，即一頁三十六字；上述指引卻把同一頁上限訂在三十字。兩者都寫得斬釘截鐵，"
     "兩者都沒有引用研究，而實務界已有文章主張六六法則應該淘汰。當兩條被廣泛使用的慣例相差百分之二十，而兩者都指不出證據，"
     "被傳遞下去的其實是習慣，不是知識。")
para("這裡值得分開三種錨定，因為它們份量不同，設計上必須區別對待。")
table(["錨定類型", "例子", "從哪裡來", "能否支撐量度"],
      [["正式標準", "WCAG 2.2 AA 對比 4.5:1", "知覺研究，經規範固定", "可以——可對使用者驗證"],
       ["實務慣例", "24 pt；30 字；6 行", "在指南間重複，無引用鏈", "不可以——是預設值，不是發現"],
       ["經驗數值", "重疊大於 5%", "對特定語料擬合", "只有在樣本足夠時才可以"]],
      [3.3, 4.4, 5.0, 3.6], cap="表 2. 三種錨定。只有第一種是通常意義下的證據；第三種只有在樣本支持時才算證據。")
para("慣例之所以流傳，原因與效度無關。它們容易寫、容易查，而且表面上合理。當一條慣例是錯的，沒有人需要負責，因為錯的閾值帶來的代價看不見："
     "一頁稍為太密，簡報照樣進行，觀眾只是讀得少一點。一條指引可以單靠「聽起來合理」流傳幾十年。")
para("真要驗證一條慣例，需要做什麼？改變數值、固定內容與觀眾，然後量度理解或偏好——這個設計有嚴重的混淆，因為內容質素的影響遠大於密度。"
     "這種研究在簡報領域並不存在，也不是本項目的貢獻。所以誠實的立場不是「慣例錯了」，而是「慣例承擔不起一件量度工具的重量」。")
para("後果是方法論上的。沒有已驗證的值可以 fit，而四十張校準 slide 支撐不起六個 fit 出來的閾值——每個 gate 大約六張——這樣選出的值只會是樣本的產物。"
     "所以設計改為按來源分開 gate：")
table(["Gate", "規則", "閾值", "來源"],
      [["G1 出界", "所有形狀在版面內", "0 pt", "二元規則——無自由參數"],
       ["G4 對比", "WCAG 2.2 AA，填充對背景", "4.5:1（大字 3:1）", "公開標準"],
       ["G3 字級", "依 slide 角色的內文字與標題", "按角色", "慣例；掃描，不 fit"],
       ["G6 密度", "依角色的字數與 bullet 數", "按角色", "慣例；掃描，不 fit"],
       ["G2 重疊", "文字交集 ÷ 較小框", "> 5%", "經驗值；掃描"],
       ["G5 文字溢出", "渲染高度 ÷ 框高", "≤ 0.95", "渲染容差；掃描"]],
      [2.9, 6.5, 2.8, 5.1], cap="表 3. Gate 來源。兩個 gate 由規則或公開標準固定；其餘四個只掃描，全部不 fit。")

para("「掃描，不 fit」的意思是：數值在一段範圍內報告，結論只有在整段範圍都成立時才接受。兩個標準錨定的 gate 完全沒有自由參數。"
     "由於本項目自己生成 deck，每頁的角色——標題、議程、內容、圖表、結論——在生成時已知，所以密度與字級可以按角色不同，"
     "而不需要分類器。這就消除了「標題頁與方法頁不能共用同一密度上限」的反對：它們不再共用。")

# ---------------- 7 ----------------
heading("7. 計劃與時間表")
para("工作分四條流。每條都獨立可報告，所以一條滑掉，不會令整個項目沒有結果。")
bullet("W1 量度。在 .pptx 物件模型上實作六個 gate；對每份 deck 計算 SRR 與 deck-ready。")
bullet("W2 修復。每類違規一個決策程序，先做最便宜且可逆的動作，並有護欄禁止新增內容或改動數字。")
bullet("W3 控制。在 W1 的訊號下套用 W2 的迴圈：貪心、迭代，再到預算感知。")
bullet("W4 證據。以人手標註驗證 detector；跨系統的區辨效度；驗證器的受控消融；人評。")
para("兩個檢查在主要研究之前執行，因為任何一個失敗都會令其餘失效。區辨效度問：SRR 有否按應有的次序排列系統——"
     "人手做的 deck 高於 PPTAgent，高於 naive pipeline。如果人手 deck 不是最高分，就是 gate 定義有誤，必須在任何迴圈開跑之前修訂。"
     "收斂效度問：SRR 是否跟隨人類偏好。該相關性會預先註冊，無論結果如何都會報告。")

para("有兩處刻意偏離 brief 建議的時間表。第一，brief 把「檢查」放在第 5 階段（第 12–14 週）；本項目提前到第 5 週，因為指標必須先驗證，"
     "依賴它的迴圈才建得穩。第二，brief 第 6 階段列明比較六個維度：accuracy、coverage、readability、design、latency、cost。"
     "其中 coverage——論文的重點有幾多留在 deck 裡——會獨立量度，每篇標註五至八個 claim，令六個維度全部有數。")
table(["週", "工作流", "交付", "里程碑"],
      [["W1–2", "範圍與文獻", "38 篇已讀；缺口確定", "Proposal：11 月 5 日"],
       ["W3–4", "環境與 spike", "解析與渲染可用", "Workshop 1：11 月 9 日"],
       ["W5–7", "Rulebook 與 detector", "六個 gate；40 張校準", "區辨效度檢查"],
       ["W8–11", "版面與渲染", "修復動作；110 張測試集", "首次 SRR 比較"],
       ["W12–14", "校準與迴圈", "掃描凍結；迴圈收斂", "Interim：2027 年 1 月 7 日"],
       ["W15–18", "實驗與人評", "消融；20 人研究", "偏好相關性"],
       ["W19–20", "報告與示範", "報告、demo、slides", "Final：4 月 8 日；簡報 4 月 9–21 日"]],
      [2.4, 4.4, 6.0, 4.4], cap="表 4. 對照大學時間表的排程。")

# ---------------- 8 ----------------
heading("8. 聲明")
para("本文件在撰寫與程式碼生成上使用了生成式 AI 工具。所有設計決定、指標定義、評測協議、標註與分析，均為作者本人所做。"
     "所用工具及其使用程度記錄於日誌，連同報告一併提交，符合大學的生成式 AI 使用指引。")

# ---------------- refs ----------------
heading("References")
refs = [
 "Chen, H., Zhou, X., Zhou, W., et al. (2026). X+Slides: Benchmarking audience-conditioned slide generation. arXiv:2606.19256.",
 "Hu, H., Dang, C., Liu, Y., et al. (2026). PosterMELD: Multi-agent paper-to-poster generation with editable print-ready outputs. arXiv:2608.02218.",
 "Huang, Z., Liu, X., Hu, T., Zhang, K., & Liu, Y. (2025). PPTBench: Holistic evaluation of LLMs for PowerPoint layout and design understanding. arXiv:2512.02624.",
 "IEEE Nanotechnology Materials and Devices Conference. (2021). Presentation preparation guidelines and requirements. https://ieeenmdc.org/past-conferences/nmdc-2021/call-for-papers/presentation-preparation-guidelines-and-requirements/",
 "Jang, D., Heisler, M. L., Xing, L., et al. (2026). DECKBench: Benchmarking multi-agent frameworks for academic slide generation and editing. arXiv:2602.13318.",
 "Ofengenden, M., Man, Y., Pang, Z., Gui, L.-Y., & Wang, Y.-X. (2025). PPTArena: A benchmark for PowerPoint editing. arXiv:2512.03042.",
 "Ozden, T. C., VS, S., Horoz, F., et al. (2026). Narrative-driven paper-to-slide generation via ArcDeck. arXiv:2604.11969.",
 "Pang, W., Lin, K. Q., Jian, X., He, X., & Torr, P. (2025). Paper2Poster: Towards multimodal poster automation from scientific papers. arXiv:2505.21497.",
 "Tian, M., Zeng, Z., Yang, Y., et al. (2026). ReDeck: Step-level render-grounded refinement for document-to-slide generation. arXiv:2609.00194.",
 "Vats, V., Sharma, K., & Wang, Y. (2026). SlideLab: Audience-centered scientific slide generation and evaluation. arXiv:2609.30294.",
 "Zhang, Z. J., Chen, R., Zhong, M., & Wobbrock, J. O. (2025). SlideAudit: A dataset and taxonomy for automated evaluation of presentation slides. arXiv:2508.03630.",
 "Zheng, H., Guan, X., Kong, H., et al. (2025). PPTAgent: Generating and evaluating presentations beyond text-to-slides. arXiv:2501.03936.",
 "Zheng, H., Mo, G., Yan, X., et al. (2026a). DeepPresenter: Environment-grounded reflection for agentic presentation generation. arXiv:2602.22839.",
 "Zheng, H., Wang, F., Xiong, T., et al. (2026b). SLIDEFORGE: An LLM agent for controllable editing of slides as structured artifacts. arXiv:2609.03109.",
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.first_line_indent = Cm(-0.6)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(ref); r.font.size = Pt(8.4); r.font.color.rgb = INK

out = "/Users/yeetungchan/Documents/deepseek-harness/default-workspace/capstone-ppt-agent/docs/Proposal_Background_and_Plan_ZH.docx"
doc.save(out)
print("saved", out)
