# Called to Go Ministry

Production: https://calledtogoministry.org/ . GitHub Pages publishes the main branch root. Updating a draft branch does not publish it. The custom domain is served at `/`; repository-subpath previews are not the supported deployment target.

## Editing and verification

`index.html` is the editable home document and shared interface. `site-pages.json` contains the real section URLs, page titles and descriptions. After edits run:

```
python3 build_pages.py
python3 verify_site.py
```

The builder produces seven section entry documents plus the home document, canonical metadata, structured data, sitemap.xml and exact inline-script hashes for the Content Security Policy. Do not hand-edit generated section documents or copy a stale CSP after changing JavaScript. The build is deterministic. The previously mentioned external build-site.py source is not present in this checkout; this repository now contains the build for these entry pages.

Local preview: run `python3 -m http.server 8765 --bind 127.0.0.1` in this folder and open http://127.0.0.1:8765/ . Tabs remain instant with JavaScript; the real navigation links and selected page content are present in the static HTML. The PDF delivery text is pre-rendered too.

## Security and privacy limits

CSP is delivered by HTML meta on GitHub Pages. Scripts require exact hashes; inline event handlers and eval are not allowed. Styles retain unsafe-inline because the existing design uses style attributes. The policy permits the existing Google Fonts, YouTube artwork/player and the named chatbot origin. The referrer policy is set in HTML.

HTML meta cannot set HSTS, X-Content-Type-Options, Permissions-Policy or enforce CSP frame-ancestors. Those require hosting/edge HTTP headers; a Cloudflare `_headers` file would not configure GitHub Pages. Do not claim those protections are active merely by adding a file here. HTTPS redirect has been enabled in GitHub Pages separately.

The live chatbot Worker is separate from this repository’s Pages deployment. Cloudflare operational logs remain enabled; the deployed Worker redacts raw upstream response bodies. Google optional request storage was observed disabled in the owner-identified account’s project, which is Free tier. Google’s provider abuse monitoring and unpaid-service data-use terms still apply. No zero-retention promise is made. No API key belongs in this repository.

Before website publication, align the live Worker prompt’s navigation references with the new Prayer/Songs pages. The website PR remains draft until the owner approves publishing. Search Console submission and search-engine indexing are separate post-publication checks.

© 2026 Christine Grace Masiba Cabason. All rights reserved. See COPYRIGHT.md.
