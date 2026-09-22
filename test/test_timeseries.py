import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

import sqlite3

conn = sqlite3.connect("anammox.db")

cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM experiment_timeseries
""")

print(
    "Rows:",
    cursor.fetchone()[0]
)

conn.close()