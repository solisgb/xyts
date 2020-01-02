# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 19:20:26 2020

@author: solis
"""

def test_select():
    import pyodbc
    dbpath = r'C:\Users\solis\Documents\DB\Ipasub97.mdb'
    con_str = r'DRIVER={Microsoft Access Driver ' +\
        '(*.mdb, *.accdb)}; ' + f'DBQ={dbpath};'
    con = pyodbc.connect(con_str)
    cur = con.cursor()
    ifid = 1
    select = "select * from masub_pm where fid=?;"
    cur.execute(select, ifid)
    print('ok')


if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import littleLogging as logging

        now = datetime.now()

        startTime = time()

        test_select()

        xtime = time() - startTime

    except ValueError:
        msg = traceback.format_exc()
        logging.append(f'ValueError exception\n{msg}')
    except ImportError:
        msg = traceback.format_exc()
        print (f'ImportError exception\n{msg}')
    except Exception:
        msg = traceback.format_exc()
        logging.append(f'Exception\n{msg}')
    finally:
        # print('El script tardó {0}'.format(str(timedelta(seconds=xtime))))
        logging.dump()
        print('\nFin')

