# Paper Guide Reference

## Contents

- [固定章節](#固定章節)
- [Manifest 與證據](#manifest-與證據)
- [寫作契約](#寫作契約)
- [由淺入深](#由淺入深)
- [側欄與 notes](#側欄與-notes)
- [版面與互動](#版面與互動)
- [公式、圖表與素材](#公式圖表與素材)
- [Static validation](#static-validation)

## 固定章節

所有 computing／資訊工程論文使用以下順序。每章都保留在頁面與 TOC 中；把原本的細節併入最能支援該主張的章節，不另建獨立 figures 或 appendix 章。

| ID | 中文標題 | 必備內容 |
| --- | --- | --- |
| `overview` | 論文概覽 | 以至少兩個連貫段落交代背景、缺口、問題、方法、主要證據與貢獻；證據邊界與限制放入深入層。 |
| `context` | 背景與研究定位 | 必要背景、相關工作類型、現有方法限制，以及本文如何定位。 |
| `problem` | 問題定義 | 研究問題／任務、範圍、假設、輸入輸出、notation、目標與約束。 |
| `approach` | 方法與系統設計 | pipeline、模組／架構、演算法、資料流、公式、座標與理論推導。 |
| `setup` | 實作與驗證設計 | 資料集或資料取得、preprocessing、training、implementation、baselines、metrics、hardware/software 與 reproduction details；缺失項標狀態。 |
| `results` | 結果與分析 | 先定義 metric，再解讀主結果、比較、ablation、runtime／complexity、qualitative 與 error analysis；維持 PDF 的表格與來源順序。 |
| `discussion` | 討論與限制 | 結果含義、trade-off、限制、threats to validity、failure cases、generalizability 與 paper 支援的 ethics。 |
| `conclusion` | 結論與延伸 | 只收束有證據支持的結論、意涵與 future work，不新增主張。 |

每個 `<section>` 都要先有至少一個 `<p class="section-intro">` 作為概覽層；`overview` 要有至少兩個。概覽段落仍須是完整敘事：建立脈絡，說明關係或機制，再接證據或意涵。不要以一句話版、TL;DR、slogan、single takeaway 或單句卡片取代它。

## Manifest 與證據

Manifest 是 build-time schema 與 audit aid，不是 generic renderer 的輸入。頁面與 manifest 一起交付，並固定使用下列鍵：

```json
{
  "paper_id": "...",
  "title": "...",
  "language": "zh-Hant",
  "section_order": [
    "overview", "context", "problem", "approach",
    "setup", "results", "discussion", "conclusion"
  ],
  "sections": {
    "overview": {"status": "present", "source_pages": [1, 2]},
    "context": {"status": "not reported", "source_pages": []}
  },
  "evidence": [
    {
      "id": "approach-block-1",
      "section_id": "approach",
      "source_pages": [4],
      "refs": ["Fig. 2", "Eq. (3)"],
      "evidence_kind": "paper-stated",
      "status": "verified"
    }
  ]
}
```

Section status 只能是 `present`、`not reported`、`not applicable` 或 `unverified`。Evidence kind 只能是 `paper-stated`、`derived` 或 `guide-inference`；verification status 只能是 `verified`、`unverified` 或 `not reported`。每一組技術段落、公式、圖表解讀、結果、限制與重要結論都應有 evidence block，包含 source page；找不到來源時明確標示狀態，不把猜測寫成 paper fact。

## 寫作契約

主要解釋、章節摘要、方法解讀、結果詮釋、公式解說與重要圖表導讀一律使用完整段落。段落至少要建立「脈絡＋關係或機制＋證據或意涵」；用證據界線區分 paper-stated、derived 與 guide-inference。

可以保持原子形式的內容只有標題、控制標籤、術語／符號定義、caption、source page、`Fig./Table/Eq.` 標識與 status badge。主要內容放在 `<p>`、`<div>`、`<ol>` 或語意化 figure/table 內，不塞進僅供排版的 `<span>`，也不以單句卡片堆成章節摘要。

各章內容邊界如下：

- `overview` 第一段說背景、缺口與問題，第二段說方法、主要證據與貢獻；限制放入深入層，且只在 paper 有支持時說明。
- `context` 說明必要概念與相關工作類型，指出現有方法的限制，再交代本文定位。
- `problem` 明確寫任務、輸入／輸出、notation、目標、假設、範圍與約束。
- `approach` 連接 pipeline、模組、架構、演算法、資料流、公式、座標與推導，並用段落說明每個機制的作用。
- `setup` 逐項記錄資料與取得方式、preprocessing、training、implementation、baselines、metrics、hardware/software 與 reproduction details；未報告就保留 `not reported` 狀態。
- `results` 先定義 metric，再按 PDF 順序讀主結果、比較、ablation、runtime／complexity、qualitative 與 error analysis。表格的列、欄與來源順序不可重排。
- `discussion` 連結結果與含義，整理 trade-off、限制、threats to validity、failure cases、generalizability；ethics 只有在 paper 支援時加入。
- `conclusion` 只收束已由 evidence 支持的結論、意涵與 future work，不由結果表外推新主張。

## 由淺入深

每章的 `.section-intro` 是固定概覽層；研究細節用原生 `<details>` 分層：

```html
<details data-depth="study">
  <summary>研讀：實驗設定如何支持比較</summary>
  <p>完整段落……</p>
</details>
<details data-depth="deep">
  <summary>深入：限制與替代解釋</summary>
  <p>完整段落……</p>
</details>
```

頁面提供 `data-depth-preset="overview"`、`data-depth-preset="study"`、`data-depth-preset="deep"` 三個控制，中文顯示「概覽／研讀／深入」。preset 只能改變同一批 details 的 `open` 狀態，不複製或替換內容：概覽關閉 study/deep，研讀開 study、關 deep，深入開 study/deep。使用者仍可逐一展開或收合，且目前 preset 以 localStorage 記住；無法讀寫 storage 時仍正常使用預設值。

## 側欄與 notes

完整寬度與半寬抽屜共用同一份 TOC 與 notes DOM。保留以下狀態規則：半寬同時只開一個 drawer；close button、backdrop 與 `Escape` 都能關閉；關閉後 focus 回到 opener；closed drawer 與被遮蔽的 main 使用 `inert`；resize 回完整寬度時清除 drawer、backdrop、focus 與 scroll-lock 狀態。TOC link 在半寬選取後關閉 drawer。notes 只做 section-level 更新，不做 block observer 或 pin。

Notes tab 固定為四類：

| key | 中文 | 內容 |
| --- | --- | --- |
| `context` | 脈絡 | 以段落解釋本章和研究問題或前後章的關係。 |
| `terms` | 詞彙 | 術語、符號與簡短定義。 |
| `evidence` | 證據 | `Fig.`、`Table`、`Eq.`、source page 或 evidence status。 |
| `review` | 複習 | 以段落整理讀者應回看什麼、哪個機制或證據支持它。 |

`notes-data` 必須以八個 section ID 為 keys；每個 value 都必須有 `context`、`terms`、`evidence`、`review` 四個 array。`context` 與 `review` 的 entry 由段落呈現；`evidence` 可使用原子 reference label，但不替代正文的證據解釋。

## 版面與互動

Full width 使用左 TOC、中央 paper guide、右 notes；half width 使用 sticky compact toolbar 打開同一份 TOC 與 notes side drawers。維持 quiet research-dashboard 視覺、serif prose、sans-serif UI、固定側欄獨立捲動與兩寬度共用內容。頁面 root 不得產生 horizontal overflow；寬公式與表格只在自身 wrapper 橫向捲動。

必要互動包括 TOC anchors／active state、三個 depth presets、四個 notes tabs、半寬 drawer、backdrop／Escape、focus restoration 與 keyboard-friendly figure lightbox。保留 `prefers-reduced-motion: reduce`，並只使用既有 MathJax CDN；不要加入另一份 vendor 或 runtime。

## 公式、圖表與素材

每個主要公式要有 label、可讀 body、短段落解釋、source page 或 `Eq.` reference，以及 MathJax 失效時可讀的 `.formula-fallback`。使用 local asset path，為每個 image 提供非空 alt。保留 PDF 的 figures、tables、equations 與 table rows 順序，但把 figure 放回支援其主張的 `approach`、`setup` 或 `results`；appendix 深入內容同樣回放到相應章節的 details。

Paper-specific canvas 或 simulator 只有在能解釋明確機制時才加入，並在相同章節提供簡單、可驗的靜態 fallback marker：互動元素對應 `data-fallback-for="canvas"` 或 `data-fallback-for="simulator"` 的 fallback element。沒有這個 marker 就視為未完成。Sortable table 一律維持禁止；reading notes、best badge 等 guide annotation 不得改寫 paper values 或順序。

## Static validation

執行：

```bash
python3 skills/paper-navigator/scripts/quick_validate.py path/to/paper-guide.html --strict
```

Strict validator 應檢查：

- HTML 可讀、unique IDs、local image/script paths 與 anchors；
- HTML section order、manifest `section_order`、`sections` coverage 與 evidence `section_id` 是否完全符合八章；
- `notes-data` 是否只含八個 keys，且每章都有四個 array；
- `overview` 是否至少有兩個 `p.section-intro`，其他章是否至少有一個；
- depth preset 三個 controls，以及每章是否都有 `details[data-depth="study"]`／`details[data-depth="deep"]`；
- 未完成 placeholders／draft markers、formula fallback coverage、允許的 MathJax external runtime 與 inline JavaScript syntax；
- sortable table 一律報錯；canvas／simulator 必須位於章節內，且缺少同章對應 fallback marker 時報錯。

Paragraph contract 只做結構檢查，不做語意、字數或 NLP 判斷。`blank-paper-explainer.html` 保留 placeholders，供實際 guide 以 paper evidence 填入；strict fixture 必須先替換所有 placeholders 並使用真實存在的 local assets。
