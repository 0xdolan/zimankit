# Contributing to zimankit

## Branches (git flow)

| branch | purpose |
|---|---|
| `main` | released code only. Every commit on `main` is a tagged release (`vX.Y.Z`). The website is deployed from `main`. |
| `develop` | the integration branch. Features are merged here. |
| `feature/<name>` | one feature or fix, branched from `develop` and merged back with `--no-ff`. |
| `release/X.Y.Z` | release preparation: version bump and changelog, branched from `develop`. |
| `hotfix/X.Y.Z` | an urgent fix to a release, branched from `main`. |

```bash
git switch develop && git switch -c feature/my-change
# … commit …
python -m pytest -q
git switch develop && git merge --no-ff feature/my-change
```

## Making a release

1. `git switch -c release/X.Y.Z develop`
2. Set `__version__` in `zimankit/__init__.py`, and move the `[Unreleased]` notes in `CHANGELOG.md` under a new `[X.Y.Z] - YYYY-MM-DD` heading.
3. Check it: `python -m pytest -q && scripts/build_release.sh`
4. Merge it into `main` with `--no-ff` and tag it there: `git tag -a vX.Y.Z -m "zimankit X.Y.Z"`
5. Merge `main` back into `develop`, delete the release branch, and push `main`, `develop` and the tag.

Pushing the tag starts [`.github/workflows/release.yml`](.github/workflows/release.yml). It runs the tests, builds the wheel, sdist, `.deb` and source archives, and publishes them on a GitHub release with the changelog section as its notes.

## Tests and generated files

- `python -m pytest -q` runs the whole suite, including the ground-truth matrix and the tutorial drift check.
- Tutorial tables are generated: run `python scripts/gen_tutorials.py` after changing a skill.
- Brand files are generated: run `uv run python scripts/make_brand.py` after changing the logo (needs Inkscape and ImageMagick).
- The website lives in [`site/`](site/). Preview it with `python -m http.server -d site` after `scripts/build_site.sh`.
