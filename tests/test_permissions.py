"""
Unit Tests for PermissionManager & Security Layer.
"""
import unittest
from engines.permissions import PermissionManager, RiskLevel
from engines.shared.errors import PermissionDeniedError

class TestPermissionManager(unittest.TestCase):
    def setUp(self):
        self.perm = PermissionManager()

    def test_risk_classification(self):
        self.assertEqual(self.perm.get_risk_level("shutdown_pc"), RiskLevel.CRITICAL)
        self.assertEqual(self.perm.get_risk_level("clean_temp"), RiskLevel.SENSITIVE)
        self.assertEqual(self.perm.get_risk_level("open_url"), RiskLevel.NORMAL)

    def test_authorization(self):
        self.assertTrue(self.perm.authorize("open_url"))

    def test_user_confirmation_rejection(self):
        self.perm.set_confirmation_callback(lambda cap, risk: False)
        with self.assertRaises(PermissionDeniedError):
            self.perm.authorize("shutdown_pc")

        # Reset callback
        self.perm.set_confirmation_callback(None)

if __name__ == "__main__":
    unittest.main()
