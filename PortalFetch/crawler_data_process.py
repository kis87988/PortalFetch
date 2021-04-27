#!/usr/bin/env python
"""Process html course information to save in a .json file.

It requires file 'user.ini' to load the user's own user name and password.
"""
from bs4 import BeautifulSoup
import json
import time
import os


class DataProcess:
    """Deputy .html file to .json file.

    It needs to import an .html file from De Anza courses information website.
    """

    def __getRustContents(self, html):
        """
        Get rust list contents from html.

        Input: html is html of the courses
        Output : courseList will include all the courses list in text and some other contents
        Parameters: String
        Returns: List
        """
        rustCourseList = []
        soup = BeautifulSoup(html, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            ui = []
            for td in tr:
                if td == '\n':
                    continue
                elif td.string:
                    ui.append(str(td.string))
                else:
                    ui.append(td)
            if len(ui) == 19:
                rustCourseList.append(ui[:18])
        return rustCourseList

    def __getList(self, courseList, html):
        """
        Get course list from html.

        Input: html is html of the courses, courseList is an empty list []
        Output : courseList will include all the courses list in text
        Parameters: List, String
        Returns: None
        """
        ui = self.__getRustContents(html)
        for course in ui:
            temp = []
            for ele in course:
                if type(ele) is not str:
                    soup = BeautifulSoup(str(ele), 'lxml')
                    ele = soup.get_text()
                temp.append((ele))
            courseList.append(temp)

    def __deputyList(self, courseList):
        """
        Deputy courseList to a json file.

        Input: courseList is courses list from __getContents
        Output : .json file  will include all the courses information
        Parameters: List
        Returns: None
        """
        dic = {}
        title = ['Select', 'CRN', 'Coreq', 'Subj', 'Crse', 'Sec', 'Cmp', 'Cred', 'Title', 'Days', 'Time', 'Act', 'Rem',
                'WL Rem', 'Instructor', 'Date (MM/DD)', 'Location', 'Attribute', 'lab']
        for i in range(len(courseList)):
            # Create a new subject
            if courseList[i][0] == 'Select':
                subj = courseList[i+1][3]
                d = []
                dic[subj] = d
            else:
                # deputy one line of course information
                if courseList[i][0] != '\xa0':
                    di = {}
                    self.__deputyCourseLine(title, courseList[i], di)
                    dic[courseList[i][3]].append(di)
                # deputy lab information
                else:
                    dl = {}
                    # find the subject
                    j = i - 1
                    while courseList[j][3] == '\xa0':
                        j -= 1
                    subj = courseList[j][3]
                    self.__deputyLabLine(title, courseList[i], dl)
                    dic[subj][-1]['lab'].append(dl)
        return dic

    def __deputyCourseLine(self, title, oneLine, emptyDiction):
        """
        Deputy one line of courseList to the diction.

        Input: title is a list of courses' key words, oneLine is a line of course information, emptyDiction is {}
        Parameters: List, List, Dictionary
        Returns: None
        """
        count = -1
        for ele in oneLine:
            count += 1
            if count != 2 and count != 3:
                emptyDiction[title[count]] = ele if ele != '\xa0' else ''
        emptyDiction['lab'] = []

    def __deputyLabLine(self, title, labLine, emptyDiction):
        """
        Deputy one line of lab information to the diction.

        Input: title is a list of courses' key words, labLine is a line of course information, emptyDiction is {}
        Parameters: List, List, Dictionary
        Returns: None
        """
        count = -1
        for ele in labLine:
            count += 1
            if ele != '\xa0':
                emptyDiction[title[count]] = ele

    def htmlToJson(self, htmlFile, jsonFilename, quarter, fetchTime):
        """
        Deputy htmlFile to a json file.

        Input:  htmlFile is a .html file got from __deputyList,
                jsonFilename is .json file name you want to give for the output
                quarter is the name of the course quarter.
                fetchTime is the fetch time of crawler
        Output : .json file  will include all the courses information
        Parameters: string, string, string, string
        Returns: None
        """
        courseList = []
        self.__getList(courseList, htmlFile)
        d = self.__deputyList(courseList)
        output = {}
        output[quarter] = {}
        output[quarter]["FetchTime"] = fetchTime
        output[quarter]["CourseData"] = d
        if not os.path.exists('../output'):
            try:
                os.makedirs('../output')
            except OSError as e:
                logger.error("Unable to create output directory: %s", e)

        with open('../output/' + jsonFilename, 'w') as outfile:
            json.dump(output, outfile, indent=4)

    def data_process(self, html, filename, quarter):
        """
        Deputy HTML text to save in a .json file.

        input:  'html' is the HTML string.
                'filename' is the name of the saved .json.
                'quarter' is the quarter of the json file'
        output: save courses in a file 'filename'.json.
        Parameters: String, String, String
        Return: None
        """
        self.htmlToJson(html, filename, quarter, int(time.time()))

