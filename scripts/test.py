"""Portão local sem dependências Python externas."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
    if result.returncode:
        return result.returncode
    result = subprocess.run([sys.executable, "scripts/config.py", "verify"], cwd=ROOT)
    if result.returncode:
        return result.returncode
    spec = importlib.util.spec_from_file_location("config_tool", ROOT / "scripts" / "config.py")
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    with tempfile.TemporaryDirectory() as directory:
        release = Path(directory) / "public"
        config.export(ROOT, release)
        problems = config.audit(release)
        if problems:
            print("Artefato exportado inválido.", file=sys.stderr)
            return 1
        config.run_gitleaks(release)
    print("Testes, sintaxe, privacidade, segredos e exportação passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
