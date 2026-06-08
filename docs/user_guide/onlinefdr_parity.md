# onlineFDR Parity Profile

This project is aligned against the Bioconductor release semantics of
`onlineFDR` (`2.18.0`, Bioconductor release `3.22`) for overlapping methods.
Local and CI parity execution requires R `4.5.x` to use this Bioconductor track.

## Live Parity Policy

Parity tests are required for parity-covered behavior and run against the live R
package through `rpy2`.
The suite fails fast when:

- `rpy2` is unavailable
- R is unavailable
- `onlineFDR` is unavailable
- `onlineFDR` is not pinned to `2.18.0`

The parity harness uses deterministic long p-value sequences and checks:

- Exact equality for rejection decisions
- Alpha-threshold closeness with absolute tolerance `1e-12` (`rel=0`)

## Status Labels

- `Parity`: Same method-level testing semantics as `onlineFDR` for overlapping scope.
- `IntentionalDivergence`: Deliberate API/product difference.
- `Extension`: Implemented here but not a direct `onlineFDR` counterpart.

## Method Mapping

| Method | Status | Notes |
|---|---|---|
| `Addis` | `Parity` | Enforces `0 < tau < 1` and `0 <= lambda_ < tau`. |
| `Saffron` | `Parity` | Candidate-based online FDR as in `onlineFDR`. |
| `SaffronAsync` | `Extension` | True lifecycle API with dedicated live R parity against `SAFFRONstar(version="async")`. |
| `AddisAsync` | `Extension` | True lifecycle API with dedicated live R parity against `ADDIS(async=TRUE)`. |
| `LordThree` | `Parity` | Sequential LORD-3 semantics. |
| `LordPlusPlus` | `Parity` | LORD++ semantics under strict guaranteed payout mode (`reward == alpha`). |
| `LordDiscard` | `Parity` | First-rejection state keyed to first discovery time. |
| `LordDependent` | `Parity` | Dependence-robust LORD variant for the supported reference regime. |
| `Lond` | `Parity` | Original/modified and dependent options supported. |
| `Gai` | `Parity` | Alpha-investing family equivalent. |
| `WeightedGaiPlusPlus` | `Extension` | Prior/penalty-weighted GAI++ checked against the authors' `OnlineFDRCode` formula. |
| `AlphaSpending` | `Parity` | Boundary uses `p_t <= alpha_t`. |
| `OnlineFallback` | `Parity` | Boundary uses `p_t <= alpha_t`. |
| `BatchBH` | `Parity` | Batch online BH semantics. |
| `BatchPRDS` | `Parity` | Batch PRDS variant. |
| `BatchStoreyBH` | `Parity` | `R+` computed on same-size batch via replacement, not append. |
| `BatchBY` | `Extension` | Added here as a conservative BY-style batch extension; no direct `onlineFDR` counterpart. |
| `Toad` | `Extension` | Decision-deadline online FDR checked against Fisher's AISTATS supplementary `toad.r`. |
| `LORDMemoryDecay` | `Extension` | Not a direct `onlineFDR` release method. |
| `BatchBHOfficial` | `Extension` | Matches the AISTATS supplementary BatchBH code profile, including the normalized `j^-2` small-batch gamma sequence. |
| Stateful `test_one` / `test_batch` API | `IntentionalDivergence` | True-online interface by design. |
| Date-level internal randomization | `IntentionalDivergence` | Not done internally; caller controls ordering. |

## References

1. https://www.bioconductor.org/packages/release/bioc/html/onlineFDR.html
2. https://bioc-release.r-universe.dev/onlineFDR/doc/manual.html
3. https://dsrobertson.github.io/onlineFDR/articles/theory.html
4. https://dsrobertson.github.io/onlineFDR/articles/onlineFDR.html
5. https://dsrobertson.github.io/onlineFDR/reference/LORD.html
6. https://dsrobertson.github.io/onlineFDR/reference/SAFFRON.html
7. https://dsrobertson.github.io/onlineFDR/reference/BatchBH.html
8. https://dsrobertson.github.io/onlineFDR/reference/online_fallback.html
9. https://rdrr.io/github/dsrobertson/onlineFDR/man/ADDIS.html
10. https://dsrobertson.github.io/onlineFDR/reference/StoreyBH.html
11. https://proceedings.mlr.press/v108/zrnic20a.html
12. https://github.com/fanny-yang/OnlineFDRCode
13. https://arxiv.org/abs/1812.05068
14. https://arxiv.org/abs/1905.11465
15. https://proceedings.neurips.cc/paper/7148-more-powerful-and-flexible-rules-for-online-fdr-control-with-memory-and-weights
16. https://proceedings.mlr.press/v151/fisher22a.html
