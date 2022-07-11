import sys
import time

from colorama import Fore
from selenium.common.exceptions import *
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager

from .course_elements import *
from .user_info import TakenCourses
from .web_class import PortalSite


class SelectedYearIsNotFoundException(Exception):
    pass


class AvailableCoursesIsNotExistException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


def initialize_chrome_options():
    options = Options()
    # ウィンドウ非表示
    options.add_argument('--headless')
    # サンドボックスを無効化
    options.add_argument('--no-sandbox')
    # GPUアクセラレータを使用しない
    options.add_argument('--disable-gpu')
    # WebRTC メディア利用許可ダイアログを回避する
    options.add_argument('--use-fake-ui-for-_media-stream')
    # 拡張機能を無効化する
    options.add_argument('--disable-extensions')
    # ロギングの無効化
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    return options


def login_web_class(browser: Chrome, login_id: str, password: str):
    # ポータルサイトへアクセス
    browser.get(PortalSite.LOGIN_URL)
    # ログイン処理
    browser.find_element(by=By.ID, value='UserName').send_keys(login_id)
    browser.find_element(by=By.ID, value='Password').send_keys(password)
    browser.find_element(by=By.XPATH, value='/html/body/div[1]/div/section[1]/form/div[4]/input').click()
    # WebClassへアクセス(JSの実行) -> 新規タブで開く
    browser.execute_script(PortalSite.OPEN_WEB_CLASS_SCRIPT)
    # 新規タブを操作対象に変更
    browser.switch_to.window(browser.window_handles[-1])
    return browser


def fetch_course_list(my_crs: TakenCourses):
    # ブラウザの自動ダウンロードと起動
    browser = Chrome(ChromeDriverManager(path='.').install(), options=initialize_chrome_options())
    try:
        # ログイン
        browser = login_web_class(browser, my_crs.user_info.id, my_crs.user_info.password)

        # ログインに成功したかどうか(URLがログインURLから変更されたかどうか)
        for _ in range(3):
            if not re.fullmatch('.*portal/Account/Login.*', browser.current_url):
                break
            time.sleep(1)
        else:
            raise UnauthorizedException

        # 年度を指定する場合
        if my_crs.course_year is not None:
            try:
                year_select = Select(browser.find_element(by=By.NAME, value='year'))
                year_select.select_by_value(value=str(my_crs.course_year))
                time.sleep(0.5)
            except NoSuchElementException:
                print(Fore.LIGHTRED_EX +
                      f'{my_crs.course_year}年の情報はWebClassに存在しません。(ユーザー[{my_crs.user_info.id}])' +
                      Fore.RESET)
                raise SelectedYearIsNotFoundException

        if my_crs.course_semester is not None:
            try:
                semester_select = Select(browser.find_element(by=By.NAME, value='semester'))
                semester_select.select_by_value(value=my_crs.course_semester)
                time.sleep(0.5)
            except NoSuchElementException:
                pass

        # WebClassから結果を取得する
        print(Fore.CYAN + 'Web Classからコースリストを取得中...' + Fore.RESET)

        # コースリストを表す[class='course-title']要素を取得
        course_list = browser.find_elements(by=By.CLASS_NAME, value='course-title')
        # コースが1つも存在しない場合、例外を送出
        if not course_list:
            print(Fore.BLUE + '利用可能なコースはありません。' + Fore.RESET)
            raise AvailableCoursesIsNotExistException

        # 履修中のコースを取得する
        for course in course_list:
            # コース名の要素を取得
            course_element = course.find_element(by=By.TAG_NAME, value='a')
            my_crs.append_course(crs=course_element.text, url=course_element.get_attribute('href'))
        return my_crs

    except UnauthorizedException as e:
        # 認証に失敗した場合
        print(e)
        print(Fore.LIGHTRED_EX + 'ログインIDまたはパスワードが無効です。' + Fore.RESET)
        sys.exit(1)
    except NoSuchElementException as e:
        print(e)
        sys.exit(1)
    except JavascriptException as e:
        print(e)
        sys.exit(1)
    except ElementClickInterceptedException as e:
        print(e)
        sys.exit(1)
    except SelectedYearIsNotFoundException as e:
        print(e)
        sys.exit(1)
    except AvailableCoursesIsNotExistException as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print('中断しました')
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        browser.quit()


