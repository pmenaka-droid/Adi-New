import csv
import ast
import sqlite3


DATABASE = 'cookbook.db'
CSV_FILE = 'kaggle_recipes.csv'
MAX_RECIPES_TO_IMPORT = 200


csv.field_size_limit(10_000_000)
def get_db():
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  db.execute("PRAGMA foreign_keys = ON")
  return db


def parse_ingredient_list(raw_value):
  try:
         ingredients = ast.literal_eval(raw_value)
         if isinstance(ingredients, list):
                return [i.strip() for i in ingredients if i and i.strip()]
  except (ValueError, SyntaxError):
         pass
  return []


def recipe_already_imported(db, title):
  row = db.execute('SELECT recipe_id FROM recipes WHERE title = ?',
(title,)).fetchone()
  return row is not None


def import_recipes():
  db = get_db()
  total_added = 0
  total_skipped = 0


  with open(CSV_FILE, newline='', encoding='utf-8') as f:
         reader = csv.DictReader(f)


         for row in reader:
                if total_added >= MAX_RECIPES_TO_IMPORT:
                   break


                title = (row.get('Title') or '').strip()
            instructions = (row.get('Instructions') or '').strip()
            raw_ingredients = row.get('Ingredients') or '[]'


            if not title or not instructions:
                total_skipped += 1
                continue


            if recipe_already_imported(db, title):
                total_skipped += 1
                continue


            ingredient_list = parse_ingredient_list(raw_ingredients)
            if not ingredient_list:
                total_skipped += 1
                continue


            cursor = db.execute(
                '''INSERT INTO recipes (title, instructions, category, cook_time,
difficulty)
                    VALUES (?, ?, ?, ?, ?)''',
                (title, instructions, 'Uncategorized', None, 'Medium')
            )
            recipe_id = cursor.lastrowid


            for ingredient_phrase in ingredient_list:
                name = ingredient_phrase.lower()
                db.execute(
                     'INSERT OR IGNORE INTO ingredients (name) VALUES (?)',
                     (name,)
                )
                ingredient_row = db.execute(
                     'SELECT ingredient_id FROM ingredients WHERE name = ?',
                     (name,)
                ).fetchone()


                db.execute(
    '''INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
      VALUES (?, ?, ?)''',
    (recipe_id, ingredient_row['ingredient_id'], '')
)


            total_added += 1
 db.commit()
 db.close()
 print(f"Done. Added {total_added} recipes ({total_skipped} skipped).")


if __name__ == '__main__':
 import_recipes()
