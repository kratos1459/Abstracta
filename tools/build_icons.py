"""Build a compact, recolourable icon pack from a Bioicons checkout.

Usage: python3 -I build_icons.py <bioicons_repo> <out.json> [max_kb]

For each icon: strip editor metadata, round coordinates, namespace ids so icons
never clash, and replace its most common colours with tokens (§0§ ...)
so the editor can recolour them. Share-alike licences are skipped.
"""
import hashlib, json, math, os, re, sys
import xml.etree.ElementTree as ET

ROOT, OUT = sys.argv[1], sys.argv[2]
MAX = float(sys.argv[3]) * 1000 if len(sys.argv) > 3 else 30000
LIC_OK = {"cc-0", "cc-by-3.0", "cc-by-4.0", "mit", "bsd"}
NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "blue": "#0000ff",
         "green": "#008000", "gray": "#808080", "grey": "#808080", "yellow": "#ffff00"}

meta = {}
for m in json.load(open(os.path.join(ROOT, "static/icons/icons.json"))):
    meta[(m["category"], m["name"])] = m


def norm_hex(c):
    c = c.lower()
    if c in NAMED:
        return NAMED[c]
    if re.fullmatch(r"#[0-9a-f]{3}", c):
        return "#" + "".join(ch * 2 for ch in c[1:])
    return c if re.fullmatch(r"#[0-9a-f]{6}", c) else None


SVGNS = "http://www.w3.org/2000/svg"; XL = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVGNS); ET.register_namespace("xlink", XL)
DROP_TAGS = {"script", "foreignObject", "metadata", "title", "desc", "style"}


def clean(el):
    for ch in list(el):
        ns, _, local = ch.tag.rpartition("}") if isinstance(ch.tag, str) else ("", "", "")
        ns = ns.lstrip("{")
        if not isinstance(ch.tag, str) or ns != SVGNS or local in DROP_TAGS:
            el.remove(ch); continue
        clean(ch)
    for k in list(el.attrib):
        ns = k[1:].split("}")[0] if k.startswith("{") else ""
        local = k.split("}")[-1]
        if (ns and ns != XL) or local.lower().startswith("on") or (local == "href" and not el.attrib[k].startswith("#")):
            del el.attrib[k]


def inline_css(root):
    css = ""
    for st in root.iter(f"{{{SVGNS}}}style"):
        css += st.text or ""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@[\w-]+[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)  # drop @font-face/@media blocks
    rules = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        body = body.strip().rstrip(";")
        for one in sel.split(","):
            one = one.strip()
            if re.fullmatch(r"\.[\w-]+", one) or re.fullmatch(r"[a-zA-Z]+", one) or re.fullmatch(r"[a-zA-Z]+\.[\w-]+", one):
                rules.append((one, body))
    if not rules:
        return
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        tag = el.tag.split("}")[-1]
        classes = set((el.get("class") or "").split())
        add = [b for sel, b in rules if (sel.startswith(".") and sel[1:] in classes) or sel == tag or ("." in sel and not sel.startswith(".") and sel.split(".")[0] == tag and sel.split(".")[1] in classes)]
        if add:
            el.set("style", ";".join(add + ([el.get("style")] if el.get("style") else [])))
        if "class" in el.attrib:
            del el.attrib["class"]


