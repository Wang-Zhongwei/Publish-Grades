import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--course_id', help='ID of the course', required=True, type=int)
parser.add_argument('-q', '--quiz_id', help='ID of the quiz', required=True, type=int)
parser.add_argument('-Q', '--question_id', help='ID of the first question', required=True, type=int)
parser.add_argument('-a', '--assignment_id', help='ID of the assignment', required=True, type=int)
parser.add_argument('-e', '--excel_path', help='Path to Excel file', required=True, type=str)
parser.add_argument('-d', '--dir_path', help='Path to attachment directory', required=False, type=str)
args = parser.parse_args()

course_id = args.course_id
quiz_id = args.quiz_id
question_id = args.question_id
assignment_id = args.assignment_id
excel_path = args.excel_path
dir_path = args.dir_path
upload_attachment = True if dir_path else False

# check if the path is valid
import os
import logging

if not os.path.exists(excel_path):
    logging.warning('Please check on the path to Excel file: {}'.format(excel_path))
    exit(1)
if upload_attachment and not os.path.exists(dir_path):
    logging.warning('Please check on the path to attachment directory: {}'.format(dir_path))
    exit(1)

import dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

from utils import *

logging.basicConfig(level=logging.WARNING)

# load environment variables from test or production environment
dotenv.load_dotenv('production.env')
BASE_URL = os.getenv('BASE_URL')  # Canvas API BASE URL
API_KEY = os.getenv('API_KEY') # Canvas API key

client = Canvas(BASE_URL, API_KEY)
try: 
    course = client.get_course(course_id)
    quiz = course.get_quiz(quiz_id)
    assignment = course.get_assignment(assignment_id)
except CanvasException as e:
    logging.warning(e)
    exit(1)

# get id2score and id2path
id2score = get_id2score(excel_path)
id2path = get_id2path(dir_path) if upload_attachment else None
# submit scores and attachments
for submission in quiz.get_submissions():
    user_id = submission.user_id
    try: 
        submission.update_score_and_comments(
            quiz_submissions=[
                {
                    'attempt': 1,
                    'questions': {
                        question_id: {
                            'score': id2score[user_id],
                        },
                    }
                }
            ]
        )
        if not upload_attachment: continue
        file_path = id2path[user_id]
        assignment.get_submission(user_id).upload_comment(file_path)
        print('File {} has been uploaded for user {}'.format(file_path, user_id))
    except KeyError as e:
        logging.warning('Please check on user {}: failed at entering score or uploading attachment'.format(user_id))
    except CanvasException as e:
        logging.warning(e)
    