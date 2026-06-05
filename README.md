# Meta-Nav APP

Meta-Nav is an **Android application**. The web version is a secondary companion interface and does not represent the full functionality of the app.

## Download Android App

Download the latest APK from the [Releases page](https://github.com/Jyotsna-cloud-prog/Team-Six-Seven/releases/tag/First-release).

Install on your Android device:
1. Download the `.apk` file
2. Enable **Install from unknown sources** in your device settings
3. Open the downloaded file and install

---

## Web Version (Secondary / Limited)

> ⚠️ The web version is a lightweight companion interface. It is **not** the primary app and does not replicate the full Android experience.

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
