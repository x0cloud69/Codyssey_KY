"""Olist 이커머스 데이터 분석 파이프라인.

`notebooks/analysis_report1.ipynb`에서 검증한 로직을 재사용할 수 있게 클래스로 정리했다.
이미지는 matplotlib(imread)과 NumPy만 사용한다(OpenCV, Pillow를 직접 쓰지 않는다).
"""
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np
import pandas as pd


class DataAnalyzer:
    """CSV 하나를 읽어 품질 점검, 결측 처리, 이상치 탐지, 피처 생성, RFM 분석을 한다."""

    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.df = None

    # ------------------------------------------------------------------ 공통
    def _require_data(self):
        if self.df is None:
            raise ValueError("먼저 load_data()를 실행하세요.")

    def load_data(self, **read_csv_kwargs):
        """CSV를 읽어 self.df에 저장한다. usecols 등 read_csv 옵션을 그대로 넘길 수 있다."""
        self.df = pd.read_csv(self.data_path, **read_csv_kwargs)
        return self.df

    # ------------------------------------------------------------------ 품질 점검
    def check_quality(self):
        """행/열 수, 컬럼별 결측 개수, 중복 행 수를 딕셔너리로 돌려준다."""
        self._require_data()
        return {
            "shape": self.df.shape,
            "missing": self.df.isna().sum().sort_values(ascending=False),
            "duplicates": int(self.df.duplicated().sum()),
        }

    # ------------------------------------------------------------------ 결측 처리
    def handle_missing_values(self, group_col, target_col, fallback="median"):
        """같은 그룹의 중앙값으로 결측을 채운다.

        group_col 그룹 안에 값이 하나도 없어 남은 결측은 전체 중앙값(fallback="median")으로
        채운다. fallback=None이면 남겨 둔다.
        """
        self._require_data()
        self.df[target_col] = self.df[target_col].fillna(
            self.df.groupby(group_col)[target_col].transform("median")
        )
        if fallback == "median":
            self.df[target_col] = self.df[target_col].fillna(self.df[target_col].median())
        return self.df

    # ------------------------------------------------------------------ 이상치
    def detect_outliers(self, column, multiplier=1.5):
        """IQR 기준 이상치 행을 모든 컬럼과 함께 돌려준다(원본은 수정하지 않는다)."""
        self._require_data()
        series = self.df[column]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        return self.df.loc[series.notna() & ((series < lower) | (series > upper))]

    def iqr_bounds(self, column, multiplier=1.5):
        """IQR 하한과 상한을 (lower, upper)로 돌려준다."""
        self._require_data()
        series = self.df[column]
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        return q1 - multiplier * iqr, q3 + multiplier * iqr

    # ------------------------------------------------------------------ 텍스트 피처
    def add_text_features(self, products_path, translation_path, key="product_id"):
        """상품 정보에서 텍스트 피처 3개를 self.df에 붙인다.

        Olist에는 상품명 텍스트가 없어 다음으로 대체한다.
        - product_category_name_english: 번역한 카테고리명
        - name_word_count: 카테고리명의 단어 수
        - name_length: 상품명 글자 수(product_name_lenght)
        """
        self._require_data()
        products = pd.read_csv(products_path)
        trans = pd.read_csv(translation_path, encoding="utf-8-sig")
        products = products.merge(trans, on="product_category_name", how="left")
        products["name_word_count"] = (
            products["product_category_name_english"]
            .fillna("").str.replace("_", " ").str.split().str.len()
        )
        by_product = products.set_index(key)
        # map은 여러 번 실행해도 컬럼이 중복되지 않는다.
        self.df["product_category_name_english"] = self.df[key].map(
            by_product["product_category_name_english"]
        )
        self.df["name_word_count"] = self.df[key].map(by_product["name_word_count"])
        self.df["name_length"] = self.df[key].map(by_product["product_name_lenght"])
        return self.df

    # ------------------------------------------------------------------ 이미지 피처
    @staticmethod
    def build_image_features(image_dir, pattern="*.jpg"):
        """폴더의 이미지를 읽어 이미지별 평균 밝기와 표준편차를 DataFrame으로 돌려준다.

        크기가 다른 이미지는 가운데를 잘라 가장 작은 크기로 맞춘 뒤 하나로 쌓고,
        axis=(1, 2, 3)로 이미지마다 한 번에 계산한다. 값 범위도 assert로 확인한다.
        """
        paths = sorted(Path(image_dir).glob(pattern))
        if not paths:
            raise FileNotFoundError(f"이미지 파일이 없습니다: {image_dir}")

        arrays = [mpimg.imread(p) for p in paths]
        arrays = [a[..., :3] if a.ndim == 3 else np.stack([a] * 3, axis=-1) for a in arrays]
        min_h = min(a.shape[0] for a in arrays)
        min_w = min(a.shape[1] for a in arrays)

        def center_crop(a):
            y, x = (a.shape[0] - min_h) // 2, (a.shape[1] - min_w) // 2
            return a[y:y + min_h, x:x + min_w]

        batch = np.stack([center_crop(a) for a in arrays])
        if batch.dtype.kind == "f":          # PNG는 0~1 실수이므로 0~255로 맞춘다
            batch = batch * 255.0

        result = pd.DataFrame({
            "file": [p.name for p in paths],
            "image_mean": batch.mean(axis=(1, 2, 3)),
            "image_std": batch.std(axis=(1, 2, 3)),
        })
        assert result["image_mean"].between(0, 255).all()
        assert result["image_std"].between(0, 127.5).all()
        return result

    # ------------------------------------------------------------------ 통계
    def describe_numeric(self):
        """숫자형 컬럼의 기초 통계량."""
        self._require_data()
        return self.df.select_dtypes(include="number").describe().T

    def correlation(self):
        """숫자형 컬럼의 상관행렬."""
        self._require_data()
        return self.df.select_dtypes(include="number").corr()

    # ------------------------------------------------------------------ RFM
    def calculate_rfm(
        self, customer_col, date_col, amount_col, reference_date=None, order_col=None
    ):
        """고객별 recency, frequency, monetary를 계산한다.

        order_col을 주면 frequency를 고유 주문 수(nunique)로, 주지 않으면 행 수(count)로 센다.
        reference_date가 없으면 마지막 주문일 + 1일을 기준일로 쓴다.
        """
        self._require_data()
        data = self.df.copy()
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        data = data.dropna(subset=[customer_col, date_col, amount_col])

        if reference_date is None:
            reference_date = data[date_col].max() + pd.Timedelta(days=1)
        else:
            reference_date = pd.Timestamp(reference_date)

        freq_col, freq_func = (order_col, "nunique") if order_col else (date_col, "count")
        rfm = data.groupby(customer_col).agg(
            last_order=(date_col, "max"),
            frequency=(freq_col, freq_func),
            monetary=(amount_col, "sum"),
        )
        rfm["recency"] = (reference_date - rfm["last_order"]).dt.days
        return rfm[["recency", "frequency", "monetary"]]

    @staticmethod
    def score_rfm(rfm):
        """RFM 점수(1~4)와 세그먼트를 붙인다.

        R, M은 qcut 4등분(rank로 동점 해소), F는 구매 1회 고객이 대부분이라 구간을 직접 정한다.
        """
        rfm = rfm.copy()
        rfm["R_score"] = pd.qcut(rfm["recency"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
        rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        rfm["F_score"] = np.select(
            [rfm["frequency"] >= 3, rfm["frequency"] == 2], [3, 2], default=1
        )

        def assign_segment(row):
            if row["F_score"] >= 2 and row["M_score"] >= 3:
                return "VIP"
            if row["F_score"] >= 2:
                return "Loyal"
            if row["R_score"] >= 3:
                return "New_or_Recent"
            return "At_Risk_or_Churned"

        rfm["segment"] = rfm.apply(assign_segment, axis=1)
        return rfm

    # ------------------------------------------------------------------ 거래 데이터
    @staticmethod
    def build_transactions(data_dir, items):
        """배송 완료 주문의 거래 표(주문당 1행)를 만든다.

        items(주문 항목 DataFrame)의 price를 주문별로 합산해 orders, customers와 연결한다.
        컬럼: order_id, customer_unique_id, order_date, amount
        """
        data_dir = Path(data_dir)
        orders = pd.read_csv(
            data_dir / "olist_orders_dataset.csv",
            usecols=["order_id", "customer_id", "order_status", "order_purchase_timestamp"],
        )
        customers = pd.read_csv(
            data_dir / "olist_customers_dataset.csv",
            usecols=["customer_id", "customer_unique_id"],
        )
        amount = items.groupby("order_id")["price"].sum().rename("amount")
        tx = (orders.merge(customers, on="customer_id", how="left")
                    .merge(amount, on="order_id", how="inner"))
        tx = tx[tx["order_status"] == "delivered"].copy()
        tx["order_date"] = pd.to_datetime(tx["order_purchase_timestamp"], errors="coerce")
        tx = tx.dropna(subset=["customer_unique_id", "order_date", "amount"])
        return tx[["order_id", "customer_unique_id", "order_date", "amount"]]


def main():
    """직접 실행(▶ 버튼, python src/pipeline.py)하면 모든 기능을 차례로 시험해 결과를 출력한다."""
    import pandas as pd

    pd.set_option("display.max_columns", 30)
    pd.set_option("display.width", 160)

    root = Path(__file__).resolve().parent.parent      # A1-1 폴더 (실행 위치와 무관)
    raw = root / "data" / "raw"

    def title(text):
        print("\n" + "=" * 8, text, "=" * 8)

    a = DataAnalyzer(raw / "olist_order_items_dataset.csv")

    title("1. load_data")
    print("행과 열:", a.load_data().shape)

    title("2. check_quality")
    q = a.check_quality()
    print("shape:", q["shape"], "| 중복 행:", q["duplicates"])
    print(q["missing"])

    title("3. detect_outliers / iqr_bounds (price)")
    lower, upper = a.iqr_bounds("price")
    out = a.detect_outliers("price")
    print(f"하한 {lower:.1f} | 상한 {upper:.1f} | 이상치 {len(out):,}개 ({len(out) / len(a.df) * 100:.2f}%)")
    print(out.nlargest(5, "price")[["order_id", "product_id", "price", "freight_value"]])

    title("4. add_text_features")
    a.add_text_features(raw / "olist_products_dataset.csv", raw / "product_category_name_translation.csv")
    print(a.df[["product_category_name_english", "name_word_count", "name_length"]].describe(include="all").T)
    print("결측:", a.df[["product_category_name_english", "name_word_count", "name_length"]].isna().sum().to_dict())

    title("5. handle_missing_values (seller_id 그룹 중앙값)")
    before = int(a.df["name_length"].isna().sum())
    a.handle_missing_values("seller_id", "name_length")
    print(f"name_length 결측: {before:,} -> {int(a.df['name_length'].isna().sum())}")

    title("6. describe_numeric / correlation")
    print(a.describe_numeric().round(2))
    corr = a.correlation()
    print(corr.round(3))
    print("가격-배송비 상관:", round(corr.loc["price", "freight_value"], 3))

    title("7. build_image_features")
    print(DataAnalyzer.build_image_features(raw / "images").round(2))

    title("8. build_transactions -> calculate_rfm -> score_rfm")
    tx = DataAnalyzer.build_transactions(raw, a.df)
    print("배송 완료 주문:", f"{len(tx):,}", "| 고객:", f"{tx['customer_unique_id'].nunique():,}")
    t = DataAnalyzer(raw / "olist_orders_dataset.csv")
    t.df = tx
    rfm = t.calculate_rfm("customer_unique_id", "order_date", "amount", order_col="order_id")
    print(rfm.head())
    print(rfm.describe().round(1))
    scored = DataAnalyzer.score_rfm(rfm)
    summary = scored.groupby("segment").agg(
        customers=("segment", "size"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    )
    print(summary.round(1))


if __name__ == "__main__":
    main()
