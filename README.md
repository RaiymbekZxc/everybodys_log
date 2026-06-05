# Meta-Nav APP

## Launch Web Version

The web version is in the `web/` folder and runs as a static site.

From the project root, start a local static server:

```bash
python3 -m http.server 5173 -d web
```

Open the app in your browser:

```text
http://localhost:5173/login.html
```

After signing in, the app redirects to the dashboard at `index.html`.

The frontend uses the deployed API baked into `web/js/app.js`:

```text
https://everybodys-log.onrender.com
```

Main web pages:

- `login.html`
- `register.html`
- `index.html`
- `activity.html`
- `network.html`
- `profile.html`
- `admin.html`

More web-specific details are in `web/README.md`.
