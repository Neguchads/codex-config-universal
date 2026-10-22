import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("config_tool", ROOT / "scripts" / "config.py")
config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(config)


def directory_link(link, target):
    if os.name == "nt":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if result.returncode:
            raise RuntimeError("Não foi possível criar junction temporária para regressão.")
    else:
        link.symlink_to(target, target_is_directory=True)


class ConfigTests(unittest.TestCase):
    def test_safe_defaults(self):
        config.validate_defaults(ROOT / "templates" / "config.toml")

    def test_rejects_unsafe_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text('approval_policy = "never"\nsandbox_mode = "danger-full-access"\n')
            with self.assertRaises(ValueError):
                config.validate_defaults(path)

    def test_privacy_examples_are_rejected_without_echoing_values(self):
        samples = [
            "C:" + "\\Users\\Example\\file.txt",
            "person" + "@example.test",
            "192." + "168.5.6",
            "12345678-1234-" + "1234-1234-123456789abc",
            "-----BEGIN " + "PRIVATE KEY-----",
        ]
        for sample in samples:
            with self.subTest(category=samples.index(sample)):
                problems = config.privacy_findings("fixture.md", sample)
                self.assertTrue(problems)
                self.assertNotIn(sample, " ".join(problems))

    def test_plain_documentation_is_accepted(self):
        self.assertEqual(config.privacy_findings("README.md", "Use $HOME/.codex e https://learn.chatgpt.com"), [])

    def test_manifest_rejects_traversal_and_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for entries in [["../private.md"], ["safe.md", "safe.md"], ["/private.md"]]:
                (root / "public-manifest.json").write_text(json.dumps(entries))
                with self.assertRaises(ValueError):
                    config.public_files(root)

    def test_unlisted_file_blocks_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "public-manifest.json").write_text('["public-manifest.json"]')
            (root / "personal.txt").write_text("local only")
            self.assertTrue(config.audit(root))

    def test_missing_gitleaks_is_a_failure(self):
        with self.assertRaises(RuntimeError):
            config.run_gitleaks(ROOT, executable="missing-security-scanner-for-test")

    def test_git_identity_rejects_personal_email_and_accepts_noreply(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            environment = os.environ.copy()
            environment.update({"GIT_AUTHOR_NAME": "fixture", "GIT_COMMITTER_NAME": "fixture"})
            public_email = "fixture" + "@users.noreply.github.com"
            environment.update({"GIT_AUTHOR_EMAIL": public_email, "GIT_COMMITTER_EMAIL": public_email})
            subprocess.run(["git", "-C", str(root), "commit", "--allow-empty", "-m", "test: public identity"], env=environment, check=True, capture_output=True)
            config.audit_git_identity(root)
            private_email = "fixture" + "@example.test"
            environment.update({"GIT_AUTHOR_EMAIL": private_email, "GIT_COMMITTER_EMAIL": private_email})
            subprocess.run(["git", "-C", str(root), "commit", "--allow-empty", "-m", "test: private identity"], env=environment, check=True, capture_output=True)
            with self.assertRaises(ValueError) as caught:
                config.audit_git_identity(root)
            self.assertNotIn(private_email, str(caught.exception))

    def test_real_gitleaks_rejects_synthetic_secret_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic = "".join(["ghp_", "Ab3cD4eF5gH6iJ7kL8mN9pQ0rS1tU2vW3xY4"])
            (root / "fixture.txt").write_text("token = " + synthetic)
            with self.assertRaises(RuntimeError) as caught:
                config.run_gitleaks(root)
            self.assertNotIn(synthetic, str(caught.exception))

    def test_local_codex_loads_isolated_config_without_inference(self):
        binary = shutil.which("codex")
        self.assertIsNotNone(binary, "Gate completo requer Codex CLI instalado.")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "codex"
            config.install(ROOT, target)
            environment = os.environ.copy()
            environment["CODEX_HOME"] = str(target)
            result = subprocess.run([binary, "features", "list"], env=environment, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, "Codex não conseguiu carregar os defaults isolados.")

    def test_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "codex"
            config.install(ROOT, target)
            first = {p.name: p.read_bytes() for p in target.iterdir()}
            config.install(ROOT, target)
            self.assertEqual(first, {p.name: p.read_bytes() for p in target.iterdir()})
            self.assertEqual(set(first), {"AGENTS.md", "config.toml"})

    def test_install_preserves_existing_config_without_partial_write(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            current = target / "config.toml"
            current.write_text("# private configuration\n")
            with self.assertRaises(FileExistsError):
                config.install(ROOT, target)
            self.assertEqual(current.read_text(), "# private configuration\n")
            self.assertFalse((target / "AGENTS.md").exists())

    def test_export_contains_only_manifest_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "release"
            config.export(ROOT, target)
            files = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
            self.assertEqual(files, set(config.public_files(ROOT)))
            with self.assertRaises(FileExistsError):
                config.export(ROOT, target)

    def test_export_accepts_documented_relative_sibling_target(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as directory:
            target = Path(directory) / "release"
            relative = Path(os.path.relpath(target, Path.cwd()))
            config.export(ROOT, relative)
            self.assertEqual(set(config.public_files(ROOT)), set(config.public_files(target)))

    def test_manifest_rejects_source_junction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            (outside / "fixture.md").write_text("private fixture")
            source = root / "public"
            source.mkdir()
            directory_link(source / "linked", outside)
            (source / "public-manifest.json").write_text('["public-manifest.json", "linked/fixture.md"]')
            with self.assertRaises(ValueError):
                config.public_files(source)

    def test_install_rejects_destination_junction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            target = root / "linked"
            directory_link(target, outside)
            with self.assertRaises(ValueError):
                config.install(ROOT, target)
            self.assertEqual(list(outside.iterdir()), [])

    def test_install_rejects_existing_and_broken_leaf_links_before_writing(self):
        for broken in (False, True):
            with self.subTest(broken=broken), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                outside = root / "outside"
                if not broken:
                    outside.mkdir()
                target = root / "codex"
                target.mkdir()
                directory_link(target / "config.toml", outside)
                with self.assertRaises(ValueError):
                    config.install(ROOT, target)
                self.assertFalse((target / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
