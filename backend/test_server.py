import unittest

from backend.server import AnalyzeRequest, analyze, health


class AnalyzerApiContractTests(unittest.TestCase):
    def test_health(self) -> None:
        self.assertEqual(health(), {"status": "ok"})

    def test_analysis_separates_tokens_and_errors(self) -> None:
        result = analyze(
            AnalyzeRequest(source="let distance = 100m;\nlet invalid = @;")
        )

        self.assertGreater(len(result["tokens"]), 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["type"], "ERR")
        self.assertEqual(result["errors"][0]["line"], 2)
        self.assertNotIn("EOF", [token["type"] for token in result["tokens"]])

    def test_camel_case_comments_option(self) -> None:
        request = AnalyzeRequest.model_validate(
            {"source": "// retained", "keepComments": True}
        )
        result = analyze(request)

        self.assertEqual(result["tokens"][0]["type"], "CMT")


if __name__ == "__main__":
    unittest.main()
