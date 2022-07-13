import os

from colorama import Fore
from dotenv import load_dotenv
from redminelib import Redmine

# read .env
load_dotenv()

# 接続先RedmineのURLを表示
print(f'{Fore.LIGHTBLUE_EX}Redmine is running: {os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}{Fore.RESET}')

redmine = Redmine(f'{os.getenv("REDMINE_URL")}:{os.getenv("REDMINE_PORT")}',
                  key=os.getenv("REDMINE_API_KEY"))

projects = redmine.project.all(include=['enabled_modules'])

for project in projects:
    print(project.name, "を削除します")
    project.delete()
