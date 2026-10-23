# Help-centre article reader regression coverage

The public help centre's reader currently works, but its regression coverage was
lost while moving it out of the main server. Add a standard-library `unittest`
suite in `tests/` that protects the reader's behavior. Leave production files
unchanged. The suite must run with `python3 -m unittest discover -s tests -v` on
Python 3.11 or later, without a server, network, credentials, or additional
packages.

The site has these product requirements:

- Articles are public only when marked listed and their publication timestamp
  has arrived. Publication is inclusive of the exact timestamp. Unknown,
  unlisted, and future articles all return the same generic 404 response,
  including when reached through an alias.
- Supported URL languages are English (`en`), French (`fr`), and German (`de`).
  A reader gets the requested translation if the article has it; otherwise they
  get that article's default translation. The document's language describes the
  text actually shown. A missing translation does not redirect the reader.
- Slug lookup accepts aliases and case differences. A public article reached
  through a noncanonical path gets a permanent 308 redirect to its canonical
  slug, retaining the language chosen in the URL. A trailing slash is also
  canonicalized. A redirect has an empty body.
- Article titles and body text are plain text, even when editorial content
  contains angle brackets, ampersands, or quotation marks. The rendered document
  must display those characters without turning the content into HTML markup.
- Related articles appear in the order chosen by the editor. Omit missing,
  unlisted, and future references. Link titles use each related article's
  requested translation or its own default. Links retain the URL language even
  when the current article or a related article falls back to a default.
- Successful pages return status 200 and the UTF-8 HTML content type. The generic
  404 body is `Not found` with the UTF-8 plain-text content type. Unsupported
  language paths and paths without exactly a language and article name are 404s.

`app.py` is the adapter used by the hosting server. It receives a decoded path
without a query string and a timezone-aware current timestamp. `reading_room.py`
contains the article snapshot and presentation logic. Catalogue data meets the
configuration guarantees documented there; validation of publication input is
outside this task.
