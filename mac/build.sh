#!/bin/bash
# Builds Abstracta.app from this repository and installs it in ~/Applications.
# Run from Terminal:  bash mac/build.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v swiftc >/dev/null 2>&1; then
  echo ""
  echo "The Swift compiler is not installed yet."
  echo "A window will open asking to install the Command Line Tools: click Install."
  echo "When it finishes, run this same command again."
  xcode-select --install || true
  exit 1
fi

APP="build/Abstracta.app"
echo "1/6  Preparing app folder"
rm -rf build
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" build/AppIcon.iconset

echo "2/6  Building the offline editor (icons embedded)"
python3 - <<'PY'
src = open("../index.html", encoding="utf-8").read()
pack = open("../icons.json", encoding="utf-8").read().replace("</", "<\\/")
assert "/*ICONPACK*/" in src, "index.html is missing the /*ICONPACK*/ placeholder"
open("build/Abstracta.html", "w", encoding="utf-8").write(src.replace("/*ICONPACK*/", pack))
PY

echo "3/6  Compiling (about 30 seconds)"
swiftc -O main.swift -o "$APP/Contents/MacOS/Abstracta" -framework Cocoa -framework WebKit

echo "4/6  Adding the editor and icon"
cp Info.plist "$APP/Contents/Info.plist"
cp build/Abstracta.html "$APP/Contents/Resources/Abstracta.html"
for s in 16 32 128 256 512; do
  sips -z $s $s icon-1024.png --out "build/AppIcon.iconset/icon_${s}x${s}.png" >/dev/null
  d=$((s * 2))
  sips -z $d $d icon-1024.png --out "build/AppIcon.iconset/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns build/AppIcon.iconset -o "$APP/Contents/Resources/AppIcon.icns"

echo "5/6  Signing for this Mac"
xattr -cr "$APP"
codesign --force --deep --sign - "$APP"

echo "6/6  Installing to ~/Applications"
mkdir -p "$HOME/Applications"
if [ -d "$HOME/Applications/Abstracta.app" ]; then
  mv "$HOME/Applications/Abstracta.app" "$HOME/.Trash/Abstracta-old-$(date +%s).app"
fi
cp -R "$APP" "$HOME/Applications/Abstracta.app"
touch "$HOME/Applications/Abstracta.app"

echo ""
echo "Done. Abstracta is in your Applications folder (~/Applications)."
echo "To keep it in the Dock: right-click its Dock icon > Options > Keep in Dock."
open "$HOME/Applications/Abstracta.app"
