# Ohsumed 資料集分類說明

這個資料夾主要進行 Ohsumed 醫療文獻資料集建立與基本 EDA 分析。共包含兩個主要腳本：
1.  `create_dataset.py`: 用於從原始的資料夾結構中建立一個完整的 CSV 資料集。
2.  `readfile.py`: 用於讀取已生成的 CSV 檔案，並對其進行探索性資料分析 (EDA)。

---

## `create_dataset.py` 所需資料架構

`create_dataset.py` 腳本需要一個特定的資料夾結構來生成 `ohsumed_dataset.csv` 檔案。腳本會掃描其所在的目錄，尋找代表不同**類別 (Label)** 的子資料夾。

### 架構要求：

-   每一個類別都必須是一個**獨立的子資料夾**。
-   腳本預設會尋找名稱以 `C` 開頭的資料夾 (例如 `C01`, `C02`, `C23` 等)。
-   每個子資料夾內的**每一個檔案**都應包含一篇醫療文獻的**原始文本 (Text)**。

### 示範結構：

執行 `create_dataset.py` 之前，您的資料夾結構應如下所示：

```
.
├── C01/
│   ├── 1.txt
│   ├── 2.txt
│   └── ...
├── C04/
│   ├── 101.txt
│   ├── 102.txt
│   └── ...
├── C23/
│   ├── 250.txt
│   ├── 251.txt
│   └── ...
├── create_dataset.py
└── readfile.py
```

執行後，腳本會生成一個名為 `ohsumed_dataset.csv` 的檔案。腳本會將每個檔案的第一行作為 `title`，其餘內容作為 `abstract`。其內容格式如下：

| title                      | abstract                  | label |
| -------------------------- | ------------------------- | ----- |
| (檔案 `C01/1.txt` 的第一行) | (檔案 `C01/1.txt` 的剩餘內容) | C01   |
| (檔案 `C04/101.txt` 的第一行)| (檔案 `C04/101.txt` 的剩餘內容)| C04   |
| ...                        | ...                       | ...   |

---

## 探索性資料分析 (EDA)
- Total number of `ohsumed_dataset.csv` records: 56984
- `readfile.py` 腳本會讀取 `ohsumed_dataset.csv` 並針對 `label`, `title`, 和 `abstract` 三個欄位進行獨立分析，生成以下關於資料集分佈的圖表。

### 標籤分佈 (Label Distribution)

下圖顯示了資料集中各個類別（標籤）的樣本數量分佈。可以看出不同類別的樣本數存在不平衡的狀況。

![標籤分佈](img/eda_labels_complete_dataset.png)

### 標題長度分佈 (Title Length Distribution)

下圖顯示了資料集中所有**標題**的字元長度分佈狀況。

![標題長度分佈](img/eda_title_length_complete_dataset.png)

### 摘要長度分佈 (Abstract Length Distribution)

下圖顯示了資料集中所有**摘要**的字元長度分佈狀況。

![摘要長度分佈](img/eda_abstract_length_complete_dataset.png)

## Sample
```
title,abstract,label
Haemophilus influenzae meningitis with prolonged hospital course.,"A retrospective evaluation of Haemophilus influenzae type b meningitis observed over a 2-year period documented 86 cases.
 Eight of these patients demonstrated an unusual clinical course characterized by persistent fever (duration: greater than 10 days), cerebrospinal fluid pleocytosis, profound meningeal enhancement on computed tomography, significant morbidity, and a prolonged hospital course.
 The mean age of these 8 patients was 6 months, in contrast to a mean age of 14 months for the entire group.
 Two patients had clinical evidence of relapse.
 Four of the 8 patients tested for latex particle agglutination in the cerebrospinal fluid remained positive after 10 days.
 All patients received antimicrobial therapy until they were afebrile for a minimum of 5 days.
 Subsequent neurologic examination revealed a persistent seizure disorder in 5 patients (62.5%), moderate-to-profound hearing loss in 2 (25%), mild ataxia in 1 (12.5%), and developmental delay with hydrocephalus which required shunting in 1 (12.5%).
 One patient had no sequelae.",C01
```
```
Sample Record 1:
title       Haemophilus influenzae meningitis with prolong...
abstract    A retrospective evaluation of Haemophilus infl...
label                                                     C01
Name: 0, dtype: object

Sample Record 2:
title          Augmentation mentoplasty using Mersilene mesh.
abstract    Many different materials are available for aug...
label                                                     C01
Name: 1, dtype: object

Sample Record 3:
title       Multiple intracranial mucoceles associated wit...
abstract    The purpose of this article is to alert clinic...
label                                                     C01
Name: 2, dtype: object

Sample Record 4:
title       Replacement of an aortic valve cusp after neon...
abstract    Septic arthritis developed in a neonate after ...
label                                                     C01
Name: 3, dtype: object

Sample Record 5:
title       Mucosal intussusception to avoid ascending cho...
abstract    Many methods have been devised to prevent asce...
label                                                     C01
Name: 4, dtype: object
```