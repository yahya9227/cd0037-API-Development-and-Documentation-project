from crypt import methods
import os
import sys
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
import random
from random import choice
import collections
collections.Iterable = collections.abc.Iterable
from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def dictionary_categories(selection):
    categories = {category.id: category.type for category in selection}

    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    #CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    
    @app.route("/categories")
    def get_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = dictionary_categories(selection)
        
        if len(current_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": current_categories,
                "total_categories": len(Category.query.all())
            }
        )

    
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        c_selection = Category.query.order_by(Category.id).all()
        categories = dictionary_categories(c_selection)
        
        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category": "Placeholder",
                "categories": categories
            }
        )


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question_del = Question.query.filter(Question.id==question_id).one_or_none()

        try:

            if question_del is None:
                abort(404)

            question_del.delete()
            

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "total_questions": len(Question.query.all())

                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.


    """
    @app.route("/questions", methods=["POST"])
    def create_question():

        try:
            body = request.get_json()

            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
            search = body.get("searchTerm", None)

            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                    )
                current_questions = paginate_questions(request, selection)

                return jsonify(
                       {
                          "success": True,
                          "questions": current_questions,
                          "total_questions": len(selection.all()),
                       }
                    )
            else:    
                 question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                 question.insert()


                 return jsonify({
                        "success":True,
                        "created": question.id,
                        "total_questions": len(Question.query.all()),
                     })

        except:
            abort(422)

   

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def question_by_category(category_id):
        selection = Question.query.order_by(Question.id).filter(
            Question.category == category_id
        )
        questions = paginate_questions(request, selection)

        if len(questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "total_questions": len(selection.all()),
            }
        )
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods = ['POST'])
    def get_quizzes():
        body = request.get_json()
        previous_question = body.get("previous_questions", None)
        category = body.get("quiz_category", None)
        try:
            if category['id'] != 0:
               questions_query = Question.query.filter_by(category = category['id']).filter(Question.id.notin_(previous_question)).all()
               question = choice(questions_query).format()
            else:
               questions_query = Question.query.filter(Question.id.notin_(previous_question)).all()
               question = choice(questions_query).format()
        except:
              print(sys.exc_info())
              abort(404)

        return jsonify({
            "success": True,
            "question": question
            })


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app
