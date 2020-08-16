import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_question(request, selection):
  page = request.args.get('page', 1, type=int)
  print(page)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

   
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  @cross_origin()
  def retrieve_categories():
    categories=Category.query.order_by(Category.id).all()
    catlist={}
    for cat in categories:
      catlist[cat.id]=cat.type

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': catlist,
    }),200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions')
  @cross_origin()
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_question = paginate_question(request, selection)
    categories=Category.query.order_by(Category.id).all()
    catlist={}
    currcatlist={}
    for cat in categories:
      catlist[cat.id]=cat.type
    
    for q in selection:
      c=Category.query.filter(Category.id==q.category).first()
      currcatlist[c.id]= c.type
    if len(current_question) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_question,
      'totalQuestions': len(Question.query.all()),
      'categories': catlist,
      'current_category':currcatlist
    }),200
  

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<quest_id>', methods=['DELETE'])
  @cross_origin()
  def delete_question(quest_id):
  
    try:
      question=Question.query.filter(Question.id == quest_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()
      return jsonify({
      'success': True,
      'deleted': quest_id,
      
        }),200
    except:
      abort(422)
      
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  @cross_origin()
  def create_question():
    body = request.get_json()
    new_question =body.get('question', None) 
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty,category=new_category )
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id,
        'totalQuestions': len(Question.query.all())
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  @cross_origin()
  def search_question():
    exp=''
    body = request.get_json()
    searchTerm =body.get('searchTerm', None)
    if searchTerm is not None:
      exp='%'+searchTerm+'%'
    question_result=Question.query.filter(Question.question.ilike(exp)).all()
    questions = [question.format() for question in question_result]

    catlist={}
    for q in question_result:
      c=Category.query.filter(Category.id==q.category).first()
      catlist[c.id]= c.type

    return jsonify({
      'success': True,
      'questions': questions,
      'totalQuestions': len(questions),
      'current_category':catlist
    }),200


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 



  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<cat_id>/questions')
  def get_question_by_Category(cat_id):
    questions =Question.query.filter(Question.category==cat_id).all()
    current_question = paginate_question(request, questions)
    if len(current_question) == 0:
      abort(404)
    categories=Category.query.filter(Category.id==cat_id).first()
    currcatlist={}
    currcatlist[categories.id]=categories.type
   
    return jsonify({
      'success': True,
      'questions': current_question,
      'totalQuestions': len(questions),
      'current_category':currcatlist
    }),200


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 


  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  @cross_origin()
  def quizzes():
    body = request.get_json()
    previousQuestions =body.get('previous_questions')
    quizCategory =body.get('quiz_category', None)
    catid=quizCategory['id']
    if catid ==0:
      question_result =Question.query.all()
      
    else:  
      question_result =Question.query.filter(Question.category==catid).all()

    questions = [question.format() for question in question_result]
    currentQuestion=get_rondom_question(questions,previousQuestions)
    return jsonify({
        'success': True,
        "question": currentQuestion
    })

  def get_rondom_question(questions,previousQuestions):
      randomnum=random.randint(0,len(questions)-1)
      question = questions[randomnum]
      
      while question['id']  in previousQuestions:
        randomnum=random.randint(0,len(questions)-1)
        question = questions[randomnum]
        print("the rondom loop" ,randomnum )
        if len(previousQuestions) == len(questions):
          question = None
          break

      return question





  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
      }), 404

    @app.errorhandler(422)
    def unprocessable(error):
      return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
      }), 422

    
  return app

    