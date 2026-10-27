// Portable core of the zimankit rules.  Run: node kurdish.ts  (Node >= 22.18) or npx tsx kurdish.ts
import { readFileSync } from "node:fs";

const CKB_MAP: Record<string, string> = { "ك": "ک", "ي": "ی", "ى": "ی", "ھ": "ه", "ة": "ە" };
const KMR_MAP: Record<string, string> = {
  "é": "ê", "è": "ê", "ë": "ê", "í": "î", "ì": "î", "ï": "î", "ú": "û", "ù": "û", "ü": "û", "ı": "i", "ș": "ş",
};
const CKB_SPLIT = /^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$/u;
const KMR_SPLIT = /^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$/u;
const KMR_FEATS: Record<string, string> = {
  "ekê": "indef.obl.f", "ekî": "indef.obl.m", "eke": "indef.ezafe", "ek": "indef",
  "ên": "ezafe.pl", "an": "obl.pl", "a": "ezafe.f", "ê": "ezafe.m|obl.f", "î": "obl.m",
};

const mapChars = (s: string, m: Record<string, string>): string => [...s].map((c) => m[c] ?? c).join("");

export function normalizeCkb(s: string): string {
  return mapChars(s.normalize("NFC"), CKB_MAP).replaceAll("ه‌", "ە").replace(/(^|\s)ر/gu, "$1ڕ");
}

export function normalizeKmr(s: string): string {
  return mapChars(s.normalize("NFC"), KMR_MAP);
}

const isArabic = (s: string): boolean => /[؀-ۿ]/u.test(s);

const inputs = readFileSync(new URL("../inputs.txt", import.meta.url), "utf8").split("\n").map((l) => l.trim()).filter(Boolean);
for (const w of inputs) {
  if (isArabic(w)) {
    const n = normalizeCkb(w);
    const m = CKB_SPLIT.exec(n);
    const seg = m ? `stem=${m[1]} def=${m[2]} clitic=${m[3] ?? "-"}` : `stem=${n}`;
    console.log(`ckb ${w} -> ${n} | ${seg}`);
  } else {
    const n = normalizeKmr(w);
    const low = n.toLowerCase();
    const m = KMR_SPLIT.exec(low);
    const seg = m ? `stem=${m[1]} suffix=${m[2]} ${KMR_FEATS[m[2]]}` : `stem=${low}`;
    console.log(`kmr ${w} -> ${n} | ${seg}`);
  }
}
