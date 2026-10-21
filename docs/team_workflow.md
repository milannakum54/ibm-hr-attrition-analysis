# Two-person project workflow

## Responsibilities

| Package | Milan Nakum | Rudra Patel |
|---|---|---|
| Data | Validation, cleaning, group rates and quality audit | Source interpretation and data dictionary |
| Plots | Distribution, overtime, department/role, age, level, satisfaction, travel | Income, tenure, distance, numeric correlation, role x overtime |
| Analysis | Small-group interpretation and categorical results | Statistical assumptions, effect sizes and adjusted p-values |
| Notebooks | 01 and 02a | 02b, 03 and optional 04 |
| Completion | Shared setup, command-line integration and results documentation | Statistical checks and optional model evaluation |
| Review | Review Rudra's portion | Review Milan's portion |

The source sample is fictional. Both members should understand the methods and avoid interpreting association as causation. Assignments describe responsibility; completed reviews should be recorded separately.

## Commit organization

The initial implementation is grouped into shared setup, Milan's data/categorical package, Rudra's numeric/statistical package, and shared integration/testing. Shared setup and integration use the repository owner's identity.

| Assigned author | Git name | Commit email |
|---|---|---|
| Milan | milannakum54 | milanynakum@gmail.com |
| Rudra | rudrapatel8626 | rdp5125@gmail.com |

Git records author and committer separately. An upload uses the signed-in GitHub account; it does not change each commit's recorded author. See the actual history for the final commits and upload state.

```powershell
git log --format="%h | author: %an <%ae> | committer: %cn <%ce> | %s"
git status --short
```

## Running each portion

Create the environment as described in README.md. Milan can run the data/categorical package independently:

```powershell
python run_milan.py
python -m pytest tests/test_milan.py tests/test_validation_matrix.py -q
```

Rudra can check the statistical/model package and execute his notebooks:

```powershell
python -m pytest tests/test_analysis.py tests/test_model_safety.py -q
python scripts/verify_notebooks.py --notebook 02b_numeric_visualization.ipynb
python scripts/verify_notebooks.py --notebook 03_statistical_checks.ipynb
python scripts/verify_notebooks.py --notebook 04_optional_ml_model.ipynb
```

For the combined project:

```powershell
python -m pytest -q
python scripts/verify_notebooks.py
python run_analysis.py --model
python run_milan.py
```

## Future changes and reviews

Each member should use a separate local clone and configure their own repository-local name and verified email. Start a new branch from the updated main branch, stage the files actually changed, inspect the diff, commit and open a pull request for the other member to review. Keep original commits when merging if individual history is required for submission.

Shared interfaces: prepare(path) returns the prepared DataFrame and audit; group_rates(df, column) returns counts, leavers and percentages; AttritionFlag is binary. Preserve the raw input and keep the model optional. Avoid editing the same notebook at the same time.

## Review log

Add entries after the review or improvement actually occurs. Include the relevant commit or PR, what was checked and the result.

| Person | Completed task or review | Commit or PR | Verification | Date |
|---|---|---|---|---|

For presentation, use [faculty_demo.md](faculty_demo.md) and [testing_report.md](testing_report.md). Explain each person's actual contribution and reasoning rather than relying only on commit counts.
