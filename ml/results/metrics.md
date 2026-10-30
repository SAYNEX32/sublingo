Data: 240 labels, 238 distinct words, 2 user(s), 27% known. Source: placement. 20x repeated 5-fold cross-validation, folds grouped by word.

| Model | AUC | Log-loss | Brier |
|---|---|---|---|
| prior (no features) | 0.500 ± 0.000 | 0.584 ± 0.000 | 0.197 |
| app formula (fixed slope) | 0.774 ± 0.001 | 0.620 ± 0.002 | 0.172 |
| logreg: frequency | 0.769 ± 0.004 | 0.497 ± 0.004 | 0.159 |
| logreg: frequency+form | 0.762 ± 0.012 | 0.500 ± 0.010 | 0.163 |
| logreg: frequency+cognate | 0.760 ± 0.005 | 0.504 ± 0.006 | 0.162 |
| logreg: all features | 0.756 ± 0.013 | 0.507 ± 0.012 | 0.165 |
| boosting: all features | 0.693 ± 0.016 | 0.611 ± 0.026 | 0.198 |

± is the standard deviation over repeated cross-validation splits. It shows split-to-split variability, not the uncertainty of the data itself.

Bootstrap 95% intervals over words (1000 draws). A difference counts as real only if its interval excludes 0.

| Model | AUC 95% interval | AUC difference vs logreg: frequency |
|---|---|---|
| prior (no features) | 0.500 to 0.500 | -0.269 (-0.333 to -0.197) |
| app formula (fixed slope) | 0.704 to 0.839 | +0.006 (+0.003 to +0.010) |
| logreg: frequency | 0.697 to 0.833 | +0.000 (+0.000 to +0.000) |
| logreg: frequency+form | 0.700 to 0.835 | +0.000 (-0.038 to +0.035) |
| logreg: frequency+cognate | 0.690 to 0.825 | -0.008 (-0.012 to -0.005) |
| logreg: all features | 0.693 to 0.828 | -0.006 (-0.046 to +0.030) |
| boosting: all features | 0.629 to 0.774 | -0.065 (-0.110 to -0.016) |
