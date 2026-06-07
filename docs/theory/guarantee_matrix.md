# Guarantee Matrix

This page summarizes the guarantee status of each method in this package.

## Status Labels

- **Proven**: Theoretical guarantee exists under the listed assumptions.
- **Parity**: Behavior is aligned to `onlineFDR` reference semantics for overlapping scope.
- **Extension**: Implemented in this package but not a direct `onlineFDR` counterpart.
- **Experimental**: Utility method without formal FDR/FWER guarantee claim in this package.

## Method Matrix

| Method | Error Target | Assumptions | Status | Notes |
|---|---|---|---|---|
| `EBH` | FDR | Valid e-values | Proven | Controls FDR under arbitrary dependence; large e-values are stronger evidence. |
| `ELond` | Online FDR | Valid e-values and summable gamma sequence | Proven | e-LOND controls online FDR under arbitrary dependence. |
| `Lond` | FDR | Independence / PRDS / dep-corrected mode | Proven + Parity | Use `dependent=True` for arbitrary dependence correction. |
| `LordThree` | FDR | Independence, valid reward budget | Proven + Parity | Requires `reward > 0` and `wealth + reward <= alpha`. |
| `LordPlusPlus` | FDR | Independence, guaranteed payout regime | Proven + Parity | This implementation enforces `reward == alpha`. |
| `LordDependent` | FDR | Arbitrary dependence (dependent LORD assumptions) | Proven + Parity | Uses dependent-LORD sequence scaling compatible with `onlineFDR` semantics. |
| `LordDiscard` | FDR | Conservative/null-adaptive regime with valid `tau` | Parity | Requires `0 < tau < 1`. |
| `Saffron` | FDR | Independence | Proven + Parity | Candidate-threshold method; parity-tested against `onlineFDR`. |
| `SaffronAsync` | mFDR | Independent p-values, asynchronous conflict-set assumptions | Proven + Extension | Lifecycle API; parity-tested against `onlineFDR` async reference paths. |
| `Addis` | FDR/mFDR regime | Conservative nulls, `0 < tau < 1`, `0 <= lambda < tau` | Proven + Parity | Parameter checks enforce supported region. |
| `AddisAsync` | mFDR | Conservative nulls plus asynchronous conflict-set assumptions | Proven + Extension | Lifecycle API with active unfinished tests counted in conflict accounting. |
| `Gai` | FDR/mFDR | Alpha-investing assumptions | Parity | Strict guarantees depend on payout specification. |
| `WeightedGaiPlusPlus` | FDR | Prior and penalty weights fixed independently of null p-values; valid memory decay | Proven + Extension | Implements weighted/memory GAI++ with author-code oracle tests. |
| `AlphaSpending` | FWER | Valid finite-horizon spending rule | Proven + Parity | Finite horizon is enforced for finite-`k` rules. |
| `OnlineFallback` | FWER | Online fallback assumptions | Proven + Parity | Boundary uses `p <= alpha_t`. |
| `BatchBH` | FDR | Batching assumptions from reference | Parity | Empty batch is a no-op. |
| `BatchStoreyBH` | FDR | Batching + Storey pi0 assumptions | Parity | `R+` uses same-size replacement semantics. |
| `BatchPRDS` | FDR | PRDS within-batch assumptions | Parity | Empty batch is a no-op. |
| `BatchBY` | FDR-style batch control | BY within-batch correction; no direct `onlineFDR` reference | Extension | Added conservative extension beyond the `onlineFDR` overlap set. |
| `Toad` | FDR | Decision deadlines and valid summable weights | Proven + Extension | Finite helper reduces to BH for a single uniform-deadline group. |
| `BatchBHOfficial` | FDR | AISTATS supplementary implementation assumptions | Extension | Alternate BatchBH profile using the authors' adaptive gamma policy. |
| `LORDMemoryDecay` | N/A (utility/monitoring use) | Application-specific | Experimental / Extension | Not claimed as a general FDR/FWER-control method in this package docs. |
| E-value calibrators | E-value construction | Valid input p-values and calibrator assumptions | Tooling | Construction-level guarantee only; FDR control comes from feeding valid e-values to a valid procedure. |
| E-value merging helpers | E-value construction | Fixed weights for arithmetic means; independence/conditional validity for products | Tooling | The package documents assumptions but cannot infer whether user-supplied evidence satisfies them. |
| E-process helpers | E-value construction | Caller-supplied model, betting, filtration, and stopping assumptions | Tooling | Stopped values are valid e-values only under the relevant e-process assumptions. |

## Important Scope Notes

- Guarantees apply only under each method's stated assumptions.
- Parity means semantic alignment for overlapping functionality, not identity of every API surface.
- Live R parity tests (`rpy2`) are mandatory in development/CI and require R plus `onlineFDR` (`2.18.0`).
- E-value toolbox helpers are construction utilities. They do not make an invalid input stream valid by themselves.

## References

1. https://www.bioconductor.org/packages/release/bioc/html/onlineFDR.html
2. https://bioc-release.r-universe.dev/onlineFDR/doc/manual.html
3. https://dsrobertson.github.io/onlineFDR/articles/theory.html
4. https://dsrobertson.github.io/onlineFDR/reference/LORD.html
5. https://dsrobertson.github.io/onlineFDR/reference/SAFFRON.html
6. https://dsrobertson.github.io/onlineFDR/reference/BatchBH.html
7. https://proceedings.mlr.press/v108/zrnic20a.html
8. https://arxiv.org/abs/1812.05068
9. https://arxiv.org/abs/1905.11465
10. https://proceedings.neurips.cc/paper/7148-more-powerful-and-flexible-rules-for-online-fdr-control-with-memory-and-weights
11. https://proceedings.mlr.press/v151/fisher22a.html
12. https://academic.oup.com/jrsssb/article/84/3/822/7056146
13. https://proceedings.mlr.press/v238/xu24a.html
