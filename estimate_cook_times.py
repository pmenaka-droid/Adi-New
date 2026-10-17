import sqlite3


DATABASE = 'cookbook.db'


COOK_TIME_BY_DIFFICULTY = {
    'Easy': 20,
    'Medium': 40,
    'High': 75,
}


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def estimate_cook_times():
    db = get_db()


    missing = db.execute(
       'SELECT recipe_id, difficulty FROM recipes WHERE cook_time IS NULL'
    ).fetchall()


    updated_counts = {'Easy': 0, 'Medium': 0, 'High': 0, 'Unknown': 0}


    for recipe in missing:
       difficulty = recipe['difficulty']
       estimated_time = COOK_TIME_BY_DIFFICULTY.get(difficulty)


       if estimated_time is None:
            # Difficulty itself was somehow missing too — fall back to a
            # safe default rather than leaving cook_time blank again.
            estimated_time = 30
            updated_counts['Unknown'] += 1
       else:
            updated_counts[difficulty] += 1


       db.execute(
            'UPDATE recipes SET cook_time = ? WHERE recipe_id = ?',
            (estimated_time, recipe['recipe_id'])
       )
   db.commit()
   db.close()


   print(f"Estimated cook_time for {len(missing)} recipes that had none:")
   for key, count in updated_counts.items():
      if count:
          print(f"   {key}: {count}")


if __name__ == '__main__':
   estimate_cook_times()
