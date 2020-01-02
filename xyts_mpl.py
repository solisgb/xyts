# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis

Serie temporal para gráficos con el módulo matplotlib

version: 0.4
"""
from datetime import date
import numpy as np


class Time_series():
    """
    define los datos y sus atributos para ser representados en un
        gráfico
    """
    def __init__(self, fechas: [], values: [], legend: str, marker: str = '.',
                 scatter: int = 0, slinestyle: str = '-',
                 copy_data: bool = True):
        """
        fechas: lista de dates
        values: lista de floats o integeres
        legend: leyenda de la serie
        marker: marcador
        scatter: tipo de línea
        linestyle: estilo de línea
        """
        from copy import deepcopy
        if fechas.size < 2 or values.size < 2:
            raise ValueError('fechas y/0 values no tienen datos')
        if fechas.size != values.size:
            raise ValueError('fechas y values != longitud')
        if copy_data:
            self.fechas = deepcopy(fechas)
            self.values = deepcopy(values)
        else:
            self.fechas = fechas
            self.values = values

        self.legend = legend
        self.marker = marker
        self.scatter = scatter
        self.linestyle = slinestyle


def minmax_fechas(t_series: list, dbtype: str) -> list():
    """
    devuelve el mínimo y el máximo de cada elemento de t_series, que es
        de tipo Time_series
    args
    t_series: lista en que cada elemento es un onjeto Time_series
    dbtype: gestor de base de datos
    output
    fecha mínima y máxima de los elementos en t_series; el tipo de fecha se
        ajusta según dbtype, de modo que el formato de fecha devuelto se
        puede utilizar directamente como parámetros en una select
    """
    minmax = np.array([[l.fechas[0], l.fechas[-1]] for l in t_series],
                      dtype='datetime64')
    minmax = [np.min(minmax[:, 0]), np.max(minmax[:, 1])]
    minmax = np.datetime_as_string(minmax, unit='D').tolist()
    if dbtype == 'ms_access':
        for i, item in enumerate(minmax):
            a = item.split('-')
            minmax[i] = date(int(a[0]), int(a[1]),int(a[2]))
        return minmax
    elif dbtype == 'sqlite':
        return minmax


def xy_ts_plot(ts: [], stitle: str, ylabel: str, dst: str, ts2: list=[],
               ylabel2: str='') -> None:
        if not ts2:
            XYt_1(ts, stitle, ylabel, dst)


def XYt_1(t_series: [], stitle: str, ylabel: str, dst: str):
    """
    dibuja un gráfico xy de una o más series

    input
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import AutoMinorLocator

    dateFmt = mdates.DateFormatter('%d-%m-%Y')
    xminorLocator = AutoMinorLocator()
    yminorLocator = AutoMinorLocator()

    fig, ax = plt.subplots()
    # El primer objeto es el principal
    for ts1 in t_series:
        if ts1.scatter == 0:
            ax.plot(ts1.fechas, ts1.values, marker=ts1.marker,
                    label=ts1.legend, linestyle=ts1.linestyle)
        else:
            ax.plot(ts1.fechas, ts1.values, marker=ts1.marker,
                    label=ts1.legend, linestyle='None')

    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)
    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    plt.legend(loc='best', framealpha=0.5)
    plt.tight_layout()
    plt.grid(True)

    fig.savefig(dst)
    plt.close('all')


def XYt_1_xml(t_series: [], stitle: str, ylabel: str, dst: str):
    """
    graba un fichero xml con los datos de un gráfico xy de una o más series

    input
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
    """
    from os.path import splitext

    name, ext = splitext(dst)
    fo = open(name + '.xml', 'w')
    fo.write('<?xml version="1.0" encoding="windows-1252"?>\n')
    fo.write('<xy>\n')
    fo.write('<titulo>{}</titulo>\n'.format(stitle))
    fo.write('<eje_y_nombre>{}</eje_y_nombre>\n'.format(ylabel))
    # El primer objeto es el principal
    for ts1 in t_series:
        fo.write('<id>{}\n'.format(ts1.legend))
        for fecha, value in zip(ts1.fechas, ts1.values):
            fo.write('<d>{0:s}\t{1:0.2f}</d>\n'.
                     format(fecha.strftime("%d/%m/%Y %H"), value))
        fo.write('</id>\n')
    fo.write('</xy>\n')
    fo.close()
