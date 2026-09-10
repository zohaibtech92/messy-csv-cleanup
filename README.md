# Messy CSV Cleanup: College Scorecard

Cleaning and documenting a real, messy public dataset — U.S. Department of
Education College Scorecard — with every cleaning decision explained and
justified, not just applied.

## What this is

The College Scorecard dataset tracks admissions, cost, and outcome data for
every U.S. postsecondary institution. The raw file used here
(`MERGED2017_18_PP.csv`) has **1,977 columns** and a mix of missing-data
patterns, inconsistent formatting, and mutually-exclusive fields — genuinely
messy, real-world government data, not a synthetic "dirty data" toy set.

This project scopes, cleans, and documents a working subset of that data:
**selective, predominantly bachelor's-granting (4-year) institutions.**

Full reasoning for every decision — why columns were dropped, why some
missing data was combined instead of dropped, why some rows were removed
entirely — is documented in [`docs/decisions.md`](docs/decisions.md).

## Results

| Stage | Rows | Columns |
|---|---|---|
| Raw (loaded subset) | 7,112 | 39 |
| After scoping to selective 4-year schools | 1,671 | 39 |
| After SAT/ACT combine + drop | 1,287 | 38 |
| After final low-missingness drop | 1,253 | 38 |

**Final output:** [`data/cleaned/scorecard_cleaned.csv`](data/cleaned/scorecard_cleaned.csv)

## Key cleaning decisions (see `docs/decisions.md` for full detail)

- **Scoped** the dataset to predominantly bachelor's-granting institutions
  that report an admission rate, since admissions-related missingness in the
  raw file was structural (open-admission schools don't have this data),
  not random.
- **Combined SAT and ACT scores** into one comparable metric using the
  official 2018 ACT-to-SAT concordance table, recovering 78 rows that would
  otherwise have been dropped — with every converted value traceable via a
  `test_score_source` column.
- **Merged** `NPT4_PUB` and `NPT4_PRIV` into a single `net_price` column
  after verifying they are mutually exclusive by institution type (public vs.
  private), rather than treating them as two separately "missing" columns.
- **Normalized ZIP codes** to a consistent 5-digit format (raw data mixed
  5-digit and ZIP+4 formats).
- **Verified zero duplicate rows** and zero duplicate institution IDs —
  checked explicitly, not assumed.
- Remaining low-missingness columns (under 6%) were handled by **dropping
  rows**, not imputing, to avoid introducing fabricated values into the
  dataset.


## Running this yourself

1. Clone the repo and set up the environment:
```bash
   git clone https://github.com/zohaibtech92/messy-csv-cleanup.git
   cd messy-csv-cleanup
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

2. Download `MERGED2017_18_PP.csv` from the
   [College Scorecard dataset on Kaggle](https://www.kaggle.com/datasets)
   and place it in `data/raw/`. (Not included in this repo — see
   `.gitignore` — since it's large and publicly redistributable from the
   source.)

3. Run the cleaning pipeline:
```bash
   python scripts/clean_data.py
```

   This prints row/column counts at each stage and writes the cleaned file
   to `data/cleaned/scorecard_cleaned.csv`.

## Why this dataset

Chosen specifically for genuine, non-synthetic messiness: a missing-value
placeholder (`PrivacySuppressed`) that silently corrupts column types if not
handled at load time, two structurally complementary columns that look like
one badly-missing column, and admissions data that's missing for real
domain-specific reasons rather than at random — the kind of judgment calls
that come up in real data engineering and data science work.

## Tech stack

- Python 3
- pandas
- NumPy