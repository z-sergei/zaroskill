"""Article lookup and presentation for a small public help centre."""
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True)
class Translation:
    title: str
    body: str


@dataclass(frozen=True)
class Article:
    slug: str
    translations: Mapping[str, Translation]
    default_language: str
    published_at: datetime
    listed: bool = True
    aliases: tuple[str, ...] = ()
    related: tuple[str, ...] = ()


class Catalog:
    """An in-memory snapshot loaded by the site at publication time.

    Content configuration guarantees unique slugs/aliases, lowercase URL-safe
    slugs, a default translation, and timezone-aware publication timestamps.
    Related references may be stale while an editor revises the catalogue.
    """

    def __init__(self, articles: tuple[Article, ...]):
        self._by_name: dict[str, Article] = {}
        for article in articles:
            for name in (article.slug, *article.aliases):
                key = name.casefold()
                if key in self._by_name:
                    raise ValueError(f"Duplicate article name: {name}")
                self._by_name[key] = article

    def find(self, name: str) -> Article | None:
        return self._by_name.get(name.casefold())


@dataclass(frozen=True)
class Link:
    href: str
    title: str


@dataclass(frozen=True)
class Page:
    language: str
    title: str
    body: str
    links: tuple[Link, ...]


def is_public(article: Article, now: datetime) -> bool:
    return article.listed and article.published_at <= now


def _translation(article: Article, requested: str) -> tuple[str, Translation]:
    if requested in article.translations:
        return requested, article.translations[requested]
    return article.default_language, article.translations[article.default_language]


def build_page(catalog: Catalog, article: Article, requested: str, now: datetime) -> Page:
    language, text = _translation(article, requested)
    links = []
    for related_slug in article.related:
        related = catalog.find(related_slug)
        if related is None or not is_public(related, now):
            continue
        _, related_text = _translation(related, requested)
        links.append(Link(f"/{requested}/{related.slug}", related_text.title))
    return Page(language, text.title, text.body, tuple(links))
