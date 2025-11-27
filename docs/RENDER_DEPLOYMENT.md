# 🚀 Deploying to Render.com

Follow these simple steps to deploy your FastAPI application to Render.

## 1. Push to GitHub
First, make sure all your latest changes (including the new `render.yaml`) are pushed to your GitHub repository.

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## 2. Create Web Service on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub repository (`ai-mcq-meme-generator`).
4.  Render should automatically detect the `render.yaml` file and configure the service.
    *   **Runtime:** Python 3
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## 3. Configure Environment Variables
In the Render Dashboard for your new service, go to the **Environment** tab and add the following variables. 
*(You can copy these from your local `.env` file or PythonAnywhere config)*

| Key | Value (Example) |
| :--- | :--- |
| `PYTHON_VERSION` | `3.10.12` |
| `GOOGLE_CLIENT_ID` | `your_google_client_id` |
| `GOOGLE_CLIENT_SECRET` | `your_google_client_secret` |
| `GROQ_API_KEY` | `gsk_...` |
| `REPLICATE_API_TOKEN` | `r8_...` |
| `HF_TOKEN` | `hf_...` |
| `APP_BASE_URL` | `https://your-app-name.onrender.com` (You'll get this URL after creating the service) |
| `DATABASE_URL` | `sqlite:///./backend/mcq_meme_v2.db` (Or use Render's Postgres if you want persistence) |

## 4. Deploy!
Click **Create Web Service**. Render will start building your app. It might take a few minutes.
Once it's live, you will see a URL like `https://ai-mcq-meme-generator.onrender.com`.

## 5. Final Google OAuth Update
Once you have your Render URL:
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Update your **Authorized JavaScript Origins** to: `https://your-app-name.onrender.com`
3.  Update your **Authorized Redirect URIs** to: `https://your-app-name.onrender.com/api/auth/callback/google`

That's it! Your app should now run smoothly without timeouts. 
