import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--course_id', help='ID of the course', required=True, type=int)
parser.add_argument('-a', '--assignment_id', help='ID of the assignment', required=True, type=int)
parser.add_argument('-e', '--excel_path', help='Path to Excel file', required=True, type=str)
parser.add_argument('-d', '--dir_path', help='Path to attachment directory', required=True, type=str)
args = parser.parse_args()

course_id = args.course_id
assignment_id = args.assignment_id
excel_path = args.excel_path
dir_path = args.dir_path

import os

# check if the path is valid
if not os.path.exists(excel_path):
    logging.warning('Please check on the path to Excel file: {}'.format(excel_path))
    exit(1)
if not os.path.exists(dir_path):
    logging.warning('Please check on the path to attachment directory: {}'.format(dir_path))
    exit(1)

import logging

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from dotenv import load_dotenv

from utils import *

logging.basicConfig(level=logging.WARNING)

# load environment variables from test or production environment
load_dotenv('test.env') 
BASE_URL = os.getenv('BASE_URL')  # Canvas API BASE URL
API_KEY = os.getenv('API_KEY') # Canvas API key

# retrieve course and assignment
client = Canvas(BASE_URL, API_KEY)
try:
    course = client.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
except CanvasException as e:
    print(e)
    exit(1)

# read scores from excel
id2score=get_id2score(excel_path)

# read attachments from directory
id2path = get_id2path(dir_path)

# upload attachment to comments using assignment_id
submissions = assignment.get_submissions()
for submission in submissions:
    user_id = submission.user_id
    try:
        submission.edit(submission={
            'posted_grade': id2score[user_id]
        })
        print('User {} has been graded'.format(user_id))
        file_path = id2path[user_id]
        submission.upload_comment(file_path)
        print('File {} has been uploaded for user {}'.format(file_path, user_id))
    except KeyError as e:
        logging.warning('Please check on user {}: failed at entering score or uploading attachment'.format(user_id))
    except CanvasException as e:
        logging.warning(e)


