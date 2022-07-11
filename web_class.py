import enum


class PortalSite(object):
    # CampusPlan URL
    LOGIN_URL = 'https://portal.kaishi-pu.ac.jp/portal/Account/Login?ReturnUrl=%2Fportal%2F'
    # WebClass ウィンドウを開くJavaScript
    OPEN_WEB_CLASS_SCRIPT = """\
window.open('/portal/External/WebClass','LMS',\
'width=1200px,height=900px,menubar=no,status=no,titlebar=no,toolbar=no,\
resizable=yes,scrollbars=yes,location=no,close=yes');return false;\
"""

    @staticmethod
    def get_asc_param(url):
        # "asc_" GETパラメータを取得
        get_param = url.split('?')[1]
        return get_param.split('=')[1]


class SemesterSelector(enum.Enum):
    ALL = 'all'
    FIRST_SECOND = '1'
    THIRD_FOURTH = '2'
    FIRST = '3'
    SECOND = '4'
    THIRD = '5'
    FOURTH = '6'
