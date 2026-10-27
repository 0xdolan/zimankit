//! Portable core of the zimankit rules, std only.  Run: cargo run -q
use std::fs;

const CKB_MAP: &[(char, char)] = &[('ك', 'ک'), ('ي', 'ی'), ('ى', 'ی'), ('ھ', 'ه'), ('ة', 'ە')];
const KMR_MAP: &[(char, char)] = &[
    ('é', 'ê'), ('è', 'ê'), ('ë', 'ê'), ('í', 'î'), ('ì', 'î'), ('ï', 'î'),
    ('ú', 'û'), ('ù', 'û'), ('ü', 'û'), ('ı', 'i'), ('ș', 'ş'),
];
const CKB_DEF: &[&str] = &["ەکان", "ەکە", "کان", "کە"];
const CKB_CLITIC: &[&str] = &["مان", "تان", "یان", "م", "ت", "ی"];
const KMR_SUFFIX: &[(&str, &str)] = &[
    ("ekê", "indef.obl.f"), ("ekî", "indef.obl.m"), ("eke", "indef.ezafe"), ("ek", "indef"),
    ("ên", "ezafe.pl"), ("an", "obl.pl"), ("a", "ezafe.f"), ("ê", "ezafe.m|obl.f"), ("î", "obl.m"),
];

fn map_chars(s: &str, table: &[(char, char)]) -> String {
    s.chars().map(|c| table.iter().find(|(a, _)| *a == c).map(|(_, b)| *b).unwrap_or(c)).collect()
}

fn normalize_ckb(s: &str) -> String {
    let s = map_chars(s, CKB_MAP).replace("ه\u{200c}", "ە");
    // word-initial ر -> ڕ
    let mut out = String::new();
    let mut at_start = true;
    for c in s.chars() {
        out.push(if at_start && c == 'ر' { 'ڕ' } else { c });
        at_start = c.is_whitespace();
    }
    out
}

/// ^(.+?)(DEF)(CLITIC)?$ : the shortest non-empty stem whose remainder is DEF [+ CLITIC]
fn split_ckb(w: &str) -> Option<(String, &'static str, Option<&'static str>)> {
    let idx: Vec<usize> = w.char_indices().map(|(i, _)| i).skip(1).collect();
    for &i in &idx {
        let (stem, rest) = w.split_at(i);
        for d in CKB_DEF {
            if let Some(after) = rest.strip_prefix(d) {
                if after.is_empty() {
                    return Some((stem.to_string(), d, None));
                }
                if let Some(c) = CKB_CLITIC.iter().find(|c| **c == after) {
                    return Some((stem.to_string(), d, Some(c)));
                }
            }
        }
    }
    None
}

fn split_kmr(w: &str) -> Option<(String, &'static str, &'static str)> {
    let idx: Vec<usize> = w.char_indices().map(|(i, _)| i).skip(1).collect();
    for &i in &idx {
        let (stem, rest) = w.split_at(i);
        if let Some((s, f)) = KMR_SUFFIX.iter().find(|(s, _)| *s == rest) {
            return Some((stem.to_string(), s, f));
        }
    }
    None
}

fn main() {
    let path = if std::path::Path::new("../inputs.txt").exists() { "../inputs.txt" } else { "inputs.txt" };
    let text = fs::read_to_string(path).expect("inputs.txt");
    for w in text.lines().map(str::trim).filter(|l| !l.is_empty()) {
        if w.chars().any(|c| ('\u{0600}'..='\u{06FF}').contains(&c)) {
            let n = normalize_ckb(w);
            match split_ckb(&n) {
                Some((s, d, c)) => println!("ckb {w} -> {n} | stem={s} def={d} clitic={}", c.unwrap_or("-")),
                None => println!("ckb {w} -> {n} | stem={n}"),
            }
        } else {
            let n = map_chars(w, KMR_MAP);
            let low = n.to_lowercase();
            match split_kmr(&low) {
                Some((s, suf, f)) => println!("kmr {w} -> {n} | stem={s} suffix={suf} {f}"),
                None => println!("kmr {w} -> {n} | stem={low}"),
            }
        }
    }
}
