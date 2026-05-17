import xgboost as xgb
import numpy as np
import joblib


X = np.random.rand(1000, 20)
y = np.random.randint(0, 2, 1000)

group = [100] * 10


model = xgb.XGBRanker(
    objective="rank:pairwise",
    learning_rate=0.05,
    max_depth=6,
    n_estimators=200
)

model.fit(X, y, group=group)

joblib.dump(model, "ranker.pkl")