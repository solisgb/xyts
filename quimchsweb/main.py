# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 14:18:46 2021

@author: LUISSOLIS
"""

db = r'D:\IGME20\20211124_calidad_subt_chs\data\quim_chs.db'
dir_output = r'D:\IGME20\20211124_calidad_subt_chs\xyno3'

if __name__ == "__main__":

    try:
        llog = False
        import littleLogging as logging
        llog = True

        import traceback
        from time import time
        from sqlitequimchs import quimchs

        start = time()

        data = quimchs(db, dir_output)

        data.quimchs_1()

        end = time()
        print('ellapsed time ', end-start)

    except ValueError:
        msg = traceback.format_exc()
        logging.append(f'ValueError exception\n{msg}')
    except Exception:
        msg = traceback.format_exc()
        if not llog:
            print(msg)
        else:
            logging.append(f'Exception\n{msg}')
    finally:
        print('\nFin')
