"""Verify hosted mode cannot expose the shared demo login or local records."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from deployment_config import load_settings


ROOT = Path(__file__).resolve().parents[1]


class DeploymentTests(unittest.TestCase):
    def test_local_mode_preserves_existing_database_and_demo(self):
        settings = load_settings(ROOT, {})
        self.assertTrue(settings.demo_login)
        self.assertTrue(settings.authenticate("admin", "admin123"))
        self.assertEqual(settings.database_path, ROOT / "smart_budget_tracker.db")

    def test_production_requires_credentials_and_absolute_database_path(self):
        env = {"BUDGET_DEPLOYMENT": "production"}
        with self.assertRaises(ValueError):
            load_settings(ROOT, env)
        env.update(BUDGET_USERNAME="owner", BUDGET_PASSWORD="test-password-for-deployment")
        for path in ("", "relative.db"):
            env["BUDGET_DB_PATH"] = path
            with self.assertRaises(ValueError):
                load_settings(ROOT, env)

    def test_host_detection_cannot_fall_back_to_demo(self):
        for host_env in ({"RENDER": "true"}, {"RAILWAY_PROJECT_ID": "test-project"}, {"VERCEL": "1"}):
            with self.assertRaises(ValueError):
                load_settings(ROOT, host_env)

    def test_vercel_login_warns_about_temporary_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "budget.db"
            env = {
                "VERCEL": "1",
                "BUDGET_STORAGE": "ephemeral",
                "BUDGET_USERNAME": "owner",
                "BUDGET_PASSWORD": "test-password-for-deployment",
                "BUDGET_DB_PATH": str(database),
            }
            with patch.dict("os.environ", env, clear=True):
                app = AppTest.from_file(str(ROOT / "Smart_Budget_Tracker_Professional.py"), default_timeout=20).run()
                self.assertFalse(list(app.exception))
                self.assertFalse(list(app.error))
                self.assertTrue(any("temporary storage" in item.value for item in app.warning))
                self.assertEqual(len(app.text_input), 2)
                self.assertFalse(database.exists())

    def test_hosted_ui_rejects_demo_and_saves_to_isolated_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "records" / "budget.db"
            env = {
                "BUDGET_DEPLOYMENT": "production",
                "BUDGET_USERNAME": "owner",
                "BUDGET_PASSWORD": "test-password-for-deployment",
                "BUDGET_DB_PATH": str(database),
            }
            with patch.dict("os.environ", env):
                app = AppTest.from_file(str(ROOT / "Smart_Budget_Tracker_Professional.py"), default_timeout=20).run()
                self.assertFalse(list(app.exception))
                self.assertFalse(database.exists())
                self.assertFalse(any("admin123" in item.value for item in app.markdown))
                app.text_input[0].set_value("admin")
                app.text_input[1].set_value("admin123")
                app.button[0].click().run()
                self.assertFalse(app.session_state["logged_in"])
                app.text_input[0].set_value("owner")
                app.text_input[1].set_value(env["BUDGET_PASSWORD"])
                app.button[0].click().run()
                self.assertFalse(list(app.exception))
                self.assertTrue(app.session_state["logged_in"])
                self.assertTrue(database.exists())

    def test_missing_hosted_credentials_stops_before_login(self):
        with patch.dict("os.environ", {"BUDGET_DEPLOYMENT": "production"}, clear=True):
            app = AppTest.from_file(str(ROOT / "Smart_Budget_Tracker_Professional.py"), default_timeout=20).run()
            self.assertFalse(list(app.exception))
            self.assertTrue(list(app.error))
            self.assertFalse(list(app.text_input))


if __name__ == "__main__":
    unittest.main()
