import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


DATA_PATH = "data/loan_data.csv"
MODEL_PATH = "models/loan_model.pkl"

df = pd.read_csv(DATA_PATH)

df.columns = [
    column.strip()
    for column in df.columns
]


for column in [
    "education",
    "self_employed",
    "loan_status",
]:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


features = [
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

X = df[features]

y = df["loan_status"].map(
    {
        "Approved": 1,
        "Rejected": 0,
    }
)


categorical_features = [
    "education",
    "self_employed",
]

numeric_features = [
    column
    for column in features
    if column not in categorical_features
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
        (
            "numeric",
            StandardScaler(),
            numeric_features,
        ),
    ]
)


pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
            ),
        ),
    ]
)

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
)



pipeline.fit(
    X_train,
    y_train,
)


predictions = pipeline.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions,
)

print(
    "Test accuracy:",
    round(accuracy * 100, 2),
    "%",
)

print(
    classification_report(
        y_test,
        predictions,
    )
)


joblib.dump(
    pipeline,
    MODEL_PATH,
)

print(
    "Saved model:",
    MODEL_PATH,
)
