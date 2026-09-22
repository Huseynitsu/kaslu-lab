import joblib

data = {
    "hello": "world"
}

joblib.dump(
    data,
    "test.pkl"
)

loaded = joblib.load(
    "test.pkl"
)

print(loaded)