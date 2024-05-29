Economic News Scraper and Updater
This project is a Python script designed to fetch, sort, and store economic news data from Investing.com. It continuously monitors for new data, updates an SQLite database, and ensures that news items are correctly sorted by date. The script handles multiple time zones and gracefully manages the database, preventing duplication and ensuring data integrity.

Features
Continuous Data Fetching: The script runs indefinitely, fetching new economic news data every hour.
Multi-Day Handling: News items are sorted and stored by their respective dates, ensuring that data from different days are correctly segregated.
Time Zone Conversion: Event times are converted to the local time zone of the respective country.
Conflict Handling: The script uses SQLite's ON CONFLICT clause to update existing entries, ensuring the database remains up-to-date without duplication.
Graceful Shutdown: The script handles keyboard interrupts, allowing for a graceful shutdown and proper closing of the database connection.
Requirements
Python 3.x
Libraries: requests, beautifulsoup4, arrow, pytz, sqlite3
Install the required libraries using pip:

pip install requests beautifulsoup4 arrow pytz

Usage
Clone the repository:

git clone https://github.com/yourusername/economic-news-scraper.git
cd economic-news-scraper
Ensure all dependencies are installed:

pip install -r requirements.txt
Run the script:


python update_economic_news.py
The script will begin running, fetching new data every hour, and updating the database. It will print progress messages to the console, so you can monitor its activity.

Script Overview
Initialization
The Investing class is initialized with a URL to the economic calendar and a path to the SQLite database. The database connection is established, and the news_meta table is created if it doesn't already exist.

Data Fetching
The fetch_news method scrapes the economic calendar, converts event times to local times, and sorts news items by date. It returns a dictionary of news items grouped by date.

Database Updating
The update_database method checks for existing tables for each date and creates new ones as needed. It then inserts or updates news items in the corresponding tables.

Continuous Monitoring
The main function runs the update_database method in an infinite loop, with a one-hour delay between each iteration. This ensures the script continuously fetches and updates data.

Contributing
Contributions are welcome! Please fork the repository, create a new branch for your changes, and submit a pull request.

License
This project is licensed under the MIT License.

Contact
snapchat:Blackfox0x
