# -*- coding: latin-1 -*
from datetime import date
import numpy as np
from math import sqrt
from tkinter import messagebox
import xml.etree.ElementTree as ET
import littleLogging as logging
from xyts_mpl import Time_series
from xyts_mpl import Plot_time_series as plot_ts

# Tipos de bases de datos soportadas =========================================
dbtypes = ('ms_access', 'postgres', 'sqlite')
# Nombre del fichero resumen de datos en gráficos xy =========================
SUMMARY_FILE = '_xyts_resumen.txt'
# Tipo de punto en gráfico ===================================================
TIPO_MASTER = 'master'
TIPO_UPPER_AUX = 'upper_aux'
TIPO_LOWER_AUX = 'lower_aux'


class Project(object):

    XML_FILE_INI = 'xyts.xml'
    ROOT_ELEMENT_NAME = 'xyts'
    PROJECT_ELEMENT_NAME = 'project'

    def __init__(self, element: ET.Element, check: bool=True):
        """
        Un proyecto está formado por un elemento xml de estructura determinada
            en base a la cual se pueden grabar los gráficos de una serie de
            puntos
        """
        if check:
            Project.check(element)
        self.p = element


    def name_get(self) -> str:
        return self.p.get('name').strip()


    @staticmethod
    def read_projects(xml_file: str=None) -> list:
        """
        lee un fichero xml con los datos de los proyectos e instancio objetos
            Project
        """
        if not xml_file:
            xml_file = Project.XML_FILE_INI

        tree = ET.parse(xml_file)
        root = tree.getroot()

        if root.tag != Project.ROOT_ELEMENT_NAME:
            raise ValueError(f'El elemento raiz en {xml_file} debe ser ' +\
                             f'{Project.ROOT_ELEMENT_NAME}')

        elements = root.findall(Project.PROJECT_ELEMENT_NAME)
        if not elements:
            raise ValueError(f'El fichero {xml_file} no tiene elementos ' +\
                             f'{Project.PROJECT_ELEMENT_NAME}')
        projects = []
        ner = 0
        for i, element in enumerate(elements):
            try:
                prj = Project(element)
                projects.append(prj)
            except Exception:
                ner += 1
                logging.append(f'El project {i+1:d} está mal formado',
                               toScreen=False)
        if ner > 0:
            messagebox.showinfo(f'No se han cargado {ner:d} proyecto/s' +\
                                'porque está/n mal formado/s')
        return projects


    @staticmethod
    def check(prj_node: ET.Element):
        """
        Comprueba que el elemento prj_node tiene de nombre project y tiene los
            elementos requeridos -no se comprueba el contenido de los
            elementos ni el de los atributos-
        Hay elementos opcionales que no pueden ser comprobados:
            upper_relation: si existe el elemento toma sus datos de la select
                grahp/upper_ts, que es requerido
            upper_relation/select_distancia: si existe sirve para calcular
                la distancia entre un elemento en master/select y otro con
                el que está relacionado mediante upper_relation -se requiere
                que master/select devuelva las coordenadas x, y del punto-
            lower_relation/select, de donde se toman los datos del gráfico
                inferior
            lower_relation/select_distancia: si existe sirve para calcular
                la distancia entre un elemento en master/select y otro con
                el que está relacionado mediante lower_relation
        """
        def element_get(element: ET.Element, path2: str, required: bool=True,
                        unique: bool=True) -> list:
            """
            comprueba la existencia de un elemento que puede ser requerido o
                único; no se analiza el contenido del elemento
            devuelve la lista con o sin elementos
            """
            l = element.findall(path2)
            if not l:
                if required:
                    raise ValueError('El proyecto debe tener un ' +\
                                     f' elemento {path2}')
            if len(l) > 1:
                if unique:
                    raise ValueError('El proyecto debe tener un solo' +\
                                     f' elemento {path2}')
            return l

        if prj_node.tag != Project.PROJECT_ELEMENT_NAME:
            raise ValueError('El elemento raiz debe ser ' +\
                             f'{Project.PROJECT_ELEMENT_NAME}')

        node = element_get(prj_node, 'db')[0]
        dbtype = node.get('type')
        if dbtype:
            if not dbtype in dbtypes:
                raise ValueError(f'{dbtype} no es un tipo válido de db')
        else:
            raise ValueError('El elemento db debe tener un atributo type')

        _ = element_get(prj_node, 'graph')
        nodes1 = element_get(prj_node, 'graph/y_axis_name',
                             unique=False)
        nodes2 = element_get(prj_node, 'graph/axis_type',
                             unique=False)
        if len(nodes1) != len(nodes2):
            raise ValueError('Desde haber el mismo número de elementos' +\
                             ' y_axis_name que elementos axis_type')
        if len(nodes1) not in (1, 2):
            raise ValueError('El número de elementos y_axis_name' +\
                             ' debe ser 1 o 2')

        _ = element_get(prj_node, 'master')
        _ = element_get(prj_node, 'master/select')
        nodes = element_get(prj_node, 'master/col', unique=False)
        col_types = ('cod', 'xutm', 'yutm')
        cod_exists = False
        for node in nodes:
            col_type = node.get('type')
            if col_type:
                if not col_type in col_types:
                    raise ValueError(f'{col_type} no es un tipo ' +\
                                     'válido en master/select/col')
                else:
                    if col_type == 'cod':
                        cod_exists = True
            else:
                raise ValueError('El elemento master/select/col debe' +\
                                 ' tener un atributo type')
        if not cod_exists:
            raise ValueError('El elemento master/select/col debe' +\
                             ' tener un atributo type="cod"')

        nodes = element_get(prj_node, 'master/title', unique=False)
        nnodes2 = 0
        for node in nodes:
            _ = element_get(node, 'text')
            nodes2 = element_get(node, 'col', unique=False, required=False)
            if nodes2:
                nnodes2 += len(nodes2)
        if nnodes2 == 0:
            raise ValueError('Alguno de los elementos title debe tener un' +\
                                 ' subelemento col')

        _ = element_get(prj_node, 'master/file/name')
        _ = element_get(prj_node, 'master/file/col', unique=False)

        _ = element_get(prj_node, 'upper_ts/select')

        node = element_get(prj_node, 'lower_relation', required=False)
        if node:
            _ = element_get(prj_node, 'lower_ts/select')


    def element_get(self, path2: str, attrib: str = None) -> ET.Element:
        """
        devuelve el subelemento de self.p en path2 o uno de sus
            atributos
        """
        if attrib is None:
            return self.p.find(path2)
        else:
            if self.p.find(path2).get(attrib) is None:
                return None
            else:
                return self.p.find(path2)


    def elements_get(self, path2: str) -> ET.Element:
        """
        devuelve los subelementos de self.p en path2
        """
        return self.p.findall(path2)


    def element_with_atribb_get(self, path2: str, attrib: str,
                                attrib_value: str) -> str:
        """
        devuelve el texto subelementos de self.p en path2 cuyo atributo attrib
            tiene el valor attrib_value
        """
        for element in self.p.findall(path2):
            if element.get(attrib) == attrib_value:
                return element.text.strip()
        return None


    def exists_element(self, path2: str) ->bool:
        """
        devuelve True si path2 es un subelemento de self.p
        """
        e = self.p.find(path2)
        if isinstance(e, ET.Element):
            return True
        return False


    def pretty_xml_get(self) -> str:
        """
        devuelve el elemento para visualización
        """
        s1 = ET.tostring(self.p, encoding='Latin-1')
        s2 = s1.decode('Latin-1')
        s3 = s2.replace('\t', ' ')
        return s3


    def xygraphs(self, dir_plots: str, date1: date, date2: date,
                 only_master: int, only_upper_graph: int, write_data: int):
        """
        Se ejecutan los select y se preparan los datos para llamar a las
            funciones de matplotlib que dibuja los graficos XY
        dir_plots: directorio donde se graban los gráficos
        date1, date2: fechas inicial y final para las select de datos
        only_master: si existe un elemento upper_relation y only_master es 1
            no se representarán los puntos relacionados con el master en el
            gráfico superior
        only_upper_graph: si existe un elemento lower_relation y
            only_upper_graph es 1 no se representarán los puntos relacionados
            con el master en el gráfico inferior
        write_data: si 1 graba los datos de cada figura en un fichero
        """
        from os.path import join
        from traceback import format_exc
        from db_connection import con_get

        not_sqlites_dbtypes = [dbtype for dbtype in dbtypes \
                               if dbtype != 'sqlite']

        # conexión a la base de datos
        dbtype = self.element_get('db').get('type').strip()
        con = con_get(dbtype, self.element_get('db').text.strip())
        cur = con.cursor()

        # puntos en los que van a hacer los gráficos xy
        select = self.element_get('master/select').text.strip()
        cur.execute(select)
        data_master = [row for row in cur]

        if not data_master:
            st = 'la select master no devuelve datos'
            logging.append(st, False)
            raise ValueError(st)

        icod, ixutm, iyutm = self.master_indices_get()
        f_summary = open(join(dir_plots, SUMMARY_FILE), 'w')
        st = 'cod\ttipo\tfecha1\tfecha2\tnum_datos\txutm\tyutm\n'
        f_summary.write(f'{st}')

        if dbtype == 'sqlite':
            date1 = date1.strftime('%YYYY-%mm-%dd')
            date2 = date2.strftime('%YYYY-%mm-%dd')

        for i, row_dm in enumerate(data_master):
            select = self.element_get('upper_ts/select').text.strip()
            cur.execute(select, (row_dm[icod], date1, date2))
            x_upper, y_upper = Project.ts_get(dbtype, cur)
            yield(i+1, len(data_master))
            if x_upper.size < 2:
                logging.append(f'El punto {row_dm[icod]} tiene ' +\
                               f'{x_upper.size:d} datos y no se hace' +\
                               f' gráfico', False)
                continue
            ts = [Time_series(x_upper, y_upper, row_dm[icod])]

            st = self.line_to_summary(TIPO_MASTER, row_dm, x_upper, icod,
                                      ixutm, iyutm)

            f_summary.write(f'{st}\n')

            if only_master !=1:
                upper_ts = \
                self.related_ts_get('upper_relation/select', cur, row_dm[icod],
                                    'upper_ts/select', date1, date2, dbtype,
                                    'upper_relation/select_location',
                                    (row_dm[ixutm], row_dm[iyutm]),
                                    TIPO_UPPER_AUX, f_summary)
                if upper_ts:
                    ts = ts + upper_ts

            if only_upper_graph !=1:
                min_date, max_date = Time_series.minmax_fechas(ts)
                if dbtype in not_sqlites_dbtypes:
                    min_date = Project.strfecha_2_date(min_date)
                    max_date = Project.strfecha_2_date(max_date)
                lower_ts = \
                self.related_ts_get('lower_relation/select', cur, row_dm[icod],
                                    'lower_ts/select', min_date, max_date,
                                    dbtype, 'lower_relation/select_location',
                                    (row_dm[ixutm], row_dm[iyutm]),
                                    TIPO_LOWER_AUX, f_summary)
            else:
                lower_ts = []

            title = self.title_get(row_dm)
            file_name = self.file_name_get(row_dm)
            dst = join(dir_plots, file_name)
            ylabels = self.y_axis_names_get()

            try:
                _ = plot_ts(title, ts, ylabels[0], dst, write_data,
                            lower_ts, ylabels[1])
            except Exception:
                st = format_exc()
                logging.append(st, False)
                messagebox.showerror(self.__module__, st)
                if f_summary:
                    f_summary.close()
                if con:
                   con.close()
                return

        f_summary.close()
        con.close()
        messagebox.showinfo(self.__module__, 'Proceso finalizado')


    def master_indices_get(self) -> tuple:
        """
        devuelve los subscripts de interés para ser sads en la select master
        """
        icod = self.element_with_atribb_get('master/col', 'type', 'cod')
        icod = int(icod) - 1
        ixutm = self.element_with_atribb_get('master/col', 'type', 'xutm')
        if ixutm: #  es un elemento opcional
            ixutm = int(ixutm) - 1
        iyutm = self.element_with_atribb_get('master/col', 'type', 'yutm')
        if iyutm:
            iyutm = int(iyutm) - 1
        return (icod, ixutm, iyutm)


    def line_to_summary(self, tipo: str, row: list, xts: np.ndarray,
                        icod: int, ixutm: int, iyutm: int) -> str:
        """
        Prepara un str para escribir en el fichero resumen
        args
        tipo: de punto (TIPO_MASTER, TIPO_UPPER_AUX, TIPO_LOWER_AUX)
        row: lista con los datos del punto que se va a grabar en el
            fichero de summary
        xts: np.array con las fechas con datos
        icod, ixutm, iyutm: índices del código del punto y sus coordenadas
            en row (ixutm, iyutm pueden ser None)
        """
        st0 = f'{row[icod]}\t{tipo}'

        if row[ixutm] is None:
            st = f"{row[icod]} {tipo} has None x"
            logging.append(st, False)
            return st0

        if row[iyutm] is None:
            st = f"{row[icod]} {tipo} has None y"
            logging.append(st, False)
            return st0

        if xts[0] is None:
            st = f"{row[icod]} {tipo} has None x"
            logging.append(st, False)
            return st0

        if xts[-1] is None:
            st = f"{row[icod]} {tipo} has None y"
            logging.append(st, False)
            return st0

        st = f'{row[icod]}\t{tipo}\t{xts[0]}\t{xts[-1]}\t{xts.size:d}'
        st = st + f'\t{row[ixutm]:0.0f}\t{row[iyutm]:0.0f}'
        return st


    def related_ts_get(self, path_relation: str, cur, cod_master,
                       path_data: str, date1, date2, dbtype: str,
                       path_location: str, xy_dm: list, point_type: str,
                       f_summary) -> list:
        """
        Extrae las series temporales relacionadas con un punto master
        LLamada solo desde xygraphs
        args
        path_relation: nombre de la select de relación (upper_relation/select,
        lower_relation/select)
        cur: cursor a la base de datos abierto en la func xygraphs
        cod_master: es el código del punto obtenido en master/select y que ya
            se ha comprobado que tiene datos, aunque no se sabe todavía si
            tiene datos relacionados
        path_data: path a la select de datos relacionados. Si se representan
            en upper graph será upper_ts/select; si en lower graph
            lower_ts/select lower_ts/select
        date1, date2: fechas inferior y superior para hacer la select de datos
            relacionados; el tipo depende de la base de datos (gestionado en
            xygraphs)
        dbtype: tipo de la base de datos
        path_location: es un path opcional que si está presente sirve para
            extraer las coordenadas del punto relacionado
        xy_dm: son las coordenadas del punto master; si no se han obtenido sus
            2 elementos serán None
        point_type: tipo de punto, uno de los siguientes: TIPO_MASTER,
            TIPO_UPPER_AUX, TIPO_LOWER_AUX
        f_summay: objeto file abierto -se puede escribir-
        returns
        Una lista de instancias Time_series; la lista puede estar vacía
        """
        ts_related = []
        if not self.exists_element(path_relation):
            return ts_related

        # puntos relacionados con cod_master
        select = self.element_get(path_relation).text.strip()
        cur.execute(select, (cod_master,))
        related_points = [row_ur[0] for row_ur in cur]

        for cod in related_points:
            # datos de cada punto relacionado con el punto principal
            # en el graph superior o inferior
            select = self.element_get(path_data)\
            .text.strip()
            cur.execute(select, (cod, date1, date2))
            x_arr, y_arr = Project.ts_get(dbtype, cur)
            if x_arr.size < 2:
                logging.append(f'El punto principal {cod_master} ' +\
                               f'está relacionado con {cod} que no tiene ' +\
                               'datos en el rango de fechas', False)
                continue
            if xy_dm[0] and xy_dm[1] and self.exists_element(path_location):
                select = \
                self.element_get(path_location).text.strip()
                cur.execute(select, (cod,))
                xyutm = cur.fetchone()
                dist = self.__diste(xy_dm, xyutm)
                leg = f'{cod}, {dist:0.0f} m'
            else:
                xyutm = ['', '']
                leg = f'{cod}'

            st = f'{cod}\t{point_type}\t{x_arr[0]}\t{x_arr[-1]}\t' +\
            f'{x_arr.size:d}\t{xyutm[0]}\t{xyutm[1]}'
            f_summary.write(f'{st}\n')
            ts_related.append(Time_series(x_arr, y_arr, leg))
        return ts_related


    @staticmethod
    def strfecha_2_date(strfecha: str, sep: str='-'):
        a = strfecha.split(sep)
        return date(int(a[0]), int(a[1]),int(a[2]))


    @staticmethod
    def ts_get(dbtype: str, cur):
        """
        devuelve la serie x e y para el gráfico como np.arrays
        cur es un objeto cursor
        """

        tmp = [row for row in cur]
        y_upper = np.array([row[1] for row in tmp])
        if dbtype == 'ms_access' or dbtype == 'postgres':
            x_upper = [row[0].strftime('%Y-%m-%d') for row in tmp]
        elif dbtype == 'sqlite':
            x_upper = (row[0] for row in tmp)
        else:
            raise ValueError('xyts_project, ts_get,\n ' +\
                             f' {dbtype} no es un tipo de db válido')
        return np.array(x_upper, dtype='datetime64'), y_upper


    def title_get(self, row: list) -> str:
        """
        Forma el título de un gráfico
        args
        row: es fila activa devuelta por select master, de donde se
            va a extraer el título del gráfico
        return
            un str con el título del gráfico (puede tener más de una línea)
        """
        titles = self.p.findall('master/title')
        stitles = [title.find('text').text.strip() for title in titles]
        for i, title in enumerate(titles):
            cols = title.findall('col')
            if cols:
                subs = [row[int(col.text)-1] for col in cols]
                stitles[i] = stitles[i].format(*subs)
        return '\n'.join(stitles)


    def file_name_get(self, row: list) -> str:
        """
        Forma el nombre de cada fichero de gráfico/s
        args
        row: es la fila que devuelve master/select
        return
        sname: str que contiene el nombre del fichero
        """
        fname = self.p.find('master/file/name').text.strip()
        cols = self.p.findall('master/file/col')
        subs = [row[int(col.text)-1] for col in cols]
        for i, subs1 in enumerate(subs):
            if isinstance(subs1, str):
                subs[i] = subs1.replace('.', '_')
        return fname.format(*subs)


    def y_axis_names_get(self) -> list:
        """
        Devuelve el nombre de los ejes de los 2 gráficos; si sólo hay un
            gráfico el segundo elemento de la lista es ''
        """
        y_axis_names = [node.text.strip() for node in \
                        self.elements_get('graph/y_axis_name')]
        if len(y_axis_names) == 1:
            y_axis_names.append('')
        return y_axis_names


    def __diste(self, xy_dm, xyutm):
        """
        Distancia euclídea
        """
        for t1 in (xy_dm, xyutm):
            for t2 in t1:
                if t2 is None:
                   return -1.
        d = sqrt((xy_dm[0] - xyutm[0])**2 + (xy_dm[1] - xyutm[1])**2)
        return d
