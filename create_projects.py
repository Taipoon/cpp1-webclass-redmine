import datetime
import os

import redminelib
from dotenv import load_dotenv
from redminelib import Redmine

from webclass.course_elements import Courses


def export_to_redmine(courses: Courses, categories_filter: list = None):

    # .envを読み込む
    load_dotenv()

    # APIキーを用いて
    redmine = Redmine(f'{os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}',
                      key=os.getenv("REDMINE_API_KEY"))

    # 各講義を1つのプロジェクトとして作成する
    for course in courses.courses:
        try:
            r = redmine.project.get(course.course_code.lower())
            print(f'「{r}」は既に存在しています')

        # プロジェクトが存在しない場合に新規作成
        except redminelib.exceptions.ResourceNotFoundError:
            r = redmine.project.create(
                name=f'{course.title}',
                identifier=f'{course.course_code.lower()}',
                description=f'コース名: {course.title}\n講義コード: {course.course_code}\n',
                is_public=True,
                enabled_module_names=['documents',
                                      'files',
                                      'calendar',
                                      'gantt',
                                      'issue_tracking',
                                      'time_tracking',
                                      'news',
                                      'wiki',
                                      'repository',
                                      'boards']
            )
            print(r, "のチケットを作成します")

            # コンテンツごとにチケット(issue)を作成します
            for content in course.contents:
                # カテゴリで絞り込む
                if categories_filter is not None:
                    if content.content_category not in categories_filter:
                        continue

                # 説明文を作成
                description = f'コンテンツ名：『{content.content_name}』\nカテゴリ：{content.content_category}\n'

                start_date = None
                due_date = None

                for content_detail in content.content_detail_list_item:
                    for label, value in content_detail.items():

                        # 締め切りが設定されている場合はRedmineのガントチャートにも反映する
                        if label == '利用可能期間':
                            s, d = value.split(' - ')
                            t_s = datetime.datetime.strptime(s, '%Y/%m/%d %H:%M')
                            start_date = datetime.date(t_s.year, t_s.month, t_s.day)

                            t_d = datetime.datetime.strptime(d, '%Y/%m/%d %H:%M')
                            due_date = datetime.date(t_d.year, t_d.month, t_d.day)

                        description += f'{label}：{value}\n'

                # チケット(issue)の新規作成
                try:
                    created_issue = redmine.issue.create(
                        project_id=f'{course.course_code.lower()}',
                        subject=f'{content.content_name}',
                        description=description,
                        tracker_id=1,
                        start_date=start_date,
                        due_date=due_date,
                    )
                    print(f'「{created_issue}」を作成しました')
                except redminelib.exceptions.ServerError as e:
                    print('失敗しました', e)
