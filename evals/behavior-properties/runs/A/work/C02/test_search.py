import unittest

from search import SearchApp


class RecordingGateway:
    def __init__(self):
        self.requests = []

    def start(self, token, query):
        self.requests.append((token, query))


class SearchAppTests(unittest.TestCase):
    def test_search_starts_one_request_and_active_answer_becomes_visible(self):
        gateway = RecordingGateway()
        app = SearchApp(gateway)

        token = app.search("red fox")

        self.assertEqual([(token, "red fox")], gateway.requests)
        app.receive(token, ["fox result", "another fox result"])
        self.assertEqual(("fox result", "another fox result"), app.visible)

    def test_new_search_keeps_visible_results_until_its_empty_answer(self):
        gateway = RecordingGateway()
        app = SearchApp(gateway)
        previous = app.search("red fox")
        self.assertEqual([(previous, "red fox")], gateway.requests)
        app.receive(previous, ["fox result"])
        self.assertEqual(("fox result",), app.visible)

        current = app.search("no matches")

        self.assertEqual(
            [(previous, "red fox"), (current, "no matches")], gateway.requests
        )
        self.assertEqual(("fox result",), app.visible)
        app.receive(current, [])
        self.assertEqual((), app.visible)

    def test_older_answer_cannot_change_visible_results_in_either_completion_order(self):
        for order in (("older", "current"), ("current", "older")):
            with self.subTest(completion_order=order):
                gateway = RecordingGateway()
                app = SearchApp(gateway)
                older = app.search("red fox")
                self.assertEqual([(older, "red fox")], gateway.requests)
                current = app.search("blue whale")
                self.assertEqual(
                    [(older, "red fox"), (current, "blue whale")], gateway.requests
                )
                self.assertEqual((), app.visible)
                visible = ()

                for completed in order:
                    if completed == "older":
                        app.receive(older, ["fox result"])
                    else:
                        app.receive(current, ["whale result"])
                        visible = ("whale result",)
                    self.assertEqual(visible, app.visible)
