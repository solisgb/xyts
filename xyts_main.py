# -*- coding: utf-8 -*-
"""
Created on 06/09/2019

@author: Luis Solís

Programa para hacer gráficos de series temporales; es una evolución del
    programa dislin; permite hacer un gráfico con 2 subplots
"""
import littleLogging as logging


if __name__ == "__main__":

    try:
        import traceback
        from tkinter import Tk
        from xyts_gui import User_interface

        root = Tk()
        User_interface(root)

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
        logging.dump()
