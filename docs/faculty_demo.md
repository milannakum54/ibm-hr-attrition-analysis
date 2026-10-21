# Faculty demonstration: seven minutes

1. Milan, 1 minute: Explain the question, fictional dataset, proposal and actual audited dimensions.
2. Milan, 2 minutes: Run the project. Show cleaning, attrition rate and categorical charts. Explain the within-group denominator and sample-size flags.
3. Rudra, 2 minutes: Show income/tenure distributions, correlations and statistical table. Explain effect sizes, sparse expected counts and Holm adjustment.
4. Rudra, 1 minute: If included, compare optional model metrics to the majority baseline and explain training-only preprocessing.
5. Both, 1 minute: Show real PRs, reviews, commits and contribution log. Explain one improvement each person made and the limitations.

## Evidence

Submit repository URL, final commit hash, executed notebooks, 12 figures, audit, computed results, statistical table, optional model metrics, contribution log and run instructions. Show `git log --all --graph --decorate --oneline` alongside PR reviews. Do not measure contribution only by commit counts.

## Viva questions and short answers

1. Why Pandas/NumPy? DataFrames support structured validation/grouping; arrays support numeric operations.
2. Attrition rate? Leavers divided by all employees in the same group.
3. Why drop constants and IDs? Constants provide no variation; identifiers do not describe employee characteristics.
4. Why retain outliers? Extreme values may be valid and require inspection rather than automatic deletion.
5. Correlation versus causation? Association cannot establish a causal mechanism, especially in a fictional snapshot.
6. Chi-square? Tests independence of categorical variables, subject to adequate expected counts.
7. Mann-Whitney U? Compares ranks/distributions; median interpretation needs distribution-shape assumptions.
8. Effect size and adjusted p-values? Magnitude and multiple-testing control answer different questions.
9. Why not accuracy alone? A majority prediction can look accurate while detecting no leavers.
10. How did you split the work? Explain actual tasks, reviews, commits and methods each person understands.
