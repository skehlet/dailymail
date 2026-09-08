import unittest

import en_core_web_sm
from unstructured.documents.elements import NarrativeText
from unstructured.partition.html import partition_html


class UnstructuredCompatibilityTests(unittest.TestCase):
    def test_spacy_model_is_installed(self):
        self.assertEqual(en_core_web_sm.load().meta["lang"], "en")

    def test_html_partition_produces_narrative_text(self):
        elements = partition_html(
            text="""
                <html>
                    <head><title>Test article</title></head>
                    <body>
                        <article>
                            <p>This is a substantial paragraph containing enough meaningful prose
                            for Unstructured to identify it as narrative article text.</p>
                        </article>
                    </body>
                </html>
            """
        )

        narrative_text = [
            str(element) for element in elements if isinstance(element, NarrativeText)
        ]
        self.assertTrue(narrative_text)
        self.assertIn("substantial paragraph", narrative_text[0])


if __name__ == "__main__":
    unittest.main()