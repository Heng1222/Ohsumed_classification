import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 讀取資料
df = pd.read_csv('mesh_dataset.csv')

# 1. 基本資訊與統計
print("--- 基本資訊 ---")
print(df.info())
print("\n--- 數值統計 ---")
print(df['wup_similarity'].describe())

# 2. 檢查缺失值
print("\n--- 缺失值檢查 ---")
print(df.isnull().sum())

# 3. 詞彙統計
unique_words = len(set(df['word_i']).union(set(df['word_j'])))
print(f"\n總唯一詞彙數: {unique_words}")

# 4. 繪製相似度分佈圖
plt.figure(figsize=(10, 6))
sns.histplot(df['wup_similarity'], bins=50, kde=True, color='skyblue')
plt.title('Distribution of MeSH WUP Similarity')
plt.xlabel('Similarity Score')
plt.ylabel('Count')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# 5. 查看最常出現的詞彙
print("\n--- 出現次數最高的詞彙 (word_i) ---")
print(df['word_i'].value_counts().head(10))