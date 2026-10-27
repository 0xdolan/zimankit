// Portable core of the zimankit rules.  Run: dotnet run   (.NET 8)
using System.Text;
using System.Text.RegularExpressions;

Console.OutputEncoding = Encoding.UTF8;

var ckbMap = new Dictionary<string, string> { ["ك"] = "ک", ["ي"] = "ی", ["ى"] = "ی", ["ھ"] = "ه", ["ة"] = "ە" };
var kmrMap = new Dictionary<string, string>
{
    ["é"] = "ê", ["è"] = "ê", ["ë"] = "ê", ["í"] = "î", ["ì"] = "î", ["ï"] = "î",
    ["ú"] = "û", ["ù"] = "û", ["ü"] = "û", ["ı"] = "i", ["ș"] = "ş",
};
var ckbSplit = new Regex("^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$", RegexOptions.CultureInvariant);
var kmrSplit = new Regex("^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$", RegexOptions.CultureInvariant);
var feats = new Dictionary<string, string>
{
    ["ekê"] = "indef.obl.f", ["ekî"] = "indef.obl.m", ["eke"] = "indef.ezafe", ["ek"] = "indef",
    ["ên"] = "ezafe.pl", ["an"] = "obl.pl", ["a"] = "ezafe.f", ["ê"] = "ezafe.m|obl.f", ["î"] = "obl.m",
};

string MapChars(string s, Dictionary<string, string> m)
{
    var sb = new StringBuilder();
    foreach (var rune in s.Normalize(NormalizationForm.FormC).EnumerateRunes())
    {
        var c = rune.ToString();
        sb.Append(m.TryGetValue(c, out var r) ? r : c);
    }
    return sb.ToString();
}

string NormalizeCkb(string s) =>
    Regex.Replace(MapChars(s, ckbMap).Replace("ه‌", "ە"), @"(^|\s)ر", "$1ڕ");

bool IsArabic(string s) => s.Any(c => c >= '؀' && c <= 'ۿ');

var path = File.Exists("../inputs.txt") ? "../inputs.txt" : "inputs.txt";
foreach (var line in File.ReadLines(path, Encoding.UTF8))
{
    var w = line.Trim();
    if (w.Length == 0) continue;
    if (IsArabic(w))
    {
        var n = NormalizeCkb(w);
        var m = ckbSplit.Match(n);
        var seg = m.Success
            ? $"stem={m.Groups[1].Value} def={m.Groups[2].Value} clitic={(m.Groups[3].Success ? m.Groups[3].Value : "-")}"
            : $"stem={n}";
        Console.WriteLine($"ckb {w} -> {n} | {seg}");
    }
    else
    {
        var n = MapChars(w, kmrMap);
        var low = n.ToLowerInvariant();
        var m = kmrSplit.Match(low);
        var seg = m.Success ? $"stem={m.Groups[1].Value} suffix={m.Groups[2].Value} {feats[m.Groups[2].Value]}" : $"stem={low}";
        Console.WriteLine($"kmr {w} -> {n} | {seg}");
    }
}
