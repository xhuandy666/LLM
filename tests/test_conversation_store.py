import unittest

from api.conversation_store import ConversationStore


class ConversationStoreTest(unittest.TestCase):
    def test_histories_are_isolated_by_session_id(self):
        store = ConversationStore()

        store.add_exchange("session-a", "生成学生表", "表格 A")
        store.add_exchange("session-b", "生成订单表", "表格 B")

        self.assertEqual(
            store.get_history("session-a"),
            [
                {"role": "user", "content": "生成学生表"},
                {"role": "assistant", "content": "表格 A"},
            ],
        )
        self.assertEqual(
            store.get_history("session-b"),
            [
                {"role": "user", "content": "生成订单表"},
                {"role": "assistant", "content": "表格 B"},
            ],
        )

    def test_clear_only_removes_requested_session(self):
        store = ConversationStore()
        store.add_exchange("session-a", "A", "reply A")
        store.add_exchange("session-b", "B", "reply B")

        store.clear("session-a")

        self.assertEqual(store.get_history("session-a"), [])
        self.assertEqual(
            store.get_history("session-b"),
            [
                {"role": "user", "content": "B"},
                {"role": "assistant", "content": "reply B"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
