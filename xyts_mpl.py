# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis

Serie temporal para gráficos con el módulo matplotlib

version: 0.4
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

class Time_series():
    """
    Define los datos y sus atributos para ser representados en un
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


    @staticmethod
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


class Plot_time_series():

    def __init__(self, title: str, ts1: [], ylabel1: str, dst: str,
                 write_data: int, ts2: list=[], ylabel2: str=''):
        """
        Llama a la función que dibuja uno o dos gráficos por figura
        args
        st: lista de objetos Time_series que se dibujan en el gráfico principal
        title: título de la figura
        ylabel1: nombre del eje de las Y upper graph
        dst: dirección y nombre del fichero a grabar
        ts2: lista de Time_series que se dibujan en el gráfico inferior; puede
            valer []
        ylabel2: nombre del eje de las Y del gráfico inferior, si ts2 no es []
        """
        for item in ts1 + ts2:
            if not isinstance(item, Time_series):
                raise ValueError('Los elementos de ts1 y ts2 deben ser ' +\
                                 'instancias Time_series')
        if ts2:
            Plot_time_series.xy_ts_plot_2g(title, ts1, ylabel1, ts2, ylabel2,
                                           dst)
        else:
            Plot_time_series.xy_ts_plot_1g(title, ts1, ylabel1, dst)
        if write_data:
            Plot_time_series.write_data_2xml(dst, title, ts1, ylabel1,
                                             ts2, ylabel2)


    @staticmethod
    def xy_ts_plot_1g(title: str, tsu: list, ylabelu: str, dst: str):
        """
        Dibuja una figura con 1 gráfico (axis) xy
        args
        title: título de la figura
        tsu: lista de objetos Time_series para el gráfico superior
        ylabelu: label eje y gráfico superior
        tsl: lista de objetos Time_series para el gráfico inferior
        dst: nombre fichero destino (debe incluir la extensión png)
        """
        # parámetros específicos
        mpl.rc('font', size=8)
        mpl.rc('axes', labelsize=8, titlesize= 10, grid=True)
        mpl.rc('axes.spines', right=False, top=False)
        mpl.rc('xtick', direction='out', top=False)
        mpl.rc('ytick', direction='out', right=False)
        mpl.rc('lines', linewidth=0.8, linestyle='-', marker='.', markersize=4)
        mpl.rc('legend', fontsize=8, framealpha=0.5, loc='best')

        fig, ax = plt.subplots()

        plt.suptitle(title)
        ax.set_ylabel(ylabelu)

        fig.autofmt_xdate()

        for ts1 in tsu:
            ax.plot(ts1.x, ts1.y, label=ts1.legend)
            ax.legend()

        fig.savefig(dst)
        plt.close('all')
        plt.rcdefaults()


    @staticmethod
    def xy_ts_plot_2g(title: str, tsu: list, ylabelu: str, tsl: list,
                      ylabell: str, dst: str):
        """
        Dibuja una figura con 2 gráfico (axis) xy de una o más series cada uno
            que comparten el eje x. El superior es el principal y ocupa 2/3 de
            la altura de la figura. El inferior es secundario y ocupa 1/3 de la
            altura de la figura
        title: título de la figura
        tsu: lista de objetos Time_series para el gráfico superior
        ylabelu: label eje y gráfico superior
        tsl: lista de objetos Time_series para el gráfico inferior
        dst: nombre fichero destino (debe incluir la extensión png)
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
            markerline, _, _ = ax2.stem(ts1.x, ts1.y, markerfmt=' ',
                                        basefmt=' ', label=ts1.legend,
                                        use_line_collection=True)
            markerline.set_markerfacecolor('none')
            ax2.legend()

        fig.savefig(dst)
        plt.close('all')
        plt.rcdefaults()


    @staticmethod
    def write_data_2xml(dst: str, title: str, ts1: [], ylabel1: str,
                        ts2: list=[], ylabel2: str=''):
        """
        graba un fichero xml con los datos de un gráfico xy de una o más series
        args
        dst: nombre del fichero png del gráfico
        title: título de la figura
        ts1: lista de objetos Time_series en el gráfico superior
        ylabel1: título del eje Y en el gráfico superior
        ts2: lista de objetos Time_series en el gráfico inferior
        ylabel2: título del eje Y en el gráfico inferior
        """
        from os.path import splitext

        name, ext = splitext(dst)
        fo = open(name + '.xml', 'w')
        fo.write('<?xml version="1.0" encoding="windows-1252"?>\n')
        fo.write('<fig>\n')
        fo.write('<titulo>{title}</titulo>\n')
        Plot_time_series.write_time_series_list(fo, ts1, ylabel1)
        if ts2:
            Plot_time_series.write_time_series_list(fo, ts2, ylabel2)
        fo.write('</fig>\n')
        fo.close()


    @staticmethod
    def write_time_series_list(fo, t_series, ylabel):
        """
        graba una lista de instancias Time_series
        args
        fo: objecto File, abierto
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        ylabel: título del eje Y
        """
        fo.write('<xy>\n')
        fo.write(f'<eje_y>{ylabel}</eje_y>\n')
        for ts1 in t_series:
            fo.write(f'<punto>{ts1.legend}\n')
            for x1, v1 in zip(ts1.x, ts1.y):
                fo.write(f'<d>{x1}\t{v1:0.2f}</d>\n')
            fo.write('</punto>\n')
        fo.write('</xy>\n')

