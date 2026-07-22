import tempfile
import unittest
from pathlib import Path

from dorkinator import load_domains, make_entries, normalise_domain


class DorkinatorTests(unittest.TestCase):
    def test_normalises_domain_and_rejects_paths(self):
        self.assertEqual(normalise_domain("https://Example.COM/path"), "example.com")
        with self.assertRaises(ValueError):
            normalise_domain("../../output")

    def test_file_input_ignores_comments_and_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "domains.txt"
            file.write_text("# scope\nexample.com\nexample.com\napi.example.org\n")
            self.assertEqual(load_domains(str(file)), ["example.com", "api.example.org"])

    def test_entries_have_encoded_search_urls(self):
        entries = make_entries("example.com", "google", ["api"])
        self.assertTrue(entries[0]["url"].startswith("https://www.google.com/search?q="))
        self.assertIn("site%3Aexample.com", entries[0]["url"])


if __name__ == "__main__":
    unittest.main()
