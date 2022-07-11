import enum
import re
import typing
from typing import List

from CPP_WebClassAPI.webclass.web_class import SemesterSelector


class FormatErrorException(Exception):
    pass


class IncorrectSemesterException(Exception):
    pass


class IncorrectGradeException(Exception):
    pass


class Faculty(enum.Enum):
    BUSINESS = 1
    ICT = 2
    ANIME = 3


class User(object):
    def __init__(self, student_number: str, password: str):

        if not re.fullmatch(r'[1-3]012\d0(0[1-9]|[1-7]\d|80)', student_number):
            raise FormatErrorException
        # Campus Plan Authentication
        self._student_number = student_number
        self._password = password

        # Admission Year
        self._admission_year = int('202' + self._student_number[4])

        # Faculty
        if int(self._student_number[0]) == Faculty.BUSINESS.value:
            self._faculty = '事業創造学部'
        elif int(self._student_number[0]) == Faculty.ICT.value:
            self._faculty = '情報学部'
        elif int(self._student_number[0]) == Faculty.ANIME.value:
            self._faculty = 'アニメ・マンガ学部'

    @property
    def id(self):
        return self._student_number

    @property
    def password(self):
        return self._password

    @property
    def faculty(self):
        return self._faculty

    @property
    def admission_year(self):
        return self._admission_year


class TakenCourses(object):
    def __init__(self,
                 user: User,
                 grade: int = None,
                 semester: List[int] = None,
                 target_courses: List[str] = None,
                 exclude_courses: List[str] = None,
                 strict_mode: bool = False):

        self._user = user

        # 学年は None または 1以上４以下の整数
        if grade is not None:
            if grade not in [1, 2, 3, 4]:
                raise IncorrectGradeException
        self._grade = grade

        # 学期は None または 1以上4以下の整数を要素とする集合
        if semester is not None:
            if not set(semester).issubset({1, 2, 3, 4}):
                raise IncorrectSemesterException
        self._semester = set(semester) if isinstance(semester, typing.Iterable) else None

        prefix, suffix = ('^', '$') if strict_mode else ('.*', '.*')
        self._target_courses = target_courses or []
        # この正規表現にマッチするコース名は取得する
        self._target_regexes = '|'.join(map(lambda element: f'{prefix}{element}{suffix}', self._target_courses))
        self._exclude_courses = exclude_courses or []
        # この正規表現にマッチするコース名は取得しない
        self._exclude_regexes = '|'.join(map(lambda element: f'{prefix}{element}{suffix}', self._exclude_courses))

        self._course_titles = []
        self._course_links = []
        self._title_link_dict = {}

    @property
    def user_info(self):
        return self._user

    @property
    def course_year(self):
        if self._grade is None:
            return
        return self._user.admission_year + (self._grade - 1)

    @property
    def course_semester(self):
        if self._semester is None:
            return

        if self._semester == {1, 2}:
            return SemesterSelector.FIRST_SECOND.value
        elif self._semester == {3, 4}:
            return SemesterSelector.THIRD_FOURTH.value
        elif self._semester == {1}:
            return SemesterSelector.FIRST.value
        elif self._semester == {2}:
            return SemesterSelector.SECOND.value
        elif self._semester == {3}:
            return SemesterSelector.THIRD.value
        elif self._semester == {4}:
            return SemesterSelector.FOURTH.value
        elif self._semester == {1, 2, 3, 4}:
            return SemesterSelector.ALL.value

    @property
    def target_regexes(self) -> str:
        return self._target_regexes

    @property
    def exclude_regexes(self) -> str:
        return self._exclude_regexes

    @property
    def titles(self):
        return tuple(self._course_titles)

    @property
    def links(self):
        return tuple(self._course_links)

    @property
    def titles_and_links(self):
        return self._title_link_dict

    def append_course(self, crs: str, url: str = None):
        # 余分な [» ] を消す
        course_name = crs.replace('» ', '')
        # 除外するコース名の正規表現にマッチしたら終了
        if re.fullmatch(self._exclude_regexes, course_name):
            return False
        # コース名に条件指定がない、または指定した正規表現にマッチすれば追加
        if self._target_regexes == '' or re.fullmatch(self._target_regexes, course_name):
            self._course_titles.append(course_name)
            url = '' if url is None else url
            self._course_links.append(url)
            self._title_link_dict[course_name] = url
            return True
        return False