def fetch_contents(my_crs: TakenCourses):
    # ブラウザを起動
    browser = Chrome(ChromeDriverManager(path='.').install(), options=initialize_chrome_options())
    try:
        # ログイン
        browser = login_web_class(browser, my_crs.user_info.id, my_crs.user_info.password)

        # ログインに成功したかどうか(URLがログインURLから変更されたかどうか)
        for _ in range(3):
            if not re.fullmatch('.*portal/Account/Login.*', browser.current_url):
                break
            time.sleep(1)
        else:
            raise UnauthorizedException

        # WebClassから結果を取得する
        print(Fore.CYAN + 'Web Classからコンテンツを取得中...' + Fore.RESET)

        # すべてのコースを保持する Courses オブジェクト
        courses = Courses()
        # asc_ パラメータ
        # PortalSite.ASC_PARAM = None
        asc_param = None
        # 取得した講義数
        current_index = 0
        # (講義名で絞り込み済みの)すべての講義に対してアクセス
        for course_title, course_url in my_crs.titles_and_links.items():
            # １つのコースを保持する Course オブジェクト
            course = Course(course_title=course_title, course_url=course_url)

            # 進捗の表示
            current_index += 1
            progress = f'{Fore.LIGHTBLUE_EX} {(current_index / len(my_crs.titles) * 100):.1f} % 取得 {Fore.RESET}'
            print(progress, end='\r')

            if asc_param:
                # 現在のURLから asc_ パラメータの値を取得して、
                # 次のURLの asc_ パラメータの新しい値とする
                tmp = course_url.split('?')[0]
                course_url = tmp + f'?asc_={asc_param}'
            # 1つ1つの講義ページにアクセス
            browser.get(course_url)
            # 次のページのために asc_ パラメータの値を取得する
            asc_param = PortalSite.get_asc_param(browser.current_url)

            # 1つの講義のすべてのコンテンツ要素を取得
            contents_div = browser.find_elements(by=By.CLASS_NAME,
                                                 value='cl-contentsList_contentInfo')
            if not contents_div:
                # １つもコンテンツが存在しない場合は次のコースへ
                course.add_content(Content())
                courses.add_course(course)
                continue

            # 講義内のすべてのコンテンツにアクセス
            for content_div in contents_div:
                # １つのコンテンツを保持する Content オブジェクト
                content = Content()

                # コンテンツ名の要素を取得
                content_name_div = content_div.find_element(by=By.CLASS_NAME,
                                                            value='cm-contentsList_contentName')
                # コンテンツ名を取得
                content.content_name = content_name_div.text.replace('New\n', '')
                # コンテンツはアクセス可能か (リンクとしてクリックできるかどうか)
                try:
                    content.content_url = content_name_div.find_element(by=By.TAG_NAME,
                                                                        value='a').get_attribute('href')
                except NoSuchElementException:
                    pass
                # コンテンツカテゴリ
                try:
                    content.content_category = content_div.find_element(by=By.CLASS_NAME,
                                                                        value='cl-contentsList_categoryLabel').text
                except NoSuchElementException:
                    pass

                # ContentDetailListItem
                list_item_divs = content_div.find_elements(by=By.CLASS_NAME,
                                                           value='cm-contentsList_contentDetailListItem')

                for list_item_div in list_item_divs:
                    try:
                        list_item_label = list_item_div.find_element(by=By.CLASS_NAME,
                                                                     value='cm-contentsList_contentDetailListItemLabel').text
                    except NoSuchElementException:
                        list_item_label = ''

                    try:
                        list_item_data = content_div.find_element(by=By.CLASS_NAME,
                                                                  value='cm-contentsList_contentDetailListItemData').text

                    except NoSuchElementException:
                        list_item_data = None

                    content.add_content_detail_list_item({list_item_label: list_item_data})

                course.add_content(content)
            courses.add_course(course)
            time.sleep(0.1)

        return courses

    except UnauthorizedException as e:
        # 認証に失敗した場合
        print(Fore.LIGHTRED_EX + 'ログインIDまたはパスワードが無効です。' + Fore.RESET)
        sys.exit(1)
    except NoSuchElementException as e:
        print(e)
        sys.exit(1)
    except JavascriptException as e:
        print(e)
        sys.exit(1)
    except ElementClickInterceptedException as e:
        print(e)
        sys.exit(1)
    except SelectedYearIsNotFoundException as e:
        print(e)
        sys.exit(1)
    except AvailableCoursesIsNotExistException as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print('中断しました')
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        browser.quit()
