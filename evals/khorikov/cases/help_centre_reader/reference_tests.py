"""Private reference suite; no mutation or evaluation code runs on import."""
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import unittest

from app import handle_get
from reading_room import Article, Catalog, Translation

NOW = datetime(2031, 6, 4, 12, tzinfo=timezone.utc)
EN_TITLE = 'Read <first> & learn'
EN_BODY = 'Use <script>alert("x")</script> & keep &copy; literal.'


class Document(HTMLParser):
    """Observe displayed text without requiring optional tags or layout wrappers.

    Title metadata and script/style raw text are not visible article content.
    This is a bounded HTML observer, not a CSS layout or script engine.
    """

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.language = None
        self.visible_text = ''
        self.links = []
        self.tags = []
        self._non_visible_tag = None
        self._link = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        self.tags.append(tag)
        if tag == 'html':
            self.language = attributes.get('lang')
        elif tag in ('title', 'script', 'style'):
            self._non_visible_tag = tag
        elif tag == 'a':
            self._link = [attributes.get('href'), '']

    def handle_endtag(self, tag):
        if tag == self._non_visible_tag:
            self._non_visible_tag = None
        elif tag == 'a' and self._link is not None:
            self.links.append(tuple(self._link))
            self._link = None

    def handle_data(self, data):
        if self._non_visible_tag is None:
            self.visible_text += data
            if self._link is not None:
                self._link[1] += data


def sample_catalog():
    past = NOW - timedelta(days=2)
    return Catalog((
        Article(
            'reading',
            {'fr': Translation('Lire & apprendre', 'Un guide en français.'),
             'en': Translation(EN_TITLE, EN_BODY)},
            'en', past, aliases=('old-reader',),
            related=('zebra', 'missing', 'private', 'scheduled', 'alpha'),
        ),
        Article('alpha', {'fr': Translation('Alpha française', 'Texte alpha.')}, 'fr', past),
        Article('scheduled', {'en': Translation('Launch plans', 'Embargoed.')},
                'en', NOW + timedelta(hours=1), aliases=('old-scheduled',)),
        Article('zebra', {'fr': Translation('Zèbre <suite>', 'Encore.'),
                          'en': Translation('Zebra & extras', 'More detail.')}, 'en', past),
        Article('private', {'en': Translation('Internal draft', 'Private.')},
                'en', past, listed=False, aliases=('old-private',)),
        Article('just-published', {'en': Translation('Now available', 'Fresh.')}, 'en', NOW),
    ))


