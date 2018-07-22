import MySQLdb
from volmem import client
import time
import inspect

def connect():
    conn = client.get().get("cnf")["mysql"]
    try:
        db = MySQLdb.connect(conn["host"], conn["user"], 
            conn["pwd"], conn["schema"])
        cur = db.cursor()
        return db, cur
    except TypeError:
        print("Error Connection Value")
        return False
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        return False

def write(query=None):
    if not query:
        raise ValueError("No query defined")

    ret_val = None
    caller_func = str(inspect.stack()[1][3])
    db, cur = connect()

    try:
        a = cur.execute(query)
        db.commit()
    except IndexError:
        print("IndexError on ", inspect.stack()[1][3])
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e, caller_func)
    finally:
        db.close()
        return ret_val

def read(query=''):
    if not query:
        raise ValueError("No query defined")
    
    ret_val = None
    caller_func = str(inspect.stack()[1][3])
    db, cur = connect()
    try:
        a = cur.execute(query)
        try:
            a = cur.fetchall()
            ret_val = a
        except ValueError:
            ret_val = None
    except MySQLdb.OperationalError:
        print("MySQLdb.OperationalError on ", caller_func)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e, caller_func)
    except KeyError:
        print("KeyError on ", caller_func)
    finally:
        db.close()
        return ret_val
