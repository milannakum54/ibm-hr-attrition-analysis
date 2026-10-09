# Understanding Employee Attrition: An Exploratory HR Analytics Study of the IBM HR Dataset



B.Tech Computer Science (C.S.E - G) | Programming for Scientific Computing

Submitted to: Vatsal Shingala



## Team



| Name | Enrollment No. | Role |

|---|---|---|

| Milan Nakum | IU2441230688 | Repository setup, data validation and cleaning, categorical visualizations, README |

| Rudra Patel | IU2441230682 | Data dictionary, numeric visualizations, statistical checks, optional ML notebook |



## Project Summary



This project explores which employee characteristics are associated with

attrition (employees leaving an organization) using the IBM HR Analytics

Employee Attrition & Performance dataset. It uses Python for data cleaning,

exploratory analysis, visualization, and basic statistical checks. An optional

logistic regression baseline model may be added if time permits.



The project reports **associations, not causes**. The dataset is fictional, so

findings describe this dataset only and not real IBM employees.



## Dataset



- **Name:** IBM HR Analytics Employee Attrition & Performance

- **Source:** Kaggle (`pavansubhasht/ibm-hr-analytics-attrition-dataset`),

&#x20; originally IBM Watson Analytics sample data

- **Nature:** Fictional/synthetic data created by IBM data scientists

- **Size:** 1,470 rows and 35 columns in the standard version

&#x20; (confirmed on our file: _update after running `df.shape`_)

- **Target variable:** `Attrition` (Yes/No)

- **How to get it:** Download the CSV from Kaggle and place it in `data/raw/`.

&#x20; Check the dataset license on the Kaggle page before reusing it.



See `docs/data_dictionary.md` for column descriptions.



## Objectives



1. Validate and clean the dataset and document data quality.

2. Measure the overall attrition rate and class imbalance.

3. Compare attrition across job roles, departments, job levels, and age groups.

4. Examine how overtime, income, tenure, and satisfaction relate to attrition.

5. Identify correlations among numeric HR variables.

6. Summarize findings as practical, cautious HR insights.

7. (Optional) Build and evaluate a baseline classification model.



## Repository Structure



```

ibm-hr-attrition-analysis/

|-- README.md

|-- requirements.txt

|-- .gitignore

|-- data/

|   |-- raw/             original dataset

|   `-- processed/       cleaned dataset

|-- docs/

|   |-- data_dictionary.md

|   `-- proposal.pdf

|-- notebooks/

|   |-- 01_data_validation_cleaning.ipynb

|   |-- 02_eda_visualization.ipynb

|   |-- 03_statistical_checks.ipynb

|   `-- 04_optional_ml_model.ipynb

|-- src/                 helper functions

`-- visualizations/      exported plots (PNG)

```



## How to Run



```bash

git clone https://github.com/MILAN-USERNAME/ibm-hr-attrition-analysis.git

cd ibm-hr-attrition-analysis

pip install -r requirements.txt

jupyter notebook

```



Place the dataset CSV in `data/raw/`, then run the notebooks in order (01 to 04).



## Tools and Libraries



Python, Pandas, NumPy, Matplotlib, Seaborn, SciPy, scikit-learn (optional),

Jupyter Notebook / Google Colab, Git and GitHub.



## Methods



- Data validation and cleaning (missing values, duplicates, constant and ID columns)

- Descriptive statistics and attrition-rate tables by group

- Visualization (bar charts, box plots, correlation heatmap)

- Chi-square and Mann-Whitney U tests with effect sizes

- Optional: logistic regression with stratified split and class weighting



## Key Findings



_To be added after the analysis is completed. No results are claimed yet._



## Limitations



- The data is fictional/synthetic, so patterns reflect how it was built.

- It is a single snapshot with no documented date or sampling method.

- Attrition is imbalanced and some groups are small.

- Results show association, not causation.



## References



1. Kaggle. IBM HR Analytics Employee Attrition & Performance (pavansubhasht).

&#x20;  https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

2. IBM Watson Analytics Lab, as cited in the R `modeldata` package documentation.

&#x20;  https://modeldata.tidymodels.org/reference/attrition.html

