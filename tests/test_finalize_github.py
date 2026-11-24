import unittest
from scripts.finalize_github import policy, CHECKS, OWNER, RELEASE_PLANNING

class PolicyTests(unittest.TestCase):
    def test_scope(self):
        self.assertEqual(OWNER, "Neguchads")
        self.assertEqual(len(CHECKS), 8)
        self.assertNotIn("comfyui", CHECKS)
        self.assertEqual(set(RELEASE_PLANNING), {"starlight-bi", "favorite-manager"})

    def test_active_policy_without_bypass(self):
        check = {"context": "test", "integration_id": 15368}
        result = policy("publish/public-safe", [check], 0)
        self.assertEqual(result["enforcement"], "active")
        self.assertEqual(result["bypass_actors"], [])
        self.assertEqual(result["conditions"]["ref_name"]["include"], ["refs/heads/publish/public-safe"])
        rules = {r["type"]: r.get("parameters", {}) for r in result["rules"]}
        self.assertEqual(set(rules), {"deletion", "non_fast_forward", "pull_request", "required_status_checks"})
        self.assertEqual(rules["pull_request"]["allowed_merge_methods"], ["squash"])
        self.assertTrue(rules["pull_request"]["required_review_thread_resolution"])
        self.assertEqual(rules["pull_request"]["required_approving_review_count"], 0)
        self.assertTrue(rules["required_status_checks"]["strict_required_status_checks_policy"])
        self.assertEqual(rules["required_status_checks"]["required_status_checks"], [check])

    def test_human_review_option(self):
        result = policy("main", [{"context": "CI"}], 1)
        rule = next(r for r in result["rules"] if r["type"] == "pull_request")
        self.assertEqual(rule["parameters"]["required_approving_review_count"], 1)

if __name__ == "__main__":
    unittest.main()
