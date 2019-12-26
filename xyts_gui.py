# -*- coding: latin-1 -*-
import tkinter as tk
from traceback import format_exc
import numpy as np
import littleLogging as logging


class User_interface(tk.Frame):
    """
    incialización de variables
    """

    __width = 660
    __height = 460
    __xoffset = 200
    __yoffset = 150

    __file_last_do = 'xyts_lastdo.txt'
    __file_last_do_sections = ('Files', 'Select_dates')
    __xml = 'xyts.xml'
    __file_help = 'xyts_help.txt'
    __file_summary = '_xyts_resumen.txt'
    __file_locations = '_xyts_locations.txt'
    __lower_date = '01/01/1900'
    __title_window = 'xyts -xy time series-'
    __program_files = (__file_last_do, __file_help)


    def __init__(self, master):
        """
        Se dibula la gui
        """
        try:
            # geometría
            self.master = master
            self.master.title(User_interface.__title_window)
            self.master.geometry("{0:d}x{1:d}+{2:d}+{3:d}" \
                                 .format(User_interface.__width,
                                         User_interface.__height,
                                         User_interface.__xoffset,
                                         User_interface.__yoffset))
            self.master.maxsize(User_interface.__width,User_interface.__height)
            self.master.protocol('WM_DELETE_WINDOW',self.__exitMethod)

            self.fname=User_interface.__xml

            # variables específicas
            # lista de objetos Project en el fichero xyts_gui.__xml
            self.projects = []
            # índice del proyecto seleccionado en self.projects
            self.selected_project: int = -1
            # nombre del proyecto seleccionado
            self.selected_project_show = tk.StringVar()
            # directorio de resultados
            self.path_out = tk.StringVar()
            # indicador del número de gráfico terminado
            self.icount = tk.IntVar()
            # número total de gráficos potenciales en el proyecto
            self.ngraf = tk.IntVar()
            # indicador de grabar los datos representados [0, 1]
            self.dataToFile = tk.IntVar()
            # indicador de grabar solo el primer gráfico
            self.only1UpperPlot = tk.IntVar()
            # indicador de grabar solo el gráfico superior
            self.upperPlotOnly = tk.IntVar()
            # indicador de grabar el fichero de localizaciones de los puntos
            self.grabar_localizaciones = tk.IntVar()

            self.__readLastDo()
            self.dataToFile.set(1)

            self.__cuerpo_put()
            self.__action_buttons_put()

            self.master.mainloop()

        except:
            a = format_exc()
            logging.append(a, toScreen=False)
            tk.messagebox.showerror(self.__module__,a)
            self.__exitMethod()


    def __cuerpo_put(self):
        """
        lee el fichero xyts.xml y muestra la lista de proyectos disponibles
        """

        frm_grupo_01 = tk.Frame(self.master, borderwidth=2,
                                relief=tk.GROOVE, pady=3)

        frm_01 = tk.Frame(frm_grupo_01)
        tk.Label(frm_01, text= 'Proyectos en {}' \
                 .format(User_interface.__xml), pady=5).pack(side=tk.TOP,
                        anchor=tk.CENTER)
        frm_01.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        # list box para proyectos disponibles
        frm_05 = tk.Frame(frm_grupo_01,borderwidth=2, relief=tk.SUNKEN)
        v_scrollbar_05_01 = tk.Scrollbar(frm_05, orient=tk.VERTICAL)
        self.listbox_05_01 = tk.Listbox(frm_05,selectmode=tk.BROWSE,
                yscrollcommand=v_scrollbar_05_01.set,
                width=45, height=9)
        self.__cargar_lista_proyectos_en_listbox()
        self.listbox_05_01.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.listbox_05_01.bind("<Button-3>", self.__project_show)
        v_scrollbar_05_01.pack(side=tk.RIGHT, fill=tk.Y)
        v_scrollbar_05_01.config(command=self.listbox_05_01.yview)
        frm_05.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        frm_07 = tk.Frame(frm_grupo_01)
        h_scrollbar_07_01 = tk.Scrollbar(frm_07, orient=tk.HORIZONTAL)
        h_scrollbar_07_01.pack(side=tk.TOP, fill=tk.X)
        h_scrollbar_07_01.config(command=self.listbox_05_01.xview)
        frm_07.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        frm_grupo_01.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH,
                          expand=tk.YES)

        frm_08 = tk.Frame(self.master,borderwidth=2)
        tk.Button(frm_08, text="Seleccionar", padx=5, pady=2,
                  command=self.__select_project) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_08, text="Ver selección", padx=5, pady=2,
                  command=self.__verProyecto) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_08, text="Quitar selección", padx=5, pady=2,
                  command=self.__deSelectProyecto) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        frm_08.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        frm_grupo_10 = tk.Frame(self.master, borderwidth=2,
                                relief=tk.GROOVE, pady=3)

        frm_10 = tk.Frame(frm_grupo_10)
        tk.Label(frm_10, text = "Projecto seleccionado: ", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm_10, textvariable = self.selected_project_show, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_10 = tk.Frame(frm_grupo_10)
        tk.Label(frm_10,
                 text = "Rango de fechas. Fecha inferior",
                 pady=2).pack(side=tk.LEFT, anchor=tk.W)
        self.edlb=tk.Entry(frm_10,textvariable=self.lower_date, width=10,
                           state=tk.DISABLED)
        self.edlb.pack(side=tk.LEFT)
        tk.Label(frm_10, text = "Fecha superior", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        self.edub = tk.Entry(frm_10,textvariable=self.upper_date,
                             width=10, state=tk.DISABLED)
        self.edub.pack(side=tk.LEFT)
        tk.Button(frm_10,text="Validar", padx=1, pady=1,
                  command=self.validar_lub_date) \
                  .pack(side=tk.LEFT,anchor=tk.W, padx=4)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_12 = tk.Frame(frm_grupo_10)
        self.ckb1=tk.Checkbutton(frm_12,
                                 text="Gráfico superior, solo serie principal",
                                 variable=self.only1UpperPlot, pady=2,
                                 state=tk.DISABLED)
        self.ckb1.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb2=tk.Checkbutton(frm_12, text="Gráfico inferior deshabilitado",
                                 variable=self.upperPlotOnly, pady=2,
                                 state=tk.DISABLED)
        self.ckb2.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb3=tk.Checkbutton(frm_12, text="Grabar datos",
                                 variable=self.dataToFile) \
                                 .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm_12.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_grupo_10.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH,
                          expand=tk.YES)

        frm_grupo_05 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE,
                                pady=3)
        frm_05_01 = tk.Frame(frm_grupo_05)
        tk.Label(frm_05_01, text = "Directorio de resultados   ", pady=2) \
            .pack(side=tk.LEFT)
        tk.Button(frm_05_01,text="Seleccionar", padx=1, pady=2,
                  command=self.__select_dir_proyecto).pack(side=tk.LEFT)
        frm_05_01.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)
        frm_05_01 = tk.Frame(frm_grupo_05)
        tk.Entry(frm_05_01,textvariable=self.path_out, width=108) \
        .pack(side=tk.LEFT, expand=tk.YES, pady=2)
        frm_05_01.pack(side=tk.TOP, anchor=tk.W, expand=tk.YES)

        frm_05_01.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_grupo_05.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH,
                          expand=tk.YES)

        frm_grupo_15 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE,
                                pady=3)

        frm_10 = tk.Frame(frm_grupo_15)
        tk.Label(frm_10, text = "En ejecución:", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm_10, textvariable = self.icount, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm_10, text = '/',pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm_10, textvariable = self.ngraf, padx=8, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)

        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_grupo_15.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH,
                          expand=tk.YES)


    def __action_buttons_put(self):
        """
        Opciones de ejecución y resultados
        """
        frm_08 = tk.Frame(self.master,borderwidth=2)
        tk.Button(frm_08, text="Ejecutar", padx=5, pady=2,
                  command=self.__do_graphs) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_08, text="Finalizar", padx=5, pady=2,
                  command=self.__exitMethod) \
                  .pack(side=tk.RIGHT , anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_08, text="Ayuda", padx=5, pady=2,
                  command=self.__helpMenu) \
                  .pack(side=tk.RIGHT , anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_08, text="Ver log", padx=5, pady=2,
                  command=self.__wachtLogFile) \
                  .pack(side=tk.RIGHT, anchor=tk.W, fill=tk.X, padx=1)
        frm_08.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)


    def __readLastDo(self):
        """
        lee parámetros seleccionados de la última vez que se ejecutó el
        programa
        """
        import configparser
        from os import getcwd
        from os.path import exists
        from time import strftime

        defaults={'path_out': getcwd(),
                  'upper_date': strftime('%d/%m/%Y'),
                  'lower_date':User_interface.__lower_date}

        config = configparser.RawConfigParser()

        try:
            config.read(User_interface.__file_last_do)
            existsFileIni = True
        except:
            a='{}'.format(format_exc())
            logging.append(a, toScreen=False)
            existsFileIni = False

        try:
            self.path_out.set(config.get('Files', 'path_out'))
            if not exists(self.path_out.get()):
                self.path_out.set(defaults['path_out'])
        except:
            if not existsFileIni:
                a='{}'.format(format_exc())
                logging.append(a)
            self.path_out.set(defaults['path_out'])

        self.upper_date.set(defaults['upper_date'])
        self.lower_date.set(defaults['lower_date'])


    def __writeLastDo(self):
        """
        escribe parámetros seleccionados de la ejecución a la salida del
            programa
        se añade una nueva seccion, darla de alta en
            Csv_tk.__file_last_do_sections
        si se escribe una nueva variable, modificar el método sessionLastRead
        """
        import configparser
        from shutil import copyfile
        from os.path import exists

        try:
            if exists(User_interface.__file_last_do):
                copyfile(User_interface.__file_last_do, '{}.bak' \
                         .format(User_interface.__file_last_do))

            config = configparser.RawConfigParser()

            config.add_section('Project')
            try:
                config.set('Project', 'last project', '{}' \
                           .format(self.selected_project_show.get()))
            except:
                config.set('Project', 'last project', '')

            config.add_section('Files')
            config.set('Files', 'path_out', '{}'.format(self.path_out.get()))

            config.add_section('Select_dates')
            config.set('Select_dates', 'upper_date', '{}' \
                       .format(self.upper_date.get()))
            config.set('Select_dates', 'lower_date', '{}' \
                       .format(self.lower_date.get()))

            with open(User_interface.__file_last_do, 'w') as configfile:
                config.write(configfile)

        except:
            a = format_exc()
            logging.append(a, toScreen=False)


    def __exitMethod(self):
        """
        acciones cuando abandono la gui
        """
        self.__writeLastDo()
        self.master.destroy()


    def __helpMenu(self):
        """
        lee el fichero de ayuda
        """
        from io import StringIO
        lines = StringIO()
        try:
            f = open(User_interface.__file_help, 'r')
            for line in f.readlines():
                lines.write(line)
            f.close()
        except:
            a = format_exc()
            logging.append(a, toScreen=False)
            lines.write(f'Error al leer {User_interface.__file_help}')

        contents=lines.getvalue()
        Child_show_text(self.master,contents,'Ayuda')


    def __wachtLogFile(self):
        """
        muestra el contenido del fichero de log
        """
        contents = logging.get_as_str()
        Child_show_text(self.master, contents, 'Fichero log')


    def __select_dir_proyecto(self):
        """
        selecciona el directorio de resultados
        """
        from os.path import normpath
        from tkinter.filedialog import askdirectory

        dst = askdirectory(initialdir=self.path_out.get(),
                           title='Seleccionar directorio', parent=self.master)
        if dst is None:
            return
        if not dst:
            return

        self.path_out.set(normpath(dst))


    def __cargar_lista_proyectos_en_listbox(self):
        """
        carga la lista de proyetos leidos en el fichero xml
        """
        from xyts_project import Project

        self.projects=Project.read_projects()
        if not self.projects:
            return
        if self.listbox_05_01.size() > 0:
            self.listbox_05_01.delete(0, tk.END)
        for project in self.projects:
            self.listbox_05_01.insert(tk.END, '{}' \
                                      .format(project.project_name_get()))


    def __select_project(self):
        """
        selecciona un projecto de la lista y activa widgets según contenido
        """
        from os.path import isfile
        items = list(map(int, self.listbox_05_01.curselection()))
        if not items:
            return
        db = self.projects[items[0]].element_get('db').text.strip()
        self.master.config(cursor="wait")
        if not isfile(db):
            self.master.config(cursor="arrow")
            logging.append(f'No se encuentra el fichero {db}')
            tk.messagebox.showerror('', f'No se encuentra el fichero\n{db}')
            return
        self.master.config(cursor="arrow")
        self.selected_project = items[0]
        n = len(self.selected_project_show.get())
        self.selected_project_show.set(n*' ')
        self.selected_project_show.set(self.projects[self.selected_project] \
                                       .project_name_get())
        self.listbox_05_01.selection_clear(0, tk.END)

        if self.projects[self.selected_project] \
               .exists_element('upper_relation'):
            self.only1UpperPlot.set(0)
            self.ckb1.config(state='normal')

        if self.projects[self.selected_project] \
               .exists_element('lower_relation'):
            self.upperPlotOnly.set(0)
            self.ckb2.config(state='normal')

        self.edlb.config(state='normal')
        self.edub.config(state='normal')


    def __project_show(self, event):
        """
        llama a __verProyecto, esto podría mejorarse
        """
        self.__verProyecto()


    def __verProyecto(self):
        """
        muestra la informacion del projecto seleccionado
        """
        if not self.selected_project:
            return
        a = self.projects[self.selected_project]
        Child_show_text(self.master, str(a), 'Proyecto seleccionado')


    def __deSelectProyecto(self):
        """
        deselecciona un projecto previamente seleccionado
        """
        self.ckb1.config(state='disabled')
        self.ckb2.config(state='disabled')
        self.edub.config(state='disabled')
        self.edlb.config(state='disabled')
        self.listbox_05_01.selection_clear(0, tk.END)
        self.selected_project =- 1
        i = len(self.selected_project_show.get())
        self.selected_project_show.set(i*' ')


    def __do_graphs(self):
        """
        llamada al metodo en el que se ejecutan los select y se
        preparan los graficos
        """
        from xyts_drv_to_matplotlib import test
        if not self.selected_project:
            tk.messagebox.showinfo(self.__module__,
                                   "No ha seleccionado un proyecto")
            return
        self.master.configure(cursor='watch')
        self.ngraf.set(0)
        self.icount.set(0)
        try:
            for n, m in test():
                self.icount.set(n)
                self.ngraf.set(m)
                self.master.update_idletasks()
                tk.messagebox.showerror('', 'Proceso terminado')
