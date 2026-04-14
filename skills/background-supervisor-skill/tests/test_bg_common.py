import pathlib
import sys
import unittest


SCRIPTS_ROOT = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import bg_common  # type: ignore  # noqa: E402
import bg_repair  # type: ignore  # noqa: E402


class ExtractJobTests(unittest.TestCase):
    def test_extract_job_from_background_bash_event(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "cwd": r"C:\repo",
            "tool_input": {
                "command": "python train.py --epochs 10",
                "run_in_background": True,
            },
            "tool_response": {
                "stdout": "started",
            },
        }

        job = bg_common.extract_job_from_hook(payload)

        self.assertIsNotNone(job)
        self.assertEqual(job["command"], "python train.py --epochs 10")
        self.assertEqual(job["cwd"], r"C:\repo")
        self.assertEqual(job["session_id"], "session-1")
        self.assertEqual(job["tool_use_id"], "tool-1")
        self.assertEqual(job["status"], "active")
        self.assertEqual(job["restart_count"], 0)
        self.assertEqual(job["repair_count"], 0)

    def test_extract_job_ignores_short_or_foreground_commands(self):
        short_payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "cwd": r"C:\repo",
            "tool_input": {
                "command": "git status",
                "run_in_background": True,
            },
        }
        foreground_payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "cwd": r"C:\repo",
            "tool_input": {
                "command": "python train.py --epochs 10",
                "run_in_background": False,
            },
        }

        self.assertIsNone(bg_common.extract_job_from_hook(short_payload))
        self.assertIsNone(bg_common.extract_job_from_hook(foreground_payload))


class IncidentTests(unittest.TestCase):
    def test_extract_failure_incident_from_post_tool_use_failure(self):
        payload = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "cwd": r"C:\repo",
            "tool_input": {
                "command": "python train.py --epochs 10",
                "run_in_background": True,
            },
            "error": "Command exited with non-zero status code 1",
        }

        incident = bg_common.extract_incident_from_hook(payload)

        self.assertIsNotNone(incident)
        self.assertEqual(incident["kind"], "tool_failure")
        self.assertEqual(incident["tool_use_id"], "tool-1")
        self.assertIn("non-zero", incident["summary"])

    def test_recovery_policy_prefers_restart_then_repair_then_escalation(self):
        base_job = {
            "status": "failed",
            "restart_count": 0,
            "repair_count": 0,
            "max_restarts": 2,
            "max_repairs": 1,
        }

        self.assertEqual(
            bg_common.choose_recovery_action(base_job, {"kind": "process_exit"})["action"],
            "restart",
        )
        self.assertEqual(
            bg_common.choose_recovery_action(
                {**base_job, "restart_count": 2},
                {"kind": "process_exit"},
            )["action"],
            "repair",
        )
        self.assertEqual(
            bg_common.choose_recovery_action(
                {**base_job, "restart_count": 2, "repair_count": 1},
                {"kind": "process_exit"},
            )["action"],
            "needs_human",
        )

    def test_repair_prompt_contains_command_and_incident_summary(self):
        job = {
            "job_id": "job-1",
            "cwd": r"C:\repo",
            "command": "python train.py --epochs 10",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "transcript_path": r"C:\repo\.claude\session.jsonl",
        }
        incident = {
            "kind": "tool_failure",
            "summary": "Command exited with non-zero status code 1",
        }

        prompt = bg_repair.build_repair_prompt(job, incident)

        self.assertIn("python train.py --epochs 10", prompt)
        self.assertIn("non-zero status code 1", prompt)


if __name__ == "__main__":
    unittest.main()
