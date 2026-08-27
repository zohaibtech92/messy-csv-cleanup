"""
College Scorecard Cleanup - MEGED2017_18_PP.csv
Scope: selective, predominantly-bachelor's-granting (4-year) institutions.
See docs/decisions.md for full reasoning behind each step.
"""

import pandas as pd
import numpy as np

RAW_PATH = 'data/raw/MERGED2017_18_PP.csv'
CLEANED_PATH = 'data/cleaned/scorecard_cleaned.csv'

WIDE_COLUMNS = [
	'UNITID', 'OPEID6', 'INSTNM', 'CITY', 'STABBR', 'ZIP',
	'PREDDEG', 'HIGHDEG', 'CONTROL', 'REGION', 'LOCALE', 'MAIN', 'NUMBRANCH',
	'ADM_RATE', 'SATVR25', 'SATVR75', 'SATMT25', 'SATMT75', 'ACTCM25', 'ACTCM75',
	'NPT4_PUB', 'NPT4_PRIV', 'COSTT4_A', 'TUITIONFEE_IN', 'TUITIONFEE_OUT',
	'UGDS', 'UG', 'PCTFLOAN', 'PCTPELL',
	'C150_4', 'C150_L4', 'RET_FT4', 'RET_PT4',
	'DEBT_MDN', 'GRAD_DEBT_MDN', 'DEFAULT_RATE', 'PPTUG_EF',
	'MD_EARN_WNE_P10', 'MN_EARN_WNE_P10', 'COUNT_WNE_P10',
]

ACT_POINTS = [11, 14, 17, 20, 23, 26, 29, 32, 35, 36]
SAT_POINTS = [670, 800, 930, 1040, 1140, 1240, 1340, 1430, 1540, 1590]

LOW_MISSING_COLS = [
	'GRAD_DEBT_MDN', 'DEBT_MDN', 'PCTPELL', 'PCTFLOAN', 'PPTUG_EF',
    	'UGDS', 'LOCALE', 'C150_4', 'COSTT4_A',
    	'TUITIONFEE_IN', 'TUITIONFEE_OUT', 'RET_FT4', 'net_price',
]


def load_raw(path):
	return pd.read_csv(
		path,
		usecols=lambda c: c in WIDE_COLUMNS,
		na_values=['NULL', 'PrivacySuppressed']
	)

def scope_to_selective_4year(df):
	return df[(df['PREDDEG'] == 3) & (df['ADM_RATE'].notna())].copy()

def combine_sat_act(df):
	df = df.copy()
	df['sat_combined_25'] = df['SATVR25'] + df['SATMT25']
	df['sat_combined_75'] = df['SATVR75'] + df['SATMT75']

	act_converted_25 = pd.Series(np.interp(df['ACTCM25'], ACT_POINTS, SAT_POINTS), index=df.index)
	act_converted_75 = pd.Series(np.interp(df['ACTCM75'], ACT_POINTS, SAT_POINTS), index=df.index)

	df['test_score_source'] = np.where(
		df['sat_combined_25'].notna(), 'SAT',
		np.where(df['ACTCM25'].notna(), 'ACT_coverted', 'missing')
	)

	df['sat_combined_25'] = df['sat_combined_25'].fillna(act_converted_25)
	df['sat_combined_75'] = df['sat_combined_75'].fillna(act_converted_75)

	return df[df['sat_combined_25'].notna()].copy()

def merge_net_price(df):
	df = df.copy()
	df['net_price'] = df['NPT4_PUB'].fillna(df['NPT4_PRIV'])
	return df

def drop_dead_columns(df):
	dead_cols = ['COUNT_WNE_P10', 'MD_EARN_WNE_P10', 'MN_EARN_WNE_P10', 'UG', 'C150_L4']
	return df.drop(columns=[c for c in dead_cols if c in df.columns])

def drop_remaining_low_missing_rows(df):
	cols_present = [c for c in LOW_MISSING_COLS if c in df.columns]
	return df.dropna(subset=cols_present).copy()

def normalize_zip(df):
	df = df.copy()
	df['ZIP'] = df['ZIP'].str[:5]
	return df

def clean():
	df = load_raw(RAW_PATH)
	print(f"Loaded raw: {df.shape}")

	df = scope_to_selective_4year(df)
	print(f"After scoping filter: {df.shape}")

	df = drop_dead_columns(df)
	df = merge_net_price(df)
	df = combine_sat_act(df)
	print(f"After SAT/ACT combine + drop: {df.shape}")

	df = normalize_zip(df)
	df = drop_remaining_low_missing_rows(df)
	print(f"After final low missingness drop: {df.shape}")

	df.to_csv(CLEANED_PATH, index=False)
	print(f"Saved cleaned data to {CLEANED_PATH}")

	return df
if __name__ == '__main__':
	clean()

