// Portable core of the zimankit rules.  Run: go run .
package main

import (
	"bufio"
	"fmt"
	"os"
	"regexp"
	"strings"
	"unicode"
)

var ckbMap = strings.NewReplacer("ك", "ک", "ي", "ی", "ى", "ی", "ھ", "ه", "ة", "ە", "ه‌", "ە")
var kmrMap = strings.NewReplacer("é", "ê", "è", "ê", "ë", "ê", "í", "î", "ì", "î", "ï", "î",
	"ú", "û", "ù", "û", "ü", "û", "ı", "i", "ș", "ş")
var initialR = regexp.MustCompile(`(^|\s)ر`)
var ckbSplit = regexp.MustCompile(`^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$`)
var kmrSplit = regexp.MustCompile(`^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$`)
var feats = map[string]string{"ekê": "indef.obl.f", "ekî": "indef.obl.m", "eke": "indef.ezafe", "ek": "indef",
	"ên": "ezafe.pl", "an": "obl.pl", "a": "ezafe.f", "ê": "ezafe.m|obl.f", "î": "obl.m"}

func isArabic(s string) bool {
	for _, r := range s {
		if unicode.In(r, unicode.Arabic) {
			return true
		}
	}
	return false
}

func main() {
	f, err := os.Open("../inputs.txt")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		w := strings.TrimSpace(sc.Text())
		if w == "" {
			continue
		}
		if isArabic(w) {
			n := initialR.ReplaceAllString(ckbMap.Replace(w), "${1}ڕ")
			if m := ckbSplit.FindStringSubmatch(n); m != nil {
				c := m[3]
				if c == "" {
					c = "-"
				}
				fmt.Printf("ckb %s -> %s | stem=%s def=%s clitic=%s\n", w, n, m[1], m[2], c)
			} else {
				fmt.Printf("ckb %s -> %s | stem=%s\n", w, n, n)
			}
		} else {
			n := kmrMap.Replace(w)
			low := strings.ToLower(n)
			if m := kmrSplit.FindStringSubmatch(low); m != nil {
				fmt.Printf("kmr %s -> %s | stem=%s suffix=%s %s\n", w, n, m[1], m[2], feats[m[2]])
			} else {
				fmt.Printf("kmr %s -> %s | stem=%s\n", w, n, low)
			}
		}
	}
}
