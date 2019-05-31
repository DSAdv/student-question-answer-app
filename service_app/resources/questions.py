from flask import Blueprint
from flask_restful import fields, Resource, Api, marshal_with



answer_fields = {
    "id": fields.Integer(),
    "text": fields.String(),
    "rating": fields.Integer(default=0),
    "question_id": fields.Integer(),
}

question_fields = {
    "id": fields.Integer(),
    "text": fields.String(),
    "subject": fields.String(),
    "user_id": fields.Integer(),
    "rating": fields.Integer(default=0),
    "tags": fields.List(cls_or_instance=str),
    "answers": fields.Nested(answer_fields, allow_null=True),
}

bp = Blueprint("questions", __name__, url_prefix="/questions")
api = Api(bp, prefix="/api/v1")


class AnswerList(Resource):
    @marshal_with(answer_fields)
    def get(self):
        return [question["answers"] for question in connector.db.questions.find()]


class Answer(Resource):
    @marshal_with(answer_fields)
    def get(self):
        pass

    @marshal_with(answer_fields)
    def post(self):
        pass

    @marshal_with(answer_fields)
    def put(self):
        pass

    def delete(self):
        pass


class QuestionList(Resource):

    @marshal_with(question_fields)
    def get(self):
        return list(connector.db.questions.find())


class Question(Resource):

    @marshal_with(question_fields)
    def get(self, question_id):
        pass

    @marshal_with(question_fields)
    def post(self, question_id):
        pass

    @marshal_with(question_fields)
    def put(self, question_id):
        pass

    def delete(self, question_id):
        pass


api.add_resource(QuestionList, "/")
api.add_resource(Question, "/<question_id>")


from service_app.app import connector

