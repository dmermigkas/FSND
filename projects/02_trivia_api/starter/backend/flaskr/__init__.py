import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  cors = CORS(app, resources={r"*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()

    if categories is None:
        abort(404)
    else:
      return jsonify({
        'success': True,
        'categories': {category.id :category.type for category in categories}
      })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query
    formatted_questions = [q.format() for q in questions.order_by(Question.id).all()]

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    if questions is None:
        abort(404)
    else:
      return jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'totalQuestions': questions.count(),
        'categories': {category.id :category.type for category in categories},
        'currentCategory': formatted_categories[0]
      })

  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    print(body.get('searchTerm'))
    if body.get('searchTerm') is None:
      try:
        question = Question(question=body.get('question'), answer=body.get('answer'), category=body.get('category'), difficulty=body.get('difficulty'))
        question.insert()

        return jsonify({
          'success': True
        })
      except e as Exception:
        abort(422)
    else:
      questions = Question.query.filter(Question.question.contains(body.get('searchTerm')))

      if questions is None:
        abort(404)
      else:
        return jsonify({
          'success': True,
          'questions': [q.format() for q in questions.order_by(Question.id).all()],
          'totalQuestions': questions.count(),
          'currentCategory': {}
        })
  
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    question = Question.query.filter(Question.id == question_id).one()

    try:
      question.delete()
      return jsonify({
        'success': True
      })
    except e as Exception:
      abort(404)
      

  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

    category = Category.query.filter(Category.id == category_id).one()

    questions = Question.query.filter(Question.category == category.id).order_by(Question.id)
    formatted_questions = [q.format() for q in questions.all()]

    if questions is None:
        abort(404)
    else:
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'totalQuestions': questions.count(),
        'currentCategory': category.format()
      })

  @app.route('/quizzes', methods=['POST'])
  def post_quiz():

    body = request.get_json()
    formatted_questions = []
    
    if int(body.get('quiz_category')['id']) == 0:
      questions = Question.query.order_by(Question.id)
      formatted_questions = [q.format() for q in questions.all()]

      if len(body.get('previous_questions')) > 0:
        temp = []
        for q in formatted_questions:
          if q['id'] not in body.get('previous_questions'):
            temp.append(q)
        formatted_questions = temp

      print(len(formatted_questions), 'lennnn1')

      if formatted_questions is None:
          abort(404)
      else:
        return jsonify({
          'success': True,
          'question': random.choice(formatted_questions)
        })
    else:
      category = Category.query.filter(Category.id == int(body.get('quiz_category')['id'])).one()
      print(category)

      questions = Question.query.filter(Question.category == category.id).order_by(Question.id)
      formatted_questions = [q.format() for q in questions.all()]

      if len(body.get('previous_questions')) > 0:
        temp = []
        for q in formatted_questions:
          if q['id'] not in body.get('previous_questions'):
            temp.append(q)
        formatted_questions = temp

      print(formatted_questions, 'lennnn')

      if formatted_questions is None:
          abort(404)
      else:
        return jsonify({
          'success': True,
          'question': random.choice(formatted_questions)
        })

  @app.route('/')
  def index():
    return jsonify({
      'test': 'testing'
    })

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not found'
    }), 404

  @app.errorhandler(422)
  def unproccessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Entity'
    }), 422

  @app.errorhandler(500)
  def unproccessable(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500
  
  # '''
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  # '''

  # '''
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  # '''

  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests 
  # for all available categories.
  # '''


  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests for questions, 
  # including pagination (every 10 questions). 
  # This endpoint should return a list of questions, 
  # number of total questions, current category, categories. 

  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 
  # '''

  # '''
  # @TODO: 
  # Create an endpoint to DELETE question using a question ID. 

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 
  # '''

  # '''
  # @TODO: 
  # Create an endpoint to POST a new question, 
  # which will require the question and answer text, 
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  
  # '''

  # '''
  # @TODO: 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
  # '''

  # '''
  # @TODO: 
  # Create a GET endpoint to get questions based on category. 

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # '''


  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
  # '''

  # '''
  # @TODO: 
  # Create error handlers for all expected errors 
  # including 404 and 422. 
  # '''

  
  return app

    