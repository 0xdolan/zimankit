<!-- nav:top -->
[← Regex cookbook](17-regex-cookbook.md) · [⌂ Contents](00-index.md) · [Testing and the verification matrix →](19-testing.md)
<!-- nav:top -->

# Examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java

All programs live in [`examples/`](../examples/README.md), read `examples/inputs.txt` and must print exactly `examples/expected_output.txt`:

```
ckb كتێبەكەم -> کتێبەکەم | stem=کتێب def=ەکە clitic=م
ckb پیاوەکە -> پیاوەکە | stem=پیاو def=ەکە clitic=-
ckb رۆژ -> ڕۆژ | stem=ڕۆژ
kmr jinekê -> jinekê | stem=jin suffix=ekê indef.obl.f
kmr Kürdistan -> Kûrdistan | stem=kûrdist suffix=an obl.pl
```

| language | file | how to run | verified |
|---|---|---|---|
| Bash + GNU sed/grep | [shell/kurdish.sh](../examples/shell/kurdish.sh) | `bash examples/shell/kurdish.sh` | ✔ |
| Python 3 (no deps) | [python/kurdish.py](../examples/python/kurdish.py) | `python3 examples/python/kurdish.py` | ✔ |
| Python, full library | [python/zimankit_api.py](../examples/python/zimankit_api.py) | `python examples/python/zimankit_api.py` | ✔ |
| TypeScript | [typescript/kurdish.ts](../examples/typescript/kurdish.ts) | `node examples/typescript/kurdish.ts` | ✔ (Node 24) |
| Java | [java/Kurdish.java](../examples/java/Kurdish.java) | `cd examples/java && java Kurdish.java` | ✔ (JDK 25) |
| Rust (std only) | [rust/src/main.rs](../examples/rust/src/main.rs) | `cd examples/rust && cargo run -q` | ✔ |
| Go | [go/main.go](../examples/go/main.go) | `cd examples/go && go run .` | ✔ |
| C# (.NET 8) | [csharp/Program.cs](../examples/csharp/Program.cs) | `cd examples/csharp && dotnet run` | not compiled in this environment |
| F# (.NET 8) | [fsharp/Program.fs](../examples/fsharp/Program.fs) | `cd examples/fsharp && dotnet run` | not compiled in this environment |

Check them all at once:

```bash
./scripts/check_examples.sh
```

## Porting notes

| concern | Python | JS/TS | .NET | Java | Go | Rust |
|---|---|---|---|---|---|---|
| NFC | `unicodedata.normalize` | `s.normalize("NFC")` | `s.Normalize(FormC)` | `Normalizer.normalize` | `golang.org/x/text/unicode/norm` | `unicode-normalization` crate |
| iterate code points | `for c in s` | `[...s]` | `EnumerateRunes()` | `codePoints()` | `for _, r := range s` | `s.chars()` |
| Unicode regex | default | `u` flag | default | default | RE2 default | `regex` crate |
| lowercase | use `skills_kmr.orthography.lower` | `toLowerCase()` | `ToLowerInvariant()` | `toLowerCase(Locale.ROOT)` | `strings.ToLower` | `to_lowercase()` |

Never use a Turkish locale for Kurmanji casing (`I` must lowercase to `i`, not `ı`).

## Calling the full analyzer from any language

The CLI emits JSON, so any stack can shell out to it:

```bash
python -m zimankit analyze --json --top 3 کتێبەکەم
python -m zimankit ipa --lang kmr dîtin
echo "Min tu dîtim." | python -m zimankit ergativity
```

```typescript
import { execFileSync } from "node:child_process";
const out = execFileSync("python", ["-m", "zimankit", "analyze", "--json", "کتێبەکەم"], { encoding: "utf8" });
console.log(JSON.parse(out).analyses[0].segmentation); // کتێب+ەکە+م
```

```csharp
var psi = new ProcessStartInfo("python", "-m zimankit analyze --json کتێبەکەم") { RedirectStandardOutput = true, StandardOutputEncoding = Encoding.UTF8 };
var json = Process.Start(psi)!.StandardOutput.ReadToEnd();
```

The wordlist CSVs are plain UTF-8 and load directly anywhere (`csv` module, `papaparse`, `CsvHelper`, `encoding/csv`, the `csv` crate).

<!-- nav:bottom -->
---
[← Regex cookbook](17-regex-cookbook.md) · [⌂ Contents](00-index.md) · [Testing and the verification matrix →](19-testing.md)
<!-- nav:bottom -->
