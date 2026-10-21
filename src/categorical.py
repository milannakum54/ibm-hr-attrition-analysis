"""Milan's categorical charts; numeric charts remain in src.plots."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .data import group_rates, GROUPS, validate_prepared


def save(fig, folder, name):
    path = Path(folder) / (name + '.png')
    try:
        fig.tight_layout()
        fig.savefig(path, dpi=160, bbox_inches='tight')
    finally:
        plt.close(fig)
    return path


def rate_chart(df, col, ax):
    table = group_rates(df, col)
    bars = ax.barh(table[col].astype(str), table.rate_pct, color='#287c8e')
    for bar, row in zip(bars, table.itertuples()):
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                f'{row.rate_pct:.1f}% (n={row.n})' + (' *' if row.small_group else ''), va='center', fontsize=8)
    ax.set_xlim(0, max(20, float(table.rate_pct.max()) * 1.55))
    ax.set_xlabel('Employees who left (%)')
    ax.set_title(col.replace('Label', '') + ' | * n < 30')

def categorical_plots(df, folder):
    validate_prepared(df, GROUPS)
    Path(folder).mkdir(parents=True, exist_ok=True)
    generated = []
    fig, ax = plt.subplots(figsize=(8, 4))
    counts = df.Attrition.value_counts().reindex(['No', 'Yes'], fill_value=0)
    bars = ax.bar(counts.index, counts/len(df)*100, color=['#287c8e', '#cf6d48'])
    for bar, n in zip(bars, counts):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                f'{n/len(df):.1%} (n={n})', ha='center')
    ax.set_ylim(0, 110); ax.set_ylabel('Employees (%)'); ax.set_title('Attrition distribution')
    generated.append(save(fig, folder, '01_attrition_distribution'))
    for name, cols in [('02_overtime', ['OverTime']),
                       ('03_department_jobrole', ['Department', 'JobRole']),
                       ('04_age_groups', ['AgeGroup']), ('06_job_level', ['JobLevel']),
                       ('07_satisfaction', ['JobSatisfactionLabel', 'EnvironmentSatisfactionLabel', 'WorkLifeBalanceLabel']),
                       ('10_business_travel', ['BusinessTravel'])]:
        fig, axes = plt.subplots(len(cols), 1, figsize=(11, 4*len(cols)), squeeze=False)
        for col, ax in zip(cols, axes[:, 0]):
            rate_chart(df, col, ax)
        generated.append(save(fig, folder, name))
    return sorted(generated)
