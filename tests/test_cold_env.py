import os
import unittest
from unittest.mock import patch

from cold import env


class ColdEnvironmentTest(unittest.TestCase):
    def test_function_test_timeout_uses_default_override_and_explicit_value(
        self,
    ) -> None:
        self.assertTrue(
            hasattr(env, "resolve_function_test_timeout"),
            "cold.env must expose resolve_function_test_timeout",
        )

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env.resolve_function_test_timeout(), 3600)

        with patch.dict(
            os.environ,
            {"COLD_FUNCTION_TEST_TIMEOUT": "10800"},
            clear=True,
        ):
            self.assertEqual(env.resolve_function_test_timeout(), 10800)
            self.assertEqual(env.resolve_function_test_timeout(7200), 7200)


if __name__ == "__main__":
    unittest.main()
