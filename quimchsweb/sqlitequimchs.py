# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 10:23:40 2021

@author: LUISSOLIS
"""
import datetime
from os.path import join
import sqlite3
import traceback

import littleLogging as logging
import xyts_mpl as xyt


class quimchs():

    pequ = {'HCO3': 61, 'Na': 23, 'Cl': 35.5, 'K': 39.1, 'SO4': 48, 'Ca': 20,
            'NO3': 62, 'Mg': 12}


    def __init__(self, db: str, dir_output: str):
        self.db =  db
        self.dir_output = dir_output


    def quimchs_1(self):
        """

        Parameters
        ----------
        db : str
            sqlite db

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """

        param = ('NITRAT', 'COND25')
        select_puntos = """
    select p.fid , p.id_mas , p.acu
    from puntos p
    order by p.id_mas , p.acu , p.fid
        """
        select_param_punto = """
    select fecha, valor
    from analisis
    where param=? and fid=?
    order by fecha
        """
        ylabel1 = 'NO3 mg/l'

        try:
            connected = False
            con = sqlite3.connect(self.db)
            connected = True
            cur = con.cursor()

            cur.execute(select_puntos)
            puntos = cur.fetchall()
            m = len(puntos)
            for i, punto in enumerate(puntos):
                print(f'{i:n}/{m:n}')
                # time serie param 1
                cur.execute(select_param_punto, (param[0], punto[0]))
                rows = cur.fetchall()
                if len(rows) == 0:
                    logging.append(f'{punto[0]} no tiene datos de {param[0]}',
                                   False)
                    continue
                dates1, values1 = \
                zip(*[(datetime.datetime.strptime(row[0][0:10],
                                                  "%Y-%m-%d").date(),
                       row[1]) for row in rows])
                if len(values1) == 0:
                    logging.append(f'{punto[0]} sin datos', False)
                    continue
                elif len(values1) == 1:
                    logging.append(f'{punto[0]} 1 dato', False)
                    continue

                dst = f'{punto[1]}_{punto[2]}_{punto[0]}'
                dst = dst.replace(' ', '_')
                dst = dst.replace('.', '_') + '.png'
                dst = join(self.dir_output, dst)
                title = f'{punto[0]}, Acuífero {punto[2]} (MAS {punto[1]})'
                ts1 = xyt.Time_series(dates1, values1, punto[0],
                                      copy_data=False)
                l_ts = [ts1]
                if max(values1) >= 40:
                    x = [min(dates1), max(dates1)]
                    y = [50., 50.]
                    l_ts.append(xyt.Time_series(x, y, '', copy_data=False))

                xyt.Plot_time_series(title, l_ts, ylabel1, dst=dst,
                                     write_data=0)

        except sqlite3.Error:
            raise ValueError(sqlite3.Error)
        except ValueError:
            msg = traceback.format_exc()
            logging.append(f'ValueError exception\n{msg}')
        finally:
            if connected:
                con.commit()
                con.close()


    def error_balance_ionico(self):
        """

        Parameters
        ----------
        db : str
            sqlite db

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """

        param = ('NITRAT',)
        select_puntos = """
    select p.fid , p.id_mas , p.acu
    from puntos p
    order by p.id_mas , p.acu , p.fid
        """
        select_param_punto = """
    select fecha, valor
    from analisis
    where param=? and fid=?
    order by fecha
        """
        ylabel1 = 'NO3 mg/l'

        try:
            connected = False
            con = sqlite3.connect(self.db)
            connected = True
            cur = con.cursor()

            cur.execute(select_puntos)
            puntos = cur.fetchall()
            for punto in puntos:
                # time serie param 1
                cur.execute(select_param_punto, (param[0], punto[0]))
                rows = cur.fetchall()
                if len(rows) == 0:
                    logging.append(f'{punto[0]} no tiene datos de {param[0]}',
                                   False)
                    continue
                dates1, values1 = zip(*[(row[0], row[1]) for row in rows])

                dst = f'{punto[1]}_{punto[2]}_{punto[0]}.png'
                dst = dst.replace(' ', '_')
                dst = join(self.dir_output, dst)
                title = f'{punto[0]}, {punto[2]} ({punto[1]})'

                xy.xy1(title,  dst1, dates1, values1, ylabel1)

        except sqlite3.Error:
            raise ValueError(sqlite3.Error)
        except ValueError:
            msg = traceback.format_exc()
            logging.append(f'ValueError exception\n{msg}')
        finally:
            if connected:
                con.commit()
                con.close()




