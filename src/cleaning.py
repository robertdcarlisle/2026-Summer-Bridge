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

#Growth Score Data preparation.
def clean_growth(filename):
    
    path = DATA_RAW / filename
    df = pd.read_csv(path, skiprows=3)
    df = df[df['Student ID'].notna()]

    # split Growth Quadrant into Proficiency and Growth
    split_names = df['Growth Quadrant'].str.split(',', expand=True)
    df['Proficiency'] = split_names[0]
    df['Growth'] = split_names[1]

    # rename important columns
    df = df.rename(columns={
        "Student ID": "student_id",
        "Scale Score Difference": "BM1_gain_score"
    })
    #Adjust gain score to numeric
    df["BM1_gain_score"] = pd.to_numeric(
        df["BM1_gain_score"],
        errors="coerce"
    )
    # keep only what you need
    df = df[["student_id", "BM1_gain_score"]]
    # standardize types
    df["student_id"] = df["student_id"].astype(str)
    return df

# %%   
growth = clean_growth("GrowthModelReport_134140268800195983.csv") 

#Enrollment file data preparation.
# %%
def clean_enrollment(filename):
    
    path = DATA_RAW / filename
    df = pd.read_csv(path)

    # rename important columns
    df = df.rename(columns={
        "PermID": "student_id",
        "SAISID": "state_student_id",
        "School": "school_name"
    })

     # keep only what you need
    df = df.drop(columns=['HomeRoom', 'FirstName', 'LastName', 'Email', 'MiddleName', 'Birth Date', 'Status'])

    # standardize types
    df["student_id"] = df["student_id"].astype(str)
    df["state_student_id"] = df["state_student_id"].astype(str)
    return df

# %%   
enrollment = clean_enrollment("Qualtrics_Daily_Enrollment_2026-01-27T08_01_52-07_00.csv") 

