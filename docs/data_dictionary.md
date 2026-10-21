# Data dictionary

Source: Kaggle dataset linked in data_source.md. Do not infer undocumented units.

| Raw field | Meaning / handling |
|---|---|
| Age | Age in years |
| Attrition | Yes: left; No: stayed (analysis target) |
| BusinessTravel | Travel category: Non-Travel, Travel_Rarely, Travel_Frequently |
| DailyRate | Dataset daily-rate field; do not assume a documented salary unit |
| Department | Department category |
| DistanceFromHome | Distance field; unit unspecified in source |
| Education | 1 Below College; 2 College; 3 Bachelor; 4 Master; 5 Doctor |
| EducationField | Field of education |
| EmployeeCount | Constant 1; removed |
| EmployeeNumber | Employee identifier; removed after duplicate-ID check |
| EnvironmentSatisfaction | 1 Low; 2 Medium; 3 High; 4 Very High |
| Gender | Recorded gender category |
| HourlyRate | Hourly-rate field; units unspecified |
| JobInvolvement | 1 Low; 2 Medium; 3 High; 4 Very High |
| JobLevel | Ordinal job level |
| JobRole | Job role category |
| JobSatisfaction | 1 Low; 2 Medium; 3 High; 4 Very High |
| MaritalStatus | Recorded marital status |
| MonthlyIncome | Monthly income field; currency unspecified |
| MonthlyRate | Monthly-rate field; not assumed equivalent to MonthlyIncome |
| NumCompaniesWorked | Number of companies worked at |
| Over18 | Constant Y; removed |
| OverTime | Yes/No overtime category |
| PercentSalaryHike | Salary hike percentage |
| PerformanceRating | 1 Low; 2 Good; 3 Excellent; 4 Outstanding (only some levels may occur) |
| RelationshipSatisfaction | 1 Low; 2 Medium; 3 High; 4 Very High |
| StandardHours | Constant 80; removed |
| StockOptionLevel | Ordinal stock-option level |
| TotalWorkingYears | Total years worked |
| TrainingTimesLastYear | Training count last year |
| WorkLifeBalance | 1 Bad; 2 Good; 3 Better; 4 Best |
| YearsAtCompany | Years at company |
| YearsInCurrentRole | Years in current role |
| YearsSinceLastPromotion | Years since last promotion |
| YearsWithCurrManager | Years with current manager |

Derived fields: AttritionFlag (No=0, Yes=1), AgeGroup (18-29, 30-39, 40-49, 50+), and JobSatisfactionLabel, EnvironmentSatisfactionLabel, WorkLifeBalanceLabel. Raw rating codes remain available for analysis.
