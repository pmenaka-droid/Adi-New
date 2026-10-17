import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
from datetime import date, timedelta
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'cookbook-secret-2025'


DATABASE = 'cookbook.db'


def get_db():
   """Open one database connection per request"""
   db = sqlite3.connect(DATABASE)
   db.row_factory = sqlite3.Row
   db.execute("PRAGMA foreign_keys = ON")
   return db


def init_db():
   """Create application tables without replacing existing data."""
   db = get_db()
   db.executescript('''
      CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email      TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
      );


      CREATE TABLE IF NOT EXISTS recipes (
            recipe_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title          TEXT NOT NULL,
            instructions TEXT NOT NULL,
            category       TEXT,
            cook_time      INTEGER,
            difficulty     TEXT,
            dietary        TEXT,
            image_file     TEXT,
            likes          INTEGER DEFAULT 0,
            dislikes       INTEGER DEFAULT 0,
            uploader_id    INTEGER,
               FOREIGN KEY (uploader_id) REFERENCES users(user_id)
          );


          CREATE TABLE IF NOT EXISTS ingredients (
               ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
               name            TEXT NOT NULL UNIQUE
          );


          CREATE TABLE IF NOT EXISTS recipe_ingredients (
               recipe_id       INTEGER,
               ingredient_id INTEGER,
               quantity        TEXT,
               PRIMARY KEY (recipe_id, ingredient_id),
               FOREIGN KEY (recipe_id)
                  REFERENCES recipes(recipe_id),
               FOREIGN KEY (ingredient_id)
                  REFERENCES ingredients(ingredient_id)
          );


          CREATE TABLE IF NOT EXISTS saved_recipes (
               user_id     INTEGER,
               recipe_id INTEGER,
               PRIMARY KEY (user_id, recipe_id),
               FOREIGN KEY (user_id)
                  REFERENCES users(user_id),
               FOREIGN KEY (recipe_id)
                  REFERENCES recipes(recipe_id)
          );
      CREATE TABLE IF NOT EXISTS meal_plans (
          user_id INTEGER NOT NULL REFERENCES users(user_id),
          meal_date TEXT NOT NULL,
          meal_type TEXT NOT NULL CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner')),
          recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id),
          PRIMARY KEY (user_id, meal_date, meal_type)
      );
   ''')
   db.commit()
   db.close()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
   def __init__(self, user_id, username, email):
          self.id = user_id
          self.username = username
          self.email = email
@login_manager.user_loader
def load_user(user_id):
   db = get_db()
   row = db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
   db.close()
   if row:
         return User(row['user_id'], row['username'], row['email'])
   return None


@app.route('/')
def index():
   db = get_db()


   ingredient_query = request.args.get('ingredient', '').strip()
   category_query = request.args.get('category', '').strip()
   difficulty_query = request.args.get('difficulty', '').strip()
   dietary_query = request.args.get('dietary', '').strip()
   cook_time_query = request.args.get('cook_time', '').strip()


   sql = '''
         SELECT DISTINCT recipes.*
         FROM recipes
         LEFT JOIN recipe_ingredients ON recipes.recipe_id =
recipe_ingredients.recipe_id
         LEFT JOIN ingredients ON recipe_ingredients.ingredient_id =
ingredients.ingredient_id
         WHERE 1=1
   '''
   params = []


   if ingredient_query:
         sql += ' AND ingredients.name LIKE ?'
         params.append('%' + ingredient_query + '%')


   if category_query:
         sql += ' AND recipes.category = ?'
         params.append(category_query)


   if difficulty_query:
         sql += ' AND recipes.difficulty = ?'
         params.append(difficulty_query)
   if dietary_query:
       sql += ' AND recipes.dietary = ?'
       params.append(dietary_query)


   if cook_time_query == 'under30':
       sql += ' AND recipes.cook_time < 30'
   elif cook_time_query == '30to60':
       sql += ' AND recipes.cook_time >= 30 AND recipes.cook_time <= 60'
   elif cook_time_query == 'over60':
       sql += ' AND recipes.cook_time > 60'


   recipes = db.execute(sql, params).fetchall()


   categories = [row['category'] for row in db.execute('SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL').fetchall()]
   difficulties = [row['difficulty'] for row in db.execute('SELECT DISTINCT difficulty FROM recipes WHERE difficulty IS NOT NULL').fetchall()]
   dietary_options = [row['dietary'] for row in db.execute('SELECT DISTINCT dietary FROM recipes WHERE dietary IS NOT NULL').fetchall()]


   sidebar_saved_recipes = []
   if current_user.is_authenticated:
       sidebar_saved_recipes = db.execute(
           """SELECT recipes.recipe_id, recipes.title FROM recipes
              JOIN saved_recipes ON recipes.recipe_id = saved_recipes.recipe_id
              WHERE saved_recipes.user_id = ? ORDER BY recipes.title""",
           (current_user.id,)
       ).fetchall()

   db.close()
   return render_template(
       'index.html',
       sidebar_saved_recipes=sidebar_saved_recipes,
       recipes=recipes,
       categories=categories,
       difficulties=difficulties,
       dietary_options=dietary_options
   )




@app.route('/register', methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']
       hashed_pw = generate_password_hash(password)


       db = get_db()
       try:
           db.execute(
               'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
               (username, email, hashed_pw)
           )
           db.commit()
       except sqlite3.IntegrityError:
           flash('Username or email already taken.')
           db.close()
           return redirect(url_for('register'))
       db.close()
       return redirect(url_for('login'))


   return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']


      db = get_db()
      row = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
      db.close()


      if row and check_password_hash(row['password'], password):
           user = User(row['user_id'], row['username'], row['email'])
           login_user(user)
           return redirect(url_for('index'))
      else:
           flash('Invalid email or password.')


   return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('index'))




