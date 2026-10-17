# Code extracted from GitHub Code (1).pdf

The project started as a text extraction of the supplied 41-page PDF. The application now includes a weekly meal planner and repairs to the main application needed to run it. The original extraction is preserved in `docs/pdf-extraction.txt`. Original source filenames were inferred from template references and function names.

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

The main application formatting has been repaired. The standalone dataset utility scripts still contain the PDF’s line wrapping and indentation errors and need repairs before use. The CSV (`kaggle_recipes.csv`), food images, and database contents are not included in the PDF; the application includes database schema initialization. No data or assets have been invented.

The unmodified text extraction, including page separators, is retained in `docs/pdf-extraction.txt`.

Original extraction syntax check results (the `app.py` issues below have since been repaired):

- `app.py`: line 157: unterminated string literal (detected at line 157).
- `estimate_cook_times.py`: line 51: unindent does not match any outer indentation level.
- `import_recipes.py`: line 51: unindent does not match any outer indentation level.
- `link_images.py`: line 106: unexpected indent.
- `reassign_categories.py`: line 19: unterminated string literal (detected at line 19).

## Run the application

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The development server uses port 5001. In Codespaces, open that port through the Ports panel. Startup creates any missing SQLite tables while keeping existing data.

Register or log in, then choose **Meal Planner** in the navigation. Select a recipe for any breakfast, lunch, or dinner slot and click **Save slot**. Use **Remove** to clear a slot and the week links to plan other weeks. Plans are saved separately for each account. Recipes must already exist in the database; the PDF did not include a recipe dataset.

Run the feature tests with:

```bash
python -m unittest discover -s tests -v
```
