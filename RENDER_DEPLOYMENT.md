# Render Deployment

This project is ready for Render Blueprint deployment with:

- `targ-api`: FastAPI backend Docker web service
- `targ-web`: Streamlit Docker web service
- `targ-postgres`: persistent Render Postgres database

## Deploy

1. Push this folder to a GitHub repository.
2. In Render, choose **New > Blueprint**.
3. Connect the repository and select `render.yaml`.
4. Apply the Blueprint.

Render will create the Postgres database and inject its connection string into `DATABASE_URL` for the backend.

## Important URLs

The included `render.yaml` uses these service names:

- Backend: `https://targ-api.onrender.com`
- Web: `https://targ-web.onrender.com`

If Render changes the generated URL because the name is already taken, update:

- `render.yaml` `TARG_API_URL`
- `render.yaml` backend `CORS_ORIGINS`
- Android build property `TARG_API_BASE_URL`

## Android APK for Render

The APK now reads its API base URL from Gradle:

```bash
cd targ-android
./gradlew assembleDebug -PTARG_API_BASE_URL=https://targ-api.onrender.com/
```

For local emulator testing:

```bash
./gradlew assembleDebug -PTARG_API_BASE_URL=http://10.0.2.2:8080/
```

## Persistent Database

The backend uses SQLAlchemy and reads `DATABASE_URL`.

- Local default: `sqlite:///./targ.db`
- Render production: Postgres connection string from `targ-postgres`

Tables are created automatically on startup with `Base.metadata.create_all`.
