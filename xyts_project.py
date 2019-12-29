# -*- coding: latin-1 -*
from datetime import date
import numpy as np
from tkinter import messagebox
import xml.etree.ElementTree as ET
import littleLogging as logging


dbtypes = ('ms_access', 'sqlite')
SUMMARY_FILE = '_xyts_resumen.txt'


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
                logging.append(f'El project {i:d} está mal formado',
                               toScreen=False)
        if ner > 0:
            messagebox.showinfo(f'No se han cargado {ner:d} proyectos' +\
                                'porque están mal formados')
        return projects


    @staticmethod
    def check(prj_node: ET.Element):
        """
        Comprueba que el elemento prj_node tiene de nombre project y tiene los
            elementos requeridos
        Hay dos elementos que son opcionales y que no se comprueban:
            upper_relation: si existe el element toma sus datos de la select
                grahp/upper_serie, que es requerido
            upper_relation/select_distancia: si existe sirve para calcular
                la distancia entre un elemento en master/select y otro con
                el que está relacionado mediante upper_relation
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

        nodes = element_get(prj_node, 'master/titul', unique=False)
        for node in nodes:
            _ = element_get(node, 'text')

        _ = element_get(prj_node, 'master/file/name')
        _ = element_get(prj_node, 'master/file/col', unique=False)

        _ = element_get(prj_node, 'upper_serie/select')

        node = element_get(prj_node, 'lower_relation', required=False)
        if node:
            _ = element_get(prj_node, 'lower_serie/select')


    def element_get(self, path2: str, attrib: str = None) -> ET.Element:
        """
        devuelve el subelemento de self.p en path2 o uno de sus
            atributos
        """
        if attrib is None:
            return self.p.find(path2)
        else:
            return self.p.find(path2).get(attrib)


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
                return element.get(attrib)
        return None


    def exists_element(self, path2: str) ->bool:
        """
        devuelve True si path2 es un subelemento de self.p
        """
        e = self.p.find(path2)
        if e:
            return True
        return False


    def pretty_xml_get(self):
        """
        devuelve el elemento para visualización
        """
        s1 = ET.tostring(self.p, encoding='Latin-1')
        s1 = s1.decode('Latin-1')
        s1 = s1.replace('\t', ' ')
        return s1


    def xygraphs(self, dir_dst: str, date1: date, date2: date):
        """
        se ejecutan los select y se preparan los datos para llamar a las
            funciones de matplotlib que dibuja los graficos XY
        """
        from math import sqrt
        import os.path
        from xyts_mpl import plt1_nst, plt2_nst, plt1_nst_2_xml, plt2_nst_2_xml
        from db_connection import con_get

        # conexión a la base de datos
        dbtype = self.element_get('db').get('type').strip()
        con = con_get(dbtype, self.element_get('db').text.strip())
        cur = con.cursor()

        # puntos en los que vana hacer los gráficos xy
        select = self.element_get('master/select').text.strip()
        cur.execute(select)
        data_master = [row for row in cur]

        if not data_master:
            a = 'la select master no devuelve datos'
            logging.append(a, False)
            raise ValueError(a)

        # posiciones de elementos clave en la select
        icod = self.element_with_atribb_get('master/col', 'type', 'cod')
        icod = int(icod) - 1
        ixutm = prj.element_with_atribb_get('master/col', 'type', 'xutm')
        if ixutm:
            ixutm = int(ixutm) - 1
        iyutm = prj.element_with_atribb_get('master/col', 'type', 'yutm')
        if iyutm:
            iyutm = int(iyutm) - 1
        if ixutm and iyutm:
            utm = True
            st = 'cod\tfecha1\tfecha2\tnum_datos\ttipo\t' +\
            'xutm\tyutm\n'
        else:
            utm = False
            st = 'cod\tfecha1\tfecha2\tnum_datos\ttipo\n'

        f_summary = open(SUMMARY_FILE, 'w')
        f_summary.write(f'{st}')

        ngraph = 0
        minmax = None
        for i, row in enumerate(data_master):
            date1 = Project.date_in_where(dbtype, date1)
            date2 = Project.date_in_where(dbtype, date2)
            select = prj.element_get('upper_serie/select').text.strip()
            cur.execute(select, (row[icod], date1, date2))
            x_upper, y_upper = Project.ts_get(dbtype, cur)
            if x_upper < 2:
                logging.append('El punto {row[icod]} tiene < 2 datos')
                yield(i+1, len(data_master))
                continue

            data_in_upper_plot = True
            x_upper_plot = [x]
            y_upper_plot = [y]
            legends_upper_plot = [data[ini][icod]]
            axis_name_upper_plot = prj.graf_axis_name_get()[1]

            cod_master.append(data[ini][icod])
            mindate = x_upper_plot[0][0]
            maxdate = x_upper_plot[0][-1]
            if not minmax:
                minmax = [mindate, maxdate]
            else:
                if mindate < minmax[0]:
                    minmax[0] = mindate
                if maxdate>minmax[1]:
                    minmax[1] = maxdate

            dt = ['{}/{}/{}'.format(dt1.day, dt1.month, dt1.year) \
                  for dt1 in (mindate, maxdate)]
            data_summary.write('{0}\t{1}\t{2}\t{3:d}\n' \
                               .format(data[ini][icod], dt[0], dt[1], len(x)))

            if prj.sql_upper_relation_bdd_get() and \
            self.only1UpperPlot.get() == 0:

                # puntos relacionados con el punto principal de plot(1, 1)
                select1 = prj.sql_upper_relation_select_get() \
                .format(data[ini][icod])
                cur.execute(select1)
                data_ur = [row1 for row1 in cur1]

                for row in data_ur:
                    # datos de cada punto relacionado con el punto principal
                    # en plot(1, 1)
                    col = prj.sql_upper_relation_others_cod_get()
                    select2 = prj.sql_upper_select_get().format(row[col-1])
                    cur2 = cursors[prj.sql_upper_bdd_get()]
                    cur2.execute(select2)
                    data_u = [row2 for row2 in cur2]

                    if len(data_u) < 2:
                        a = 'Punto {}, upper_relation: el punto asociado ' +\
                        '{} tiene <2 datos'.format(str(data[ini][icod]),
                                                   str(row[col-1]))
                        logging.append(a, toScree=False)
                        numIncidencias += 1
                        continue

                    xdistancia = -1.
                    if prj.sql_upper_relation_sql_distancia_bdd_get():
                        # coordenadas para calcular la distancia entre 2 puntos
                        select3 = \
                        prj.sql_upper_relation_sql_distancia_select_get() \
                        .format(row[0],row[1])
                        cur3 = \
                        cursors[prj.sql_upper_relation_sql_distancia_bdd_get()]
                        cur3.execute(select3)
                        data_d = [row3 for row3 in cur3]
                        if len(data_d) == 2:
                            xdistancia = sqrt((data_d[0][0]-data_d[1][0])**2 \
                                              + (data_d[0][1]-data_d[1][1])**2)

                    data_u = np.array(data_u)
                    ix_u = prj.sql_upper_x_col_get() - 1
                    x_u = [date(item.year, item.month, item.day) \
                           for item in data_u[:, ix_u]]
                    y_u = data_u[:, prj.sql_upper_y_col_get() - 1]
                    mindate = min(mindate, x_u[0])
                    maxdate = max(maxdate, x_u[-1])

                    x_upper_plot.append(x_u)
                    y_upper_plot.append(y_u)
                    if xdistancia > 0.:
                        a = '{0:s} ({1:0.1f} m)' \
                            .format(row[col - 1], xdistancia)
                        legends_upper_plot.append(a)
                    else:
                        legends_upper_plot.append(row[col - 1])

                    if row[col - 1] not in cod_upper:
                        cod_upper.append(row[col - 1])

            if prj.sql_lower_relation_bdd_get() and \
            self.upperPlotOnly.get() == 0:
                # puntos relacionados con el punto principal de plot(1, 1)
                # para representar en plot(1, 2)
                select_lr = prj.sql_lower_relation_select_get() \
                .format(data[ini][icod])
                cur_lr = cursors[prj.sql_lower_relation_bdd_get()]
                cur_lr.execute(select_lr)
                data_lr = [row_lr for row_lr in cur_lr]

                x_lower_plot = []
                y_lower_plot = []
                legends_lower_plot = []
                axis_name_lower_plot = prj.graf_axis_name_get()[2]
                for row in data_lr:
                    d1 = "{0:d}/{1:d}/{2:d}" \
                    .format(mindate.month,mindate.day,mindate.year)
                    d2 = "{0:d}/{1:d}/{2:d}" \
                    .format(maxdate.month,maxdate.day,maxdate.year)
                    # datos de cada punto en plot(1, 2)
                    col = prj.sql_lower_relation_others_cod_get()
                    select_l = prj.sql_lower_select_get() \
                    .format(row[col - 1], d1, d2)
                    cur_l = cursors[prj.sql_lower_bdd_get()]
                    cur_l.execute(select_l)
                    data_l = [row_l for row_l in cur_l]
                    if len(data_l) < 2:
                        a = 'El punto {}, lower_relation: el punto asociado' +\
                        ' {} tiene <2 datos  entre las fechas {} y {}' \
                        .format(str(data[ini][icod]), str(row[col-1]),
                                d1, d2)
                        logging.append(a, toScreen=False)
                        numIncidencias += 1
                        continue

                    data_in_lower_plot = True
                    data_l = np.array(data_l)

                    a = [data_l[:, prj.sql_lower_x_col_get() - 1].tolist()]
                    b = [date(item.year, item.month, item.day) \
                         for item in a[0]]
                    x_lower_plot.append(b)
                    a = [data_l[:, prj.sql_lower_y_col_get() - 1].tolist()]
                    y_lower_plot.append(a[0])
                    legends_lower_plot.append(str(row[col - 1]))

                    if row[col - 1] not in cod_lower:
                        cod_lower.append(row[col - 1])

            try:
                titulos = [User_interface.__str_from_row(titulo['text'],
                                                         data[ini],
                                                         titulo['iths']) \
                        for titulo in prj.sql_master_titul_get()]
                if len(titulos) > 1:
                    titulos = '\n'.join(titulos)
                    titulos = titulos
            except:
                if isinstance(data[ini][icod], str):
                    a = 'error al formar el nombre del fichero del punto {}' \
                    .format(data[ini][icod])
                else:
                    a = 'error al formar el nombre del fichero del punto {}' \
                    .format(data[ini][icod])
                logging.append(a, toScreen=False)
                raise ValueError(a)

            # nombre del fichero
            ngraph += 1
            try:
                name_file = User_interface.__str_from_row(prj.file_name_get(),
                                                          data[ini],
                                                          prj.file_name_iths_get(),
                                                          'png',
                                                          num_graf)
            except:
                a = 'Error al formar el nombre del fichero del punto {}' \
                .format(data[ini][icod])
                logging.append(a, toScreen=False)
                raise ValueError(a)

            dst = os.path.join(dir_dst, name_file)

            # se graba el grafico
            try:
                if data_in_upper_plot and data_in_lower_plot:
                    plt2_nst(x_upper_plot, y_upper_plot, legends_upper_plot,
                             axis_name_upper_plot, x_lower_plot, y_lower_plot,
                             legends_lower_plot, axis_name_lower_plot,
                             titulos, dst)

                    if self.dataToFile.get() == 1:
                        names = os.path.splitext(name_file)
                        dst=os.path.join(dir_dst,names[0] + '.xml')
                        plt2_nst_2_xml(x_upper_plot, y_upper_plot,
                                       legends_upper_plot,
                                       axis_name_upper_plot, x_lower_plot,
                                       y_lower_plot, legends_lower_plot,
                                       axis_name_lower_plot, titulos, dst)

                elif data_in_upper_plot and not data_in_lower_plot:
                    plt1_nst(x_upper_plot, y_upper_plot, legends_upper_plot,
                             titulos, axis_name_upper_plot, dst)

                    if self.dataToFile.get() == 1:
                        names = os.path.splitext(name_file)
                        dst = os.path.join(dir_dst,names[0]+'.xml')
                        plt1_nst_2_xml(x_upper_plot, y_upper_plot,
                                       legends_upper_plot,
                                       axis_name_upper_plot, titulos, dst)

            except SystemExit:
                self.ngraf.set(0)
                self.icount.set(0)
                return
            except:
                a = 'Error en grafico punto {}\n{}\nContinuar?' \
                .format(cod_master[len(cod_master)-1], format_exc())
                logging.append(a, toScreen=False)
                numIncidencias += 1
                if tk.messagebox.askyesno(self.__module__, a):
                    continue
                else:
                    self.ngraf.set(0)
                    self.icount.set(0)
                    return

            if self.dataToFile.get() == 1:
                names = os.path.splitext(name_file)
                dst = os.path.join(dir_dst, names[0] + '.xml')  # ,

            self.icount.set(self.icount.get() + 1)
            self.master.update()

            if ini == 0 and self.pauseXY1.get() == 1:
                if not tk.messagebox.askyesno(self.__module__,
                                              "Se ha grabado el primer' +\
                                              ' gráfico\nDesea continuar?"):
                    break

        if minmax is not None:
            strminmax = ['{0:d}/{1:d}/{2:d}'.format(dt1.day, dt1.month,
                         dt1.year) for dt1 in minmax]

        # grabar_localizaciones
        if self.grabar_localizaciones.get() == 1:
            n = len(cod_master) + len(cod_upper) + len(cod_lower)
            self.ngraf.set(n)
            self.icount.set(0)
            ic=0
            f = open(os.path.join(dir_dst,
                                  User_interface.__file_locations), 'w')

            if prj.sql_upper_locations_bdd_get() and \
            len(prj.sql_upper_locations_select_get()) > 0:
                f.write('#puntos representados\n#COD\tX\tY\tTipo\n')
                for cod1 in cod_master:
                    select_ul = prj.sql_upper_locations_select_get() \
                    .format(cod1)
                    cur_ul = cursors[prj.sql_upper_locations_bdd_get()]
                    cur_ul.execute(select_ul)
                    data_ul = [row_ul for row_ul in cur_ul]
                    if len(data_ul) > 0:
                        for row in data_ul:
                            ic += 1
                            self.icount.set(ic)
                            f.write('{0}\t{1:0.2f}\t{2:0.2f}\tprincipal\n' \
                                    .format(row[0], row[1], row[2]))
                for cod1 in cod_upper:
                    select_ul = prj.sql_upper_locations_select_get() \
                    .format(cod1)
                    cur_ul = cursors[prj.sql_upper_locations_bdd_get()]
                    cur_ul.execute(select_ul)
                    data_ul = [row_ul for row_ul in cur_ul]
                    if len(data_ul) > 0:
                        for row in data_ul:
                            if row[0] not in cod_master:
                                ic += 1
                                self.icount.set(ic)
                                f.write('{0}\t{1:0.2f}\t{2:0.2f}\tauxiliar\n'\
                                        .format(row[0], row[1], row[2]))
            else:
                tk.messagebox.showinfo(self.__module__,
                                       'No está definido el elemento sql' +\
                                       ' type=upper_locations' )
                n = len(cod_lower)
                self.ngraf.set(n)

            if prj.sql_lower_locations_bdd_get() and \
            len(prj.sql_lower_locations_select_get()) > 0:
                for cod1 in cod_lower:
                    select_ll = prj.sql_lower_locations_select_get() \
                    .format(cod1)
                    cur_ll = cursors[prj.sql_lower_locations_bdd_get()]
                    cur_ll.execute(select_ll)
                    data_ll = [row_ll for row_ll in cur_ll]
                    if len(data_ll) > 0:
                        for row in data_ll:
                            ic += 1
                            self.icount.set(ic)
                            f.write('{0}\t{1:0.2f}\t{2:0.2f}\tgraf. ' +\
                                    'inferior\n' \
                                    .format(row[0], row[1], row[2]))
            else:
                tk.messagebox.showinfo(self.__module__,
                                       'No está definido el elemento sql' +\
                                       ' type=lower_locations' )

            f.close()

        self.ngraf.set(0)
        self.icount.set(0)

        self.master.configure(cursor='arrow')
        a = 'Proceso finalizado\nLas series de los puntos principales se' +\
        ' sitúan entre\n{} y {}'.format(strminmax[0], strminmax[1])
        if numIncidencias > 0:
            a = a + '\nSe han producido {0:d} incidencias, grabadas en\n{1}\n'\
            .format(numIncidencias, logging.file_name_get())
        tk.messagebox.showinfo(self.__module__, a)

        a = os.path.join(dir_dst, User_interface.__file_summary)
        contents = data_summary.getvalue()
        f = open(a, 'w')
        f.write('{}\n'.format(prj.project_name_get()))
        f.write('{}\n'.format(contents))
        f.close()


    @staticmethod
    def date_in_where(dbtype: str, date1: str, sep: str='/'):
        """
        devuelva una fecha válida para usar en el where de la select que
            devuelve los datos
        """
        a = date1.split(sep)
        d = date(int(a[2]), int(a[1]), int(a[0]))
        if dbtype == 'ms_access':
            return d
        elif dbtype == 'sqlite':
            return d.strftime('%Y-%m-%d')
        else:
            raise ValueError(f'{dbtype} no es un tipo d bdd válido')


    @staticmethod
    def ts_get(dbtype: str, cur):
        """
        devuelve la serie x e y para el gráfico
        cur es un objeto cursor
        """
        def acces_aux(item):
            d = date(item.year, item.month, item.day)
            return d.strftime('%Y-%m-%d')

        tmp = [row for row in cur]
        y_upper = np.array([row[1] for row in tmp])
        if dbtype == 'ms_access':
            x_upper = (acces_aux(row[0]) for row in tmp)
        elif dbtype == 'sqlite':
            x_upper = (row[0] for row in tmp)
        else:
            raise ValueError(f'{dbtype} no es un tipo d bdd válido')
        return np.array(x_upper, dtype='datetime64'), y_upper



# =========================================================================

    def select_get(self, path2: str) -> str:
        """
        devuelve el texto del elemento path2
        """
        e = self.p.find(path2)
        if e:
            return e.text.strip()
        return None


    def col(self, path2col: str, col_type: str) -> int:
        """
        devuelve el texto del elemento col que es un subelemento en path
            y cuyo type es col_type
        """
        cols = self.p.findall(path2col)
        for col in cols:
            if col.get('type') == col_type:
                return int(col.text)
        return None


    def sql_get(self, mtype: str) -> bool:
        """
        devuelve el elemento sql con type==mtype
        """
        sqls = self.p.findall('sql')
        if not sqls:
            raise ValueError('El proyecto no tiene elementos sql')
        for sql in sqls:
            if sql.get('type').strip() == mtype:
                return sql
        return None


    def sql_type_exists(self, mtype: str) -> bool:
        """
        devuelve True si encuentra un elemento sql con type==mtype
        """
        e = self.p.sql_get(mtype)
        if e:
            return True
        return False


#    def col_get(self, sql_type: str, col_type: str ) -> int:
#        """
#        devuelve el texto del elemento col con type col_type en el elemento
#        sql con type sql_type
#        """
#        esql = self.p.sql_get(sql_type)


