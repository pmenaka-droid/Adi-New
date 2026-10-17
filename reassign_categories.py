import sqlite3


DATABASE = 'cookbook.db'


CATEGORY_KEYWORDS = [
    ('Breakfast', ['breakfast', 'pancake', 'waffle', 'omelet', 'oatmeal', 'granola',
'muffin', 'brunch', 'french toast']),
    ('Dessert',      ['cake', 'cookie', 'pie', 'brownie', 'dessert', 'pudding', 'tart',
'ice cream', 'chocolate', 'cheesecake', 'sweet']),
    ('Beverage',     ['smoothie', 'cocktail', 'drink', 'juice', 'lemonade', 'shake',
'punch']),
    ('Soup',         ['soup', 'stew', 'chili', 'bisque', 'chowder']),
    ('Salad',        ['salad']),
    ('Bread',        ['bread', 'loaf', 'roll', 'biscuit', 'bagel']),
    ('Snack',        ['snack', 'dip', 'popcorn', 'chips', 'bar']),
    ('Dinner',       ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'curry',
                       'casserole', 'roast', 'steak', 'taco', 'burger', 'pizza', 'stir
fry', 'meatball', 'lamb']),
]


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def guess_category(title):
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS:
       for keyword in keywords:
               if keyword in title_lower:
                   return category
    return 'Other'


def guess_difficulty(ingredient_count, instruction_word_count):
    if ingredient_count <= 5 and instruction_word_count <= 80:
       return 'Easy'
    if ingredient_count >= 12 or instruction_word_count >= 250:
       return 'High'
    return 'Medium'


def reassign():
   db = get_db()


   uncategorized = db.execute(
      "SELECT recipe_id, title FROM recipes WHERE category = 'Uncategorized'"
   ).fetchall()


   category_counts = {}
   for recipe in uncategorized:
      new_category = guess_category(recipe['title'])
      db.execute(
             'UPDATE recipes SET category = ? WHERE recipe_id = ?',
             (new_category, recipe['recipe_id'])
      )
      category_counts[new_category] = category_counts.get(new_category, 0) + 1


   all_recipes = db.execute('SELECT recipe_id, instructions FROM recipes').fetchall()


   difficulty_counts = {'Easy': 0, 'Medium': 0, 'High': 0}
   for recipe in all_recipes:
      ingredient_count = db.execute(
             'SELECT COUNT(*) as c FROM recipe_ingredients WHERE recipe_id = ?',
             (recipe['recipe_id'],)
      ).fetchone()['c']


      instruction_word_count = len((recipe['instructions'] or '').split())


      new_difficulty = guess_difficulty(ingredient_count, instruction_word_count)
      db.execute(
             'UPDATE recipes SET difficulty = ? WHERE recipe_id = ?',
             (new_difficulty, recipe['recipe_id'])
      )
      difficulty_counts[new_difficulty] += 1


   db.commit()
   db.close()


   print(f"Categories reassigned for {len(uncategorized)} previously 'Uncategorized'
recipes:")
   for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
      print(f"     {cat}: {count}")


   print(f"\nDifficulty recomputed for all {len(all_recipes)} recipes:")
   for diff, count in difficulty_counts.items():
      print(f"   {diff}: {count}")


if __name__ == '__main__':
   reassign()
