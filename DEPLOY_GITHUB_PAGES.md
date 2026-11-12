# Hosting on GitHub Pages

GitHub Pages serves static files only. This repo handles that automatically:

- `site/` is the full local site (includes the admin page used with `python server.py`).
- `scripts/build_pages.py` builds `dist/`: the public pages only, with the admin page,
  its links and the local-backend scripts removed.
- `.github/workflows/pages.yml` runs that build and publishes `dist/` on every push to `main`.

## One-time setup

1. Create a GitHub repository and push this project to the `main` branch.
2. Repo **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
3. Push (or run the workflow from the **Actions** tab). The site appears at
   `https://<username>.github.io/<repo-name>/`.

## Custom domain (optional)

Settings -> Pages -> Custom domain. Add a DNS CNAME record pointing to
`<username>.github.io`, then tick **Enforce HTTPS**.

## Test the public build locally

```
python scripts/build_pages.py
python -m http.server 8080 --directory dist
```
Open http://127.0.0.1:8080/

## Updating the live site

Edit files in `site/`, commit, push. The workflow republishes automatically.
Content added through the local admin page is stored on your computer only and does
NOT appear on GitHub Pages. Edit the HTML directly for the online version.
