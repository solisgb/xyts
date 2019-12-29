# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 17:48:42 2019

@author: solis
"""
import pyodbc
import sqlite3


def con_get(dbtype: str, dbpath: str):
    """
    conexión a una base de datos
    """
    if dbtype == 'ms_access':
        con_str = r'DRIVER={Microsoft Access Driver ' +\
        '(*.mdb, *.accdb)}; ' + f'DBQ={dbpath};'
        return pyodbc.connect(con_str)
    elif dbtype == 'sqlite':
        return sqlite3.connect(dbpath)
    else:
        raise ValueError('El tipo de db no está implementado')
