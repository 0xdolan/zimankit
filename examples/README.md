# Cross-language examples

Every program implements the same **portable core** of the zimankit rules and prints the same output for the same five inputs, so you can port the logic to any stack and diff the result against `expected_output.txt`.

The portable core:

1. Central Kurdish character normalisation: `ك→ک`, `ي ى→ی`, `ھ→ه`, `ة→ە`, legacy `ه+ZWNJ→ە`, word-initial `ر→ڕ`.
2. Northern Kurdish look-alike folding: `é è ë→ê`, `í ì ï→î`, `ú ù ü→û`, `ı→i`, `ș→ş`.
3. Central Kurdish segmentation `STEM + DEF + ENCLITIC`: `^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$`.
4. Northern Kurdish case suffix: `^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$` with the gender/case table from [chapter 13](../docs/13-kmr-morphology.md).

| folder | run | tested here |
|---|---|---|
| shell | `bash shell/kurdish.sh` | ✔ (GNU sed, perl-free) |
| python | `python3 python/kurdish.py` | ✔ (+ `python/zimankit_api.py` for the full library) |
| typescript | `node typescript/kurdish.ts` (Node ≥ 22.18 strips types) or `npx tsx` | ✔ |
| rust | `cd rust && cargo run -q` (std only) | ✔ |
| go | `cd go && go run .` | ✔ |
| java | `java java/Kurdish.java` | ✔ |
| csharp | `cd csharp && dotnet run` | not compiled here (.NET SDK unavailable) |
| fsharp | `cd fsharp && dotnet run` | not compiled here (.NET SDK unavailable) |

The full analyzer (lexicon-backed ranking, verbs, IPA, ergativity) lives in the Python package; call it from other languages through the CLI with `--json`:

```bash
python -m zimankit analyze --json کتێبەکەم | jq '.analyses[0].segmentation'
```

> Note the last line of `expected_output.txt`: the portable regex splits `Kûrdistan` as `kûrdist+an` (oblique plural).
> That is exactly why the real analyzer *generates and ranks* candidates against a lexicon and corpus
> frequencies instead of trusting the first regex match — `python -m zimankit analyze Kurdistan` keeps it whole.
