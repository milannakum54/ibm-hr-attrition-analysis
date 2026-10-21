# Computed results

Input: 1470 rows, 35 columns.
Attrition: 237/1470 (16.12%).

## Group comparisons

### OverTime
- No: 10.44% (110/1054)
- Yes: 30.53% (127/416)

### Department
- Human Resources: 19.05% (12/63)
- Research & Development: 13.84% (133/961)
- Sales: 20.63% (92/446)

### JobRole
- Healthcare Representative: 6.87% (9/131)
- Human Resources: 23.08% (12/52)
- Laboratory Technician: 23.94% (62/259)
- Manager: 4.90% (5/102)
- Manufacturing Director: 6.90% (10/145)
- Research Director: 2.50% (2/80)
- Research Scientist: 16.10% (47/292)
- Sales Executive: 17.48% (57/326)
- Sales Representative: 39.76% (33/83)

### AgeGroup
- 18-29: 27.91% (91/326)
- 30-39: 14.31% (89/622)
- 40-49: 9.74% (34/349)
- 50+: 13.29% (23/173)

### JobLevel
- 1: 26.34% (143/543)
- 2: 9.74% (52/534)
- 3: 14.68% (32/218)
- 4: 4.72% (5/106)
- 5: 7.25% (5/69)

### BusinessTravel
- Non-Travel: 8.00% (12/150)
- Travel_Frequently: 24.91% (69/277)
- Travel_Rarely: 14.96% (156/1043)

## Statistical checks

Full test statistics, effect sizes, raw p-values, Holm-adjusted p-values, status and assumptions are in statistical_tests.csv.
Testable comparisons: 12/12. Undefined comparisons are marked not_testable; Holm adjustment covers only testable comparisons.
Exploratory tests describe associations. Statistical significance does not measure practical importance.

## Actual outcomes for the 12 proposal figures

| Figure | Computed outcome |
|---|---|
| 01 Distribution | 237/1470 left (16.12%); target is imbalanced. |
| 02 OverTime | Highest: Yes 30.53% (n=416); lowest: No 10.44% (n=1054). |
| 03 JobRole | Highest: Sales Representative 39.76% (n=83); lowest: Research Director 2.50% (n=80). |
| 04 AgeGroup | Highest: 18-29 27.91% (n=326); lowest: 40-49 9.74% (n=349). |
| 06 JobLevel | Highest: 1 26.34% (n=543); lowest: 4 4.72% (n=106). |
| 07 JobSatisfactionLabel | Highest: 1 Low 22.84% (n=289); lowest: 4 Very high 11.33% (n=459). |
| 10 BusinessTravel | Highest: Travel_Frequently 24.91% (n=277); lowest: Non-Travel 8.00% (n=150). |
| 05 MonthlyIncome | Median among leavers: 3202; among stayers: 5204. |
| 08 YearsAtCompany | Median among leavers: 3; among stayers: 6. |
| 11 DistanceFromHome | Median among leavers: 9; among stayers: 7. |
| 09 Correlation | Income/job level Spearman correlation: 0.920; association, not causation. |
| 12 Role x overtime | 4 cells have n<30; interpret role-specific overtime differences cautiously. |

Figure 03 also shows departments; Figure 07 also shows environment satisfaction and work-life balance. Complete rates and denominators for each dimension are in the exported rate tables.

## Optional held-out model

- majority_baseline: precision=0.000, recall=0.000, F1=0.000, ROC-AUC=0.500
- logistic_regression: precision=0.349, recall=0.638, F1=0.451, ROC-AUC=0.803

## Limitations

Fictional sample; no inference about actual IBM employees. Single snapshot, imbalanced target and small subgroups. Associations do not establish causes. Optional model metrics use one fixed holdout; they are not deployment validation.
Charts and tables are computed from the input file. Review them before writing HR interpretations.
