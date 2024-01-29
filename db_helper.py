import mysql.connector
from datetime import datetime

global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Darshan295@",
    database="rss_feeds",
    auth_plugin='mysql_native_password',
)


def insert_news_article(title, content, pub_date, source_url, category):
    try:
        cursor = cnx.cursor()

        query = "SELECT id FROM news_articles WHERE source_url = %s"
        cursor.execute(query, (source_url,))
        existing_article = cursor.fetchone()

        if existing_article is None:
            query = "INSERT INTO news_articles (title, content, pub_date, source_url, category) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (title, content, pub_date, source_url, category))
            cnx.commit()

            print("News article inserted successfully!")

            return 1
        else:
            print("Duplicate news article. Skipping insertion.")

        cursor.close()

        return 0

    except mysql.connector.Error as err:
        print(f"Error inserting news article: {err}")

        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()

        return -1
