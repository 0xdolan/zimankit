// Portable core of the zimankit rules.  Run: dotnet run   (.NET 8)
open System
open System.IO
open System.Text
open System.Text.RegularExpressions

let ckbMap = dict [ "ك", "ک"; "ي", "ی"; "ى", "ی"; "ھ", "ه"; "ة", "ە" ]
let kmrMap =
    dict [ "é", "ê"; "è", "ê"; "ë", "ê"; "í", "î"; "ì", "î"; "ï", "î"
           "ú", "û"; "ù", "û"; "ü", "û"; "ı", "i"; "ș", "ş" ]
let ckbSplit = Regex("^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$")
let kmrSplit = Regex("^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$")
let feats =
    dict [ "ekê", "indef.obl.f"; "ekî", "indef.obl.m"; "eke", "indef.ezafe"; "ek", "indef"
           "ên", "ezafe.pl"; "an", "obl.pl"; "a", "ezafe.f"; "ê", "ezafe.m|obl.f"; "î", "obl.m" ]

let mapChars (m: Collections.Generic.IDictionary<string, string>) (s: string) =
    s.Normalize(NormalizationForm.FormC).EnumerateRunes()
    |> Seq.map (fun r -> let c = r.ToString() in if m.ContainsKey c then m.[c] else c)
    |> String.concat ""

let normalizeCkb (s: string) =
    Regex.Replace((mapChars ckbMap s).Replace("ه‌", "ە"), @"(^|\s)ر", "$1ڕ")

let isArabic (s: string) = s |> Seq.exists (fun c -> c >= '؀' && c <= 'ۿ')

[<EntryPoint>]
let main _ =
    Console.OutputEncoding <- Encoding.UTF8
    let path = if File.Exists "../inputs.txt" then "../inputs.txt" else "inputs.txt"
    for line in File.ReadLines(path, Encoding.UTF8) do
        let w = line.Trim()
        if w <> "" then
            if isArabic w then
                let n = normalizeCkb w
                let m = ckbSplit.Match n
                let seg =
                    if m.Success then
                        let c = if m.Groups.[3].Success then m.Groups.[3].Value else "-"
                        sprintf "stem=%s def=%s clitic=%s" m.Groups.[1].Value m.Groups.[2].Value c
                    else sprintf "stem=%s" n
                printfn "ckb %s -> %s | %s" w n seg
            else
                let n = mapChars kmrMap w
                let low = n.ToLowerInvariant()
                let m = kmrSplit.Match low
                let seg =
                    if m.Success then sprintf "stem=%s suffix=%s %s" m.Groups.[1].Value m.Groups.[2].Value feats.[m.Groups.[2].Value]
                    else sprintf "stem=%s" low
                printfn "kmr %s -> %s | %s" w n seg
    0
