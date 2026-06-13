# Local fonts

✅ **The 13 font files are already in `fonts/files/`** — no setup needed.
Open any slide; rendering uses local files instead of CDN.

This document is kept for reference (and for cases where you want to
upgrade a font version, or swap in a different family).

---

## What's installed

| Family | Weights | Where |
|---|---|---|
| **Pretendard** | 400, 500, 600, 700, 800 | `fonts/files/Pretendard-*.woff2` |
| **Newsreader** | 400, 400 italic, 500, 600, 700 | `fonts/files/Newsreader-*.woff2` |
| **JetBrains Mono** | 400, 500, 700 | `fonts/files/JetBrainsMono-*.woff2` |

The `@font-face` declarations live in `fonts.css`. They are imported
once from `colors_and_type.css` (`@import url("fonts/fonts.css")`),
so any HTML that includes `colors_and_type.css` gets local fonts
automatically. A CDN fallback is also wired in, so if the local files
are ever missing the rendering still works.

---

## If you ever need to re-download or upgrade

The original sources:

### Pretendard

GitHub: <https://github.com/orioncactus/pretendard/releases>
CDN: `https://cdnjs.cloudflare.com/ajax/libs/pretendard/<version>/static/woff2/`

```bash
# macOS/Linux — refresh Pretendard to a new version
cd fonts/files
v=1.3.9
base=https://cdnjs.cloudflare.com/ajax/libs/pretendard/$v/static/woff2
for w in Regular Medium SemiBold Bold ExtraBold; do
  curl -fLO "$base/Pretendard-$w.woff2"
done
```

### Newsreader & JetBrains Mono (via @fontsource on jsDelivr)

```bash
# JetBrains Mono
cd fonts/files
jb=https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.18/files
curl -fL "$jb/jetbrains-mono-latin-400-normal.woff2" -o JetBrainsMono-Regular.woff2
curl -fL "$jb/jetbrains-mono-latin-500-normal.woff2" -o JetBrainsMono-Medium.woff2
curl -fL "$jb/jetbrains-mono-latin-700-normal.woff2" -o JetBrainsMono-Bold.woff2

# Newsreader
nr=https://cdn.jsdelivr.net/npm/@fontsource/newsreader@5.0.16/files
for s in 400-normal 400-italic 500-normal 600-normal 700-normal; do
  curl -fL "$nr/newsreader-latin-$s.woff2" -o "Newsreader-$(echo $s | sed 's/-normal//;s/-italic/-Italic/').woff2"
done
```

---

## Verifying the local fonts are active

Open any slide template (e.g. `slides/cover.html`) in a browser →
DevTools → Computed → font-family. Pretendard should resolve from the
local file (you can see the URL in the Network tab). If the request
goes to a CDN, the local file is missing or the `@font-face` is being
shadowed.

For PPTX export, the `slides-grab/convert.cjs` pipeline picks up the
local woff2 files automatically.

---

## Why these three?

- **Pretendard** — Korean + Latin balance; the upstream choice in every
  `slides-grab` template. Switching breaks visual fidelity.
- **Newsreader** — Google's modern serif with a flexible optical-size
  axis. Used only in the Editorial Magazine direction.
- **JetBrains Mono** — Standard editor mono. Used in the editor UI kit
  and as `--font-mono` for code/labels.

If you swap a family, edit `colors_and_type.css` (`--font-sans`,
`--font-mono`, `--font-serif`), add the matching `@font-face` block in
`fonts.css`, drop new .woff2 files into `fonts/files/`, and flag the
substitution in the project README.

