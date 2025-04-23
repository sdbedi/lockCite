import unittest
from unittest.mock import patch, mock_open
from typing import List, Dict
from types import SimpleNamespace
import json

from case_analysis import load_case_text, build_prompt, call_openai_for_analysis


class TestCaseAnalysis(unittest.TestCase):

    def test_prompt_contains_text(self):
        case_text = "This is a sample opinion mentioning Roe v. Wade."
        prompt = build_prompt(case_text)
        self.assertIn("Roe v. Wade", prompt)
        self.assertIn("---TEXT START---", prompt)

    @patch("builtins.open", new_callable=mock_open, read_data="<html><body>Test Opinion</body></html>")
    @patch("pathlib.Path.is_file", return_value=True)
    def test_load_case_text_from_html(self, mock_is_file, mock_file):
        text = load_case_text("dummy")
        self.assertIn("Test Opinion", text)

    @patch("case_analysis.client.responses.create")
    def test_call_openai_for_analysis_parsing(self, mock_openai):
        fake_response = {
            "citations": [
                {
                    "treated_case": "Smith v. Jones",
                    "treatment_type": "Overruled",
                    "excerpt": "Excerpted opinion text...",
                    "explanation": "It was overruled because..."
                }
            ]
        }

        # Mock .output_text to return JSON string
        mock_openai.return_value = SimpleNamespace(
            output_text=json.dumps(fake_response)
        )

        prompt = "Fake prompt text"
        results: List[Dict] = call_openai_for_analysis(prompt)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["treated_case"], "Smith v. Jones")
        self.assertEqual(results[0]["treatment_type"], "Overruled")


if __name__ == "__main__":
    unittest.main()
