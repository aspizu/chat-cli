import importlib.util
import os
from pathlib import Path
from typing import Protocol, cast

import yaml


class PluginProtocol(Protocol):
    async def plugin(self, input: str) -> str:
        raise NotImplementedError


async def load(path: str) -> PluginProtocol:
    if not Path(path).is_absolute():
        path = os.path.join(os.path.dirname(__file__), path)
    if path.startswith("~"):
        path = Path(path).expanduser().as_posix()
    if not path.endswith(".py"):
        path = path + ".py"
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load plugin from {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        raise ImportError(str(e))
    return cast(PluginProtocol, module)


def parse_config(config: str) -> dict[str, object]:
    result = yaml.safe_load(f"{{{config}}}")
    if isinstance(result, dict) and all(isinstance(key, str) for key in result.keys()):
        return result
    raise ValueError("Plugin configuration is invalid.")
