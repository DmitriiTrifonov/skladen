# configurator/

A web page for choosing what to print and downloading it as STL or 3MF, with a 3D preview
of the print plates. Static: no server, nothing is computed in the browser except the file.

## How it works

`cad/configurator_export.py` builds every offered variant with the same `model.build()` calls
as `cad/build.py` and writes each as a gzipped mesh in its printing pose to
`public/parts/` (53 parts, about 6 MB), plus `manifest.json`. The page picks parts by name
(`lid-r0.60-t1.0-recess`, `base-din934-window`, ...), lays them on 256 x 256 mm beds and
writes the file in the browser.

| Choice | Values |
|---|---|
| Lid: crush ribs | 0.50 / 0.60 / 0.70 mm |
| Lid: button tongues | 0.8 / 1.0 / 1.2 mm |
| Lid: logo | none / inlay / through (inlay is a second part) |
| Frame | closed over the buttons / with cut-out |
| Base: nut | DIN 934 / plain |
| Base: switch | window + plug (clearance 0.05 / 0.10 / 0.15) or shuttle (finger 0.5-1.5, stem 0.5-3.0) |

STL is one file in one colour. 3MF keeps each part as its own object, and the lid with its
logo inlay as a two-part object, so a slicer can give them two filaments.

## Run

```sh
cd configurator
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/, relative paths, any sub-path works
```

After changing the model, run `.venv/bin/python cad/build.py` (it checks the model), then
`.venv/bin/python cad/configurator_export.py` (about 90 s) and commit `public/parts/`.

## Embedding

The workflow `.github/workflows/configurator.yml` publishes `dist/` to GitHub Pages
(settings: Pages > Source > GitHub Actions), at `https://mitya-labs.github.io/skladen/`.
On mitya-labs.github.io:

```html
<iframe src="https://mitya-labs.github.io/skladen/?lang=en&theme=light"
        title="Skladen 2 configurator" loading="lazy"
        style="width:100%;height:720px;border:0" allow="fullscreen"></iframe>
```

Query parameters: `lang=ru|en` (default: the browser's), `theme=light|dark` (default: the
visitor's). The choice is kept in the URL hash, so a link to `...#rib=0.70&logo=through`
opens with those options. Inside an iframe the page also posts
`{type: "skladen-config", config, kit}` to the parent on every change.