# =========================================================================




    def __evaluate_1_element(self, cadena):
        """
        devuelve la evaluacion del texto del tag cadena
        se comprueba que no hay mas de 1 tag
        """
        from ast import literal_eval
        a = self.p.findall(cadena)
        if len(a) > 1:
            raise Exception('solo se permite un tag {}'.format(cadena))
        return literal_eval(a[0].text.strip())


    def project_name_get(self):
        return self.p.attrib['name']


    def project_type_get(self):
        return int(self.p.attrib['type'])


    def file_name_get(self):
        a = self.p.find('file')
        return a.attrib['name']


    def file_name_cols_get(self):
        a = self.p.findall('file/col')
        cols = [int(col.text.strip()) for col in a]
        return cols


    def file_name_iths_get(self):
        cols = self.file_name_cols_get()
        iths = [col-1 for col in cols]
        return iths


    def graf_type_get(self):
        a = self.p.findall('graf')
        if len(a) > 1:
            raise Exception('solo se permite un tag project/graf')
        return a[0].attrib['type']


    def graf_axis_name_get(self):
        a = self.__evaluate_1_element('graf/axis_name')
        return a


    def __htext(self, cad):
        a = self.p.find(cad)
        if a is None:
            return 36
        else:
            a = a.text.strip()
            if a.isdigit():
                a = int(a)
                if a > 45:
                    a = 45
                elif a < 36:
                    a = 36
                return a
            else:
                return 36


    def __sql_atrib_by_type(self, mtype, atrib):
        a = self.p.findall('sql')
        for a1 in a:
            if a1.attrib['type'].strip() == mtype:
                return a1.attrib[atrib].strip()
        return None


    def __sql_by_type(self, mtype):
        a = self.p.findall('sql')
        for a1 in a:
            if a1.attrib['type'].strip() == mtype:
                return a1
        return None


    def __sql_bdd(self, slq_type):
        a = self.__sql_by_type(slq_type)
        if a is None:
            raise Exception('sql_bdd {} no se encuentra el valor' \
                            .format(slq_type))
        return a.attrib['bdd'].strip()


    def __sql_select(self, slq_type):
        a = self.__sql_by_type(slq_type)
        if a is None:
            raise Exception('sql_select {} no se encuenra el valor' \
                            .format(slq_type))
        return a.attrib['select'].strip()


    def __sql_col(self, slq_type, tag_name):
        a = self.__sql_by_type(slq_type)
        b = a.find(tag_name)
        return int(b.attrib['col'].strip())

    @staticmethod
    def __check_keys_in_dict(d0, d1):
        """
        check that all the d1' keys are in d0
        """
        import io
        ref_keys = list(d0.keys())
        output = io.StringIO()
        for k in list(d1.keys()):
            if not k in ref_keys:
                a = ' {}'.format(k)
                output.write(a.decode('Latin-1'))
        contents = output.getvalue()
        output.close()
        if len(contents) > 0:
            raise Exception('d1 tiene keys que no están en d0: {}' \
                            .format(contents))


    def __str__(self):
        from xml.etree.ElementTree import tostring
        a = tostring(self.p, encoding="iso-8859-1" )
        return str(a, encoding="iso-8859-1")


    def sql_master_bdd_get(self):
        e = self.__sql_by_type('master')
        if e:
            return e.attrib['bdd'].strip()


    def sql_master_select_get(self):
        return self.__sql_select('master').strip()


    def sql_master_titul_get(self):
        """
        el titulo del grafico se devuelve como una lista de diccionarios en
            que cada elemento de la lista es una linea del titulo y cada linea
            tiene 3 elementos
        'line':núm de linea del titulo (recomendado más 2)
        'text':es un string que puede contener moldes para ser sustituidos por
            alguna de las columnas del select master
        'iths':es cada una de las columnas-1 que se consideran del select
            master
        """
        a = self.__sql_by_type('master')
        b = a.findall('titul')
        c = []
        for b1 in b:
            line = int(b1.attrib['line'].strip())
            text = b1.attrib['text'].strip()
            cc = b1.findall('col')
            cols = [int(cc1.text.strip())-1 for cc1 in cc]
            c.append({'line':line, 'text':text, 'iths':cols})
        return c


    def sql_master_cod_col_get(self):
        return self.__sql_col('master', 'cod')


    def sql_master_x_col_get(self):
        return self.__sql_col('master', 'x')


    def sql_master_y_col_get(self):
        return self.__sql_col('master', 'y')


    def sql_upper_relation_bdd_get(self):
        """
        el elemento sql con type upper_relation es opcional
        """
        e = self.__sql_by_type('upper_relation')
        if e:
            return e.attrib['bdd'].strip()


    def sql_upper_relation_select_get(self):
        if self.__sql_by_type('upper_relation') is None:
            return ''
        return self.__sql_select('upper_relation')


    def sql_upper_relation_master_cod_get(self):
        if self.__sql_by_type('upper_relation') is None:
            return ''
        return self.__sql_col('upper_relation', 'current')


    def sql_upper_relation_others_cod_get(self):
        if self.__sql_by_type('upper_relation') is None:
            return ''
        return self.__sql_col('upper_relation', 'others')


    def __sql_upper_relation_sql_distancia_attrib(self, sql_type, attrib_name):
        a = self.__sql_by_type('upper_relation')
        if a is None:
            return ''
        b = a.findall('sql')
        for b1 in b:
            if b1.attrib['type'].strip() == sql_type:
                return b1.attrib[attrib_name].strip()


    def sql_upper_relation_sql_distancia_bdd_get(self):
        a = self.__sql_upper_relation_sql_distancia_attrib('distancia', 'bdd')
        if a is None:
            a = ''
        return a


    def sql_upper_relation_sql_distancia_select_get(self):
        return self.__sql_upper_relation_sql_distancia_attrib('distancia',
                                                              'select')


    def sql_upper_bdd_get(self):
        """
        el elemento sql con type upper es opcional, no es necesario si
        type upper_relation no esta presente
        """
        e = self.__sql_by_type('upper')
        if e:
            return e.attrib['bdd'].strip()


    def sql_upper_select_get(self):
        if self.__sql_by_type('upper') is None:
            return ''
        return self.__sql_select('upper').strip()


    def sql_upper_cod_col_get(self):
        if self.__sql_by_type('upper') is None:
            return ''
        self.__sql_col('upper', 'cod')


    def sql_upper_x_col_get(self):
        if self.__sql_by_type('upper') is None:
            return ''
        return self.__sql_col('upper', 'x')


    def sql_upper_y_col_get(self):
        if self.__sql_by_type('upper') is None:
            return ''
        return self.__sql_col('upper', 'y')


    def sql_lower_relation_bdd_get(self):
        """
        el tag sql con type lower_relation es opcional
        """
        e = self.__sql_by_type('lower_relation')
        if e:
            return e.attrib['bdd'].strip()


    def sql_lower_relation_select_get(self):
        if self.__sql_by_type('lower_relation') is None:
            return ''
        return self.__sql_select('lower_relation')


    def sql_lower_relation_master_cod_get(self):
        if self.__sql_by_type('lower_relation') is None:
            return ''
        return self.__sql_col('lower_relation', 'current')


    def sql_lower_relation_others_cod_get(self):
        if self.__sql_by_type('lower_relation') is None:
            return ''
        return self.__sql_col('lower_relation', 'others')


    def sql_lower_bdd_get(self):
        """
        el elemento sql con type lower es opcional, no es necesario si
        type lower_relation no esta presente
        """
        e = self.__sql_by_type('lower')
        if e:
            return e.attrib['bdd'].strip()


    def sql_lower_select_get(self):
        if self.__sql_by_type('lower') is None:
            return ''
        return self.__sql_select('lower')


    def sql_lower_cod_col_get(self):
        if self.__sql_by_type('lower') is None:
            return ''
        self.__sql_col('lower', 'cod')


    def sql_lower_x_col_get(self):
        if self.__sql_by_type('lower') is None:
            return ''
        return self.__sql_col('lower', 'x')


    def sql_lower_y_col_get(self):
        if self.__sql_by_type('lower') is None:
            return ''
        return self.__sql_col('lower', 'y')


    def sql_upper_locations_bdd_get(self):
        """
        el tag sql con type upper_locations es opcional
        """
        e = self.__sql_by_type('upper_locations')
        if e:
            return e.attrib['bdd'].strip()


    def sql_upper_locations_select_get(self):
        e = self.__sql_by_type('upper_locations')
        if e:
            return e.attrib['bdd'].strip()
        if self.__sql_by_type('upper_locations') is None:
            return ''
        return self.__sql_select('upper_locations')


    def sql_lower_locations_bdd_get(self):
        """
        el tag sql con type lower_locations es opcional
        """
        e = self.__sql_by_type('lower_locations')
        if e:
            return e.attrib['bdd'].strip()


    def sql_lower_locations_select_get(self):
        if self.__sql_by_type('lower_locations') is None:
            return ''
        return self.__sql_select('lower_locations')


    def __check_sql_common(self, sqls: list, mtype: str,
                           optional: bool) -> bool:
        """
        comprueba los elementos comununes de un elemento sql
        Si está presente devuelve True; en caso contrario devuelve False
        """
        from os.path import isfile
        n = 0
        for i, e in enumerate(sqls):
            if e.get('type').strip() == mtype:
                n += 1
                ielement = i
        if optional:
            if n > 1:
                raise ValueError(f'El proyecto debe tener 0 o 1 elementos' +\
                                 f' sql type="{mtype}"')
            elif n == 0:
                return False
        else:
            if n != 1:
                raise ValueError(f'El proyecto debe tener 1 elementos sql' +\
                                 f' type="{mtype}"')

        bdd = sqls[ielement].get('bdd')
        if bdd:
            if not isfile(bdd.strip()):
                raise ValueError(f'No existe el fichero\n{bdd}\n' +\
                                 f'del elemento sql type="{mtype}"')
        else:
            raise ValueError(f'El elemento sql type="{mtype}" debe' +\
                             ' tener un atributo bdd')

        select = sqls[ielement].get('select')
        if not select:
            raise ValueError(f'El elemento sql type="{mtype}" debe' +\
                             ' tener un atributo select')
        return True


    @staticmethod
    def xml_tree_2file(xml_as_str, dst=None):
        """
        graba xml_as_str en dst
        """
        import xml.dom.minidom

        if dst==None:
            dst=Project.__xml_file_mod

        axml = xml.dom.minidom.parseString(xml_as_str)
        pretty_xml_as_string = axml.toprettyxml()

        f = open(dst, 'w')
        f.write('{}'.format(pretty_xml_as_string))
        f.close()