#            self.__call_to_matplotlib(self.projects[self.selected_project])
        except:
            from traceback import format_exc
            a = format_exc()
            logging.append(a, toScreen=False)
            tk.messagebox.showerror(self.__module__, a)
        finally:
            self.ngraf.set(0)
            self.icount.set(0)
            self.master.configure(cursor='arrow')
            self.master.update_idletasks()


    @staticmethod
    def __str_from_row(text,  row, col=[], ext='', inumber=0):
        """
        se forma un str a partir de un str en el que se sustituyen
        los valores de row indicados en col
        si se pasa ext se añade al final con un punto delante
        si col incluye un numero <0 en str se coloca inumber

        text: es un str de python con posibles moldes para ser sustituidos
            con valores en row, por ej '{0:03d}_{1}
        row: es la primera fila de datos donde se toman algunas columnas
            para formar el nombre, ej. ['llano',1,2]
        col: es una lista con los indices de row que van a ser utilizados
            si un indice tiene valor <0 indica que en vez de tomar un valor de row
            se coloca el enterno inumber, ej [0,]
        ext: extension del fichero, ej 'txt'
        igraf: numero entero
        """
        if not col:
            if ext:
                text = text + '.' + ext
            return text

        a = '"' + text + '"'
        for k, c1 in enumerate(col):
            if k == 0:
                if c1 < 0:
                    b = '.format(inumber'
                else:
                    b = '.format(row[{0:d}]'.format(c1)
            else:
                if c1 < 0:
                    b = b + ',inumber'
                else:
                    b = b + ',row[{0:d}]'.format(c1)

        c = a + b + ')'
        b = eval(c)
        if ext:
            b = b + '.' + ext
        return b


    def __call_to_matplotlib(self):
        """
        se ejecutan los select y se preparan los datos para llamar a las funciones de
        matplotlib que dibuja los graficos XY
        """
        from datetime import date
        from math import sqrt
        import os.path
        import pyodbc
        from xyts_mpl import plt1_nst, plt2_nst, plt1_nst_2_xml, plt2_nst_2_xml

        dir_dst = '{}'.format(self.path_out.get())
        prj = self.projects[self.selected_project]

        # conexiones a la base de datos
        db = prj.element_get('db')
        dbtype = db.get('type')
        if dbtype == 'ms_access':
            con_str = r'DRIVER={Microsoft Access Driver ' +\
            '(*.mdb, *.accdb)}; ' + f'DBQ={db.text};'
        else:
            raise ValueError('El tipo de db no está implementado')
        conn = pyodbc.connect(con_str)
        cur = conn.cursor()

        # datos puntos principales en plot(1, 1)
        select_master = prj.element_get('master/select').text.strip()
        cur.execute(select_master)
        data_master = [row for row in cur]

        if not data_master:
            a = 'la select master no devuelve datos'
            logging.append(a, toScree=False)
            tk.messagebox.showinfo('', a )
            return

        f_summary = open(User_interface.__file_summary, 'w')
        f_summary.write('cod\tfecha1\tfecha2\tnum_datos\n')
        icod = prj.element_with_atribb_get('master/col', 'type', 'cod')
        icod = int(icod) - 1
        ixutm = prj.element_with_atribb_get('master/col', 'type', 'xutm')
        if ixutm:
            ixutm = int(ixutm) - 1
        iyutm = prj.element_with_atribb_get('master/col', 'type', 'yutm')
        if iyutm:
            iyutm = int(iyutm) - 1

        self.ngraf.set(len(data_master))
        self.master.update_idletasks()

        ngraph = 0
        cod_master = []  # codigos principales del plot superior
        cod_upper = []   # codigos aux.s del plot sup. q no están en cod_master
        cod_lower = []
        minmax = None
        for row in data_master:
            select_upper = prj.select_get('upper')
            cur.execute(select_upper, row[icod], )


            data_in_upper_plot=data_in_lower_plot = False
            x = [date(item.year, item.month, item.day) \
                 for item in data[ini:end,ix]]
            y = [item for item in data[ini:end, iy]]

            if len(x) < 2:
                self.icount.set(self.icount.get() + 1)
                a = 'El punto {} tiene solo 1 dato y no se representa' \
                .format(str(data[ini][icod]))
                logging.append(a, toScreen=False)
                numIncidencias += 1
                if len(x) > 0:
                    dt1 = '{}/{}/{}'.format(data[ini][ix].day,
                                            data[ini][ix].month,
                                            data[ini][ix].year)
                    data_summary.write('{0}\t{1}\t{2}\t{3:d}\n' \
                                       .format(data[ini][icod],
                                               dt1, dt1, len(x)))
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

        self.master.update()
        self.ngraf.set(0)
        self.icount.set(0)
        self.master.update_idletasks()


    def validate_date(self, sd, showerror=True):
        """
        comprueba que el string sd contiene una fecha valida
        el formadto de sd es d/M/Y, los separadores pueden ser / o -
        """
        from datetime import date
        from inspect import stack

        sd=sd.strip()
        if sd:
            if sd.find('/') >= 0:
                dw = sd.split('/')
            elif sd.find('-') >= 0:
                dw = sd.split('-')
            else:
                if showerror:
                    tk.messagebox.showinfo(stack()[0][3],
                                           'los separadores válidos en la' +\
                                           ' fecha {} deben ser / o - ' \
                                           .format(sd))
                return None
            try:
                return date(int(dw[2]), int(dw[1]), int(dw[0]))
            except:
                if showerror:
                    tk.messagebox.showinfo(stack()[0][3],
                                           'la fecha {} introducida no es ' +\
                                           'válida'.format(sd))
                return None
        else:
            if showerror:
                tk.messagebox.showerror(stack()[0][3],
                                        'no ha introducido la fecha')
            return None


    def dates_compare(self, date1, date2):
        """
        compara las fechas inferior y superior de una select cuando
        ambas están definidas
        """
        from inspect import stack

        if date1 is None or date2 is None:
            return False

        if date1 == date2:
            a = tk.messagebox.askyesno(stack()[0][3],
                                       'las 2 fechas son iguales\ndesea ' +\
                                       'mantenerlas?')
            if a:
                return True
            else:
                return False
        elif date1 > date2:
            date1, date2 = date2, date1
            if a:
                d = date1
                date1 = date2
                date2 = d
                self.lower_date.set(date1.strftime('%d/%m/%Y'))
                self.upper_date.set(date2.strftime('%d/%m/%Y'))
                return True
            else:
                return False


    def validar_lub_date(self,mostrar=1):
        """
        validad lower and upper bound date
        """
        e = (self.edlb, self.edub)
        sd = (self.lower_date, self.upper_date)
        d = [None, None]
        for i in range(len(e)):
            if e[i].cget('state') == 'disabled':
                continue
            try:
                d[i] = self.validate_date(sd[i].get())
                if d[i] is None:
                    return False
            except:
                from traceback import format_exc
                tk.messagebox.showerror(self.__module__,"{}" \
                                        .format(format_exc()))
                return False
        self.dates_compare(d[0], d[1])

        if mostrar == 1:
            tk.messagebox.showinfo(self.__module__,
                                   'Las fechas introducidas son válidas')
        return True


    def replace_dates_in_select(self, select_stm):
        """
        las consultas que utilizan fechas deben tener unos placeholders
            en la select
        del fichero de inicio definidos en __lowerBoundDate_mask y
            __upperBoundDate_mask
        en el método se sustituyen los placeholders por el contenido de
            los campos de texto
        de la ui donde se introducen las fechas
        """
        if select_stm.find(self.__lowerBoundDate_mask) >= 0:
            d = self.validate_date(self.lower_date.get())
            strdate = d.strftime("%m/%d/%Y")
            select_stm = select_stm.replace(self.__lowerBoundDate_mask,
                                            strdate)
        if select_stm.find(self.__upperBoundDate_mask) >= 0:
            d = self.validate_date(self.upper_date.get())
            strdate = d.strftime("%m/%d/%Y")
            select_stm = select_stm.replace(self.__upperBoundDate_mask,
                                            strdate)
        return select_stm


