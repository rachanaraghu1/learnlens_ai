# Deploy LearnLens AI on Render

This project uses a Render web service with a persistent disk so SQLite account and quiz data can survive application restarts and deployments. The service is configured by `render.yaml`.

## Before deployment

- Push this repository to GitHub. The local database, local backups, and Streamlit secrets are excluded from the deployment repository.
- Keep `models/success_model.joblib` and `models/metrics.json` in the repository; the app loads the trained model from `models/`.
- The deployed database starts empty. Users register new accounts on the deployed site.

## Create the service

1. Sign in to Render and connect the GitHub account that can access this repository.
2. Choose **New → Blueprint** and select `learnlens_ai` on the `main` branch.
3. Review the `learnlens-ai` web service and its `learnlens-data` persistent disk, then create the resources.
4. Wait for the first deploy to pass the `/_stcore/health` check. Render provides an HTTPS `onrender.com` URL.

The service uses Python 3.12, installs `requirements.txt`, runs Streamlit on Render's assigned port, and writes SQLite data to `/var/data/learnlens.db`.

## Persistence and cost

Render's persistent disks require a paid web service. The current Starter web service is listed at $7/month, and a 1 GB disk at $0.25/GB/month, for an estimated **$7.25/month** before any usage beyond included allowances. Check Render's current pricing before creating the service. The disk is attached to a single service instance; do not scale this SQLite deployment horizontally. Deployments with a disk can briefly interrupt service while the instance is replaced.

Streamlit Community Cloud is a free alternative for a temporary portfolio preview, but its documentation says local file persistence is not guaranteed. Do not use it for accounts or histories that must survive restarts unless the database is moved to a durable external service.

## Updating the site

Render can deploy later commits pushed to the connected branch. Database files remain on the mounted disk; application code and the model are supplied by the repository. Back up the SQLite database before risky schema changes.

## References

- [Render Blueprints](https://render.com/docs/blueprint-spec)
- [Render persistent disks](https://render.com/docs/disks)
- [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Streamlit storage and database connections](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data)
