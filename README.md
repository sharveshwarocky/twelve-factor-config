# 12-Factor Config Precedence API

FastAPI service that resolves configuration values following 12-Factor precedence rules:

1. **Defaults** (baseline fallback values)
2. **YAML file** (`config.development.yaml`)
3. **.env file**
4. **OS Environment Variables**
5. **CLI / Request Query Parameters** (`?set=key=val`)

Sensory values like `api_key` are masked in output (`****`).

---

## 🚀 One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sharveshwarocky/twelve-factor-config)

### Deploying Manually:
- **Render**: New + -> Web Service -> Connect `sharveshwarocky/twelve-factor-config`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Railway**: New Project -> Deploy from GitHub repo -> Select `sharveshwarocky/twelve-factor-config`

---

## 📡 Live Endpoint

```
GET /effective-config
```

Example query override:
```
GET /effective-config?set=port=9000&set=debug=true
```

