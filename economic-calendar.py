import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import arrow
import pytz
import sqlite3
import time

class Investing:
    def __init__(self, uri='https://www.investing.com/economic-calendar/', db_path='economic_news.db'):
        self.uri = uri
        self.req = urllib.request.Request(uri)
        self.req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        self.db_path = db_path

        # Connect to the SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.create_meta_table()

    def create_meta_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS news_meta (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL UNIQUE,
                    table_name TEXT NOT NULL
                )
            ''')

    def create_daily_table(self, table_name):
        with self.conn:
            self.conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    time TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    impact INTEGER NOT NULL,
                    event TEXT NOT NULL,
                    actual TEXT,
                    forecast TEXT,
                    previous TEXT,
                    UNIQUE(time, currency, event)
                )
            ''')

    def insert_or_update_news(self, table_name, news):
        with self.conn:
            cursor = self.conn.cursor()
            for item in news:
                cursor.execute(f'''
                    INSERT INTO {table_name} (time, currency, impact, event, actual, forecast, previous)
                    VALUES (:Time, :Currency, :Impact, :Event, :Actual, :Forecast, :Previous)
                    ON CONFLICT(time, currency, event) 
                    DO UPDATE SET
                    actual=excluded.actual, forecast=excluded.forecast, previous=excluded.previous
                ''', item)
            self.conn.commit()

    def fetch_news(self):
        try:
            response = urllib.request.urlopen(self.req)
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            table = soup.find('table', {"id": "economicCalendarData"})
            rows = table.find_all('tr', {"class": "js-event-item"})

            countries_of_interest = {
                'United States': 'US/Eastern',
                'China': 'Asia/Shanghai',
                'Eurozone': 'Europe/Berlin',  # Germany
                'Germany': 'Europe/Berlin',
                'France': 'Europe/Paris',
                'Japan': 'Asia/Tokyo',
                'Australia': 'Australia/Sydney',
                'United Kingdom': 'Europe/London',
                'Canada': 'Canada/Eastern',
                'New Zealand': 'Pacific/Auckland',
                'Switzerland': 'Europe/Zurich'
            }

            news_list = []
            for row in rows:
                flag = row.find('td', {"class": "flagCur"}).find('span')
                country = flag.get('title')

                if country in countries_of_interest:
                    news = {
                        'Time': None,
                        'Currency': country,
                        'Impact': None,
                        'Event': None,
                        'Actual': None,
                        'Forecast': None,
                        'Previous': None,
                    }
                    _datetime = row.attrs['data-event-datetime']
                    utc_time = arrow.get(_datetime, "YYYY/MM/DD HH:mm:ss").replace(tzinfo='UTC')
                    local_tz = pytz.timezone(countries_of_interest[country])
                    local_time = utc_time.to(local_tz).format('YYYY-MM-DD HH:mm')

                    news['Time'] = local_time
                    news['Currency'] = country

                    impact = row.find('td', {"class": "sentiment"})
                    bull = impact.find_all('i', {"class": "grayFullBullishIcon"})
                    news['Impact'] = len(bull)

                    event = row.find('td', {"class": "event"})
                    news['Event'] = event.text.strip()

                    actual = row.find('td', {"class": "act"})
                    news['Actual'] = actual.text.strip() if actual else ''

                    forecast = row.find('td', {"class": "fore"})
                    news['Forecast'] = forecast.text.strip() if forecast else ''

                    previous = row.find('td', {"class": "prev"})
                    news['Previous'] = previous.text.strip() if previous else ''

                    news_list.append(news)

            return news_list

        except HTTPError as error:
            print("Oops... Got HTTP error {}".format(error.code))
            return []

    def update_database(self):
        news_list = self.fetch_news()
        if not news_list:
            return

        today_date = arrow.now().format('YYYY_MM_DD')
        table_name = f'news_{today_date}'

        # Check if the table for today already exists in meta table
        cursor = self.conn.cursor()
        cursor.execute('SELECT table_name FROM news_meta WHERE date = ?', (today_date,))
        row = cursor.fetchone()

        if not row:
            self.create_daily_table(table_name)
            with self.conn:
                self.conn.execute('''
                    INSERT INTO news_meta (date, table_name)
                    VALUES (?, ?)
                ''', (today_date, table_name))

        self.insert_or_update_news(table_name, news_list)

    def close(self):
        self.conn.close()

def main():
    investing = Investing()
    try:
        while True:
            investing.update_database()
            print("Database updated with the latest news.")
            time.sleep(3600)  # Wait for 1 hour before fetching new data
    except KeyboardInterrupt:
        print("Stopping the script.")
    finally:
        investing.close()

if __name__ == "__main__":
    main()

#By(Blackfo-x)
# https://github.com/blackfo-x