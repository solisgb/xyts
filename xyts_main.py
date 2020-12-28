# -*- coding: utf-8 -*-
"""
Created on 06/09/2019

@author: Luis Solís

Programa para hacer gráficos de series temporales que se graban en un fichero
    png. Cada png es una figura y cada figura puede tener 2 gráficos que
    comparten el eje de las Y; en el gráfico superior se puede presentar la
    evolución de una variable medida en varios puntos; el gráfico inferior es
    opcional y se puede presentar la evolución de otra variable en otros
    puntos
"""
mylogging = False


if __name__ == "__main__":

    import traceback
    from tkinter import Tk

    try:
        import littleLogging as logging
        mylogging = True
        from xyts_gui import GUI
        
        root = Tk()
        GUI(root)

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
        if mylogging:
            logging.dump()
