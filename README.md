# Edgar Jimenez Bedolla — researcher website

English, French and Spanish academic website.

## Publish on GitHub Pages

1. Create a public repository in the `edgar-jimenez-bedolla` account named
   `edgar-jimenez-bedolla.github.io`.
2. Upload the contents of this folder to the repository root. `index.html`,
   `styles.css`, `fr/`, `es/`, and `cv/` must appear directly in the repository.
   Do not upload the ZIP file itself or an extra enclosing folder.
3. Open Settings → Pages. Under Build and deployment, choose
   Deploy from a branch, select `main` and `/(root)`, then Save.
4. When GitHub finishes publishing, visit
   https://edgar-jimenez-bedolla.github.io/.

No custom domain, build command, package installation, or paid hosting is required.
The source repository is public.

## Edit the website

- English content: `index.html`.
- French and Spanish translations: `_maintenance/localize.py`.
- After changing content or translations, run
  `python _maintenance/localize.py` to regenerate all three pages.
  New untranslated text is flagged rather than silently published in English.
- Styling: `styles.css`.
- Interactions: `script.js`.
- CV: replace `cv/edgar-jimenez-bedolla-cv.pdf` with the approved English PDF.

After a future domain change, update `ORIGIN` in `_maintenance/localize.py`
and regenerate the pages before publishing.
