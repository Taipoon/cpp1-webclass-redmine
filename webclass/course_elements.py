import re


class Content(object):
    def __init__(self):
        self._content_name = None
        self._content_url = None
        self._content_category = None
        self._content_label = None
        self._content_detail_list_item = []

    @property
    def content_name(self):
        return self._content_name

    @content_name.setter
    def content_name(self, content_name):
        self._content_name = content_name

    @property
    def content_url(self):
        return self._content_url

    @content_url.setter
    def content_url(self, url):
        self._content_url = url

    @property
    def content_category(self):
        return self._content_category

    @content_category.setter
    def content_category(self, category):
        self._content_category = category

    @property
    def content_detail_list_item(self):
        return self._content_detail_list_item

    def add_content_detail_list_item(self, list_item: dict):
        if not isinstance(list_item, dict):
            raise TypeError
        self._content_detail_list_item.append(list_item)


class Course(object):
    def __init__(self, course_title, course_url):
        self._course_title = course_title
        self._course_url = course_url
        self._contents = []

        self._compiled_regex = re.compile(r'^\d+\w{3}\d+$')

    def add_content(self, content: Content):
        self._contents.append(content)

    @property
    def title(self):
        return self._course_title

    @property
    def url(self):
        return self._course_url

    @property
    def course_code(self):
        return self._course_url.split('/')[-2]

    @property
    def contents(self):
        return self._contents


class Courses(object):
    def __init__(self):
        self._courses = []

    def add_course(self, course: Course):
        self._courses.append(course)

    @property
    def courses(self):
        return self._courses
