# Data Cleaning Decisions — College Scorecard (MERGED2017_18_PP.csv)

## Source
U.S. Department of Education College Scorecard, 2017-18 academic year snapshot.
Raw file: `data/raw/MERGED2017_18_PP.csv` (7,112 rows, 1,977 columns in the full file).

## Scope decision: why this became a "selective 4-year schools" dataset

The raw file covers every U.S. postsecondary institution — community colleges,
trade schools, open-admission colleges, and selective universities alike. Key
admissions columns (`ADM_RATE`, SAT, ACT) were missing in 70-83% of rows, but
this was not random: open-admission and non-4-year institutions structurally
do not have an admission rate or require standardized testing, so nothing was
ever going to be there to recover.

**Decision:** filtered to `PREDDEG == 3` (predominantly bachelor's-granting)
AND `ADM_RATE` present, narrowing the dataset from 7,112 to 1,671 rows. This
reframes the project as "selective four-year institutions," not "all US
higher ed" — a deliberate scoping choice, not a data loss.

## Dropped columns (structurally empty, not just missing)

| Column | Reason |
|---|---|
| `COUNT_WNE_P10`, `MN_EARN_WNE_P10`, `MD_EARN_WNE_P10` | 100% missing in this file/year — not populated at source |
| `UG` | 100% missing in this file/year |
| `C150_L4` | Completion rate for *less-than-4-year* programs — structurally inapplicable once scoped to 4-year schools |

## SAT/ACT: combined via concordance, not dropped outright

Even after scoping to selective 4-year schools, SAT columns were still ~28%
missing. Checked whether ACT scores filled that gap: of 462 rows missing SAT,
only 78 (17%) had an ACT score — a modest but real recovery opportunity.

**Decision:** built a combined SAT score (`SATVR + SATMT`), then used the
official 2018 ACT-to-SAT concordance table (linear interpolation via
`np.interp`) to convert ACT composite scores into SAT-equivalent scores for
rows missing SAT but reporting ACT. Added a `test_score_source` column
(`SAT` / `ACT_converted` / `missing`) so every downstream row is traceable
back to its real origin — no value was fabricated, only converted using a
published, standard equivalence table.

Rows still missing both scores after this (384 rows, 23% of the filtered set)
were **dropped**, not imputed — there is no reasonable way to invent a test
score that doesn't exist, and imputing one risks misrepresenting a school's
actual selectivity.

Result: 1,671 → 1,287 rows.

## Net price: merged two mutually-exclusive columns

`NPT4_PUB` (net price, public schools) and `NPT4_PRIV` (net price, private
schools) are never populated on the same row — verified via
`groupby('CONTROL')`, which confirmed a 100% clean split with zero overlap.
Treating these as two "highly missing" columns was misleading; the underlying
data was never actually missing, just reported in two separate fields by
institution type.

**Decision:** merged into a single `net_price` column via
`NPT4_PUB.fillna(NPT4_PRIV)`. Only 11 rows (under 1%) had neither value and
were left for the final low-missingness drop below.

## Remaining low-missingness columns: dropped rows, did not impute

After the above steps, all remaining columns (`GRAD_DEBT_MDN`, `DEBT_MDN`,
`PCTPELL`, `PCTFLOAN`, `C150_4`, `COSTT4_A`, tuition fields, `RET_FT4`,
`net_price`) had under 6% missingness, with no structural explanation behind
the gaps (unlike SAT/ACT or net price above).

**Decision:** dropped rows with any remaining missing value across these
columns, rather than imputing. At this level of sparsity (34 rows, 2.6% of
the dataset), the cost of dropping is low, and it avoids introducing
artificial values into a small, already-scoped dataset where each row
represents a real institution.

Result: 1,287 → 1,253 rows.

## Formatting: ZIP code inconsistency

Checked `INSTNM`, `CITY`, `STABBR` for whitespace and casing inconsistencies —
found none; this is official government-published data and was already
well-formatted on the text side.

`ZIP` was inconsistent: 785 rows used ZIP+4 format (`35294-0110`), 468 used
plain 5-digit (`35762`) — two formats for the same information.

**Decision:** normalized every value to the first 5 characters, since every
row has at least a 5-digit ZIP but not every row has the +4 extension. This
was chosen over dropping the +4 detail selectively, to keep the column in one
consistent, comparable format.

## Duplicates

Checked for fully duplicate rows and duplicate `UNITID` (the dataset's unique
institution identifier). Found **zero** in both cases — explicitly verified,
not assumed.

## Final result

| Stage | Rows | Columns |
|---|---|---|
| Raw (loaded subset) | 7,112 | 39 |
| After scope filter | 1,671 | 39 |
| After SAT/ACT combine + drop | 1,287 | 38 |
| After final low-missingness drop | 1,253 | 38 |

Output: `data/cleaned/scorecard_cleaned.csv`