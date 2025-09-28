# 🚀 Deployment Guide for Streamlit Cloud

## Quick Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository: `guitar-agent`
   - Set main file path: `app.py`
   - Add your OpenAI API key in the secrets section

3. **Configure Secrets:**
   In Streamlit Cloud dashboard, go to **Settings > Secrets** and add:
   ```toml
   OPENAI_KEY = "your_actual_openai_api_key_here"
   ```

4. **Domain Name:**
   Your app is now deployed at: `https://findmeaguitarpls.streamlit.app`
   
   To get a custom domain like `findmyguitarplease`:
   - The subdomain is automatically generated from your app name
   - You can customize it in the Streamlit Cloud settings
   - Available domains: `findmyguitarplease.streamlit.app`, `guitar-finder.streamlit.app`, etc.

## Files Ready for Deployment:
- ✅ `requirements.txt` - All dependencies listed
- ✅ `app.py` - Main application file
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `src/config.py` - Handles both local .env and Streamlit secrets
- ✅ `pic.png` - Main image (centered)
- ✅ `.gitignore` - Excludes sensitive files

## Environment Variables:
- `OPENAI_KEY` - Required for AI functionality

## Notes:
- The app uses mock guitar data for reliable performance
- Live web scraping is disabled to avoid rate limiting
- All paths are relative for cloud deployment compatibility