import logging
import os
import re

import bs4
import pandas as pd
import requests


def get_id2path(dir_path):
    """Read the directory and return a dictionary of id -> path.

    Args:
        dir_path (str): directory that contains the files to be uploaded

    Returns:
        dictionary: mapping from id to the file's full path to be uploaded
    """    
    file_names = os.listdir(dir_path)

    id2path = {}
    for f_name in file_names:
        try:
            id2path[int(f_name.split('_')[-3])] = os.path.join(dir_path, f_name)
        except Exception as e:
            logging.warning('File \"{}\" does not have the correct format <sectionId>_<lastName>_<firstName>_<userId>_<studentId>_<Id> and thus ignored'.format(f_name))
    return id2path

def get_id2score(excel_path, id_col_idx, score_col_idx):
    """Read the excel file and return a dictionary of id -> score. Ignore the rows with empty score or non-numeric score.
    """
    df = pd.read_excel(excel_path)
    id2score = {}
    for i in range(len(df)):
        id = df.iloc[i, id_col_idx]
        score = df.iloc[i, score_col_idx]
        if not pd.isnull(score) and type(score) in [int, float]:
            id2score[id] = score
    return id2score

FIRST_QUESTION_ID=None
def get_question_id(course_id, quiz_id, question_num, API_KEY):
    """Web scrape the page. Fail at scraping webpage due to lack of authentication to view the page.
    """
    global FIRST_QUESTION_ID
    if FIRST_QUESTION_ID is None:
        url = 'https://osu.beta.instructure.com/courses/{}/quizzes/{}/take'.format(course_id, quiz_id)
        page = requests.get(url, params={'preview': '1'}, headers={'Authorization': 'Bearer {}'.format(API_KEY)})
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        question_id = soup.find_all(id=re.compile(r'^question_'))[0].get('id')
        FIRST_QUESTION_ID = question_id
    else:
        return FIRST_QUESTION_ID + question_num - 1



if __name__ == '__main__':
    # test get_id2path
    # dir_path = '/Users/wang/Library/CloudStorage/OneDrive-TheOhioStateUniversity/22 Autumn/1250/final/3pm/1250-3-f1-graded'
    # id2path = get_id2path(dir_path)
    # print(id2path)

    # test get_id2score
    # excel_path = './test_scores.xlsx'
    # id2score = get_id2score(excel_path)
    # print(id2score)

    # test get_question_id
    course_id = 130230
    quiz_id = 816752
    question_num = 1
    API_KEY = ''
    question_id = get_question_id(course_id, quiz_id, question_num, API_KEY)

   