import csv
import os
import shutil
import sqlite3


DATABASE = 'cookbook.db'
CSV_FILE = 'kaggle_recipes.csv'
IMAGE_FOLDER = 'static/Food images'
UPLOAD_FOLDER = 'static/uploads'
MAX_RECIPES_TO_CHECK = 200
VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png']


csv.field_size_limit(10_000_000)


def get_db():
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  db.execute("PRAGMA foreign_keys = ON")
  return db


def find_image_file(image_name):
  if not image_name or image_name.strip() == '' or image_name.strip() == '#NAME?':
      return None


  name = image_name.strip()
  search_folders = [
      IMAGE_FOLDER,
      os.path.join(IMAGE_FOLDER, IMAGE_FOLDER),
  ]


  for folder in search_folders:
      for ext in VALID_EXTENSIONS:
             candidate = os.path.join(folder, name + ext)
             if os.path.isfile(candidate):
                return candidate


  return None


def link_images():
  db = get_db()
  os.makedirs(UPLOAD_FOLDER, exist_ok=True)
total_linked = 0
total_missing = 0
total_no_image_name = 0


with open(CSV_FILE, newline='', encoding='utf-8') as f:
   reader = csv.DictReader(f)


   for i, row in enumerate(reader):
        if i >= MAX_RECIPES_TO_CHECK:
           break


        title = (row.get('Title') or '').strip()
        image_name = row.get('Image_Name') or ''


        if not title:
           continue


        recipe_row = db.execute(
           'SELECT recipe_id FROM recipes WHERE title = ?', (title,)
        ).fetchone()


        if recipe_row is None:
           continue


        recipe_id = recipe_row['recipe_id']


        source_path = find_image_file(image_name)


        if source_path is None:
           if not image_name or image_name.strip() == '#NAME?':
                   total_no_image_name += 1
           else:
                   total_missing += 1
           continue


        _, ext = os.path.splitext(source_path)
        dest_filename = f'recipe_{recipe_id}{ext}'
        dest_path = os.path.join(UPLOAD_FOLDER, dest_filename)
        shutil.copy(source_path, dest_path)


        web_path = f'/static/uploads/{dest_filename}'
        db.execute(
                 'UPDATE recipes SET image_file = ? WHERE recipe_id = ?',
                 (web_path, recipe_id)
            )
            total_linked += 1


 db.commit()
 db.close()


 print(f"Done.")
 print(f"       Linked:               {total_linked}")
 print(f"       Missing image file:   {total_missing}")
 print(f"       No usable image name (blank or '#NAME?'): {total_no_image_name}")


if __name__ == '__main__':
 link_images()
