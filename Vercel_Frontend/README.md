# TARG Vercel Web

This is the Vercel-compatible TARG web client. It is a static single-page app that calls the TARG API through the same-origin `/api/*` proxy configured in `vercel.json`.

Deploy this folder as the Vercel project root:

```bash
vercel --prod
```

The existing Streamlit UI remains in `Streamlit_Frontend/`. Streamlit requires a persistent interactive server, so this folder is the production Vercel frontend.
