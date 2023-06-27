#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['database'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()  # Fetch the first row
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db
        return r
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
        print(e)
    cur.close()  # Close the cursor
    conn.close()  # Close the connection to the db
    return None


################################################################################
# List Units
#   - This function performs a "SELECT" from the database to get the unit
#       of study information.
#   - This is useful for your part when we have to make the page.
################################################################################

def list_units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()  # Close the cursor
    conn.close()  # Close the connection to the db
    return val


################################################################################
# Get transcript function
#   - Your turn now!
#   - What do you have to do?
#       1. Connect to the database and set up the cursor.
#       2. You're given an SID - get the transcript for the SID.
#       3. Close the cursor and the connection.
#       4. Return the information we need.
################################################################################


def get_prereq():
    conn = database_connect()
    if (conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT r.uoSCode UoSCode, u.uoSName UosName, 
                        r.prereqUoSCode PrereqUoSCode, 
                        u2.uoSName PrereqUoSName, r.enforcedSince
                        FROM UniDB.Requires r
                        INNER JOIN UniDB.UnitOfStudy u
                        ON r.uoSCode = u.uoSCode
                        INNER JOIN UniDB.UnitOfStudy u2
                        ON r.prereqUoSCode = u2.uoSCode
                        """)
        val = cur.fetchall()
    except:
        print("Error fetching from database")

    cur.close()
    conn.close()
    return val


def get_pre_amount():
    conn = database_connect()
    if (conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT uoSCode, COUNT(*) "Number of Prerequires"
                        FROM UniDB.Requires
                        GROUP BY uoSCode
                        """)
        val = cur.fetchall()
    except:
        print("Error fetching from database")

    cur.close()
    conn.close()
    return val


def search_prereq(uosCode):
    conn = database_connect()
    if (conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        sql = """SELECT uoSCode, string_agg(prereqUoSCode, ', ') PrereqUoSCode
                    FROM UniDB.Requires
                    WHERE uoSCode = %s
                    GROUP BY uoSCode
                    """
        cur.execute(sql, (uosCode,))
        val = cur.fetchall()
    except:
        print("Error fetching from database")

    cur.close()
    conn.close()
    return val


def add(uoSCode, prereqUoSCode):
    conn = database_connect()
    if (conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        sql = """INSERT INTO UniDB.Requires VALUES (%s, %s, now())"""
        cur.execute(sql, (uoSCode, prereqUoSCode))
        conn.commit()
        cur.execute("""SELECT * FROM UniDB.Requires WHERE uoSCode = %s AND prereqUoSCode = %s""",
                    (uoSCode, prereqUoSCode))
        val = cur.fetchall()
    except:
        print("Error fetching from database")

    cur.close()
    conn.close()
    return val

def get_credits(uosCode):
    conn = database_connect()
    if (conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        sql = """SELECT r.uoSCode UoSCode, 
                string_agg(r.prereqUoSCode, ', ') PrereqUoSCode,
                sum(u.credits) "Total Credits"
                FROM UniDB.Requires r
                INNER JOIN UniDB.UnitOfStudy u
                on r.prereqUoSCode = u.uoSCode
                WHERE r.uoSCode = %s
                GROUP BY r.uoSCode"""
        cur.execute(sql, (uosCode,))
        val = cur.fetchall()
    except:
        print("Error fetching from database")

    cur.close()
    conn.close()
    return val


###############
#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")
