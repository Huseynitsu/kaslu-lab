import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

from core.dataset_builder import build_dataset

df = build_dataset(5)

print(df.head())
print()
print("Shape:", df.shape)