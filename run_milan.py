"""Run Milan's data preparation and seven categorical figures independently."""
import argparse
import json
from pathlib import Path
from src.data import RAW_NAME, GROUPS, prepare, group_rates
from src.categorical import categorical_plots
from src.outputs import staged_outputs

ROOT = Path(__file__).resolve().parent


def run(data_path, output_root):
    """Generate only Milan's outputs and return the audit and figure paths."""
    with staged_outputs(output_root, data_path) as stage:
        audit, figures = _generate(data_path, stage)
        names = [p.name for p in figures]
    return audit, [Path(output_root)/'visualizations'/name for name in names]


def _generate(data_path, output_root):
    df, audit = prepare(data_path)
    output_root = Path(output_root)
    reports = output_root/'reports'
    processed = output_root/'data'/'processed'
    reports.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed/'cleaned_hr.csv', index=False)
    (reports/'data_quality.json').write_text(json.dumps(audit, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    tables = {col:group_rates(df, col) for col in GROUPS}
    for col, table in tables.items():
        table.to_csv(reports/f'rates_{col}.csv', index=False)
    figures = categorical_plots(df, output_root/'visualizations')
    lines = ['# Milan: data and categorical results', '',
             f'Validated {len(df)} rows. Original columns: {audit["raw_columns"]}; prepared columns: {audit["clean_columns"]}.',
             f'Overall attrition: {int(df.AttritionFlag.sum())}/{len(df)} = {df.AttritionFlag.mean():.2%}.', '',
             '## Cleaning decisions', '',
             f'- Missing cells: {audit["missing_cells"]}; exact duplicates removed: {audit["duplicates_removed"]}.',
             '- Dropped: '+', '.join(audit['dropped_columns'])+'.',
             '- Required fields are retained even if constant in a filtered sample.',
             '- Pay-rate correlations are audited; weak correlation alone is insufficient grounds for deletion.',
             '- Original CSV is unchanged; its SHA-256 is recorded in data_quality.json.', '',
             '## Group results', '',
             'Each rate uses employees in that group as the denominator. An asterisk marks n < 30, a descriptive caution threshold.', '']
    for col, table in tables.items():
        lines += [f'### {col}', '', '| Group | Employees | Left | Attrition |', '|---|---:|---:|---:|']
        for row in table.itertuples(index=False):
            label = str(row[0]).replace('|', '\\|')
            lines.append(f'| {label}{" *" if row.small_group else ""} | {row.n} | {row.left} | {row.rate_pct:.2f}% |')
        lines.append('')
    overtime = tables['OverTime'].set_index('OverTime')
    if {'Yes','No'}.issubset(overtime.index):
        gap = overtime.loc['Yes','rate_pct']-overtime.loc['No','rate_pct']
        lines += ['## Interpretation', '',
                  f'The overtime-minus-no-overtime difference is {gap:.2f} percentage points in this sample.',
                  'This describes an association. It does not show that overtime caused employees to leave.', '']
    lines += ['## Limits', '', 'The source is fictional. Counts and rates describe this sample only. Small groups can give unstable percentages. These descriptive results do not include statistical tests or model evaluation.']
    (reports/'milan_results.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    manifest={'input_sha256':audit['sha256'],'rows':len(df),'figures':[p.name for p in figures]}
    (reports/'milan_run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return audit, figures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'data'/'raw'/RAW_NAME)
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        audit, figures = run(args.data, args.output_dir)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Analysis could not complete: {exc}\n')
    print(f'Milan analysis complete: {audit["clean_rows"]} rows, {len(figures)} figures.')
    print(f'Results: {args.output_dir / "reports" / "milan_results.md"}')


if __name__ == '__main__':
    main()
