import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.insert(0, PROJECT_ROOT)

from core.database import get_experiment_timeseries

df = get_experiment_timeseries(6)

print(df.head())

print()

print("Rows:", len(df))