class Child_show_text:

    def __init__(self, master, msg, title):
        """
        Ayuda del programa
        """
        self.master = master
        self.slave = tk.Toplevel(master)
        self.slave.title(title)

        frm_10 = tk.Frame(self.slave)
        vScrollbar_1 = tk.Scrollbar(frm_10, orient=tk.VERTICAL)
        self.txt_1 = tk.Text(frm_10, background='White', foreground='Black',
                             yscrollcommand=vScrollbar_1.set,
                             width=70, height=25, wrap=tk.WORD,
                             relief=tk.GROOVE, spacing2=1)
        vScrollbar_1.pack(side=tk.RIGHT,fill=tk.Y, expand=0)
        self.txt_1.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        vScrollbar_1.config(command=self.txt_1.yview)
        frm_10.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH,
                    expand=tk.YES, padx=2, pady=2)

        if isinstance(msg, type('a')):
            self.txt_1.insert(tk.END,msg)
        if isinstance(msg, type([])) or isinstance(msg, type(())):
            for linea in msg:
                self.txt_1.insert(tk.END, msg)
        self.txt_1.config(state=tk.DISABLED)
        self.slave.grab_set()
        self.slave.focus_set()
        self.slave.wait_window()


    def terminar(self):
        """
        cierra la ventana
        """
        self.slave.destroy()
        self.master.lift()
