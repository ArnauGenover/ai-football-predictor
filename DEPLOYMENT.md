# Deployment Guide

## Architecture

```
GitHub Repo
  ├── Backend  → Render (Docker, free tier)
  ├── Frontend → Vercel (Next.js, free tier)
  ├── Database → Neon (PostgreSQL, free tier)
  └── Collector → GitHub Actions (cron, free)
```

---

## 1. Database (Neon) — Already Done

Your Neon database is already set up and populated. No changes needed.

Connection string format:
```
postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require   # async (backend)
postgresql://USER:PASS@HOST/DB?sslmode=require        # sync  (collector/ml)
```

---

## 2. Backend → Render

### Step-by-step

1. Go to [render.com](https://render.com) and sign in with GitHub.

2. Click **New → Web Service**.

3. Connect your GitHub repository (`ML_Project_Football`).

4. Configure the service:

   | Setting | Value |
   |---|---|
   | **Name** | `football-analytics-api` |
   | **Region** | Frankfurt (EU) or closest to your Neon region |
   | **Branch** | `main` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Docker` |
   | **Plan** | Free |

5. Add the environment variable:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | `postgresql+asyncpg://neondb_owner:npg_Kg2hSdyCPe5X@ep-nameless-credit-alqjoi9o-pooler.c-3.eu-central-1.aws.neon.tech/neondb?ssl=require` |
   | `ENVIRONMENT` | `production` |

6. Click **Create Web Service**. Render will build the Docker image and deploy.

7. Once deployed, you'll get a URL like:
   ```
   https://football-analytics-api.onrender.com
   ```

8. Verify it works:
   ```
   https://football-analytics-api.onrender.com/health
   ```

> **Note:** Render free tier spins down after 15 minutes of inactivity.
> The GitHub Actions collector pings `/health` after every run to keep it warm.

---

## 3. Frontend → Vercel

### Step-by-step

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.

2. Click **Add New → Project**.

3. Import your GitHub repository (`ML_Project_Football`).

4. Configure the project:

   | Setting | Value |
   |---|---|
   | **Framework Preset** | Next.js |
   | **Root Directory** | `frontend` |

5. Add the environment variable:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://football-analytics-api.onrender.com` |

   (Replace with your actual Render URL from step 2.7)

6. Click **Deploy**. Vercel will build and deploy the Next.js app.

7. You'll get a URL like:
   ```
   https://ml-project-football.vercel.app
   ```

---

## 4. GitHub Actions (Collector)

The collector workflow is already configured in `.github/workflows/collector.yml`.

### Add repository secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions** → **New repository secret**:

| Secret | Value |
|---|---|
| `DATABASE_URL_SYNC` | `postgresql://neondb_owner:npg_Kg2hSdyCPe5X@ep-nameless-credit-alqjoi9o-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require` |
| `API_FOOTBALL_KEY` | `d79a7e37df4765f8a2d8b6cf0a7f1692` |
| `TARGET_LEAGUE_IDS` | `39,140,135,78,61` |
| `CURRENT_SEASON` | `2025` |
| `FALLBACK_SEASON` | `2024` |
| `HF_SPACE_URL` | `https://football-analytics-api.onrender.com` |

The workflow runs twice daily (08:00 and 20:00 UTC) and pings the Render backend to keep it awake.

---

## 5. Verify Everything

After all three services are deployed:

1. **Backend health:**
   ```
   curl https://football-analytics-api.onrender.com/health
   ```

2. **Backend data:**
   ```
   curl https://football-analytics-api.onrender.com/teams?limit=5
   ```

3. **Frontend:** Open your Vercel URL in a browser.

4. **Trigger a manual collector run:**
   Go to GitHub → Actions → "Football Data Collector" → Run workflow.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Frontend shows "Failed to load predictions" | Check `NEXT_PUBLIC_API_URL` in Vercel env vars points to your Render URL |
| Backend returns 500 on Render | Check the `DATABASE_URL` env var — must use `postgresql+asyncpg://` with `?ssl=require` |
| Render service sleeping | Trigger the GitHub Actions workflow manually, or wait for the next cron run |
| Collector fails in GitHub Actions | Check Actions logs; verify all repository secrets are set correctly |
| Empty predictions | Free API plan only covers seasons 2022-2024 (all finished). Upgrade for live data |
