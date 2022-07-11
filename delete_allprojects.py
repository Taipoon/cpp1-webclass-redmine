import os

from dotenv import load_dotenv
from redminelib import Redmine

# read .env
load_dotenv()

redmine = Redmine(f'{os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}',
                  username=os.getenv('REDMINE_USERNAME'),
                  password=os.getenv('REDMINE_PASSWORD'))

projects = redmine.project.all(include=['enabled_modules'])

for project in projects:
    print(project.name, "を削除します")
    project.delete()
