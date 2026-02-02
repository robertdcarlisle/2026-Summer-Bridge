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

bm1 = clean_benchmarks("2025-2026 BM1 Math.xlsx")
bm1 = bm1.rename(columns={"bm_score": "bm1_score"})

#Pretest Data preparation. 
# I can reuse the same function as bm1 since the structure is the same.
pretest = clean_benchmarks("2025-2026 Pretest Math.xlsx")
pretest = pretest.rename(columns={"bm_score": "pretest_score"})

#AASA Data preparation.
def clean_AASA(filename):
    
    path = DATA_RAW / filename
    df = pd.read_csv(path, delimiter="\t")

    # filter to only Math tests
    df = df[df['Test Code'].str.contains('AZAM', na=False)]

    # rename important columns
    df = df.rename(columns={
        "SSID": "state_student_id",
        "Total Scale Score": "ly_math_AASA_score"
    })

     # keep only what you need
    df = df[["state_student_id", "ly_math_AASA_score"]]

    # standardize types
    df["state_student_id"] = df["state_student_id"].astype(str)
    return df
  
aasa = clean_AASA("AZ_AASA_District_0004245_Spring_2025_Student_Data_File.txt") 