@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
   db = get_db()


   recipe_data = db.execute('SELECT * FROM recipes WHERE recipe_id = ?',
(recipe_id,)).fetchone()


   if recipe_data is None:
      db.close()
      return "Recipe not found", 404


   ingredients = db.execute('''
      SELECT ingredients.name, recipe_ingredients.quantity
      FROM recipe_ingredients
      JOIN ingredients ON recipe_ingredients.ingredient_id =
ingredients.ingredient_id
      WHERE recipe_ingredients.recipe_id = ?
   ''', (recipe_id,)).fetchall()


   is_saved = False
   if current_user.is_authenticated:
      saved_row = db.execute(
           'SELECT * FROM saved_recipes WHERE user_id = ? AND recipe_id = ?',
           (current_user.id, recipe_id)
      ).fetchone()
      is_saved = saved_row is not None


   db.close()
   return render_template('recipe.html', recipe=recipe_data, ingredients=ingredients,
is_saved=is_saved)




@app.route('/save/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_save(recipe_id):
   db = get_db()


   already_saved = db.execute(
      'SELECT * FROM saved_recipes WHERE user_id = ? AND recipe_id = ?',
      (current_user.id, recipe_id)
   ).fetchone()


   if already_saved:
      db.execute(
           'DELETE FROM saved_recipes WHERE user_id = ? AND recipe_id = ?',
           (current_user.id, recipe_id)
      )
   else:
      db.execute(
           'INSERT INTO saved_recipes (user_id, recipe_id) VALUES (?, ?)',
           (current_user.id, recipe_id)
      )


   db.commit()
   db.close()
   return redirect(url_for('recipe', recipe_id=recipe_id))




@app.route('/like/<int:recipe_id>', methods=['POST'])
@login_required
def like_recipe(recipe_id):
   db = get_db()
   db.execute('UPDATE recipes SET likes = likes + 1 WHERE recipe_id = ?',
(recipe_id,))
   db.commit()
   db.close()
   return redirect(url_for('recipe', recipe_id=recipe_id))




@app.route('/saved')
@login_required
def saved_recipes():
   db = get_db()
   recipes = db.execute('''
      SELECT recipes.*
      FROM recipes
      JOIN saved_recipes ON recipes.recipe_id = saved_recipes.recipe_id
      WHERE saved_recipes.user_id = ?
   ''', (current_user.id,)).fetchall()
   db.close()
   return render_template('saved.html', recipes=recipes)




MEAL_TYPES = ('Breakfast', 'Lunch', 'Dinner')


@app.route('/meal-planner', methods=['GET', 'POST'])
@login_required
def meal_planner():
    raw_week = request.values.get('week', date.today().isoformat())
    try:
        selected = date.fromisoformat(raw_week)
        monday = selected - timedelta(days=selected.weekday())
        days = [monday + timedelta(days=i) for i in range(7)]
        previous_week = monday - timedelta(days=7)
        next_week = monday + timedelta(days=7)
    except (ValueError, OverflowError):
        abort(400, 'Invalid week.')

    db = get_db()
    try:
        if request.method == 'POST':
            meal_date = request.form.get('meal_date', '')
            meal_type = request.form.get('meal_type', '')
            recipe_id = '' if request.form.get('action') == 'remove' else request.form.get('recipe_id', '')
            if meal_date not in [day.isoformat() for day in days] or meal_type not in MEAL_TYPES:
                abort(400, 'Invalid meal slot.')
            if recipe_id:
                if not recipe_id.isdecimal() or not db.execute(
                    'SELECT 1 FROM recipes WHERE recipe_id = ?', (recipe_id,)
                ).fetchone():
                    abort(400, 'Choose an existing recipe.')
                db.execute(
                    """INSERT INTO meal_plans (user_id, meal_date, meal_type, recipe_id)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(user_id, meal_date, meal_type)
                       DO UPDATE SET recipe_id = excluded.recipe_id""",
                    (current_user.id, meal_date, meal_type, recipe_id)
                )
            else:
                db.execute(
                    'DELETE FROM meal_plans WHERE user_id = ? AND meal_date = ? AND meal_type = ?',
                    (current_user.id, meal_date, meal_type)
                )
            db.commit()
            return redirect(url_for('meal_planner', week=monday.isoformat()))
        recipes = db.execute('SELECT recipe_id, title FROM recipes ORDER BY title').fetchall()
        rows = db.execute(
            """SELECT meal_plans.*, recipes.title FROM meal_plans
               JOIN recipes USING (recipe_id)
               WHERE user_id = ? AND meal_date BETWEEN ? AND ?""",
            (current_user.id, days[0].isoformat(), days[-1].isoformat())
        ).fetchall()
    finally:
        db.close()
    plan = {(row['meal_date'], row['meal_type']): row for row in rows}
    return render_template('meal_planner.html', days=days, meal_types=MEAL_TYPES,
                           recipes=recipes, plan=plan, week=monday.isoformat(),
                           previous_week=previous_week.isoformat(), next_week=next_week.isoformat())


if __name__ == '__main__':
   os.makedirs('static/uploads', exist_ok=True)
   init_db()
   app.run(debug=True, host='0.0.0.0', port=5001)
