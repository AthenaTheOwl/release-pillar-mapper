from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


_IMPL_ROOT = Path(__file__).resolve().parents[1] / "src" / "release_pillar_mapper"
_MODULE_CACHE: dict[str, ModuleType] = {}


def load_impl(module_name: str) -> ModuleType:
    cached = _MODULE_CACHE.get(module_name)
    if cached is not None:
        return cached

    module_path = _IMPL_ROOT / f"{module_name}.py"
    spec_name = f"_release_pillar_mapper_src_{module_name}"
    spec = importlib.util.spec_from_file_location(spec_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load release_pillar_mapper implementation module {module_name!r}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec_name, None)
        raise

    _MODULE_CACHE[module_name] = module
    return module


def export_names(module_name: str, target_globals: dict[str, object], names: tuple[str, ...]) -> None:
    module = load_impl(module_name)
    for name in names:
        target_globals[name] = getattr(module, name)

