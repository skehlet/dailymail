import importlib
import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError


with patch("boto3.client"), patch("boto3.resource"):
    ledger_mod = importlib.import_module("digest.ledger")
    alert_news = importlib.import_module("digest.alert_news")
    digest_app = importlib.import_module("digest.app")

Ledger = ledger_mod.Ledger
LedgerFact = ledger_mod.LedgerFact

RECORDS = [
    {"title": "Take-Two CEO explains", "url": "https://vgc.com/a", "summary": "No date yet."},
    {"title": "Rockstar quiet", "url": "https://rps.com/b", "summary": "Still no date."},
]


class TopicSlugTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(ledger_mod.topic_slug('gta 6 "pc" "release date"'), "gta-6-pc-release-date")


class LoadLedgerTests(unittest.TestCase):
    def test_missing_ledger_is_empty(self):
        error = ClientError({"Error": {"Code": "NoSuchKey", "Message": ""}}, "GetObject")
        with patch.object(ledger_mod, "s3") as s3:
            s3.get_object.side_effect = error
            ledger = ledger_mod.load_ledger("topic")
        self.assertEqual(ledger, Ledger(topic="topic"))


class CheckAlertForNewsTests(unittest.TestCase):
    def check(self, response, ledger=None):
        ledger = ledger or Ledger(topic="gta 6 pc", facts=[LedgerFact(date="2026-01-01", fact="No PC date", status="CONFIRMED")])
        with patch.object(alert_news, "call_llm_structured", return_value=response):
            return alert_news.check_alert_for_news("gta 6 pc", RECORDS, ledger, "2026-10-25")

    def test_nothing_new_leaves_ledger_unchanged(self):
        update = self.check(alert_news.AlertNewsCheck(new_developments=[], summary="ignored"))
        self.assertEqual(update.developments, [])
        self.assertEqual(update.summary, "")
        self.assertEqual(len(update.updated_ledger.facts), 1)

    def test_new_development_is_normalized_and_added_to_ledger(self):
        response = alert_news.AlertNewsCheck(
            new_developments=[
                alert_news.NewDevelopment(
                    kind="changed", statement="PC version due 2027", status="rumor",
                    source_urls=["https://vgc.com/a", "https://made-up.example/"],
                ),
                alert_news.NewDevelopment(kind="weird", statement="X", status="official", source_urls=[]),
            ],
            summary="PC rumored for 2027.",
        )
        update = self.check(response)
        self.assertEqual([d.kind for d in update.developments], ["CHANGED", "NEW"])
        self.assertEqual([d.status for d in update.developments], ["RUMOR", "CONFIRMED"])
        # hallucinated URL dropped, real one mapped to its title
        self.assertEqual([s.title for s in update.developments[0].sources], ["Take-Two CEO explains"])
        self.assertEqual(update.updated_ledger.facts[-2], LedgerFact(date="2026-10-25", fact="PC version due 2027", status="RUMOR"))
        self.assertEqual(len(update.updated_ledger.facts), 3)

    def test_compaction_rejected_when_it_drops_too_much(self):
        big = Ledger(topic="t", facts=[LedgerFact(date="2026-01-01", fact=f"f{i}", status="CONFIRMED") for i in range(40)])
        with patch.object(alert_news, "call_llm_structured", return_value=alert_news.CompactedLedger(facts=big.facts[:2])):
            self.assertIs(alert_news.compact_ledger(big), big)


class ProcessMessagesTests(unittest.TestCase):
    def update(self):
        return alert_news.AlertUpdate(
            topic="gta 6 pc", summary="s",
            developments=[alert_news.AlertDevelopment(kind="NEW", statement="x", status="CONFIRMED", sources=[])],
            updated_ledger=Ledger(topic="gta 6 pc"),
        )

    def test_alert_feeds_split_out_and_failures_fall_back(self):
        feeds = [("Google Alert - a", RECORDS), ("Google Alert - b", RECORDS), ("Some Blog", RECORDS)]
        nothing_new = alert_news.AlertUpdate(topic="b", summary="", developments=[], updated_ledger=Ledger(topic="b"))
        with patch.object(digest_app, "load_ledger"), \
                patch.object(digest_app, "check_alert_for_news", side_effect=[RuntimeError("llm down"), nothing_new]):
            remaining, updates = digest_app.check_alerts_for_news(feeds)
        self.assertEqual([title for title, _ in remaining], ["Google Alert - a", "Some Blog"])
        self.assertEqual(updates, [])

    def test_ledger_saved_only_after_send(self):
        for sent, expected_saves in [(True, 1), (False, 0)]:
            with patch.object(digest_app, "cleanup_group_and_sort_messages", return_value=[]), \
                    patch.object(digest_app, "check_alerts_for_news", return_value=([], [self.update()])), \
                    patch.object(digest_app, "create_email_and_send_it", return_value=sent), \
                    patch.object(digest_app, "save_ledger") as save_ledger:
                digest_app.process_messages([])
            self.assertEqual(save_ledger.call_count, expected_saves)

    def test_email_renders_with_only_alert_updates(self):
        with patch.object(digest_app, "send_email") as send_email:
            self.assertTrue(digest_app.create_email_and_send_it([], [self.update()]))
        html = send_email.call_args.kwargs["html"]
        self.assertIn("What's New", html)
        self.assertIn("gta 6 pc", html)


if __name__ == "__main__":
    unittest.main()
