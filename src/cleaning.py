"""
Data cleaning pipeline for Summer Bridge analysis.

This module:
- Loads raw assessment and enrollment files
- Standardizes student identifiers
- Selects only required fields
- Cleans and renames columns for clarity
- Filters data to relevant subjects/tests
- Calculates counts of students who were recommended vs. enrolled
- Merges all sources into one analysis-ready dataset

Run directly:
    python cleaning.py

Import functions into notebooks for testing:
    from cleaning import clean_growth
"""

from config import DATA_RAW, DATA_PROCESSED
import pandas as pd

def normalize_id(series):
    """Standardize student IDs for safe merging."""
    return series.astype(str).str.strip().str.lstrip("0")

# ---------------------------------------------------------------------
# Cleaning functions
# ---------------------------------------------------------------------

def clean_benchmarks(filename):
    """
    Load and clean a benchmark-style Excel file (BM1 or Pretest).

    Parameters
    ----------
    filename : str
        Excel filename located in DATA_RAW.

    Returns
    -------
    DataFrame
        student_id : str
        subject : str
        bm_score : numeric
    """
    path = DATA_RAW / filename
    df = pd.read_excel(path)
    
    df = df.rename(columns={
        "StudentID": "student_id",
        "ScaledScore": "bm_score",
        "Subject": "subject"
    })

    df = df[["student_id", "subject", "bm_score"]]
    df["student_id"] = normalize_id(df["student_id"])

    return df


def clean_aasa(filename):
    """
    Load and clean AASA state assessment data.

    Filters to math tests only and returns prior-year scale score.

    Returns
    -------
    DataFrame
        state_student_id : str
        ly_math_AASA_score : numeric
    """
    path = DATA_RAW / filename
    df = pd.read_csv(path, delimiter="\t", dtype={"SSID": str})

    df = df[df["Test Code"].str.contains("AZAM", na=False)]

    df = df.rename(columns={
        "SSID": "state_student_id",
        "Total Scale Score": "ly_math_AASA_score"
    })

    df = df[["state_student_id", "ly_math_AASA_score"]]
    df["state_student_id"] = normalize_id(df["state_student_id"])

    return df


def clean_growth(filename):
    """
    Load benchmark growth report and calculate numeric gain score.

    Returns
    -------
    DataFrame
        student_id : str
        BM1_gain_score : numeric
    """
    path = DATA_RAW / filename
    df = pd.read_csv(path, skiprows=3, dtype={"Student ID": str})

    df = df[df["Student ID"].notna()]

    df = df.rename(columns={
        "Student ID": "student_id",
        "Scale Score Difference": "BM1_gain_score"
    })

    df["BM1_gain_score"] = pd.to_numeric(df["BM1_gain_score"], errors="coerce")
    df = df[["student_id", "BM1_gain_score"]]
    df["student_id"] = normalize_id(df["student_id"])

    return df


def clean_enrollment(filename):
    """
    Load and clean district enrollment file.

    Returns
    -------
    DataFrame
        student_id : str
        state_student_id : str
        school_name : str
    """
    path = DATA_RAW / filename
    df = pd.read_csv(path, dtype={"SAISID": str, "PermID": str})

    df = df.rename(columns={
        "PermID": "student_id",
        "SAISID": "state_student_id",
        "School": "school_name"
    })

    drop_cols = [
        'HomeRoom', 'FirstName', 'LastName',
        'Email', 'MiddleName', 'Birth Date', 'Status'
    ]

    df = df.drop(columns=drop_cols, errors="ignore")
    df["state_student_id"] = normalize_id(df["state_student_id"])
    df["student_id"] = normalize_id(df["student_id"])

    return df


def merge_dataframes(participants_file, enrollment, pretest, bm1, aasa, growth):
    """
    Merge all cleaned datasets into one analysis-ready dataframe.

    Parameters
    ----------
    participants_file : str
        CSV listing students and intervention group.

    Returns
    -------
    DataFrame
        Fully merged student-level dataset.
    """
    df = pd.read_csv(DATA_RAW / participants_file, dtype={"student_id": str})
    df["student_id"] = normalize_id(df["student_id"])

    df = df.merge(enrollment, on="student_id", how="left")
    df = df.merge(pretest, on="student_id", how="left")
    df = df.merge(bm1, on="student_id", how="left")
    df = df.merge(aasa, on="state_student_id", how="left")
    df = df.merge(growth, on="student_id", how="left")

    return df


# ---------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------

def main():
    """Execute full cleaning and merging pipeline and save final dataset."""

    bm1 = clean_benchmarks("2025-2026 BM1 Math.xlsx").rename(
        columns={"bm_score": "bm1_score"}
    )

    pretest = clean_benchmarks("2025-2026 Pretest Math.xlsx").rename(
        columns={"bm_score": "pretest_score"}
    )

    aasa = clean_aasa("AZ_AASA_District_0004245_Spring_2025_Student_Data_File.txt")
    growth = clean_growth("GrowthModelReport_134140268800195983.csv")
    enrollment = clean_enrollment("Qualtrics_Daily_Enrollment_2026-01-27T08_01_52-07_00.csv")
    # -------------------------------------------------
    # MERGE EVERYTHING
    # -------------------------------------------------
    final_df = merge_dataframes(
        "participant_list.csv",
        enrollment,
        pretest,
        bm1,
        aasa,
        growth
    )

    # -------------------------------------------------
    # SAMPLE FLOW COUNTS
    # -------------------------------------------------
    total_recommended = len(final_df)

    enrolled_mask = final_df["state_student_id"].notna()
    enrolled_count = enrolled_mask.sum()

    not_returned = total_recommended - enrolled_count

    counts = pd.DataFrame({
        "metric": [
            "Recommended",
            "Enrolled",
            "Did not return"
        ],
        "count": [
            total_recommended,
            enrolled_count,
            not_returned
        ]
    })

    # save counts for report
    counts.to_csv(DATA_PROCESSED / "sample_sizes.csv", index=False)

    # -------------------------------------------------
    # FILTER TO ANALYTIC SAMPLE
    # -------------------------------------------------
    analysis_df = final_df[enrolled_mask].copy()

    analysis_df.to_csv(DATA_PROCESSED / "analysis_file.csv", index=False)


if __name__ == "__main__":
    main()