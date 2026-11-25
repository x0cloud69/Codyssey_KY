from pathlib import Path
import pandas as pd

data_path = Path("data/raw/olist_products_dataset.csv")
df = pd.read_csv(data_path)

print("행과 열:", df.shape)
print("\n컬럼 이름:")

# dataframe의 컬럼 이름을 리스트로 변환하여 출력
print(df.columns.tolist())
print("\n앞의 5개 행:")

# dataframe의 앞 5개 행을 출력
print(df.head())
print("\n 통계 정보:")
print(df.describe())
print("\n전체 행:")

print(df)