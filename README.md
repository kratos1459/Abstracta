# Abstracta

A free graphical-abstract editor for scientific figures, in the spirit of BioRender. It runs in any modern browser or as a native Mac app, and works offline.

**Open it now: [kratos1459.github.io/Abstracta](https://kratos1459.github.io/Abstracta/)** (no install, works on any computer)

- **1,370+ science icons**: 77 original Abstracta icons (no credit needed) plus 1,295 open-licence icons from [Bioicons](https://bioicons.com), searchable by name and category. Every icon can be recoloured.
- **Immunology and vaccine design**: original icons for immune cells (B, T helper, cytotoxic T, plasma, memory, macrophage, dendritic, NK, neutrophil), antigen presentation (MHC I/II, TCR, TLR, immune synapse, epitopes) and vaccine platforms (mRNA-LNP, viral vector, subunit, inactivated, live attenuated, VLP, multi-epitope construct, adjuvant), plus response curves, immune simulation and plasmid cloning.
- **Shapes, arrows and text**: boxes, panels, straight and curved arrows, two-way arrows, inhibition (⊣) lines, in-place text editing.
- **Editing**: drag, resize, rotate, snap guides, align and distribute, layers, undo and redo, copy and paste, drop in your own images (docking poses, plots).
- **Journal-ready export**: PNG and TIFF at 600 dpi (or any dpi) at a print width you set in cm, plus SVG for Illustrator or Inkscape. The dpi is written into the files.
- **Automatic icon credits**: the app builds the credit line for any CC BY icons you used and saves it with every export.
- **Templates**: a five-panel natural-product pipeline, an in silico multi-epitope vaccine design pipeline (reverse vaccinology), an immune-response flow, and a mechanism-of-action layout.

## Use it in the browser

The live site is **https://kratos1459.github.io/Abstracta/**, served by GitHub Pages from the `main` branch. Every push to `main` updates it within a minute or two. The editor loads `icons.json` beside it.

To try it locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Install on a Mac

Needs macOS 12 or later and the Xcode Command Line Tools (the script offers to install them).

```bash
git clone https://github.com/kratos1459/Abstracta.git
cd Abstracta
bash mac/build.sh
```

The script embeds the icon library into a single offline page, compiles a small Swift/WebKit wrapper (`mac/main.swift`), signs it for your Mac and installs **Abstracta.app** in `~/Applications`. Exports and saved projects go to Downloads.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The whole editor: HTML, CSS and JavaScript in one file |
| `icons.json` | The Bioicons pack, cleaned and made recolourable |
| `tools/build_icons.py` | Rebuilds `icons.json` from a Bioicons checkout |
| `mac/` | Native Mac wrapper: `main.swift`, `Info.plist`, app icon, `build.sh` |
| `ICON_LICENSES.md` | Licence and author of every bundled icon |

### Rebuilding the icon pack

```bash
git clone --depth 1 https://github.com/duerrsimon/bioicons /tmp/bioicons
python3 tools/build_icons.py /tmp/bioicons icons.json 25
```

The script strips editor metadata and any scripts, inlines styles, namespaces ids so icons never clash, rounds coordinates, and turns each icon's main colours into recolourable slots. It skips share-alike (CC BY-SA) icons and icons that embed bitmaps.

## Keyboard shortcuts

| Keys | Action |
| --- | --- |
| Double-click / Enter | Edit text |
| ⌘Z / ⇧⌘Z | Undo / redo |
| ⌘D, ⌥-drag | Duplicate |
| ⌘C / ⌘V | Copy / paste |
| ⌘] / ⌘[ | Bring forward / send backward |
| Arrow keys (⇧ for ×10) | Nudge |
| Space + drag | Pan |
| ⌘ + scroll | Zoom |
| ⌘S / ⌘E | Save project / export |

## Licences

- Code and the 77 Abstracta icons: MIT (see `LICENSE`).
- Bioicons icons keep their own licences (CC0, MIT, CC BY 3.0, CC BY 4.0). See `ICON_LICENSES.md`. Credit CC BY icons in your figure legend; the app writes that text for you.
- Abstracta is an independent project and is not affiliated with BioRender.
