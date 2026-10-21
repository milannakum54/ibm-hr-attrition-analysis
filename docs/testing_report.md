# Project-wide testing report

Date: 2026-10-21. Scope: both Milan's and Rudra's code, shared runners and output generation.

## Automated result

**310 tests passed; zero failures.** The final pytest run completed in approximately 41 seconds on Windows with Python 3.14.7. It emitted no pytest warnings. This is a count of executed test cases, not a claim of 100% code coverage or exhaustive correctness.

Machine-readable evidence: [test_results.xml](../reports/qa/test_results.xml) and [summary.json](../reports/qa/summary.json).

| Suite | Passed cases |
|---|---:|
| tests.test_analysis | 5 |
| tests.test_edge_cases | 18 |
| tests.test_milan | 11 |
| tests.test_model_safety | 11 |
| tests.test_pipeline | 16 |
| tests.test_properties | 150 |
| tests.test_validation_matrix | 99 |

## Notebooks and final outputs

All five notebooks were executed from fresh kernels using the current project interpreter. Every code cell has an execution count and no error outputs. The corrected notebook verifier completed with exit code 0. The final full analysis (including logistic regression) and the independent Milan analysis completed successfully. The raw source checksum is unchanged. Twelve PNG charts were regenerated.

## Conditions exercised

- Original 1,470-row dataset; single-record and single-class samples; 10,000 rows; random subsets and duplicates.
- Every required column missing in turn; unexpected/duplicate columns; missing values; blank labels; unsupported category/rating codes.
- Negative and infinite values in each numeric source field; fractional ages/counts; out-of-range ages; extremely large numeric input.
- Empty/header-only files; invalid encoding; malformed quoting; unequal row widths; NUL bytes; missing paths; spaces in paths; UTF-8 with/without BOM; reordered columns.
- 50 seeded random grouping cases checked against manual counts, 20 random subsets with duplicates, 30 Holm-adjustment cases checked against an independent step-down calculation and 40 mutated-byte CSV cases: 140 reproducible randomized cases in total.
- Zero and full attrition, unused categories, n=29/n=30 boundaries, group denominators and shuffled row order.
- Hand-calculated chi-square/Cramer's V and pairwise Mann-Whitney effect checks; constant categories; all-equal numeric values; sparse tables; invalid p-values; inconsistent target representations.
- Disjoint training/holdout, training-only scaler statistics, exclusion of target/ID/derived copies, unseen categories, constant predictors, insufficient minority samples and deterministic model results. Confusion counts are reconciled with metrics.
- Full command-line runs from another directory; model and no-model modes; repeated-run byte consistency; 12 valid PNGs; categorical/numeric output ownership; stale model-file cleanup.
- Simulated calculation, plotting and image-save permission failures; previous-output preservation during failed generation; directory/file collisions; prevention of overwriting/deleting the input CSV; figure cleanup after save failure.

## Defects found and fixed

1. Invalid constant numeric values could be dropped before validation. All present source fields are now checked first.
2. Duplicate headers and ragged CSV records could be altered implicitly by the parser. CSV structure is checked explicitly before loading.
3. Constant categories or single-class subsets stopped the statistical stage. Undefined comparisons now have a reason and `not_testable` status, allowing valid descriptive work to continue.
4. An all-equal numeric comparison produced an undefined p-value. It now reports zero pairwise effect and no inferential p-value; adjustment excludes undefined tests.
5. One-class or undersized model inputs raised unclear internal errors. They now fail explicitly before producing metrics.
6. Rate-table output names could collide with a grouping-column name. Reserved names are rejected explicitly.
7. Numeric plotting returned other people's figure paths from the same folder. It now returns exactly its five generated files.
8. Failed runs could leave partially regenerated results, and no-model reruns could leave stale model metrics. Generation is staged before publication, and stale full-run model metrics are removed after a successful no-model run.
9. Model predictors were selected by dropping known derived fields. A fixed source-feature allowlist now also excludes unknown derived copies; non-metadata constant predictors are retained until the training pipeline.
10. Plotting dependencies emitted deprecation warnings. Box plots use the supported Matplotlib interface, and the heatmap avoids the deprecated color-map mutation path.

11. On this Windows runtime, the notebook runner completed its cells but failed during native handle cleanup. It now uses an explicit selector event loop; the full five-notebook verification completed with exit code 0.

## Reproduce

From the repository with its environment selected:

```powershell
python -m pytest -q
python scripts/verify_notebooks.py
python run_analysis.py --model
python run_milan.py
```

Use `--output-dir` for experiments on different datasets. Saved outputs identify the input via SHA-256. The input contract is the documented fictional IBM HR schema, not arbitrary HR CSV data.

## Limits

- Finite tests cannot establish correctness for all unknown inputs. The seeded random cases improve coverage but are not exhaustive fuzzing.
- Validation checks the documented schema and supported numeric bounds; it cannot establish the real-world truth or causal meaning of employee records.
- Executed locally on Windows/Python 3.14. Linux/macOS, other Python versions and a clean installation on another machine were not executed here. The GitHub workflow is prepared but has not run remotely.
- Existing-directory write failures are simulated; actual disk exhaustion, hardware failure and power loss were not induced. Files are replaced individually after successful staging, so final publication is not a whole-directory atomic transaction.
- Concurrent processes writing to the same output directory are not supported/tested; use separate directories. For another dataset, use a new output directory to keep independently generated reports distinct.
- The statistical p-values remain exploratory, and sparse expected-count warnings still require interpretation. One model holdout is not deployment validation.

Reference for the training/holdout checks: [scikit-learn guidance on data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).
