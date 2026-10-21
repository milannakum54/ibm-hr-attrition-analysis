# Milan: data and categorical results

Validated 1470 rows. Original columns: 35; prepared columns: 36.
Overall attrition: 237/1470 = 16.12%.

## Cleaning decisions

- Missing cells: 0; exact duplicates removed: 0.
- Dropped: EmployeeCount, Over18, StandardHours, EmployeeNumber.
- Required fields are retained even if constant in a filtered sample.
- Pay-rate correlations are audited; weak correlation alone is insufficient grounds for deletion.
- Original CSV is unchanged; its SHA-256 is recorded in data_quality.json.

## Group results

Each rate uses employees in that group as the denominator. An asterisk marks n < 30, a descriptive caution threshold.

### OverTime

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| No | 1054 | 110 | 10.44% |
| Yes | 416 | 127 | 30.53% |

### Department

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| Human Resources | 63 | 12 | 19.05% |
| Research & Development | 961 | 133 | 13.84% |
| Sales | 446 | 92 | 20.63% |

### JobRole

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| Healthcare Representative | 131 | 9 | 6.87% |
| Human Resources | 52 | 12 | 23.08% |
| Laboratory Technician | 259 | 62 | 23.94% |
| Manager | 102 | 5 | 4.90% |
| Manufacturing Director | 145 | 10 | 6.90% |
| Research Director | 80 | 2 | 2.50% |
| Research Scientist | 292 | 47 | 16.10% |
| Sales Executive | 326 | 57 | 17.48% |
| Sales Representative | 83 | 33 | 39.76% |

### AgeGroup

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| 18-29 | 326 | 91 | 27.91% |
| 30-39 | 622 | 89 | 14.31% |
| 40-49 | 349 | 34 | 9.74% |
| 50+ | 173 | 23 | 13.29% |

### JobLevel

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| 1 | 543 | 143 | 26.34% |
| 2 | 534 | 52 | 9.74% |
| 3 | 218 | 32 | 14.68% |
| 4 | 106 | 5 | 4.72% |
| 5 | 69 | 5 | 7.25% |

### JobSatisfactionLabel

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| 1 Low | 289 | 66 | 22.84% |
| 2 Medium | 280 | 46 | 16.43% |
| 3 High | 442 | 73 | 16.52% |
| 4 Very high | 459 | 52 | 11.33% |

### EnvironmentSatisfactionLabel

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| 1 Low | 284 | 72 | 25.35% |
| 2 Medium | 287 | 43 | 14.98% |
| 3 High | 453 | 62 | 13.69% |
| 4 Very high | 446 | 60 | 13.45% |

### WorkLifeBalanceLabel

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| 1 Bad | 80 | 25 | 31.25% |
| 2 Good | 344 | 58 | 16.86% |
| 3 Better | 893 | 127 | 14.22% |
| 4 Best | 153 | 27 | 17.65% |

### BusinessTravel

| Group | Employees | Left | Attrition |
|---|---:|---:|---:|
| Non-Travel | 150 | 12 | 8.00% |
| Travel_Frequently | 277 | 69 | 24.91% |
| Travel_Rarely | 1043 | 156 | 14.96% |

## Interpretation

The overtime-minus-no-overtime difference is 20.09 percentage points in this sample.
This describes an association. It does not show that overtime caused employees to leave.

## Limits

The source is fictional. Counts and rates describe this sample only. Small groups can give unstable percentages. These descriptive results do not include statistical tests or model evaluation.
