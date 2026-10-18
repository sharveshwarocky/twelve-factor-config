from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
from dotenv import dotenv_values

# Default OS env vars for the assigned configuration if not already set in the environment
if "APP_PORT" not in os.environ:
    os.environ["APP_PORT"] = "8935"
if "APP_LOG_LEVEL" not in os.environ:
    os.environ["APP_LOG_LEVEL"] = "info"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/effective-config")

def parse_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ['true', '1', 'yes', 'on']

@app.get("/effective-config")
def get_config(request: Request):
    # 1. Defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }
    
    # 2. YAML
    try:
        with open("config.development.yaml", "r") as f:
            yaml_cfg = yaml.safe_load(f) or {}
            if "port" in yaml_cfg: config["port"] = int(yaml_cfg["port"])
            if "workers" in yaml_cfg: config["workers"] = int(yaml_cfg["workers"])
            if "NUM_WORKERS" in yaml_cfg: config["workers"] = int(yaml_cfg["NUM_WORKERS"])
            if "debug" in yaml_cfg: config["debug"] = parse_bool(yaml_cfg["debug"])
            if "log_level" in yaml_cfg: config["log_level"] = str(yaml_cfg["log_level"])
            if "api_key" in yaml_cfg: config["api_key"] = str(yaml_cfg["api_key"])
    except FileNotFoundError:
        pass

    # 3. .env
    env_cfg = dotenv_values(".env")
    if "APP_PORT" in env_cfg and env_cfg["APP_PORT"] is not None:
        config["port"] = int(env_cfg["APP_PORT"])
    if "APP_DEBUG" in env_cfg and env_cfg["APP_DEBUG"] is not None:
        config["debug"] = parse_bool(env_cfg["APP_DEBUG"])
    if "APP_LOG_LEVEL" in env_cfg and env_cfg["APP_LOG_LEVEL"] is not None:
        config["log_level"] = str(env_cfg["APP_LOG_LEVEL"])
    if "NUM_WORKERS" in env_cfg and env_cfg["NUM_WORKERS"] is not None:
        config["workers"] = int(env_cfg["NUM_WORKERS"])
    if "APP_WORKERS" in env_cfg and env_cfg["APP_WORKERS"] is not None:
        config["workers"] = int(env_cfg["APP_WORKERS"])
    if "APP_API_KEY" in env_cfg and env_cfg["APP_API_KEY"] is not None:
        config["api_key"] = str(env_cfg["APP_API_KEY"])

    # 4. OS Env
    if "APP_PORT" in os.environ:
        config["port"] = int(os.environ["APP_PORT"])
    if "APP_DEBUG" in os.environ:
        config["debug"] = parse_bool(os.environ["APP_DEBUG"])
    if "APP_LOG_LEVEL" in os.environ:
        config["log_level"] = str(os.environ["APP_LOG_LEVEL"])
    if "NUM_WORKERS" in os.environ:
        config["workers"] = int(os.environ["NUM_WORKERS"])
    if "APP_WORKERS" in os.environ:
        config["workers"] = int(os.environ["APP_WORKERS"])
    if "APP_API_KEY" in os.environ:
        config["api_key"] = str(os.environ["APP_API_KEY"])

    # 5. CLI Overrides (Query Params)
    for key, val in request.query_params.multi_items():
        if key == "set":
            if "=" in val:
                k, v = val.split("=", 1)
            else:
                continue
        else:
            k, v = key, val

        if k == "port":
            config["port"] = int(v)
        elif k in ("workers", "NUM_WORKERS", "APP_WORKERS"):
            config["workers"] = int(v)
        elif k in ("debug", "APP_DEBUG"):
            config["debug"] = parse_bool(v)
        elif k in ("log_level", "APP_LOG_LEVEL"):
            config["log_level"] = str(v)
        elif k in ("api_key", "APP_API_KEY"):
            config["api_key"] = str(v)
        else:
            config[k] = v

    config["api_key"] = "****"  # Masking requirement
    return config
