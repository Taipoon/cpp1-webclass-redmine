import os

from dotenv import load_dotenv

from .redmine import create_projects
from .webclass.fetch_data import fetch_contents, fetch_course_list
from .webclass.user_info import User, TakenCourses


def main():
    # .env ファイルを読み込む
    load_dotenv()

    # 取得するコースの絞り込み条件を指定
    taken_courses = TakenCourses(User(os.getenv('WEBCLASS_USER_ID'),
                                      os.getenv('WEBCLASS_PASSWORD')),
                                 # 取得する学年を1以上4以下の整数で指定(Noneの場合は現時点の学年)
                                 grade=None,

                                 # 取得する学期を整数のリストで指定
                                 # 1学期の場合 [1]
                                 # 3, 4学期の場合 [3, 4]
                                 semester=None,

                                 # 取得する講義名を指定(指定しない場合はすべての講義が対象)
                                 target_courses=[''],

                                 # 除外する講義名を指定
                                 # 「リメディアルコース」は講義ではないため、除外している
                                 exclude_courses=['リメディアル'],

                                 # 「取得する講義名」と「除外する講義名」の曖昧一致を許可するかどうか
                                 # True の場合、完全に講義名と一致しなければフィルタリングされない
                                 strict_mode=False)

    # Web Class から講義情報を取得する
    my_course = fetch_course_list(taken_courses)

    # 講義情報から、コースリストの詳細情報を取得する
    courses = fetch_contents(my_course)

    # Redmineにデータを流し込む(カテゴリが「レポート」「レポート（成績非公開）」のみを流し込む例)
    create_projects.export_to_redmine(courses,
                                      categories_filter=['レポート', 'レポート（成績非公開）'])

if __name__ == '__main__':
    main()
