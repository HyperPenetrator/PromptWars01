# DEPLOY TO STREAMLIT CLOUD

## Step 1: Push to GitHub

```bash
cd "/d/Promptwars Virtual"

# If not already initialized
git init
git add .
git commit -m "Initial StadiumFlow AI commit"

# Create new repo on GitHub
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/stadiumflow-ai.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy via Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `YOUR_USERNAME/stadiumflow-ai`
   - Branch: `main`
   - Main file path: `app.py`
5. Click "Deploy"

✅ Your app will be live at: `https://stadiumflow-ai.streamlit.app`

### Configuration (Optional)

Create `.streamlit/secrets.toml` (don't commit to git):
```toml
GEMINI_API_KEY = "your_actual_key_here"
```

Add to `.gitignore`:
```
.streamlit/secrets.toml
```

---

## Step 3: Share the Link!

Your live URL: `https://stadiumflow-ai.streamlit.app`

---

## Method B: Heroku (Alternative)

```bash
# Install Heroku CLI
# Create account at heroku.com

heroku login
heroku create stadiumflow-ai
git push heroku main

# View logs
heroku logs --tail
```

---

## Method C: Docker (For production)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

Deploy to Docker Hub or any cloud provider.

---

## Method D: PythonAnywhere (No Docker needed)

1. Go to PythonAnywhere.com
2. Upload your project
3. Create web app from Python web framework
4. Point to `app.py`
5. Restart app

Live at: `https://your_username.pythonanywhere.com`

