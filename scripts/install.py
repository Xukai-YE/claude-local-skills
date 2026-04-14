#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import pathlib
import shutil


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def claude_home_from_arg(value: str | None) -> pathlib.Path:
    if value:
        return pathlib.Path(value).expanduser().resolve()
    env_value = os.environ.get("CLAUDE_HOME")
    if env_value:
        return pathlib.Path(env_value).expanduser().resolve()
    return (pathlib.Path.home() / ".claude").resolve()


def skill_names() -> list[str]:
    source_root = repo_root() / "skills"
    return sorted(path.name for path in source_root.iterdir() if path.is_dir())


def install_skills(destination_root: pathlib.Path) -> list[pathlib.Path]:
    source_root = repo_root() / "skills"
    target_root = destination_root / "skills"
    target_root.mkdir(parents=True, exist_ok=True)
    installed: list[pathlib.Path] = []
    for name in skill_names():
        src = source_root / name
        dst = target_root / name
        shutil.copytree(src, dst, dirs_exist_ok=True)
        installed.append(dst)
    return installed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-home", default=None)
    args = parser.parse_args()

    claude_home = claude_home_from_arg(args.claude_home)
    installed = install_skills(claude_home)
    print("Installed Claude skill directories:")
    for path in installed:
        print(f"- {path}")


if __name__ == "__main__":
    main()