def minify(t, uid):
    t = re.sub(r"<!DOCTYPE.*?>", "", t, flags=re.S)
    try:
        root = ET.fromstring(t.encode("utf-8"))
    except ET.ParseError:
        return None
    if root.tag != f"{{{SVGNS}}}svg":
        return None
    vb = root.get("viewBox")
    if vb:
        nums = [float(x) for x in re.split(r"[\s,]+", vb.strip())]
    else:
        num = lambda v: float(re.match(r"[\d.]+", v or "").group(0)) if re.match(r"[\d.]+", v or "") else None
        w, h = num(root.get("width")), num(root.get("height"))
        if not (w and h):
            return None
        nums = [0, 0, w, h]
    if len(nums) != 4 or nums[2] <= 0 or nums[3] <= 0:
        return None
    inline_css(root)
    clean(root)
    inner = "".join(ET.tostring(ch, encoding="unicode") for ch in root)
    inner = inner.replace(f' xmlns="{SVGNS}"', "").replace(f' xmlns:xlink="{XL}"', "")
    refs = set(re.findall(r"url\(#([^)\s'\"]+)\)", inner)) | set(re.findall(r'href="#([^"]+)"', inner))
    inner = re.sub(r'\sid="([^"]+)"', lambda mm: f' id="{uid}{mm.group(1)}"' if mm.group(1) in refs else "", inner)
    inner = re.sub(r"url\(#([^)\s'\"]+)\)", lambda mm: f"url(#{uid}{mm.group(1)})", inner)
    inner = re.sub(r'href="#([^"]+)"', lambda mm: f'href="#{uid}{mm.group(1)}"', inner)
    span = max(nums[2], nums[3])
    dec = max(1, min(4, 3 - int(math.floor(math.log10(span / 100))) if span > 0 else 2))
    inner = re.sub(r"-?\d+\.\d{%d,}" % (dec + 1), lambda mm: f"{float(mm.group(0)):.{dec}f}".rstrip("0").rstrip("."), inner)
    inner = re.sub(r">\s+<", "><", inner)
    inner = re.sub(r";?-inkscape-[\w-]+:[^;\"]*", "", inner)
    # sanity: must still be well-formed
    ET.fromstring(f'<svg xmlns="{SVGNS}" xmlns:xlink="{XL}">{inner}</svg>')
    return [round(v, 2) for v in nums], inner


def tokenise(inner):
    counts = {}
    pat = re.compile(r"(fill|stroke|stop-color|color)(\s*[:=]\s*\"?)(#[0-9a-fA-F]{3,6}\b|black|white|red|blue|green|gr[ae]y|yellow)")
    for mm in pat.finditer(inner):
        c = norm_hex(mm.group(3))
        if c:
            counts[c] = counts.get(c, 0) + 1
    cols = [c for c, _ in sorted(counts.items(), key=lambda kv: -kv[1])][:8]
    idx = {c: i for i, c in enumerate(cols)}
    def sub(mm):
        c = norm_hex(mm.group(3))
        if c in idx:
            return f"{mm.group(1)}{mm.group(2)}§{idx[c]}§"
        return mm.group(0)
    return pat.sub(sub, inner), cols


out, skipped, n = [], {"img": 0, "big": 0, "bad": 0, "lic": 0}, 0
base = os.path.join(ROOT, "static/icons")
for lic in sorted(os.listdir(base)):
    if not os.path.isdir(os.path.join(base, lic)):
        continue
    if lic not in LIC_OK:
        skipped["lic"] += 1
        continue
    for dp, _, fns in os.walk(os.path.join(base, lic)):
        for fn in sorted(fns):
            if not fn.endswith(".svg"):
                continue
            p = os.path.join(dp, fn)
            parts = os.path.relpath(p, base).split(os.sep)
            cat, name = parts[1], fn[:-4]
            t = open(p, encoding="utf-8", errors="replace").read()
            if "<image" in t or "base64" in t:
                skipped["img"] += 1; continue
            n += 1
            hid = "b" + hashlib.md5(os.path.relpath(p, base).encode()).hexdigest()[:8]
            r = minify(t, hid + "_")
            if not r:
                skipped["bad"] += 1; continue
            vb, inner = r
            inner, cols = tokenise(inner)
            lim = {"Viruses": 90e3, "Plants_Algae": 60e3, "Receptors_channels": 60e3, "Cell_types": 60e3, "Animals": 40e3, "Cell_membrane": 40e3, "Cell_culture": 40e3}.get(cat, MAX)
            if len(inner) > lim:
                skipped["big"] += 1; continue
            m = meta.get((cat, name), {})
            out.append({"id": hid, "n": name.replace("_", " ").replace("-", " ").strip(), "cat": cat,
                        "lic": lic, "by": m.get("author", parts[2].replace("--", ". ").replace("-", " ")),
                        "vb": vb, "c": cols, "m": inner})

json.dump(out, open(OUT, "w"), separators=(",", ":"), ensure_ascii=False)
print(len(out), "icons", round(os.path.getsize(OUT) / 1e6, 2), "MB", skipped)
