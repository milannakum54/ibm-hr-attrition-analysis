# Verification

Verified 2026-10-22 on Windows with Python 3.14. The latest scope covers both partners' code and shared integration.

- 317 automated tests passed with zero failures and no pytest warnings.
- 140 seeded randomized test cases, malformed input cases and a 10,000-row workload are included.
- All five notebooks executed from fresh kernels with no error outputs; the notebook verifier exited successfully (0).
- Full analysis including the optional model and Milan's independent runner completed.
- Twelve regenerated charts were checked; the raw input checksum is unchanged.
- Statistical, model, parsing and output-generation defects found during testing were corrected.
- Latest repairs restore test collection and reconcile the 16 statistical comparisons across reports, saved results and documentation. Figure count remains 12.
- Latest details, limitations and reproduction commands: [testing_report.md](testing_report.md).
- Machine-readable evidence: reports/qa/test_results.xml and reports/qa/summary.json.
- Historical commits separate the data/categorical package, numeric/statistical package and shared setup/integration; the latest repair covers their shared regressions. See git log and team_workflow.md for author details.
- GitHub Actions is configured; the local checks do not establish a successful remote workflow run. Check the repository Actions page after upload.

Verification covers both portions and the shared integration. Test evidence records executed checks; it does not replace each member's code review or explanation of the methods.
