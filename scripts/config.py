"""Instala e exporta apenas os arquivos públicos declarados."""

import argparse
import ast
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tomllib

if sys.version_info < (3, 12):
    raise RuntimeError("Python 3.12 ou superior é obrigatório para validar junctions no Windows.")

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", "__pycache__", "dist"}
PRIVATE_PATTERNS = {
    "absolute-local-path": r"(?i)(?:\b[a-z]:[\\/]|/(?:Users|home)/[^/\s]+)",
    "email-address": r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
    "private-network": r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b",
    "session-identifier": r"(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b",
    "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}


def public_files(root):
    entries = json.loads((root / "public-manifest.json").read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries or any(not isinstance(p, str) for p in entries):
        raise ValueError("Manifesto precisa ser uma lista de arquivos.")
    if len(entries) != len(set(entries)):
        raise ValueError("Manifesto contém duplicatas.")
    for entry in entries:
        path = PurePosixPath(entry)
        if path.is_absolute() or ".." in path.parts or "\\" in entry or ":" in entry:
            raise ValueError("Caminho inválido no manifesto.")
        if path.as_posix() != entry or any(part in IGNORED for part in path.parts):
            raise ValueError("Caminho não canônico no manifesto.")
        full = root / entry
        for parent in (full, *full.parents):
            if parent == root.parent:
                break
            if parent.is_symlink() or parent.is_junction():
                raise ValueError("Links de filesystem não são exportáveis.")
        if not full.is_file():
            raise ValueError("Arquivo declarado ausente.")
    if "public-manifest.json" not in entries:
        raise ValueError("Manifesto deve declarar a si próprio.")
    return entries


def privacy_findings(name, content):
    return [f"{name}: {category}" for category, pattern in PRIVATE_PATTERNS.items() if re.search(pattern, content)]


def validate_defaults(path):
    settings = tomllib.loads(path.read_text(encoding="utf-8"))
    expected = {
        "approval_policy": "on-request",
        "sandbox_mode": "workspace-write",
        "sandbox_workspace_write": {"network_access": False},
    }
    if settings != expected:
        raise ValueError("Defaults devem preservar aprovação, sandbox e rede restrita.")


def audit(root):
    try:
        entries = public_files(root)
    except (ValueError, OSError) as error:
        return [f"manifest: {type(error).__name__}"]
    problems = []
    actual = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink() or path.is_junction():
            problems.append("filesystem: link não permitido")
        elif path.is_file():
            actual.add(relative.as_posix())
    if actual != set(entries):
        problems.append("manifest: arquivos extras ou ausentes; publicação bloqueada")
    for entry in entries:
        try:
            content = (root / entry).read_text(encoding="utf-8")
        except UnicodeError:
            problems.append(f"{entry}: arquivo não UTF-8")
            continue
        problems.extend(privacy_findings(entry, content))
        if re.search(r"(?m)^(?:<{7}|={7}|>{7})(?: |$)", content):
            problems.append(f"{entry}: conflito de merge")
        if entry.endswith(".py"):
            try:
                ast.parse(content, filename=entry)
            except SyntaxError:
                problems.append(f"{entry}: sintaxe Python inválida")
        if entry.endswith(".md"):
            prose = re.sub(r"(?ms)^```.*?^```[^\n]*", "", content)
            for target in re.findall(r"\]\(([^\s)]+)\)", prose):
                if "://" in target or target.startswith("#"):
                    continue
                linked = (PurePosixPath(entry).parent / target.split("#")[0]).as_posix()
                if linked not in entries:
                    problems.append(f"{entry}: link local fora do manifesto")
    try:
        validate_defaults(root / "templates" / "config.toml")
    except (ValueError, OSError):
        problems.append("config: defaults inválidos")
    return problems


def run_gitleaks(root, executable="gitleaks"):
    binary = shutil.which(executable)
    if not binary:
        raise RuntimeError("Gitleaks obrigatório. Instale-o antes de verificar ou exportar.")
    commands = [[binary, "dir", str(root), "--redact", "--no-banner", "--log-level", "error"]]
    history = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True)
    if history.returncode == 0:
        commands.append([binary, "git", str(root), "--redact", "--no-banner", "--log-level", "error"])
    for command in commands:
        result = subprocess.run(command, capture_output=True)
        if result.returncode:
            raise RuntimeError("Gitleaks bloqueou a operação; conteúdo dos achados omitido.")


def audit_git_identity(root):
    history = subprocess.run(["git", "-C", str(root), "log", "--all", "--format=%ae%n%ce"], capture_output=True, text=True)
    if history.returncode:
        return
    emails = history.stdout.splitlines()
    if any(not email.endswith(("@users.noreply.github.com", "@github.com")) for email in emails):
        raise ValueError("Metadados Git contêm e-mail fora do padrão público noreply.")


def require_safe(root):
    problems = audit(root)
    if problems:
        raise ValueError("\n".join(problems))
    audit_git_identity(root)
    run_gitleaks(root)


def safe_target(target):
    original = target.expanduser().absolute()
    for parent in (original, *original.parents):
        if parent.is_symlink() or parent.is_junction():
            raise ValueError("Destino via link não permitido.")
    return Path(os.path.abspath(original))


def install(root, target):
    require_safe(root)
    target = safe_target(target)
    pairs = [(root / "templates" / name, target / name) for name in ("AGENTS.md", "config.toml")]
    for source, destination in pairs:
        if destination.is_symlink() or destination.is_junction():
            raise ValueError("Arquivo de destino via link não permitido.")
        if destination.exists() and (not destination.is_file() or destination.read_bytes() != source.read_bytes()):
            raise FileExistsError("Configuração existente difere; faça integração manual antes de instalar.")
    target.mkdir(parents=True, exist_ok=True)
    for source, destination in pairs:
        if not destination.exists():
            with destination.open("xb") as output:
                output.write(source.read_bytes())


def export(root, target):
    require_safe(root)
    target = safe_target(target)
    if target.exists():
        raise FileExistsError("Destino da exportação já existe; escolha uma pasta nova.")
    if target == root or root in target.parents:
        raise ValueError("Exportação deve ficar fora do repositório.")
    target.mkdir(parents=True)
    for entry in public_files(root):
        destination = target / entry
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / entry, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify", "install", "export"])
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            require_safe(ROOT)
        elif args.target is None:
            parser.error("install/export exigem --target explícito")
        elif args.command == "install":
            install(ROOT, args.target)
        else:
            export(ROOT, args.target)
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Verificação concluída." if args.command == "verify" else "Operação concluída.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
