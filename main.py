from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
from dotenv import dotenv_values

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/effective-config")

def parse_bool(v):
    if isinstance(v, bool): return v
    return str(v).lower() in ['true', '1', 'yes', 'on']

@app.get("/effective-config")
def get_config(request: Request):
    # 1. Defaults
    config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
    
    # 2. YAML
    try:
        with open("config.development.yaml", "r") as f:
            yaml_cfg = yaml.safe_load(f) or {}
            for k, v in yaml_cfg.items(): config[k] = v
    except FileNotFoundError: pass

    # 3. .env
    env_cfg = dotenv_values(".env")
    if "APP_PORT" in env_cfg: config["port"] = int(env_cfg["APP_PORT"])
    if "APP_DEBUG" in env_cfg: config["debug"] = parse_bool(env_cfg["APP_DEBUG"])
    if "APP_LOG_LEVEL" in env_cfg: config["log_level"] = env_cfg["APP_LOG_LEVEL"]
    if "NUM_WORKERS" in env_cfg: config["workers"] = int(env_cfg["NUM_WORKERS"])

    # 4. OS Env
    if "APP_PORT" in os.environ: config["port"] = int(os.environ["APP_PORT"])
    if "APP_DEBUG" in os.environ: config["debug"] = parse_bool(os.environ["APP_DEBUG"])
    if "APP_LOG_LEVEL" in os.environ: config["log_level"] = os.environ["APP_LOG_LEVEL"]
    if "NUM_WORKERS" in os.environ: config["workers"] = int(os.environ["NUM_WORKERS"])

    # 5. CLI Overrides (Query Params)
    for key, val in request.query_params.multi_items():
        if key == "set":
            k, v = val.split("=", 1)
            if k == "port": config["port"] = int(v)
            elif k == "workers": config["workers"] = int(v)
            elif k == "debug": config["debug"] = parse_bool(v)
            else: config[k] = v

    config["api_key"] = "****" # Masking requirement
    return config

