# logo/

The Mitya Labs logo for the lid, as a recess and the inlay that fills it, for a
two-filament print. The device lid in [`../device/`](../device/) has no logo; the bezel
lids with a logo are in [`../bezel/`](../bezel/) and are cut from the same artwork
(`cad/logo/*.svg`).

| File | What it is |
|---|---|
| `skladen2-lid-logo.stl`, `.step` | Lid with the logo recess cut into its rear wall |
| `skladen2-logo-green.stl`, `.step` | The green inlay that fills the recess |

Print both as PETG (PLA with PETG bonds weakly). `build.py` checks that the inlay
exactly fills what the recess took out.
