import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkImageContractsTest(unittest.TestCase):
    def test_wireshark_image_installs_qt6_core5compat(self) -> None:
        dockerfile = (ROOT / "vuln/wireshark/common/Dockerfile").read_text()

        self.assertIn("qt6-5compat-dev", dockerfile)

    def test_v8_smoke_case_retries_transient_ninja_failures(self) -> None:
        build_script = (
            ROOT / "vuln/v8/v8-regress-1309769/build.sh"
        ).read_text()

        self.assertIn("max_retries=10", build_script)
        self.assertIn(
            "while [ $retry_count -lt $max_retries ]; do", build_script
        )


if __name__ == "__main__":
    unittest.main()
