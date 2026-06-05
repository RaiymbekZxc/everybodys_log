# Everyone's Log Web

Standalone browser version of the Android WebView frontend.

## Run

Serve the folder:

```bash
python3 -m http.server 5173 -d web
```

Then visit `http://localhost:5173`.

The API server is baked into `js/app.js` as `https://everybodys-log.onrender.com`.

## Pages

- `login.html`
- `register.html`
- `index.html`
- `activity.html`
- `network.html`
- `profile.html`
- `admin.html`

## API Coverage

- `POST /api/auth/register`
- `POST /api/auth/token`
- `POST /api/auth/logout`
- `GET /api/auth/users/me`
- `PUT /api/auth/users/me`
- `GET /api/activity/info`
- `POST /api/activity/{category}`
- `GET /api/posts/{category}`
- `POST /api/posts/activity`
- `DELETE /api/posts/`
- `GET /api/posts/user/id/{id}`
- `PUT /api/admin/user/{username}/giveadmin`
- `PUT /api/admin/user/{username}/deactivate`
- `DELETE /api/admin/user/{username}/delete`
