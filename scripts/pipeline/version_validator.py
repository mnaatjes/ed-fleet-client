"""Version validator resolving pinned ed-models dependency in pyproject.toml."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class VersionValidationResult:
    """Result of dependency version verification."""

    pinned_rev: str
    installed_version: str
    is_valid: bool
    details: str


class VersionValidator:
    """Validates installed ed-models package version against pyproject.toml pin."""

    def __init__(self, pyproject_path: Path | str = "pyproject.toml") -> None:
        self.pyproject_path = Path(pyproject_path)

    def extract_pinned_rev(self) -> str:
        """Extract pinned git revision tag or version from pyproject.toml."""
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"Cannot find pyproject.toml at: {self.pyproject_path}")

        with open(self.pyproject_path, "rb") as f:
            data: dict[str, Any] = tomllib.load(f)

        tool_uv = data.get("tool", {}).get("uv", {})
        sources = tool_uv.get("sources", {})
        ed_models_source = sources.get("ed-models", {})

        rev = cast(str, ed_models_source.get("rev", ""))
        if not rev:
            # Fallback to dependencies list if not found in uv sources
            deps = data.get("project", {}).get("dependencies", [])
            for dep in deps:
                if "ed-models" in dep:
                    rev = str(dep)
                    break

        if not rev:
            raise ValueError(f"Could not resolve ed-models pinning in {self.pyproject_path}")
        return rev

    def get_installed_version(self) -> str:
        """Inspect installed ed-models module version."""
        try:
            import ed_models

            return str(getattr(ed_models, "__version__", "unknown"))
        except ImportError as e:
            raise ImportError(
                "ed_models is not installed in the current Python environment."
            ) from e

    def validate(self) -> VersionValidationResult:
        """Validate that installed ed-models version matches pyproject.toml pin."""
        pinned = self.extract_pinned_rev()
        installed = self.get_installed_version()

        # Clean tags like 'v0.2.1' -> '0.2.1'
        norm_pinned = pinned.lstrip("v")
        norm_installed = installed.lstrip("v")

        is_valid = norm_pinned == norm_installed
        details = (
            f"Pinned revision: '{pinned}' matches installed ed-models '{installed}'"
            if is_valid
            else (
                f"Version mismatch: pyproject.toml requires '{pinned}', "
                f"but installed ed-models is '{installed}'."
            )
        )

        return VersionValidationResult(
            pinned_rev=pinned,
            installed_version=installed,
            is_valid=is_valid,
            details=details,
        )
