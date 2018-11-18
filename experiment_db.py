import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

credential_file = os.path.join(os.path.dirname(__file__), 'credential.json')
with open(credential_file, 'r') as dataFile:
    credential_dict = json.loads(dataFile.read())
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credential_dict, scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
gc = gspread.authorize(credentials)
spreadsheet = gc.open('GR_DB')


class SpreadSheet():
    @classmethod
    def check_exists(cls, wks, student_id):
        user_list = wks.col_values(1)
        if student_id in user_list:
            return user_list.index(student_id) + 1
        else:
            return len(user_list) + 1

    @classmethod
    def update_topic_survey(cls, username, user_answer):
        wks = spreadsheet.worksheet('topic_survey')
        num = cls.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_answer)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    @classmethod
    def update_topic_result(cls, username, user_vector):
        wks = spreadsheet.worksheet('topic_result')
        num = cls.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_vector)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    @classmethod
    def update_normalized_topic_result(cls, username, user_vector):
        wks = spreadsheet.worksheet('normalized_topic_result')
        num = cls.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_vector)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    @classmethod
    def update_recommend_result(cls, username, recommend_spots):
        wks = spreadsheet.worksheet('recommend_result')
        num = cls.check_exists(wks, username)
        cell_list = wks.range("A{}:K{}".format(num, num))

        values = [username]
        values.extend(recommend_spots)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    @classmethod
    def update_recommend_survey(cls, username, user_answer):
        wks = spreadsheet.worksheet('recommend_survey')

    @classmethod
    def update_selected_spots(cls, username, selected_spots):
        wks = spreadsheet.worksheet('selected_spots')
        num = cls.check_exists(wks, username)
        cell_list = wks.range("A{}:K{}".format(num, num))

        values = [username]
        values.extend(selected_spots)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)
