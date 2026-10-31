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

Pushing the tag starts [`.github/workflows/release.yml`](.github/workflows/release.yml). It runs the tests and builds the wheel, sdist, `.deb` and source archives. It then publishes the wheel and sdist to PyPI, and all the files on a GitHub release with the changelog section as its notes. The two publishing jobs are separate, so one can be re-run if the other fails. A version number can be uploaded to PyPI only once; a mistake needs a new version.

## PyPI: Trusted Publishing

zimankit publishes to [PyPI](https://pypi.org/project/zimankit/) with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/): PyPI trusts this repository's release workflow through OpenID Connect, so no password or API token is stored anywhere.

The connection is set up once. On PyPI, go to **Account settings → Publishing → Add a new pending publisher** and enter:

| field | value |
|---|---|
| PyPI project name | `zimankit` |
| Owner | `0xdolan` |
| Repository name | `zimankit` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

The `pypi` environment on GitHub accepts deployments only from `v*` tags. The first release turns the pending publisher into a normal one and creates the project.

Continuous integration builds the package and checks its metadata and classifiers on every push, so problems show up before a release. Links and images in `README.md` must be absolute, because PyPI shows the README without the repository; a test checks this.

## Tests and generated files

- `python -m pytest -q` runs the whole suite, including the ground-truth matrix and the tutorial drift check.
- Tutorial tables are generated: run `python scripts/gen_tutorials.py` after changing a skill.
- Brand files are generated: run `uv run python scripts/make_brand.py` after changing the logo (needs Inkscape, ImageMagick, and the Manrope and Sahel fonts).
- The website lives in [`site/`](site/). Build and preview it with `scripts/build_site.sh && python3 -m http.server -d _site 8123`.
- `uv run --no-project --with playwright python scripts/check_site.py` checks the built site in a browser at phone to desktop widths: errors, sideways scrolling, broken images, tap targets and the playground. Add `--shots assets/brand/screenshots` to retake the screenshots.
- Site colours are tokens at the top of `site/css/site.css`; a test keeps text at 4.5:1 contrast in both themes. Icons are [Lucide](https://lucide.dev) (ISC, see `site/icons/LICENSE`). Fonts are hosted in `site/fonts/` under the Open Font License: Manrope for Latin text and Sahel for the Arabic-based script, with Estedad and Vazirmatn as choices for the reader.
