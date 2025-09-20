# 🚀 Quick Deployment Guide

## Deploy to Vercel in 3 Steps

### Step 1: Fork & Clone
```bash
# Fork this repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/niflheim-x-demo.git
cd niflheim-x-demo
```

### Step 2: Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/niflheim-x-demo)

**OR** use Vercel CLI:
```bash
npm i -g vercel
vercel --prod
```

### Step 3: Set Environment Variable
In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `GEMINI_API_KEY` = `your_gemini_api_key_here`
4. Redeploy the project

## Get Your Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy it to your Vercel environment variables

## 🎉 Done!
Your Niflheim-X demo will be live at: `https://your-project.vercel.app`

---

**Need help?** Check the main [README.md](README.md) for detailed instructions.