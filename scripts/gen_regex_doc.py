#!/usr/bin/env python3
"""Generate docs/17-regex-cookbook.md from zimankit.shared_utils.text_helpers.PATTERNS."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zimankit.shared_utils.text_helpers import COMPILED, PATTERNS  # noqa: E402

EXAMPLES = {
    "ckb_word": ["کتێبەکەم", "كتاب"], "kmr_word": ["jinekê", "Erdoğan"],
    "ckb_token": ["ئەمڕۆ کتێبەکەم کڕی"], "kmr_token": ["Ez li malê me"],
    "ckb_arabic_kaf_yeh": ["كتێب", "کتێب"], "ckb_legacy_heh_zwnj": ["به‌ڕێوه‌به‌ر"],
    "ckb_heh_doachashmee": ["ھەموو"], "ckb_initial_plain_r": ["رۆژ باش", "ڕۆژ باش"],
    "ckb_double_ae": ["سەەر"], "ckb_arabic_only_letters": ["صەبر", "سەبر"],
    "ckb_definite_suffix": ["پیاوەکە", "پیاو"], "ckb_pronominal_enclitic": ["کتێبەکەم"],
    "ckb_present_verb": ["دەکەم", "نادەم", "کتێب"], "ckb_infinitive": ["کردن", "شکاندن"],
    "kmr_turkish_letters": ["Erdoğan", "Kurdistan"], "kmr_wrong_circumflex": ["şéwe", "şêwe"],
    "kmr_oblique_suffix": ["jinekê", "jin"], "kmr_ezafe_suffix": ["mala", "malên"],
    "kmr_present_verb": ["dibînim", "nakim", "bibînim"], "kmr_infinitive": ["dîtin", "çûn"],
    "kmr_oblique_pronoun": ["min", "ez"], "kmr_direct_pronoun": ["ez", "min"],
}
DESC = {
    "ckb_word": "a whole Central Kurdish word (standard letters, ZWNJ only between letters)",
    "kmr_word": "a whole Hawar-alphabet word (optional apostrophe suffix: HDP'yê)",
    "ckb_token": "find Sorani words in running text", "kmr_token": "find Kurmanji words in running text",
    "ckb_arabic_kaf_yeh": "Arabic kaf / yeh / alef maksura that must become ک / ی",
    "ckb_legacy_heh_zwnj": "legacy spelling of ە as heh + ZWNJ", "ckb_heh_doachashmee": "ھ U+06BE used for h",
    "ckb_initial_plain_r": "word-initial ر that must be ڕ (group 1 = preceding char)",
    "ckb_double_ae": "illegal doubled ە", "ckb_arabic_only_letters": "letters of Arabic loans not in the Kurdish alphabet",
    "ckb_definite_suffix": "word ends in a definite suffix", "ckb_pronominal_enclitic": "word ends in a pronominal enclitic",
    "ckb_present_verb": "shape of a present-tense verb (دە/نا + stem + ending)", "ckb_infinitive": "infinitive ending",
    "kmr_turkish_letters": "Turkish letters (foreign or mistyped)", "kmr_wrong_circumflex": "acute/grave/macron typed for the circumflex",
    "kmr_oblique_suffix": "oblique-case endings", "kmr_ezafe_suffix": "ezafe endings",
    "kmr_present_verb": "present-tense verb shape (di-/na-/ni- + stem + ending)", "kmr_infinitive": "infinitive endings",
    "kmr_oblique_pronoun": "oblique personal pronoun (ergative agent)", "kmr_direct_pronoun": "direct-case personal pronoun",
}


def show(s: str) -> str:
    return s.replace("‌", "\\u200C").replace("|", "\\|")


lines = ["# Regex cookbook", "",
         "Generated from `zimankit/shared_utils/text_helpers.py: PATTERNS` by `scripts/gen_regex_doc.py` — do not edit by hand.",
         "", "All patterns avoid look-behind and engine-specific escapes, so they work unchanged in PCRE2 (`grep -P`), "
         "Python `re`, JavaScript (`u` flag), .NET, Java, Go RE2 and Rust `regex`. `\\u200C` below stands for the literal ZWNJ character.", ""]
for name, pat in PATTERNS.items():
    lines += [f"## `{name}`", "", DESC.get(name, ""), "", "```", pat.replace("‌", "\\u200C"), "```", ""]
    ex = EXAMPLES.get(name, [])
    if ex:
        lines += ["| input | match |", "|---|---|"]
        for e in ex:
            m = COMPILED[name].search(e)
            lines.append(f"| {show(e)} | {show(m.group()) if m else '—'} |")
        lines.append("")
lines += ["## Using the patterns", "",
          "```bash", "# shell (ugrep/GNU grep -P): count Arabic kaf/yeh per file", "grep -cP '[كيى]' *.txt",
          "# Sorani words ending in a definite suffix", "grep -oP '[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+(?:ەکە|ەکان)' text.txt | sort | uniq -c | sort -rn | head",
          "# Kurmanji oblique pronouns (possible ergative agents)", "grep -owE 'min|te|wî|wê|me|we|wan' text.txt | sort | uniq -c", "```", "",
          "```python", "from zimankit.shared_utils.text_helpers import COMPILED", 'COMPILED["ckb_definite_suffix"].search("پیاوەکە")', "```", "",
          "```typescript", 'const ckbDefinite = /(?:ەکە|کە|ەکان|کان)$/u;', 'ckbDefinite.test("پیاوەکە"); // true', "```", "",
          "```csharp", 'var ckbDefinite = new Regex("(?:ەکە|کە|ەکان|کان)$");', 'ckbDefinite.IsMatch("پیاوەکە"); // true', "```", "",
          "```rust", 'let re = regex::Regex::new("(?:ەکە|کە|ەکان|کان)$").unwrap();', 'assert!(re.is_match("پیاوەکە"));', "```", "",
          "```go", 're := regexp.MustCompile(`(?:ەکە|کە|ەکان|کان)$`)', 're.MatchString("پیاوەکە") // true', "```", ""]
(ROOT / "docs" / "17-regex-cookbook.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote docs/17-regex-cookbook.md")
