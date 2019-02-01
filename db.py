from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
from app_config import app
import requests


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, public_id, username, password):
        self.public_id = public_id
        self.username  = username
        self.password  = password



class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(225))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, token):
        self.token = token



class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    currency_infos = db.relationship('Currency_info', backref='currency')

    def __init__(self, name):
        self.name = name


class Currency_info(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    통화명    = db.Column(db.String(80), nullable=False)
    심볼     = db.Column(db.String(80),  nullable=False)
    현재가    = db.Column(db.String(80), nullable=False)
    전일대비   = db.Column(db.String(80), nullable=False)
    등락률   = db.Column(db.String(80),   nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())


    def __init__(self, 통화명, 심볼, 현재가, 전일대비, 등락률, currency_id):
        self.통화명         = 통화명
        self.심볼          = 심볼
        self.현재가         = 현재가
        self.전일대비       = 전일대비
        self.등락률        = 등락률
        self.currency_id = currency_id


db.create_all()


if __name__ == "__main__":
    page_url = 'https://finance.naver.com/marketindex/worldExchangeList.nhn?key=exchange&page='

    def pages(url):
        pages = []
        count = 1
        while True:
            one = page_url + str(count)
            if count != 1:
                if requests.get(one).text != requests.get(pages[len(pages)-1]).text:
                    pages.append(one)
                    count += 1
                else:
                    break
            else:
                pages.append(one)
                count += 1
        return pages

    def menu_setting(pages):
        currency_names = []
        currency_objects = []
        for page in pages:
            html = requests.get(page).text
            soup = BeautifulSoup(html, 'html.parser')
            for line in soup.select('tr'):
                title = line.select('.tit')
                if len(title) != 0:
                    currency_names.append(title[0].text)

        currency = Currency("** 전체 **")
        currency_objects.append(currency)

        for currency_name in currency_names:
            currency = Currency(currency_name)
            currency_objects.append(currency)

        db.session.add_all(currency_objects)
        db.session.commit()

    pages = pages(page_url)
    menu_setting(pages)




















