"""Run from the repository root: python run_analysis.py [--model]."""
import argparse
import json
import pandas as pd
from pathlib import Path
from src.data import RAW_NAME, GROUPS, prepare, group_rates
from src.plots import categorical_plots, numeric_plots
from src.statistics import statistical_checks
from src.outputs import staged_outputs

ROOT = Path(__file__).resolve().parent

def run(data_path, output_root, include_model=False):
    old_model = Path(output_root)/'reports'/'model_metrics.csv'
    if not include_model:
        if old_model.resolve() == Path(data_path).resolve():
            raise ValueError('Output cleanup would overwrite the input CSV; choose another --output-dir.')
        if old_model.exists() and not old_model.is_file():
            raise ValueError('Expected model_metrics.csv to be a file, not a directory.')
    with staged_outputs(output_root, data_path) as stage:
        quality = _generate(data_path, stage, include_model)
    if not include_model:
        old_model.unlink(missing_ok=True)
    return quality


def _generate(data_path, output_root, include_model):
    df, quality = prepare(data_path)
    tests = statistical_checks(df)
    metrics = None
    if include_model:
        from src.model import evaluate_models
        metrics = evaluate_models(df)
    reports = output_root/'reports'; reports.mkdir(exist_ok=True)
    processed = output_root/'data'/'processed'; processed.mkdir(parents=True,exist_ok=True)
    df.to_csv(processed/'cleaned_hr.csv', index=False)
    (reports/'data_quality.json').write_text(json.dumps(quality, indent=2, allow_nan=False), encoding='utf-8')
    df.describe().to_csv(reports/'descriptive_statistics.csv')
    for col in GROUPS:
        group_rates(df,col).to_csv(reports/f'rates_{col}.csv',index=False)
    # Review outliers without deleting legitimate extreme observations.
    outliers = []
    for col in ['Age', 'MonthlyIncome', 'YearsAtCompany', 'DistanceFromHome']:
        q1, q3 = df[col].quantile([.25, .75])
        iqr = q3-q1
        outliers.append({'feature':col, 'q1':q1, 'q3':q3,
                         'iqr_flag_count':int(((df[col]<q1-1.5*iqr)|(df[col]>q3+1.5*iqr)).sum()),
                         'decision':'Retained; statistical extremes are not automatically errors'})
    pd.DataFrame(outliers).to_csv(reports/'outlier_review.csv',index=False)
    figures = categorical_plots(df, output_root/'visualizations') + numeric_plots(df, output_root/'visualizations')
    tests.to_csv(reports/'statistical_tests.csv', index=False)
    text = ['# Computed results', '', f'Input: {quality["raw_rows"]} rows, {quality["raw_columns"]} columns.',
            f'Attrition: {int(df.AttritionFlag.sum())}/{len(df)} ({df.AttritionFlag.mean():.2%}).', '',
            '## Group comparisons', '']
    for col in ['OverTime','Department','JobRole','AgeGroup','JobLevel','BusinessTravel']:
        table = group_rates(df,col)
        text.append(f'### {col}')
        text.extend(f'- {row[0]}: {row.rate_pct:.2f}% ({row.left}/{row.n})' + ('; small group' if row.small_group else '') for row in table.itertuples(index=False))
        text.append('')
    text += ['## Statistical checks', '',
             'Full test statistics, effect sizes, raw p-values, Holm-adjusted p-values, status and assumptions are in statistical_tests.csv.',
             f'Testable comparisons: {int((tests.status=="ok").sum())}/12. Undefined comparisons are marked not_testable; Holm adjustment covers only testable comparisons.',
             'Exploratory tests describe associations. Statistical significance does not measure practical importance.', '']
    text += ['## Actual outcomes for the 12 proposal figures', '',
             '| Figure | Computed outcome |', '|---|---|',
             f'| 01 Distribution | {int(df.AttritionFlag.sum())}/{len(df)} left ({df.AttritionFlag.mean():.2%}); target is imbalanced. |']
    for number, col in [('02','OverTime'),('03','JobRole'),('04','AgeGroup'),('06','JobLevel'),
                        ('07','JobSatisfactionLabel'),('10','BusinessTravel')]:
        table = group_rates(df,col)
        hi = table.loc[table.rate_pct.idxmax()]
        lo = table.loc[table.rate_pct.idxmin()]
        text.append(f'| {number} {col} | Highest: {hi.iloc[0]} {hi.rate_pct:.2f}% (n={hi.n}); lowest: {lo.iloc[0]} {lo.rate_pct:.2f}% (n={lo.n}). |')
    for number, col in [('05','MonthlyIncome'),('08','YearsAtCompany'),('11','DistanceFromHome')]:
        medians = df.groupby('Attrition')[col].median()
        left = f'{medians["Yes"]:g}' if 'Yes' in medians else 'unavailable (no leavers)'
        stayed = f'{medians["No"]:g}' if 'No' in medians else 'unavailable (no stayers)'
        text.append(f'| {number} {col} | Median among leavers: {left}; among stayers: {stayed}. |')
    corr = df[['Age','TotalWorkingYears','YearsAtCompany','MonthlyIncome','JobLevel']].corr(method='spearman')
    value = corr.loc['MonthlyIncome','JobLevel']
    correlation_label = f'{value:.3f}' if pd.notna(value) else 'unavailable (constant or insufficient data)'
    text.append(f'| 09 Correlation | Income/job level Spearman correlation: {correlation_label}; association, not causation. |')
    cell_rates = df.groupby(['JobRole','OverTime']).AttritionFlag.agg(['mean','size'])
    text.append(f'| 12 Role x overtime | {int((cell_rates["size"]<30).sum())} cells have n<30; interpret role-specific overtime differences cautiously. |')
    text += ['', 'Figure 03 also shows departments; Figure 07 also shows environment satisfaction and work-life balance. Complete rates and denominators for each dimension are in the exported rate tables.', '']
    if metrics is not None:
        metrics.to_csv(reports/'model_metrics.csv',index=False)
        text += ['## Optional held-out model', '']
        text.extend(f'- {r.model}: precision={r.precision:.3f}, recall={r.recall:.3f}, F1={r.f1:.3f}, ROC-AUC={r.roc_auc:.3f}' for r in metrics.itertuples())
    text += ['', '## Limitations', '',
             'Fictional sample; no inference about actual IBM employees. Single snapshot, imbalanced target and small subgroups. Associations do not establish causes. Optional model metrics use one fixed holdout; they are not deployment validation.',
             'Charts and tables are computed from the input file. Review them before writing HR interpretations.']
    (reports/'results.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    manifest = {'input_sha256':quality['sha256'], 'rows':len(df), 'model_included':include_model,
                'testable_comparisons':int((tests.status=='ok').sum()),
                'figures':[p.name for p in figures]}
    (reports/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return quality


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', action='store_true', help='Also evaluate optional logistic regression')
    parser.add_argument('--data', type=Path, default=ROOT/'data'/'raw'/RAW_NAME)
    parser.add_argument('--output-dir',type=Path,default=ROOT)
    args = parser.parse_args()
    try:
        quality = run(args.data, args.output_dir, args.model)
    except (ValueError,OSError) as exc:
        parser.exit(2,f'Analysis could not complete: {exc}\n')
    print(f'Completed: {quality["clean_rows"]} employees; results: {args.output_dir / "reports" / "results.md"}')

if __name__ == '__main__':
    main()
