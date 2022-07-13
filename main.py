import argparse
import os
from typing import List, Union

from colorama import Fore
from dotenv import load_dotenv

import create_tasks
from fetch_data import fetch_contents, fetch_course_list
from user_info import User, TakenCourses


def main(grade: int = None, semester: Union[List[int], int, None] = None,
         target_courses: Union[List[str], None] = None, exclude_courses=None,
         strict_mode: bool = False):
    # .env ファイルを読み込む
    load_dotenv(dotenv_path='./.env')

    # 取得するコースの絞り込み条件を指定
    taken_courses = TakenCourses(User(os.getenv('WEBCLASS_USER_ID'),
                                      os.getenv('WEBCLASS_PASSWORD')),
                                 # 取得する学年を1以上4以下の整数で指定(Noneの場合は現時点の学年)
                                 grade=grade,

                                 # 取得する学期を整数のリストで指定
                                 # 1学期の場合 [1]
                                 # 3, 4学期の場合 [3, 4]
                                 semester=semester,

                                 # 取得する講義名を指定(指定しない場合はすべての講義が対象)
                                 target_courses=target_courses or [''],

                                 # 除外する講義名を指定
                                 # 『リメディアルコース』は講義ではないため、「リメディアル」として曖昧検索して除外している
                                 exclude_courses=exclude_courses or ['リメディアル'],

                                 # 「取得する講義名」と「除外する講義名」の曖昧一致を許可するかどうか
                                 # True の場合、完全に講義名と一致しなければ絞り込みされない
                                 strict_mode=strict_mode)

    # Web Class から講義情報を取得する
    my_course = fetch_course_list(taken_courses)

    # 講義情報から、コースリストの詳細情報を取得する
    courses = fetch_contents(my_course)

    # 接続先RedmineのURLを表示
    print(f'{Fore.LIGHTBLUE_EX}Redmine is running: {os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}{Fore.RESET}')

    # Redmineにデータを流し込む
    create_tasks.create_projects(courses)

    # 講義ごとのコンテンツをチケットとして作成する(以下は、カテゴリが「レポート」「レポート（成績非公開）」のみを流し込んでいる)
    create_tasks.create_issues(courses, categories_filter=['レポート', 'レポート（成績非公開）'])


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-g', '--grade', help='1以上4以下の整数で学年を指定します。', type=int)

    arg_parser.add_argument('-s', '--semester', help='1以上4以下の整数で学期を指定します。', nargs='+')

    arg_parser.add_argument('-t', '--target', help='取得する講義名を指定します。', nargs='+')

    arg_parser.add_argument('-e', '--exclude', help='除外する講義名を指定します。', nargs='+')

    arg_parser.add_argument('--strict-mode',
                            help=('--target または --exclude オプションで指定する講義名の該当条件を完全一致にします。' +
                                  '指定しない場合は曖昧一致で絞り込みます。'),
                            action='store_true')

    args = arg_parser.parse_args()

    semester = args.semester if args.semester is None else list(map(int, args.semester))

    main(grade=args.grade, semester=semester, target_courses=args.target, exclude_courses=args.exclude)
