import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/pull_pvbench_images.sh"


class ImageMigrationTest(unittest.TestCase):
    def test_pulls_and_retags_all_verified_base_images(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "image migration script is missing")

        projects = [
            "cpython",
            "exiv2",
            "hdf5",
            "hermes",
            "htslib",
            "icu",
            "jasper",
            "jq",
            "libtiff",
            "libxml2",
            "llvm",
            "mruby",
            "pcapplusplus",
            "php",
            "quickjs",
            "simdjson",
            "v8",
            "vim",
            "wabt",
            "wireshark",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            call_log = temporary_path / "docker-calls.log"
            fake_docker = temporary_path / "docker"
            fake_docker.write_text(
                "#!/bin/sh\n"
                'printf \'%s\\n\' "$*" >> "$DOCKER_CALL_LOG"\n'
            )
            fake_docker.chmod(0o755)

            environment = os.environ.copy()
            environment.update(
                {
                    "DOCKER_BIN": str(fake_docker),
                    "DOCKER_CALL_LOG": str(call_log),
                }
            )
            subprocess.run([str(SCRIPT)], env=environment, check=True)

            expected_calls = []
            for project in projects:
                remote_image = (
                    "ghcr.io/tnikko/pvbench-env:"
                    f"{project}-base-pvbench-green-20260916"
                )
                expected_calls.extend(
                    [
                        f"pull {remote_image}",
                        f"tag {remote_image} pvbench-{project}-base:latest",
                    ]
                )

            self.assertEqual(call_log.read_text().splitlines(), expected_calls)


if __name__ == "__main__":
    unittest.main()
