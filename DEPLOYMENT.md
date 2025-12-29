# Deployment Guide

## Supabase Database Setup

### Step 1: Create Supabase Project

1. Go to https://supabase.com and sign up (free)
2. Click "New Project"
3. Fill in:
   - **Name**: trivia-app (or your choice)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait ~2 minutes for setup to complete

### Step 2: Get Connection String

1. Go to **Project Settings** → **Database**
2. Scroll to **Connection string** section
3. Select **URI** tab
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you created

### Step 3: Deploy to Render

1. **Push code to GitHub** (if not already done)

2. **Create Web Service on Render:**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `trivia` repository

3. **Configure Service:**
   - **Name**: trivia-backend (or your choice)
   - **Environment**: Python 3
   - **Python Version**: **IMPORTANT** - Set to Python 3.11 in Render settings (Advanced → Python Version)
     - Or Render will automatically use `runtime.txt` which specifies Python 3.11.9
     - Python 3.13 doesn't have pre-built wheels for pydantic-core yet
   - **Build Command**: 
     ```bash
     chmod +x build.sh && ./build.sh
     ```
     OR manually (if build script has issues):
     ```bash
     export CARGO_HOME=/tmp/cargo && export RUSTUP_HOME=/tmp/rustup && export CARGO_TARGET_DIR=/tmp/cargo-target && mkdir -p /tmp/cargo /tmp/rustup /tmp/cargo-target && pip install --upgrade pip && pip install -r requirements.txt
     ```
     Note: The build script handles Rust/Cargo setup for pydantic-core compilation. Python 3.11 is required to avoid compilation.
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variable:**
   - Go to **Environment** section
   - Click "Add Environment Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: Paste your Supabase connection string
   - Click "Save Changes"

5. **Add OpenAI API Key:**
   - Add another environment variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key

6. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Wait for deployment to complete (~5 minutes)

### Step 4: Verify Deployment

1. Check the logs in Render dashboard
2. Look for: "Database tables initialized successfully"
3. Test the API endpoint: `https://your-app.onrender.com/`
4. Should return: `{"status": "ok", "message": "Trivia API is running"}`

## Migration from JSON (Optional)

If you have existing quiz history in `data/quiz_history.json`:

1. **Set DATABASE_URL locally:**
   ```bash
   export DATABASE_URL="postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres"
   ```

2. **Run migration script:**
   ```bash
   python migrate_to_postgres.py
   ```

3. **Verify migration:**
   - Check Supabase dashboard → Table Editor → `quiz_attempts`
   - Should see all your quiz attempts

## Local Development

For local development, the app automatically uses SQLite if `DATABASE_URL` is not set:

```bash
# No DATABASE_URL needed for local dev
uvicorn backend.main:app --reload
```

The SQLite database will be created at `data/trivia.db` automatically.

## Troubleshooting

### Database Connection Errors

**Error**: "could not connect to server"
- Check that `DATABASE_URL` is set correctly in Render
- Verify Supabase project is active
- Check firewall settings in Supabase

**Error**: "relation 'quiz_attempts' does not exist"
- Tables are created automatically on first run
- Check Render logs for initialization messages
- Manually trigger by restarting the service

### Migration Issues

**Error**: "duplicate key value"
- Migration script skips duplicates automatically
- Safe to run multiple times

**Error**: "JSON file not found"
- This is normal if you're starting fresh
- Migration will be skipped

## Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Production | Supabase PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |

## Cost

- **Supabase Free Tier**: 500MB database, 2GB bandwidth (perfect for MVP)
- **Render Free Tier**: 750 hours/month (enough for most use cases)
- **Total**: $0/month for MVP scale

## Next Steps

1. ✅ Database setup complete
2. ✅ Deployed to Render
3. 🔄 Update frontend `API_BASE_URL` to point to Render URL
4. 🚀 Deploy frontend (or serve from FastAPI)

