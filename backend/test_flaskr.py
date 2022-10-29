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
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Why is python faster", "answer": "Thirty One", "difficulty": 3, "category": 3}
         
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
    Write at least one test for each test for successful operation,
    and for expected errors.
    """
    # Test for endpoints that handles GET requests for all available
    # categories.

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))
    

    #Test get paginated questions success
    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
    

    # Test 404 for get_paginated_questions failure.
    def test_404_get_paginated_questions(self):
        res = self.client().get("/questions>page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")


    # Test delete question for successful execution 
    def test_delete_question(self):
        res = self.client().delete("/questions/12")
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == 12).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        self.assertEqual(data["deleted"], 12)
        self.assertTrue(data["total_questions"])
        self.assertEqual(question, None)



    # Test 422 for delete question failure
    def test_422_if_book_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


   # Test for create new question
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])


    #Test 422 for create new question failure
    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
             
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    # Test for questions search with results 
    
    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"search": "Peanut"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])


    # Test for questions search without results
    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"search": "ttttt"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    # Test get questions based on category success
    def test_get_question_for_category(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        

    # Test 404 question for category failure
    def test_404_question_for_category_failure(self):
        res = self.client().get("/categories/9/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")

    
    #Test play quiz for success
    def test_post_play_quiz(self):
        res = self.client().post("/quizzes", json = {'previous_questions': [5], 'quiz_category': {'id': 4}})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))


    # Test 404 play quiz failure 
    def test_404_play_quiz_failure(self):
        res = self.client().post("/quizzes", json = {'previous_questions': [], 'quiz_category': {'id':10}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
