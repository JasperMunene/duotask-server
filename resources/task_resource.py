from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.task import Task
from models.task_image import TaskImage
from models.category import Category
from models.task_location import TaskLocation

class TaskResource:
    @jwt_required()
    def get(self):
        pass
