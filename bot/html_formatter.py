from jinja2 import Environment, FileSystemLoader
import datetime

env = Environment(loader=FileSystemLoader("templates"))

def render_news(title: str, body: str) -> str:
    template = env.get_template("news_template.html")
    date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    return template.render(title=title, body=body, date=date)
