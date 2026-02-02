"""
Code to process and clean raw data files. 
Standardize the student ID column names across different files.
Includes functions to load files, rename columns, and save processed files.
"""
# %%
from config import DATA_RAW
import pandas as pd
# %%
def clean_benchmarks(filename):
    path = DATA_RAW / filename

    df = pd.read_excel(path)

    # rename important columns
    df = df.rename(columns={
        "StudentID": "student_id",
        "ScaledScore": "bm_score",
        "Subject": "subject"
    })

    # keep only what you need
    df = df[["student_id", "subject", "bm_score"]]
    # standardize types
    df["student_id"] = df["student_id"].astype(str)

    return df
