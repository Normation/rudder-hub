import MySQLdb 

DB_IP = "localhost" # "172.20.0.100" #localhost
DB_USER = "root"
DB_PASSWORD = "password"

class Database:
    def __init__(self, database_name='grafana', create_db = False):
        if create_db:
            db = MySQLdb.connect(host=DB_IP, user=DB_USER, password=DB_PASSWORD)
            c = db.cursor()
            c.execute(f"""CREATE DATABASE IF NOT EXISTS {database_name}""")
            db.commit()
            print(f"Database '{database_name}' is ready.")
            c.close()
            db.close()
        
        self.db = MySQLdb.connect(host=DB_IP, user=DB_USER, password=DB_PASSWORD, database=database_name)
        self.db.autocommit('on')
        c=self.db.cursor()

    def create_table(self, table_name, table_schema):
        c=self.db.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_schema});")
        print(f'{table_name} created')

    def show_table(self, table_name):
        c=self.db.cursor()
        c.execute(f"""SELECT * FROM {table_name}""")
        print(c.fetchall())

    def delete_row(self, table_name, primary_key, primary_key_val):
        c=self.db.cursor()
        query = f"""DELETE FROM {table_name}
        WHERE {primary_key}='{primary_key_val}'"""
        c.execute(query)

    def update_table(self, table_name, columns, rows):
        """Update the table <table_name> in mysql database. You can use this function to 
        either create a new row with a new id, or update an existing row.
        
        Parameters:
        table_name (string): mysql table name
        columns (Tuple): the columns of the table with the primary key first. 
            Example: ('id', 'hostname', 'softwares', 'software_updates', 'software_security_updates')
        rows (List[Tuple]): the rows of the table
            Example: [('root', 'rudder', 704, 78, 54), ('736320a2-998b-45f2-9bad-864b01d48d88', 'monitoring', 650, 50, 45)]        
        """
        # Update tables only if there is data 
        if rows:
            # Primary key must be on first position in columns and rows
            c=self.db.cursor()
            values = ', '.join([str(row) for row in rows])
            query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES {values}
            ON DUPLICATE KEY UPDATE
                {', '.join([f'{column}= VALUES({column})' for column in columns[1:]])};
            """
            # print(query)
            c.execute(query)
        else:
            print(f"Table {table_name} not updated as no data has been given")