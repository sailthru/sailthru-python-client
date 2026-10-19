"""Build and smoke-test both Python distributions without publishing them."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outdir", type=Path,
        help="Keep the validated distributions in this directory for manual publication.",
    )
    options = parser.parse_args()
    destination = options.outdir.resolve() if options.outdir else None

    with tempfile.TemporaryDirectory(prefix="sailthru-client-smoke-") as temporary:
        directory = Path(temporary)
        artifacts = directory / "dist"
        # Build's default flow builds the wheel from the sdist, checking its contents too.
        subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(artifacts)],
            cwd=ROOT, check=True, timeout=180,
        )
        wheels = list(artifacts.glob("*.whl"))
        sources = list(artifacts.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sources) != 1:
            raise RuntimeError("Expected one wheel and one source distribution")

        for index, artifact in enumerate(wheels + sources):
            environment = directory / f"install-{index}"
            venv.EnvBuilder(with_pip=True).create(environment)
            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            subprocess.run(
                [str(python), "-I", "-m", "pip", "install",
                 "--disable-pip-version-check", str(artifact)],
                cwd=directory, check=True, timeout=180,
            )
            # -I prevents checkout paths, user site packages, and PYTHONPATH from masking bugs.
            subprocess.run(
                [str(python), "-I", str(ROOT / "test" / "smoke-package.py")],
                cwd=directory, check=True, timeout=30,
            )
            print(f"Package smoke check passed: {artifact.name}", flush=True)

        if destination:
            destination.mkdir(parents=True, exist_ok=True)
            for artifact in wheels + sources:
                shutil.copy2(artifact, destination / artifact.name)
            print(f"Validated distributions saved to {destination}", flush=True)


if __name__ == "__main__":
    main()
