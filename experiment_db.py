import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json


class SpreadSheet():
    def __init__(self):
        credential_file = os.path.join(os.path.dirname(__file__), 'credential.json')
        with open(credential_file, 'r') as dataFile:
            credential_dict = json.loads(dataFile.read())
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credential_dict, scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        gc = gspread.authorize(credentials)
        self.spreadsheet = gc.open('GR_DB')

    def reload_spreadsheet(self):
        credential_file = os.path.join(os.path.dirname(__file__), 'credential.json')
        with open(credential_file, 'r') as dataFile:
            credential_dict = json.loads(dataFile.read())
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credential_dict, scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        gc = gspread.authorize(credentials)
        self.spreadsheet = gc.open('GR_DB')

    @classmethod
    def check_exists(cls, wks, student_id):
        user_list = wks.col_values(1)
        if student_id in user_list:
            return user_list.index(student_id) + 1
        else:
            return len(user_list) + 1

    def update_topic_survey(self, username, user_answer):
        # self.reload_spreadsheet()
        wks = self.spreadsheet.worksheet('topic_survey')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_answer)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_topic_result(self, username, user_vector):
        wks = self.spreadsheet.worksheet('topic_result')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_vector)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_normalized_topic_result(self, username, user_vector):
        # this function called first in show_recommend
        # self.reload_spreadsheet()
        wks = self.spreadsheet.worksheet('normalized_topic_result')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_vector)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_recommend_result(self, username, recommend_spots):
        wks = self.spreadsheet.worksheet('recommend_result')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:K{}".format(num, num))

        values = [username]
        values.extend(recommend_spots)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_recommend_survey_of_new(self, username, user_answer):
        # this function called first in recommend_survey
        # self.reload_spreadsheet()
        wks = self.spreadsheet.worksheet('recommend_survey_of_new')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_answer)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_recommend_survey_of_interest(self, username, user_answer):
        wks = self.spreadsheet.worksheet('recommend_survey_of_interest')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:AY{}".format(num, num))

        values = [username]
        values.extend(user_answer)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)

    def update_selected_spots(self, username, selected_spots):
        wks = self.spreadsheet.worksheet('selected_spots')
        num = self.check_exists(wks, username)
        cell_list = wks.range("A{}:K{}".format(num, num))

        values = [username]
        values.extend(selected_spots)

        for cell, v in zip(cell_list, values):
            cell.value = v
        wks.update_cells(cell_list)
