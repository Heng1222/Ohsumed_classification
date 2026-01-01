# Model
- 這個資料夾用來存放實際訓練的 CoLab 檔案
- 將整理好的 Dataset(*.csv) 放在雲端空間，再從 CoLab 內讀取。
- 比較三種不同模式下的模型下游分類任務表現(basic/with MLM/LoRA with MeSH)

## Training/Testing data config
- 資料筆數、切割方法、seedNum、filter 等前處理設定
- 3種比較方法的分類器皆須使用相同資料集
- MLM Training/classifier Training/classifier testing

## NN classifier
- 模型頂層的分類器，訓練參數和方法都要相同
- 23種下游分類類別

## TODO
- [ ] RoBERTa basic model 直接做下游分類任務
- [ ] RoBERTa basic model + Training Data 做MLM學習後再做下游分類任務
- [ ] RoBERTa basic model + LoRA(Mesh) 後再做下游分類任務