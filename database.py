import sqlite3
from datetime import date, timedelta,datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('activities.db')
        self.conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS activities (id integer primary key, date datetime,jiraid text,jiradesc text, activity text, description text,status text)''')

    def insert_data(self, date_str,jiraid,jiradesc, activity, description,status):
        self.cursor.execute("INSERT INTO activities (date,jiraid,jiradesc, activity, description,status) VALUES (?, ?,?, ?,?,?)", (date_str, jiraid,jiradesc, activity, description,status))
        self.conn.commit()

    def get_records(self):
        self.cursor.execute("SELECT * FROM activities order by date DESC")
        return self.cursor.fetchall()
    
    def get_records_by_id(self,record_id):
        self.cursor.execute("SELECT * FROM activities WHERE id = ?", (record_id,))
        row= self.cursor.fetchone()
        if row:
                date_time = datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
                date_str = date_time.strftime('%d-%m-%Y')
                time_str = date_time.strftime('%H:%M')
                return {
                    'date': date_str,
                    'time': time_str,
                    'activity': row[4],
                    'jira_id': row[2],
                    'description': row[5],
                    'status': row[6],
                    'jira_desc': row[3]
                }
        return None

    def get_activities(self):
        self.cursor.execute("SELECT DISTINCT activity FROM activities order by date DESC")
        return [row['activity'] for row in self.cursor.fetchall()]

    def get_records_last_x_days(self, days):
        today = date.today()
        x_days_ago = today - timedelta(days=days)
        self.cursor.execute("SELECT date,jiraid, activity, description FROM activities WHERE date >= ? order by date DESC", (x_days_ago,))
        return self.cursor.fetchall()

    def delete_record(self, record_id):
        self.cursor.execute("DELETE FROM activities WHERE id = ?", (record_id,))
        self.conn.commit()
