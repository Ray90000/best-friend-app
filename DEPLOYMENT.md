# Google Cloud Deployment Guide (Cloud Run)

This guide explains how to deploy the **Good Friend App** to Google Cloud Run using a single container approach with SQLite persistence.

## Prerequisites
1.  **Google Cloud Project**: Create one in the Google Cloud Console.
2.  **gcloud CLI**: Installed and authenticated (`gcloud auth login`).
3.  **Billing**: Enabled on your project.

## Strategy
*   **Service**: Google Cloud Run (Serverless Container).
*   **Database**: SQLite stored on a **Cloud Run Volume** (Network File System) to ensure data persists between restarts.
*   **Architecture**: Single Docker container serving both the FastAPI backend and the Vue frontend (built as static files).

## Step 1: Enable APIs
Run these commands in your terminal:
```bash
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com
```

## Step 2: Build and Push Docker Image
We will use Cloud Build to build the image and store it in the Container Registry (GCR) or Artifact Registry.

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Build the image (this uses the Dockerfile we created)
gcloud builds submit --tag gcr.io/$PROJECT_ID/good-friend-app .
```

## Step 3: Deploy to Cloud Run with Volume
Since we are using SQLite, we need a persistent volume. Cloud Run supports this via network file systems, but the simplest "native" way currently in preview is using a volume mount, or simply accepting that for a *demo*, data might be lost if we don't use a volume.

**Recommended for Production (Robust):** Use **Cloud SQL** (PostgreSQL).
**Recommended for MVP (Simple):** Use **Cloud Storage FUSE** or just deploy without persistence first to test.

*For this guide, we will deploy a standard stateless container first. Note that data will reset if the container stops.*

```bash
gcloud run deploy good-friend-app \
    --image gcr.io/$PROJECT_ID/good-friend-app \
    --platform managed \
    --region asia-east1 \
    --allow-unauthenticated
```

### How to Persist SQLite Data?
To keep your data, you have two main options on Cloud Run:

**Option A: Cloud Storage FUSE (Cheapest/Easiest for SQLite)**
1. Create a Storage Bucket: `gsutil mb gs://good-friend-db-$PROJECT_ID`
2. Deploy with volume mount:
```bash
gcloud run deploy good-friend-app \
    --image gcr.io/$PROJECT_ID/good-friend-app \
    --execution-environment gen2 \
    --allow-unauthenticated \
    --add-volume name=db_volume,type=cloud-storage,bucket=good-friend-db-$PROJECT_ID \
    --add-volume-mount volume=db_volume,mount-path=/data
```
*Note: We updated `database.py` to look for the DB at `/data/good_friend.db` via the `DB_PATH` env var.*

**Option B: Cloud SQL (Best Practice)**
1. Create a Cloud SQL instance (PostgreSQL).
2. Update the backend code to use `SQLAlchemy` and connect to Postgres instead of SQLite.

## Summary
1.  We created a `Dockerfile` that bundles Frontend + Backend.
2.  We updated `main.py` to serve the frontend static files.
3.  We updated `database.py` to support a custom DB path.
4.  You can deploy using the `gcloud run deploy` commands above.
