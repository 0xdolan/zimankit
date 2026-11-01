#!/usr/bin/env python3
"""Master orchestration: harvest -> build -> rules -> export.

    python run_pipeline.py                 # all stages, cached stages reused
    python run_pipeline.py --stages build  # only rebuild outputs
    python run_pipeline.py --force         # recompute every stage
    python run_pipeline.py --stages export # Kaggle dataset in output/kaggle/
    python run_pipeline.py --stages bundle # release asset in output/bundle/ (after export)
"""

from __future__ import annotations

import argparse
import sys

from zimankit.config import load_config

STAGES = ("lexicon", "dictionaries", "corpus", "build", "rules", "export")
# Made only for a release, so a plain run does not need zstd.
OPTIONAL_STAGES = ("bundle",)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stages", default=",".join(STAGES), help="comma-separated subset of: " + ", ".join(STAGES + OPTIONAL_STAGES))
    ap.add_argument("--langs", default="ckb,kmr")
    ap.add_argument("--sources", help="alternative sources TOML")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(sources_file=args.sources)
    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    langs = [l.strip() for l in args.langs.split(",")]
    from zimankit.lexicon import harvest

    if "lexicon" in stages:
        harvest.harvest_lexicon(cfg, args.force)
    if "dictionaries" in stages:
        harvest.harvest_dictionaries(cfg, args.force)
    if "corpus" in stages:
        harvest.harvest_corpus(cfg, args.force)
    if "build" in stages:
        from zimankit.lexicon.builder import build

        for lang in langs:
            build(cfg, lang)
    if "rules" in stages:
        from zimankit.rules import export_rules

        for lang in langs:
            export_rules(cfg.output_dir / lang / f"grammar_rules_{lang}.json", lang)
    if "export" in stages:
        from zimankit.lexicon.export import export

        export(cfg, langs)
    if "bundle" in stages:
        from zimankit.lexicon.bundle import write_bundle

        print(f"bundle written to {write_bundle(cfg, langs)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
