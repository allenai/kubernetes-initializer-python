import unittest

from ai2.kubernetes.initializer.rejection import Rejection


class TestRejection(unittest.TestCase):
    def test_rejection_creates_status(self):
        test_rejection = Rejection('msg', reason='reason', code=606)

        status = test_rejection.status
        self.assertEqual(status.message, 'msg')
        self.assertEqual(status.reason, 'reason')
        self.assertEqual(status.code, 606)

    def test_reason_defaults_to_message(self):
        test_rejection = Rejection('message')
        status = test_rejection.status
        self.assertEqual(status.message, 'message')
        self.assertEqual(status.reason, 'message')
