# Code extracted from GitHub Code (1).pdf

This is a direct text extraction of the supplied 41-page PDF. Only PDF page separators were removed from the source files. No code, spelling, wrapping, or indentation repairs have been applied. Original source filenames were not shown; filenames were inferred from template references and function names.

## Source map

- `templates/base.html`: PDF pages 1–2.
- `templates/index.html`: PDF pages 3–5.
- `templates/login.html`: PDF pages 6–6.
- `templates/recipe.html`: PDF pages 7–9.
- `templates/register.html`: PDF pages 10–11.
- `templates/saved.html`: PDF pages 12–12.
- `app.py`: PDF pages 13–20.
- `estimate_cook_times.py`: PDF pages 21–22.
- `import_recipes.py`: PDF pages 23–25.
- `link_images.py`: PDF pages 26–28.
- `reassign_categories.py`: PDF pages 29–31.
- `static/recipe-detail.css`: PDF pages 32–34.
- `static/style.css`: PDF pages 35–41.

## Current limitations

The PDF includes Python line wrapping and inconsistent indentation, so this exact transcription is not runnable yet. Flask and Flask-Login are referenced. The CSV (`kaggle_recipes.csv`), food images, and database contents are not included in the PDF; the application includes database schema initialization. No data or assets have been invented.

The unmodified text extraction, including page separators, is retained in `docs/pdf-extraction.txt`.

Syntax check results (source left unchanged):

- `app.py`: line 157: unterminated string literal (detected at line 157).
- `estimate_cook_times.py`: line 51: unindent does not match any outer indentation level.
- `import_recipes.py`: line 51: unindent does not match any outer indentation level.
- `link_images.py`: line 106: unexpected indent.
- `reassign_categories.py`: line 19: unterminated string literal (detected at line 19).
