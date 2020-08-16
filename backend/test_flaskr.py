import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    
    def setUp(self):
        """Define test variables and initialize app."""
        USER = os.getenv('PGUSER')
        PASSWORD = os.environ.get('PGPASSWORD')
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            USER, PASSWORD, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            'question': 'How many minutes in the hour',
            'answer': '60',
            'difficulty': 1,
            'category': 1
        }
        
        self.wrong_question_category = {
            'question': 'How many minutes in the hour',
            'answer': '60',
            'difficulty': 1,
            'category': 70
        }
        self.quizcategory={"previous_questions":[],"quiz_category":{"type":"Science","id":"1"}}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_422_if_question_creation_fails(self):
        res = self.client().post('/questions', json=self.wrong_question_category)
        self.assertEqual(res.status_code, 422)

    def test_delete_question(self):
      
        
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], '4')

    def test_422_if_delete_question_Id_notfound(self):
        res = self.client().delete('/questions/190')
        self.assertEqual(res.status_code, 422)
      

    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={"searchTerm":"whose"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_question_of_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_question_of_invalid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Resource Not Found')

    def test_quizzes(self):
        res = self.client().post('/quizzes', json=self.quizcategory)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
      

    def test_404_access_undefined_route(self):
        res = self.client().post('/quiz')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()