import tempfile
import unittest
from pathlib import Path
import app as cookbook


class MealPlannerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_database = cookbook.DATABASE
        cookbook.DATABASE = str(Path(self.directory.name) / 'test.db')
        cookbook.app.config['TESTING'] = True
        cookbook.init_db()
        with cookbook.get_db() as db:
            db.execute("INSERT INTO users VALUES (1, 'one', 'one@example.com', 'unused')")
            db.execute("INSERT INTO users VALUES (2, 'two', 'two@example.com', 'unused')")
            db.execute("INSERT INTO recipes (title, instructions) VALUES ('Test soup', 'Boil water.')")
            db.execute("INSERT INTO recipes (title, instructions) VALUES ('Test salad', 'Mix vegetables.')")
        self.client = cookbook.app.test_client()

    def tearDown(self):
        cookbook.DATABASE = self.old_database
        self.directory.cleanup()

    def login(self, user=1):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user)
            session['_fresh'] = True

    def save(self, **overrides):
        values = dict(week='2026-10-19', meal_date='2026-10-19', meal_type='Dinner', recipe_id='1')
        values.update(overrides)
        return self.client.post('/meal-planner', data=values, follow_redirects=True)

    def test_requires_login(self):
        self.assertEqual(self.client.get('/meal-planner').status_code, 302)
        self.assertEqual(self.client.post('/meal-planner').status_code, 302)

    def test_add_replace_remove_and_persistence(self):
        self.login()
        self.assertEqual(self.save().status_code, 200)
        self.assertIn(b'Test soup</a>', self.client.get('/meal-planner?week=2026-10-19').data)
        self.save(recipe_id='2')
        with cookbook.get_db() as db:
            rows = db.execute('SELECT * FROM meal_plans').fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['recipe_id'], 2)
        self.save(action='remove', recipe_id='2')
        with cookbook.get_db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM meal_plans').fetchone()[0], 0)

    def test_users_and_weeks_are_isolated(self):
        self.login()
        self.save()
        self.assertNotIn(b'Test soup</a>', self.client.get('/meal-planner?week=2026-10-26').data)
        self.login(2)
        self.assertNotIn(b'Test soup</a>', self.client.get('/meal-planner?week=2026-10-19').data)
        self.save(action='remove')
        with cookbook.get_db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM meal_plans').fetchone()[0], 1)

    def test_invalid_input(self):
        self.login()
        for values in [dict(week='invalid'), dict(meal_date='2026-11-01'), dict(meal_type='invalid'), dict(recipe_id='999'), dict(recipe_id='invalid')]:
            self.assertEqual(self.save(**values).status_code, 400)

    def test_empty_state_and_existing_pages(self):
        self.login()
        for path in ['/', '/login', '/register', '/saved', '/recipe/1', '/meal-planner']:
            self.assertEqual(self.client.get(path).status_code, 200, path)
        with cookbook.get_db() as db:
            db.execute('DELETE FROM recipes')
        self.assertIn(b'No recipes are available yet', self.client.get('/meal-planner').data)


if __name__ == '__main__':
    unittest.main()
