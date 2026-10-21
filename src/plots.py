"""Twelve proposal visualizations; categorical rates always show denominators."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from .data import validate_prepared

def save(fig, folder, name):
    try:
        fig.tight_layout()
        fig.savefig(Path(folder) / (name + '.png'), dpi=160, bbox_inches='tight')
    finally:
        plt.close(fig)
    return Path(folder) / (name + '.png')

# Compatibility imports: existing callers keep working.
from .categorical import rate_chart, categorical_plots


def numeric_plots(df, folder):
    validate_prepared(df, ['MonthlyIncome','YearsAtCompany','DistanceFromHome','JobRole','OverTime'])
    Path(folder).mkdir(parents=True, exist_ok=True)
    generated = []
    for name, col in [('05_monthly_income', 'MonthlyIncome'), ('08_tenure', 'YearsAtCompany'),
                       ('11_distance', 'DistanceFromHome')]:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.boxplot([df.loc[df.Attrition==label,col] for label in ['No','Yes']],
                   tick_labels=['No','Yes'], patch_artist=True,
                   boxprops={'facecolor':'#74b7be'}, medianprops={'color':'#333333'})
        ax.set_xlabel('Attrition'); ax.set_ylabel(col)
        ax.set_title(col + ' by attrition (outliers retained)')
        generated.append(save(fig, folder, name))
    numeric = df.select_dtypes(include='number').drop(columns=['AttritionFlag'])
    fig, ax = plt.subplots(figsize=(13, 11))
    correlation = numeric.corr(method='spearman')
    if correlation.notna().any().any():
        sns.heatmap(correlation, cmap='vlag', vmin=-1, vmax=1, ax=ax)
    else:
        ax.text(.5,.5,'Correlation unavailable: no varying numeric pairs.',ha='center',va='center')
        ax.set_axis_off()
    ax.set_title('Spearman correlation: numeric HR variables')
    generated.append(save(fig, folder, '09_correlation'))
    grouped = df.groupby(['JobRole', 'OverTime'], observed=True).AttritionFlag.agg(['mean', 'size'])
    rates = grouped['mean'].unstack().reindex(columns=['No', 'Yes'])*100
    ns = grouped['size'].unstack().reindex(columns=['No', 'Yes'])
    labels = rates.copy().astype(object)
    for r in rates.index:
        for c in rates.columns:
            if rates.loc[r, c] == rates.loc[r, c]:
                labels.loc[r, c] = f'{rates.loc[r,c]:.1f}%\nn={int(ns.loc[r,c])}' + (' *' if ns.loc[r,c]<30 else '')
            else:
                labels.loc[r,c] = ''
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(rates, annot=labels, fmt='', cmap='YlOrRd', vmin=0, vmax=100, ax=ax)
    ax.set_title('Attrition rate by job role and overtime | * n < 30')
    generated.append(save(fig, folder, '12_overtime_jobrole'))
    return sorted(generated)
