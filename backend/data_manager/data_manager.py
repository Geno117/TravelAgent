# data manager
# manage data for the application
from typing import Optional, Tuple, Any

import sqlite3

#do not use this class directly.
class DataManager:
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def execute(self, query: str, params: Tuple[Optional[Any], ...] = ()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        self.conn.close()