import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExperimentResourceLimitsTest(unittest.TestCase):
    def _run_script(self, relative_path: str) -> tuple[list[str], str]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            bin_dir = workdir / "bin"
            bin_dir.mkdir()

            call_log = workdir / "make.log"
            script_log = workdir / "script.log"

            for name in ("buildconf", "configure"):
                command = workdir / name
                command.write_text("#!/bin/sh\nexit 0\n")
                command.chmod(0o755)

            php_test_dir = workdir / "ext/standard/tests/file"
            php_test_dir.mkdir(parents=True)
            for name in (
                "file_get_contents_file_put_contents_5gb.phpt",
                "disk_free_space_basic.phpt",
            ):
                (php_test_dir / name).touch()

            make = bin_dir / "make"
            make.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$*\" >> \"$CALL_LOG\"\n"
                "mkdir -p sapi/cli sapi/phpdbg\n"
                ": > sapi/cli/php\n"
                ": > sapi/phpdbg/phpdbg\n"
                ": > python\n"
            )
            make.chmod(0o755)

            script = bin_dir / "script"
            script.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$*\" >> \"$SCRIPT_LOG\"\n"
            )
            script.chmod(0o755)

            patch = bin_dir / "patch"
            patch.write_text("#!/bin/sh\ncat >/dev/null\n")
            patch.chmod(0o755)

            target = workdir / "run.sh"
            shutil.copy2(ROOT / relative_path, target)

            env = os.environ.copy()
            env.update(
                {
                    "BUILD_JOBS": "6",
                    "CPYTHON_BUILD_JOBS": "4",
                    "TEST_JOBS": "4",
                    "CALL_LOG": str(call_log),
                    "SCRIPT_LOG": str(script_log),
                }
            )
            if relative_path.startswith("vuln/cpython/"):
                env["COLD_REAL_MAKE"] = str(make)
                env["PATH"] = f"{ROOT / 'cold/compiler'}:{bin_dir}:{env['PATH']}"
            else:
                env["PATH"] = f"{bin_dir}:{env['PATH']}"
            subprocess.run([str(target)], cwd=workdir, env=env, check=True)

            make_calls = call_log.read_text().splitlines() if call_log.exists() else []
            script_call = script_log.read_text().strip() if script_log.exists() else ""
            return make_calls, script_call

    def test_php_build_honors_build_job_budget(self) -> None:
        make_calls, _ = self._run_script("vuln/php/common/build.sh")
        self.assertEqual(make_calls, ["-j6"])

    def test_php_test_honors_build_and_test_job_budgets(self) -> None:
        make_calls, script_call = self._run_script("vuln/php/common/test.sh")
        self.assertEqual(make_calls, ["-j6"])
        self.assertIn(" -j4 ", script_call)

    def test_cpython_build_honors_build_job_budget(self) -> None:
        make_calls, _ = self._run_script("vuln/cpython/common/build.sh")
        self.assertEqual(make_calls, ["-j4"])

    def test_cpython_test_honors_build_and_test_job_budgets(self) -> None:
        make_calls, _ = self._run_script("vuln/cpython/common/test.sh")
        self.assertEqual(make_calls, ["-j4", "test -j4 TESTOPTS=-j4"])

    def test_llvm_function_test_honors_build_job_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            bin_dir = workdir / "bin"
            bin_dir.mkdir()
            call_log = workdir / "ninja.log"

            cmake = bin_dir / "cmake"
            cmake.write_text("#!/bin/sh\nexit 0\n")
            cmake.chmod(0o755)

            ninja = bin_dir / "ninja"
            ninja.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$*\" >> \"$CALL_LOG\"\n"
            )
            ninja.chmod(0o755)

            target = workdir / "run.sh"
            shutil.copy2(
                ROOT / "vuln/llvm/llvm-gh-136814/test.sh", target
            )

            env = os.environ.copy()
            env.update(
                {
                    "BUILD_JOBS": "6",
                    "CALL_LOG": str(call_log),
                    "PATH": f"{bin_dir}:{env['PATH']}",
                }
            )
            subprocess.run([str(target)], cwd=workdir, env=env, check=True)

            self.assertEqual(
                call_log.read_text().splitlines(),
                ["-j6", "-j6 check-all"],
            )

    def test_all_cpython_case_scripts_bound_make_and_regrtest_concurrency(self) -> None:
        scripts = sorted((ROOT / "vuln/cpython").glob("*/build.sh"))
        scripts += sorted((ROOT / "vuln/cpython").glob("*/test.sh"))

        for script_path in scripts:
            relative_path = str(script_path.relative_to(ROOT))
            with self.subTest(script=relative_path):
                make_calls, _ = self._run_script(relative_path)
                self.assertTrue(make_calls, "script did not invoke make")
                for call in make_calls:
                    self.assertIn("-j4", call)
                    if call.startswith("test "):
                        self.assertIn("TESTOPTS=-j4", call)

    def test_compose_passes_the_serial_resource_budget(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "OPENAI_API_KEY": "unused",
                "ANTHROPIC_API_KEY": "unused",
                "LITELLM_MASTER_KEY": "unused",
                "COLD_MAX_PROC": "1",
                "BUILD_JOBS": "6",
                "CPYTHON_BUILD_JOBS": "4",
                "TEST_JOBS": "4",
                "RESERVE_CPU": "4",
                "RESERVE_MEMORY": "6G",
                "LIMIT_CPU": "6",
                "LIMIT_MEMORY": "9G",
            }
        )
        result = subprocess.run(
            ["docker", "compose", "--profile", "check", "config", "--format", "json"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        services = json.loads(result.stdout)["services"]

        for service_name in ("php-base", "cpython-base"):
            service = services[service_name]
            self.assertEqual(
                service["environment"],
                {
                    "BUILD_JOBS": "6",
                    "COLD_ACTION": "check",
                    "COLD_MAX_PROC": "1",
                    "CPYTHON_BUILD_JOBS": "4",
                    "HTTPS_PROXY": "",
                    "HTTP_PROXY": "",
                    "PATCH_DEBUG": "0",
                    "TEST_JOBS": "4",
                    "http_proxy": "",
                    "https_proxy": "",
                },
            )
            limits = service["deploy"]["resources"]["limits"]
            self.assertEqual(limits["cpus"], 6)
            self.assertEqual(limits["memory"], "9663676416")

    def test_compose_exposes_opt_in_proxy_to_base_checks(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "OPENAI_API_KEY": "unused",
                "ANTHROPIC_API_KEY": "unused",
                "LITELLM_MASTER_KEY": "unused",
                "BENCHMARK_HTTP_PROXY": "http://host.docker.internal:7897",
            }
        )
        result = subprocess.run(
            ["docker", "compose", "--profile", "check", "config", "--format", "json"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        service = json.loads(result.stdout)["services"]["libtiff-base"]

        self.assertEqual(
            service.get("extra_hosts"), ["host.docker.internal=host-gateway"]
        )
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            self.assertEqual(
                service["environment"][name],
                "http://host.docker.internal:7897",
            )


if __name__ == "__main__":
    unittest.main()
