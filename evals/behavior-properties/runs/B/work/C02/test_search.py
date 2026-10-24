import unittest

from search import SearchApp


class RecordingGateway:
    def __init__(self):
        self.requests = []

    def start(self, token, query):
        self.requests.append((token, query))


class SearchAppTests(unittest.TestCase):
    def test_each_search_starts_one_request_with_its_returned_token(self):
        gateway = RecordingGateway()
        app = SearchApp(gateway)

        first = app.search("mountains")
        self.assertEqual([(first, "mountains")], gateway.requests)
        second = app.search("coast")
        self.assertEqual(
            [(first, "mountains"), (second, "coast")], gateway.requests
        )

    def test_new_search_keeps_visible_results_until_its_answer_arrives(self):
        gateway = RecordingGateway()
        app = SearchApp(gateway)
        previous = app.search("previous query")
        self.assertEqual([(previous, "previous query")], gateway.requests)
        app.receive(previous, ["saved result"])
        self.assertEqual(("saved result",), app.visible)

        active = app.search("current query")
        self.assertEqual(
            [(previous, "previous query"), (active, "current query")],
            gateway.requests,
        )
        self.assertEqual(("saved result",), app.visible)

        app.receive(active, ["current result"])
        self.assertEqual(("current result",), app.visible)

    def test_older_answer_cannot_change_results_in_either_completion_order(self):
        for order in ("older first", "current first"):
            with self.subTest(order=order):
                gateway = RecordingGateway()
                app = SearchApp(gateway)
                previous = app.search("saved query")
                self.assertEqual([(previous, "saved query")], gateway.requests)
                app.receive(previous, ["saved result"])
                self.assertEqual(("saved result",), app.visible)

                older = app.search("older query")
                current = app.search("current query")
                self.assertEqual(
                    [(previous, "saved query"), (older, "older query"),
                     (current, "current query")],
                    gateway.requests,
                )
                self.assertEqual(("saved result",), app.visible)

                if order == "older first":
                    app.receive(older, ["obsolete result"])
                    self.assertEqual(("saved result",), app.visible)
                    app.receive(current, ["current result"])
                    self.assertEqual(("current result",), app.visible)
                else:
                    app.receive(current, ["current result"])
                    self.assertEqual(("current result",), app.visible)
                    app.receive(older, ["obsolete result"])
                    self.assertEqual(("current result",), app.visible)
