import os

from dotenv import load_dotenv
from redminelib import Redmine

# read .env
load_dotenv()

redmine = Redmine(f'{os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}',
                  key=os.getenv("REDMINE_API_KEY"))

projects = redmine.project.all(include=['enabled_modules'])

for project in projects:
    print(project.name, "を削除します")
    project.delete()
