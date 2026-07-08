"""Loads config.yaml into a plain dict. Single source of truth for settings."""
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_config(path: str | None = None) -> dict:
    cfg_path = pathlib.Path(path) if path else ROOT / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
