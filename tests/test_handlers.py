import importlib
import unittest
from unittest.mock import patch


with patch("boto3.client"), patch("boto3.resource"):
    rss_reader = importlib.import_module("rss_reader.index")
    scraper = importlib.import_module("scraper.index")
    summarizer = importlib.import_module("summarizer.index")
    digest = importlib.import_module("digest.index")


class HandlerSmokeTests(unittest.TestCase):
    @patch.object(rss_reader, "read_rss_feeds")
    @patch.object(rss_reader, "show_settings")
    def test_rss_reader_handler(self, show_settings, read_rss_feeds):
        rss_reader.handler({}, None)

        show_settings.assert_called_once_with()
        read_rss_feeds.assert_called_once_with()

    @patch.object(scraper, "process_record")
    @patch.object(scraper, "show_settings")
    def test_scraper_handler_reports_failed_messages(self, show_settings, process_record):
        process_record.side_effect = [None, RuntimeError("failed")]
        event = {
            "Records": [
                {"messageId": "success"},
                {"messageId": "failure"},
            ]
        }

        response = scraper.handler(event, None)

        show_settings.assert_called_once_with()
        self.assertEqual(response, {"batchItemFailures": [{"itemIdentifier": "failure"}]})

    @patch.object(summarizer, "process_sqs_record")
    @patch.object(summarizer, "show_settings")
    def test_summarizer_handler(self, show_settings, process_sqs_record):
        records = [{"messageId": "first"}, {"messageId": "second"}]

        summarizer.handler({"Records": records}, None)

        show_settings.assert_called_once_with()
        self.assertEqual([call.args[0] for call in process_sqs_record.call_args_list], records)

    @patch.object(digest, "read_from_digest_queue")
    @patch.object(digest, "show_settings")
    def test_digest_handler(self, show_settings, read_from_digest_queue):
        digest.handler({}, None)

        show_settings.assert_called_once_with()
        read_from_digest_queue.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()