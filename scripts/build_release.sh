#!/usr/bin/env bash
# Build every release artefact into dist/:
#
#   zimankit-X.Y.Z-py3-none-any.whl     Python wheel   (pip install …)
#   zimankit-X.Y.Z.tar.gz               Python sdist
#   python3-zimankit_X.Y.Z-1_all.deb    Debian / Ubuntu package (sudo apt install ./…)
#   zimankit-X.Y.Z-source.zip / .tar.gz the full repository at the release tag (docs, tutorials, brand)
#   SHA256SUMS
#
# Usage: scripts/build_release.sh [git-ref]      (default: HEAD; CI passes the tag)
# Needs: uv (or python -m build), git, dpkg-deb.
set -euo pipefail

cd "$(dirname "$0")/.."
REF="${1:-HEAD}"
VERSION="$(sed -n 's/^__version__ = "\(.*\)"/\1/p' zimankit/__init__.py)"
if [[ "$REF" == v* && "$REF" != "v$VERSION" ]]; then
  echo "tag $REF does not match zimankit.__version__ $VERSION" >&2
  exit 1
fi
DIST=dist
rm -rf "$DIST" && mkdir -p "$DIST"

# Python wheel and sdist
if command -v uv >/dev/null; then uv build -q --out-dir "$DIST"; else python3 -m build --outdir "$DIST"; fi

# Source archives of the whole repository
git archive --format=zip --prefix="zimankit-$VERSION/" -o "$DIST/zimankit-$VERSION-source.zip" "$REF"
git archive --format=tar.gz --prefix="zimankit-$VERSION/" -o "$DIST/zimankit-$VERSION-source.tar.gz" "$REF"

# Debian package: the pure-Python package in dist-packages, the CLI in /usr/bin
PKG="python3-zimankit_${VERSION}-1_all"
ROOT="$(mktemp -d)/$PKG"
SITE="$ROOT/usr/lib/python3/dist-packages"
DOC="$ROOT/usr/share/doc/python3-zimankit"
mkdir -p "$SITE" "$ROOT/usr/bin" "$DOC" "$ROOT/DEBIAN"
python3 - "$DIST/zimankit-$VERSION-py3-none-any.whl" "$SITE" <<'EOF'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    z.extractall(sys.argv[2])
EOF
cat > "$ROOT/usr/bin/zimankit" <<'EOF'
#!/usr/bin/python3
import sys
from zimankit.cli import main
sys.exit(main())
EOF
chmod 755 "$ROOT/usr/bin/zimankit"
cp README.md "$DOC/README.md"
gzip -9n -c CHANGELOG.md > "$DOC/changelog.gz"
cat > "$DOC/copyright" <<EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: zimankit
Source: https://github.com/0xdolan/zimankit

Files: *
Copyright: Dolan H.
License: GPL-3.0-or-later
 On Debian systems the full text is in /usr/share/common-licenses/GPL-3.
EOF
cat > "$ROOT/DEBIAN/control" <<EOF
Package: python3-zimankit
Version: ${VERSION}-1
Section: python
Priority: optional
Architecture: all
Depends: python3 (>= 3.11)
Maintainer: Dolan H. <https://github.com/0xdolan>
Homepage: https://0xdolan.github.io/zimankit/
Installed-Size: $(du -sk "$ROOT/usr" | cut -f1)
Description: Kurdish language toolkit for Sorani and Kurmanji
 zimankit gives Central Kurdish (Sorani) and Northern Kurdish (Kurmanji)
 orthographic normalisation and validation, IPA, syllabification,
 transliteration between the Arabic and Latin scripts, morphological
 analysis, full verb paradigms, split-ergativity checking and language
 identification, as a Python library and the zimankit command.
EOF
find "$ROOT" -type d -exec chmod 755 {} + && find "$ROOT/usr" -type f ! -path "*/usr/bin/*" -exec chmod 644 {} +
dpkg-deb --root-owner-group --build "$ROOT" "$DIST/$PKG.deb" >/dev/null

(cd "$DIST" && sha256sum -- * > SHA256SUMS)
ls -lh "$DIST"
