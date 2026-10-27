// Portable core of the zimankit rules.  Run: java Kurdish.java   (JDK 11+ single-file launch)
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;

public class Kurdish {
    static final Map<String, String> CKB = Map.of("ك", "ک", "ي", "ی", "ى", "ی", "ھ", "ه", "ة", "ە");
    static final Map<String, String> KMR = Map.ofEntries(
        Map.entry("é", "ê"), Map.entry("è", "ê"), Map.entry("ë", "ê"), Map.entry("í", "î"), Map.entry("ì", "î"),
        Map.entry("ï", "î"), Map.entry("ú", "û"), Map.entry("ù", "û"), Map.entry("ü", "û"), Map.entry("ı", "i"), Map.entry("ș", "ş"));
    static final Pattern CKB_SPLIT = Pattern.compile("^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$");
    static final Pattern KMR_SPLIT = Pattern.compile("^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$");
    static final Map<String, String> FEATS = Map.of("ekê", "indef.obl.f", "ekî", "indef.obl.m", "eke", "indef.ezafe",
        "ek", "indef", "ên", "ezafe.pl", "an", "obl.pl", "a", "ezafe.f", "ê", "ezafe.m|obl.f", "î", "obl.m");

    static String map(String s, Map<String, String> m) {
        StringBuilder b = new StringBuilder();
        s.codePoints().forEach(cp -> { String c = new String(Character.toChars(cp)); b.append(m.getOrDefault(c, c)); });
        return b.toString();
    }
    static String normalizeCkb(String s) {
        s = map(Normalizer.normalize(s, Normalizer.Form.NFC), CKB).replace("ه‌", "ە");
        return s.replaceAll("(^|\\s)ر", "$1ڕ");
    }
    static String normalizeKmr(String s) { return map(Normalizer.normalize(s, Normalizer.Form.NFC), KMR); }

    public static void main(String[] args) throws Exception {
        Path in = Files.exists(Paths.get("inputs.txt")) ? Paths.get("inputs.txt") : Paths.get("../inputs.txt");
        for (String line : Files.readAllLines(in, StandardCharsets.UTF_8)) {
            String w = line.trim();
            if (w.isEmpty()) continue;
            if (w.codePoints().anyMatch(c -> c >= 0x0600 && c <= 0x06FF)) {
                String n = normalizeCkb(w);
                Matcher m = CKB_SPLIT.matcher(n);
                String seg = m.matches() ? "stem=" + m.group(1) + " def=" + m.group(2) + " clitic=" + (m.group(3) == null ? "-" : m.group(3)) : "stem=" + n;
                System.out.println("ckb " + w + " -> " + n + " | " + seg);
            } else {
                String n = normalizeKmr(w), low = n.toLowerCase(Locale.ROOT);
                Matcher m = KMR_SPLIT.matcher(low);
                String seg = m.matches() ? "stem=" + m.group(1) + " suffix=" + m.group(2) + " " + FEATS.get(m.group(2)) : "stem=" + low;
                System.out.println("kmr " + w + " -> " + n + " | " + seg);
            }
        }
    }
}
