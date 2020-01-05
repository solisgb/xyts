# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis

Serie temporal para gráficos con el módulo matplotlib

version: 0.4
"""
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


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


    @property
    def x(self):
        return self.fechas


    @property
    def y(self):
        return self.values


def minmax_fechas(t_series: list) -> list():
    """
    devuelve el mínimo y el máximo de cada elemento de t_series, que es
        de tipo Time_series
    args
    t_series: lista en que cada elemento es un onjeto Time_series
    dbtype: gestor de base de datos
    output
    fecha mínima y máxima de los elementos en t_series en formato str
        yyyy-mm-dd
    """
    minmax = np.array([[l.fechas[0], l.fechas[-1]] for l in t_series],
                      dtype='datetime64')
    minmax = [np.min(minmax[:, 0]), np.max(minmax[:, 1])]
    minmax = np.datetime_as_string(minmax, unit='D').tolist()
    return minmax


def xy_ts_plot(ts1: [], title: str, ylabel1: str, dst: str, ts2: list=[],
               ylabel2: str='') -> None:
    """
    Desde la función se llama a otra que dibuja uno o dos gráficos por
        figura
    args
    st: lista de objetos Time_series que se dibujan en el gráfico principal
    title: título de la figura
    ylabel1: nombre del eje de las Y upper graph
    dst: dirección y nombre del fichero a grabar
    ts2: lista de Time_series que se dibujan en el gráfico inferior; puede
        valer []
    ylabel2: nombre del eje de las Y del gráfico inferior, si ts2 no es []
    """
    if ts2:
        xy_ts_plot_2g(title, ts1, ylabel1, ts2, ylabel2, dst)
    else:
        xy_ts_plot_1g(ts1, title, ylabel1, dst)


def xy_ts_plot_1g(ts: list, stitle: str, ylabel: str, dst: str):
    """
    dibuja una figura con 1 gráfico xy de una o más series
    args
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
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)

    # El primer objeto es el principal
    for ts1 in ts:
        if ts1.scatter == 0:
            ax.plot(ts1.x, ts1.y, marker=ts1.marker,
                    label=ts1.legend, linestyle=ts1.linestyle)
        else:
            ax.plot(ts1.x, ts1.y, marker=ts1.marker,
                    label=ts1.legend, linestyle='None')

    plt.ylabel(ylabel)
    plt.legend(loc='best', framealpha=0.5)
    plt.tight_layout()
    plt.grid(True)

    fig.autofmt_xdate()  # rotate & align tick labels so they look better
    fig.savefig(dst)
    plt.close('all')


def xy_ts_plot_2g(title: str, tsu: list, ylabelu: str, tsl: list, ylabell: str,
                  dst: str, cfg: dict={}):
    """
    Dibuja una figura con 2 gráfico (axis) xy de una o más series cada uno que
        comparten el eje x. El superior es el principal y ocupa 2/3 de la
        altura de la figura. El inferior es secundario y ocupa 1/3 de la
        altura de la figura
    title: título de la figura
    tsu: lista de objetos Time_series para el gráfico superior
    ylabelu: label eje y gráfico superior
    tsl: lista de objetos Time_series para el gráfico inferior
    dst: nombre fichero destino (debe incluir la extensión png)
    cfg: object Mpl_config
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    # parámetros específicos
    mpl.rc('font', size=8)
    mpl.rc('axes', labelsize=8, titlesize= 10, grid=True)
    mpl.rc('axes.spines', right=False, top=False)
    mpl.rc('xtick', direction='out', top=False)
    mpl.rc('ytick', direction='out', right=False)
    mpl.rc('lines', linewidth=0.8, linestyle='-', marker='.', markersize=4)
    mpl.rc('legend', fontsize=8, framealpha=0.5, loc='best')

    fig, _ = plt.subplots()

    plt.suptitle(title)
    plt.subplots_adjust(hspace=0.1, bottom=0.16, top=0.87)

    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)
    ax1.set_ylabel(ylabelu)
    ax2.set_ylabel(ylabell)

    fig.autofmt_xdate()

    for ts1 in tsu:
        ax1.plot(ts1.x, ts1.y, label=ts1.legend)
        ax1.legend()

    # subplot inferior (stem)
    for ts1 in tsl:
        markerline, _, _ = ax2.stem(ts1.x, ts1.y, markerfmt=' ', basefmt=' ',
                                    label=ts1.legend, use_line_collection=True)
        markerline.set_markerfacecolor('none')
        ax2.legend()

    fig.savefig(dst)
    plt.close('all')
    plt.rcdefaults()


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
