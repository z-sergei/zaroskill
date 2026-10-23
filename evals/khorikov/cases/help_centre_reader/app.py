"""HTTP-facing adapter. An embedding server passes the decoded request path."""
from dataclasses import dataclass
from datetime import datetime
from html import escape

from reading_room import Catalog, Link, Page, build_page, is_public

SUPPORTED_LANGUAGES = frozenset({"en", "fr", "de"})


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: str


def _not_found() -> Response:
    return Response(404, {"Content-Type": "text/plain; charset=utf-8"}, "Not found")


def _render_link(link: Link) -> str:
    return f'<li><a href="{escape(link.href, quote=True)}">{escape(link.title)}</a></li>'


def _render_links(links: tuple[Link, ...]) -> str:
    return "".join(_render_link(link) for link in links)


def _render(page: Page) -> str:
    return (
        '<!doctype html>'
        f'<html lang="{escape(page.language, quote=True)}">'
        f'<head><title>{escape(page.title)}</title></head>'
        f'<body><h1>{escape(page.title)}</h1>'
        f'<p class="article-body">{escape(page.body)}</p>'
        '<nav aria-label="Related articles"><ul>'
        f'{_render_links(page.links)}'
        '</ul></nav></body></html>'
    )


def handle_get(catalog: Catalog, path: str, now: datetime) -> Response:
    """Serve a decoded path such as /fr/install at the supplied aware timestamp."""
    segments = path.strip("/").split("/")
    if len(segments) != 2 or segments[0] not in SUPPORTED_LANGUAGES:
        return _not_found()
    requested, name = segments
    article = catalog.find(name)
    if article is None or not is_public(article, now):
        return _not_found()
    canonical_path = f"/{requested}/{article.slug}"
    if path != canonical_path:
        return Response(308, {"Location": canonical_path}, "")
    page = build_page(catalog, article, requested, now)
    return Response(200, {"Content-Type": "text/html; charset=utf-8"}, _render(page))
