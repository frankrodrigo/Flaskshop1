import pyodbc

print(pyodbc.drivers())

# Define your connection details
server = '34.41.71.174,1433'  # IP address of your SQL Server with the port
database = 'db1'  # The name of the database
username = 'dbuser'  # Your SQL Server username
password = 'dbuser'  # Your SQL Server password
driver = '{ODBC Driver 17 for SQL Server}'  # ODBC Driver name

# Establish a connection to SQL Server
try:
    connection = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    print("Connection successful!")

    # Create a cursor object
    cursor = connection.cursor()

    # Execute a simple query
    cursor.execute("SELECT @@VERSION;")

    # Fetch and print the result of the query
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()

    # Close the connection
    connection.close()

except Exception as e:
    print("Error connecting to SQL Server:", e)