class ReaderContractTests(unittest.TestCase):
    def setUp(self):
        self.catalog = sample_catalog()

    def test_publication_compares_instants_across_different_offsets(self):
        publication = datetime(2031, 6, 4, 14, tzinfo=timezone(timedelta(hours=2)))
        article = Article('offset', {'en': Translation('Available now', 'Read this.')},
                          'en', publication)
        catalog = Catalog((article,))
        before = handle_get(catalog, '/en/offset', NOW - timedelta(microseconds=1))
        at_publication = handle_get(catalog, '/en/offset', NOW)
        self.assertEqual(404, before.status)
        self.assertEqual(200, at_publication.status)
        self.assertIn('Available now', Document(at_publication.body).visible_text)

    def test_public_page_survives_filtering_all_related_references(self):
        article = Article('no-public-links', {'en': Translation('Still public', 'Read this.')},
                          'en', NOW, related=('missing', 'private', 'scheduled'))
        catalog = Catalog((article, self.catalog.find('private'), self.catalog.find('scheduled')))
        response = handle_get(catalog, '/en/no-public-links', NOW)
        self.assertEqual(200, response.status)
        self.assertEqual('text/html; charset=utf-8', response.headers.get('Content-Type'))
        document = Document(response.body)
        self.assertIn('Still public', document.visible_text)
        self.assertIn('Read this.', document.visible_text)
        self.assertEqual([], document.links)

    def test_public_article_returns_success_and_html_content_type(self):
        response = handle_get(self.catalog, '/en/reading', NOW)
        self.assertEqual(200, response.status)
        self.assertEqual('text/html; charset=utf-8', response.headers.get('Content-Type'))
        self.assertNotIn('Location', response.headers)
        document = Document(response.body)
        self.assertEqual('en', document.language)
        self.assertIn(EN_TITLE, document.visible_text)

    def test_editorial_text_is_displayed_literally_without_markup_or_entity_expansion(self):
        response = handle_get(self.catalog, '/en/reading', NOW)
        document = Document(response.body)
        self.assertIn(EN_TITLE, document.visible_text)
        self.assertIn(EN_BODY, document.visible_text)
        self.assertNotIn('script', document.tags)
        self.assertNotIn('first', document.tags)

    def test_requested_translation_is_shown_and_declared(self):
        response = handle_get(self.catalog, '/fr/reading', NOW)
        self.assertEqual(200, response.status)
        document = Document(response.body)
        self.assertEqual('fr', document.language)
        self.assertIn('Lire & apprendre', document.visible_text)
        self.assertIn('Un guide en français.', document.visible_text)

    def test_missing_translation_uses_article_default_without_redirect(self):
        response = handle_get(self.catalog, '/de/reading', NOW)
        self.assertEqual(200, response.status)
        self.assertNotIn('Location', response.headers)
        document = Document(response.body)
        self.assertEqual('en', document.language)
        self.assertIn(EN_TITLE, document.visible_text)
        self.assertIn(EN_BODY, document.visible_text)
        other = Document(handle_get(self.catalog, '/de/alpha', NOW).body)
        self.assertEqual('fr', other.language)
        self.assertIn('Alpha française', other.visible_text)

    def test_alias_case_and_trailing_slash_redirects_retain_url_language(self):
        examples = (
            ('/en/old-reader', '/en/reading'),
            ('/fr/old-reader', '/fr/reading'),
            ('/de/old-reader', '/de/reading'),
            ('/fr/ReAdInG', '/fr/reading'),
            ('/de/reading/', '/de/reading'),
        )
        for path, destination in examples:
            with self.subTest(path=path):
                response = handle_get(self.catalog, path, NOW)
                self.assertEqual(308, response.status)
                self.assertEqual({'Location': destination}, response.headers)
                self.assertEqual('', response.body)

    def test_unknown_unlisted_and_future_articles_share_the_generic_404(self):
        for name in ('unknown', 'private', 'old-private', 'scheduled', 'old-scheduled'):
            for language in ('en', 'fr', 'de'):
                path = f'/{language}/{name}'
                with self.subTest(path=path):
                    response = handle_get(self.catalog, path, NOW)
                    self.assertEqual(404, response.status)
                    self.assertEqual({'Content-Type': 'text/plain; charset=utf-8'}, response.headers)
                    self.assertEqual('Not found', response.body)

    def test_publication_timestamp_is_inclusive(self):
        before = handle_get(self.catalog, '/en/just-published', NOW - timedelta(microseconds=1))
        at_publication = handle_get(self.catalog, '/en/just-published', NOW)
        self.assertEqual(404, before.status)
        self.assertEqual(200, at_publication.status)
        self.assertIn('Now available', Document(at_publication.body).visible_text)

    def test_related_links_preserve_editorial_order_and_hide_unavailable_references(self):
        expected_by_language = {
            'en': [('/en/zebra', 'Zebra & extras'), ('/en/alpha', 'Alpha française')],
            'fr': [('/fr/zebra', 'Zèbre <suite>'), ('/fr/alpha', 'Alpha française')],
            'de': [('/de/zebra', 'Zebra & extras'), ('/de/alpha', 'Alpha française')],
        }
        for language, expected in expected_by_language.items():
            with self.subTest(language=language):
                response = handle_get(self.catalog, f'/{language}/reading', NOW)
                self.assertEqual(expected, Document(response.body).links)

    def test_an_article_without_related_references_has_no_links(self):
        response = handle_get(self.catalog, '/en/just-published', NOW)
        self.assertEqual(200, response.status)
        self.assertEqual([], Document(response.body).links)

    def test_unsupported_languages_and_malformed_paths_are_generic_404s(self):
        for path in ('/', '/reading', '/es/reading', '/en/reading/extra', '/en/'):
            with self.subTest(path=path):
                response = handle_get(self.catalog, path, NOW)
                self.assertEqual(404, response.status)
                self.assertEqual({'Content-Type': 'text/plain; charset=utf-8'}, response.headers)
                self.assertEqual('Not found', response.body)


if __name__ == '__main__':
    unittest.main()
