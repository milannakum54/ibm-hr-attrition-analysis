# Milan's walkthrough and commit plan

## 1. Understand the files

| File | What it does | What to explain |
|---|---|---|
| data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv | Original input, preserved | One row per fictional employee |
| src/data.py | Validate, clean, derive columns and calculate group rates | Each cleaning decision and the denominator |
| src/categorical.py | Your seven figure files | Percentages, group sizes and small-group flags |
| run_milan.py | Execute your portion independently | How input becomes outputs |
| notebooks/01_data_validation_cleaning.ipynb | Walk through validation and cleaning | Why there is no automatic imputation |
| notebooks/02a_categorical_visualization.ipynb | Walk through group rates and charts | Counts versus percentages |
| tests/test_milan.py | Regression cases for your changes | How you know the calculation is correct |
| reports/milan_results.md | Recomputed results from your portion | Findings and limitations |

Rudra's numeric plots remain in src/plots.py, tests in src/statistics.py, model in src/model.py and notebooks 02b/03/04. The old categorical imports from src/plots.py remain compatible with the combined runner.

## 2. Run from PowerShell

Open a terminal in the repository folder. For a fresh clone, set up its environment once:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then run your portion and its tests:

```powershell
.venv\Scripts\python.exe run_milan.py
.venv\Scripts\python.exe -m pytest tests/test_milan.py -q
```

To view notebooks, run `.venv\Scripts\python.exe -m notebook` and open 01, then 02a. Restart the kernel and run all cells from the top.

## 3. Explain cleaning step by step

1. `pd.read_csv` loads the CSV into a DataFrame: columns represent variables; rows represent employees.
2. Validate required columns and reject missing values, invalid categories, invalid ratings and impossible values under the documented schema. Stop with an explanation so a human can choose a correction policy.
3. `drop_duplicates` removes identical rows. A repeated employee ID with different information is a conflict and is rejected.
4. Remove the identifier and the three fixed metadata constants (EmployeeCount, StandardHours and Over18). Keep required constant fields: a filtered department subset still needs its Department column for grouping.
5. `map` converts No/Yes to 0/1. A binary mean equals the fraction of employees who left.
6. `pd.cut` assigns whole-year ages to 18-29, 30-39, 40-49 and 50+; boundary tests verify the edges.
7. Map satisfaction codes to readable labels while retaining their numerical values.
8. Export a separate cleaned file and audit. The original CSV stays unchanged, verified by its checksum.

The supplied dataset has no missing values or exact duplicates. State that honestly: checking for an issue does not mean the issue existed. Required single-valued fields are now retained; other constant predictors are retained; the three fixed metadata constants are dropped and listed in the audit. A single-class subset supports descriptive rates, although some of Rudra's inferential tests need both classes.

## 4. Explain the categorical calculation

`groupby(column)` separates employees into groups. `size` counts employees, and `sum` adds the 0/1 attrition flags to count leavers.

**Group attrition percentage = group leavers / group employees x 100.**

- Overtime: 127 / 416 x 100 = 30.53%.
- No overtime: 110 / 1,054 x 100 = 10.44%.
- Difference: 20.09 percentage points, not 20.09 percent relative growth.

The charts display percentages and sample sizes. The n<30 flag is a chosen descriptive caution rule; it does not make every larger group statistically reliable. Missing group labels and nonbinary target flags are rejected rather than silently changing the denominator.

## 5. Present three findings

Open reports/milan_results.md and verify these against the current run:

- Overall: 237 of 1,470 employees left (16.12%).
- The overtime group has a higher attrition percentage in this sample: 30.53% versus 10.44%.
- Ages 18-29 have a 27.91% rate; ages 40-49 have a 9.74% rate. Describe the pattern and group counts, without claiming an age effect causes attrition.

These fictional data show associations only. They do not establish what happens among real IBM employees.

## 6. Improvements prepared in this session

- Fixed required fields being removed when constant in a filtered sample.
- Added checks for blank categories, age-bin compatibility, valid job levels and rate-table inputs.
- Separated your categorical functions and kept existing imports working.
- Fixed categorical_plots returning unrelated numeric figure paths from the same folder.
- Added run_milan.py and a dedicated computed report.
- Added meaningful regression tests and expanded your two explanatory notebooks.

Review these changes and explain how the regression checks protect the calculations.

## 7. Git identity and assigned files

Milan's GitHub username and configured Git name are `milannakum54`; his supplied commit email is `milanynakum@gmail.com`. Rudra's assigned files use his separate author identity. Shared setup and integration are recorded under Milan's account.

Milan's core files are `src/data.py`, `src/categorical.py`, `run_milan.py`, notebooks 01/02a, the input-validation tests and categorical results. Figures 01/02/03/04/06/07/10 are the categorical outputs. The raw dataset, common utilities and final combined runner support both portions.

Before future commits, inspect the identity, changed paths and staged diff:

```powershell
git var GIT_AUTHOR_IDENT
git status --short
git diff --cached --stat
```

Use `git log` for the actual commit history. See [team_workflow.md](team_workflow.md) for the responsibility split and review log.

## Project-wide verification

Both portions received input-validation, statistical, model and output-generation checks. See [testing_report.md](testing_report.md) for measured results and remaining limits. The raw source data remains unchanged.
