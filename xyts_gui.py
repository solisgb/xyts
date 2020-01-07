# -*- coding: latin-1 -*-
from datetime import date, datetime
import tkinter as tk
from traceback import format_exc
import littleLogging as logging

WIDTH, HEIGHT = 660, 460
XOFFSET, YOFFSET = 200, 150
TKINTNULL = 9999999
FILE_HISTORY = 'xyts_history.db'
FILE_PROJECTS = 'xyts.xml'
FILE_HELP = 'xyts_help.txt'
LOWER_DATE = '01/01/1900'
TITLE_WINDOW = 'xyts -xy time series-'


class GUI(tk.Frame):
    """
    GUI con tkinter. No tiene ningún método público salvo la instanciación
        de la clase
    """

    def __init__(self, master):
        """
        Se dibula la gui
        """
        # nombre del fichero xml con la definición de los projectos
        self.fname = FILE_PROJECTS
        # lista de objetos Project en el fichero xyts_gui.FILE_PROJECTS
        self.projects = []
        # índice del proyecto seleccionado en self.projects
        self.selected_project: int = TKINTNULL
        # nombre del proyecto seleccionado
        self.selected_project_show = tk.StringVar()
        # fecha inicial en las select
        self.lower_date = tk.StringVar()
        # fecha final en las select
        self.upper_date = tk.StringVar()
        # indicador de grabar solo la primera serie del gráf. principal
        self.only_master = tk.IntVar(value=0)
        # indicador de grabar solo el gráfico principal
        self.upper_graph_only = tk.IntVar(value=0)
        # indicador de grabar los datos de cada figura
        self.write_data = tk.IntVar(value=0)
        # directorio de resultados
        self.path_out = tk.StringVar()
        # indicador del número de figuras grabadas
        self.icount = tk.IntVar(value=0)
        # número total de figuras totales en el proyecto en ejecución
        self.ngraph = tk.IntVar(value=0)
        # pausar la ejecución en la figura número n (entero)
        self.stop_from_graph = tk.IntVar(value=0)
        # siguiente pausa cada m (entero) figuras
        self.stop_graph_step = tk.IntVar(value=0)
        # elemento tkinter root
        self.master = master

        try:
            self.read_last_action()
            self.master_geometry()
            self.widgets_set()
            self.master.mainloop()
        except:
            a = format_exc()
            logging.append(a, toScreen=False)
            tk.messagebox.showerror('Error', a)
            self.exit_gui()


    def master_geometry(self):
        """
        geometría del elemento root
        """
        self.master.title(TITLE_WINDOW)
        self.master.geometry(f'{WIDTH:d}x{HEIGHT:d}+' +\
                             f'{XOFFSET:d}+{YOFFSET:d}')
        self.master.maxsize(WIDTH, HEIGHT)
        self.master.protocol('WM_DELETE_WINDOW', self.exit_gui)


    def widgets_set(self):
        """
        dibuja las widgets
        """
        self.show_selected_project()
        self.list_box_projects()
        self.select_project_buttons()
        self.entry_dates()
        self.control_series_in_graphs()
        self.stop_graphs_at_number()
        self.select_dir_output()
        self.show_graphs_progress()
        self.execute_buttons()


    def show_selected_project(self):
        """
        muestra el proyecto seleccionado
        """
        frm1 = tk.Frame(self.master, relief=tk.GROOVE, pady=2)
        tk.Label(frm1, text = "Projectos -> seleccionado: ") \
        .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm1, textvariable = self.selected_project_show) \
        .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.YES)


    def list_box_projects(self):
        """
        listbox con los projectos
        """
        frm1 = tk.Frame(self.master, relief=tk.GROOVE, borderwidth=2, pady=2)
        v_scrollbar = tk.Scrollbar(frm1, relief=tk.RAISED, orient=tk.VERTICAL)
        self.lb_prjs = tk.Listbox(frm1,selectmode=tk.BROWSE,
                                  yscrollcommand=v_scrollbar.set,
                                  width=45, height=11)
        self.projects_in_listbox_set()
        self.lb_prjs.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.lb_prjs.bind("<Button-3>", self.project_show)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        v_scrollbar.config(command=self.lb_prjs.yview)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)
        frm1 = tk.Frame(self.master, borderwidth=2, pady=2)
        h_scrollbar = tk.Scrollbar(frm1, relief=tk.RAISED,
                                   orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)
        h_scrollbar.config(command=self.lb_prjs.xview)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)


    def select_project_buttons(self):
        """
        botones para seleccionar un proyecto, visualizarlo y deseleccionarlo
        """
        frm1 = tk.Frame(self.master, relief=tk.GROOVE, borderwidth=2, pady=2)
        tk.Button(frm1, text="Seleccionar", padx=5, pady=2,
                  command=self.select_project, relief=tk.RIDGE) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm1, text="Ver selección", padx=5, pady=2,
                  command=self.project_show, relief=tk.RIDGE) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm1, text="Quitar selección", padx=5, pady=2,
                  command=self.remove_selected_project, relief=tk.RIDGE) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)


    def entry_dates(self):
        """
        Date entries y botones de utilidad relacionados con fechas
        """
        frm1 = tk.Frame(self.master, borderwidth=2, pady=2)
        tk.Label(frm1,
                 text = "Rango de fechas. Fecha inferior",
                 pady=2).pack(side=tk.LEFT, anchor=tk.W)
        self.edlb=tk.Entry(frm1, textvariable=self.lower_date, width=12,
                           justify=tk.RIGHT).pack(side=tk.LEFT)
        tk.Button(frm1, text="Primera", padx=1, pady=1,
                  command=self.date_first, relief=tk.RIDGE) \
        .pack(side=tk.LEFT, anchor=tk.W, padx=4)
        tk.Label(frm1, text="Fecha superior", pady=2) \
        .pack(side=tk.LEFT, anchor=tk.W)
        self.edub = tk.Entry(frm1, textvariable=self.upper_date, width=12,
                             justify=tk.RIGHT).pack(side=tk.LEFT)
        tk.Button(frm1, text="Hoy", padx=1, pady=1,
                  command=self.hoy, relief=tk.RIDGE) \
        .pack(side=tk.LEFT, anchor=tk.W, padx=4)
        tk.Button(frm1, text="Validar", padx=1, pady=1,
                  command=self.validate_dates, relief=tk.RIDGE) \
        .pack(side=tk.LEFT, anchor=tk.W, padx=4)
        frm1.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)


    def control_series_in_graphs(self):
        """
        Controla las series que se van a representar
        """
        frm1 = tk.Frame(self.master)
        self.ckb1=tk.Checkbutton(frm1,
                                 text="Gráfico superior, solo serie principal",
                                 variable=self.only_master, pady=2,
                                 state=tk.DISABLED)
        self.ckb1.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb2=tk.Checkbutton(frm1,
                                 text="Gráfico inferior deshabilitado",
                                 variable=self.upper_graph_only, pady=2,
                                 state=tk.DISABLED)
        self.ckb2.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb3=tk.Checkbutton(frm1, text="Grabar datos",
                                 variable=self.write_data) \
                                 .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm1.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)


    def stop_graphs_at_number(self):
        """
        Pausa la grabación de los gráficos según los valores de
            stop_from_graph y stop_graph_step
        """
        frm1 = tk.Frame(self.master)
        tk.Label(frm1,
                 text = "Pausar desde gráfico número",
                 pady=2).pack(side=tk.LEFT, anchor=tk.W)
        tk.Entry(frm1,textvariable=self.stop_from_graph,
                 width=5, justify=tk.RIGHT).pack(side=tk.LEFT)
        tk.Label(frm1, text = "Pausar cada", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Entry(frm1,textvariable=self.stop_graph_step,
                 width=10, justify=tk.RIGHT).pack(side=tk.LEFT)
        frm1.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)


    def select_dir_output(self):
        """
        Se selecciona el directorio deonde se graban los gráficos
        """
        frm1 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE, pady=2)
        tk.Button(frm1, text="Grabar en", padx=1, pady=2, relief=tk.RIDGE,
                  command=self.output_dir_set).pack(side=tk.LEFT, expand=tk.NO)
        tk.Entry(frm1, textvariable=self.path_out, width=98) \
        .pack(side=tk.LEFT, expand=tk.YES, pady=2)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)


    def show_graphs_progress(self):
        """
        Muestra el número de gráficos grabado
        """
        frm1 = tk.Frame(self.master, relief=tk.GROOVE, pady=2)
        tk.Label(frm1, text = "En ejecución:", pady=2) \
        .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm1, textvariable = self.icount, pady=2) \
        .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm1, text = '/',pady=2) \
        .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm1, textvariable = self.ngraph, padx=8, pady=2) \
        .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.YES)


    def execute_buttons(self):
        """
        Botón de ejecución y otros generales
        """
        frm1 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE, pady=2)
        tk.Button(frm1, text="Ejecutar", padx=5, pady=2,
                  command=self.do_graphs, relief=tk.RIDGE) \
        .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm1, text="Finalizar", padx=5, pady=2,
                  command=self.exit_gui, relief=tk.RIDGE) \
        .pack(side=tk.RIGHT , anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm1, text="Ayuda", padx=5, pady=2,
                  command=self.help_window, relief=tk.RIDGE) \
        .pack(side=tk.RIGHT , anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm1, text="Ver log", padx=5, pady=2,
                  command=self.show_log_file, relief=tk.RIDGE) \
        .pack(side=tk.RIGHT, anchor=tk.W, fill=tk.X, padx=1)
        frm1.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)


    @staticmethod
    def strdate8651_2sp(str_date: str, sep: str='-') -> str:
        """
        Cambia un str con formato fecha 'yyyy-mm-dd' (iso-8651) a un
            formato 'dd/mm/yyyy' (sp)
        """
        a = str_date.split(sep)
        d1 = date(int(a[0]), int(a[1]), int(a[2]))
        return d1.strftime('%d/%m/%Y')


    @staticmethod
    def strdate_sp2_8651(str_date: str, sep: str='/') -> str:
        """
        Cambia un str con formato fecha 'dd/mm/yyyy' (sp) a un
            formato 'yyyy-mm-dd' (iso-8651)
        """
        a = str_date.split(sep)
        d1 = date(int(a[2]), int(a[1]), int(a[0]))
        return d1.strftime('%Y-%m-%d')


    @staticmethod
    def strdate_sp_2date(str_date: str, sep: str='/') -> date:
        """
        Convierte un str con formato fecha 'dd/mm/yyyy' (sp) a un tipo date
        """
        a = str_date.split(sep)
        return date(int(a[2]), int(a[1]), int(a[0]))


    def insert_last_action(self):
        """
        Escribe parámetros seleccionados de la ejecución a la salida del
            programa
        """
        import sqlite3
        MAX_ACTIONS = 50

        try:
            con = sqlite3.connect(FILE_HISTORY)
            cur = con.cursor()
            cur.execute('create table if not exists history ' +\
                        '(fid integer primary key, ' +\
                        'project text, path_out text, lower_date text, ' +\
                        'upper_date text, date_action text)')

            path_out = self.path_out.get()
            lower_date = GUI.strdate_sp2_8651(self.lower_date.get())
            upper_date = GUI.strdate_sp2_8651(self.upper_date.get())
            d1 = datetime.today()
            d1 = d1.strftime('%Y-%m-%d %H:%M:%S')

            cur.execute('select fid from history')
            tmp = [item for item in cur.fetchall()]
            if len(tmp) >= MAX_ACTIONS:
                sql = 'delete from history where fid in (select min(fid) ' +\
                      'from history order by fid);'
                cur.execute(sql)
            sql = 'insert into history ' +\
                  '(path_out, lower_date, upper_date, date_action) ' +\
                  'values (?, ?, ?, ?)'
            cur.execute(sql, (path_out, lower_date, upper_date, d1))
            con.commit()
        except Exception:
            con.rollback()
            s = format_exc()
            logging.append(s, False)
        finally:
            con.close()


    def set_defaults(self, defaults: dict):
        self.path_out.set(defaults['path_out'])
        self.lower_date.set(defaults['lower_date'])
        self.upper_date.set(defaults['upper_date'])
        self.stop_from_graph.set(0)
        self.stop_graph_step.set(0)
        return


    def read_last_action(self):
        """
        Abre el fichero FILE_HISTORY y lee las columnas path_out, lower_date,
            y upper_date de la última ejecución; con estas columnas se
            rellenan las propiedades self.path_out, self.lower_date y
            self.upper_date
        """
        import sqlite3

        today1 = date.today()
        defaults = {'path_out': '',
                    'upper_date': today1.strftime('%d/%m/%Y'),
                    'lower_date': LOWER_DATE}

        try:
            con = sqlite3.connect(FILE_HISTORY)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('select * from history ' +\
                        'order by date_action desc limit 1')
            row = cur.fetchone()
            if not row:
                con.close()
                self.set_defaults(defaults)
                return
        except:
            self.set_defaults(defaults)
            return
        finally:
            con.close()
        lower_date = GUI.strdate8651_2sp(row['lower_date'])
        upper_date = GUI.strdate8651_2sp(row['upper_date'])
        self.path_out.set(row['path_out'])
        self.lower_date.set(lower_date)
        self.upper_date.set(upper_date)


    def exit_gui(self):
        """
        acciones cuando abandono la gui
        """
        self.insert_last_action()
        self.master.destroy()


    def help_window(self):
        """
        lee el fichero de ayuda y abre una ventana con su contenido
        """
        try:
            with open(FILE_HELP, 'r') as f:
                lines = f.readlines()
                lines = ''.join(lines)
        except:
            a = format_exc()
            logging.append(a, False)
            lines = (f'Error al leer {FILE_HELP}')
        Child_show_text(self.master, 'Ayuda', lines)


    def show_log_file(self):
        """
        muestra el contenido del fichero de log
        """
        contents = logging.get_as_str()
        Child_show_text(self.master, 'Fichero log', contents)


    def output_dir_set(self):
        """
        selecciona el directorio de resultados
        """
        from glob import glob
        from os.path import join, normpath
        from tkinter.filedialog import askdirectory

        dst = askdirectory(initialdir=self.path_out.get(),
                           title='Seleccionar directorio',
                           parent=self.master)
        if len(dst) == 0:
            return
        else:
            files = glob(join(dst, '*.*'))
            if files:
                if not tk.messagebox.askyesno('Directorio con ficheros',
                                              '¿Continuar?'):
                    return
        self.path_out.set(normpath(dst))


    def projects_in_listbox_set(self):
        """
        carga la lista de proyetos leidos en el fichero xml
        """
        from xyts_project import Project

        self.projects=Project.read_projects()
        if not self.projects:
            return
        if self.lb_prjs.size() > 0:
            self.lb_prjs.delete(0, tk.END)
        for project in self.projects:
            self.lb_prjs.insert(tk.END, '{}'.format(project.name_get()))


    def select_project(self):
        """
        selecciona un projecto de la lista y activa widgets según contenido
        """
        from os.path import isfile
        items = list(map(int, self.lb_prjs.curselection()))
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
                                       .name_get())
        self.lb_prjs.selection_clear(0, tk.END)

        if self.projects[self.selected_project] \
               .exists_element('upper_relation'):
            self.only_master.set(0)
            self.ckb1.config(state='normal')

        if self.projects[self.selected_project] \
               .exists_element('lower_relation'):
            self.upper_graph_only.set(0)
            self.ckb2.config(state='normal')


    def project_show(self):
        """
        muestra la informacion del projecto seleccionado
        """
        if self.selected_project > len(self.projects):
            return
        xml_str = self.projects[self.selected_project].pretty_xml_get()
        Child_show_text(self.master, 'Proyecto seleccionado', xml_str)


    def remove_selected_project(self):
        """
        deselecciona un projecto previamente seleccionado
        """
        self.ckb1.config(state='disabled')
        self.ckb2.config(state='disabled')
        if self.edub:
            self.edub.config(state='disabled')
        if self.edlb:
            self.edlb.config(state='disabled')
        self.lb_prjs.selection_clear(0, tk.END)
        self.selected_project = TKINTNULL
        i = len(self.selected_project_show.get())
        self.selected_project_show.set(i*' ')


    def do_graphs(self):
        """
        llamada al metodo en el que se ejecutan los select y se
            graban los graficos
        """
        from glob import glob
        from os.path import isdir, join

        def volver():
            self.ngraph.set(0)
            self.icount.set(0)
            self.master.configure(cursor='arrow')
            self.master.update_idletasks()

        if self.selected_project == TKINTNULL:
            tk.messagebox.showinfo(self.__module__,
                                   'No ha seleccionado un proyecto')
            return
        prj = self.projects[self.selected_project]
        dst = self.path_out.get()
        if not isdir(dst):
            tk.messagebox.showinfo(self.__module__,
                                   'El directorio seleccionado no existe')
            return
        files = glob(join(dst, '*.*'))
        try:
            self.validate_dates(False)
        except:
            return
        if files:
            if not tk.messagebox.askyesno('Directorio con ficheros',
                                          '¿Continuar?'):
                return

        self.master.configure(cursor='watch')
        self.ngraph.set(0)
        self.icount.set(0)
        d1 = GUI.strdate_sp_2date(self.lower_date.get())
        d2 = GUI.strdate_sp_2date(self.upper_date.get())
        counter = prj.xygraphs(dst, d1, d2, self.only_master.get(),
                               self.upper_graph_only.get(),
                               self.write_data.get())
        try:
            icontrol = self.stop_from_graph.get()
            for n, m in counter:
                self.icount.set(n)
                self.ngraph.set(m)
                self.master.update_idletasks()
                if n == icontrol:
                    if not tk.messagebox.askyesno(f'Gráfico {n}/{m}',
                                                  '¿Continuar?'):
                        volver()
                        return
                else:
                    icontrol += self.stop_graph_step.get()
        except ValueError as er:
            s = f'{er}'
            logging.append(s, False)
            tk.messagebox.showerror(self.__module__, s)
        except:
            from traceback import format_exc
            s = format_exc()
            logging.append(s, False)
            tk.messagebox.showerror(self.__module__, s)
        finally:
            volver()


    def validate_dates(self, show: bool=True):
        """
        Valida las fecha inicial y la final de la master select
        """
        def validate_1_date(str_date: str, sep='/') -> date:
            lst = str_date.split(sep)
            if len(lst) != 3:
                raise ValueError(f'{str_date} no es una fecha válida')
            try:
                return date(int(lst[2]), int(lst[1]), int(lst[0]))
            except:
                raise ValueError(f'{str_date} no es una fecha válida')

        try:
            d1 = validate_1_date(self.lower_date.get())
            d2 = validate_1_date(self.upper_date.get())
            if d1 > d2:
                self.lower_date.set(d2.strftime('%d/%m/%Y'))
                self.upper_date.set(d1.strftime('%d/%m/%Y'))
            if show:
                tk.messagebox.showinfo('Validar fechas',
                                       'Las fechas son válidas')
        except Exception as er:
            tk.messagebox.showerror('Validar fechas', f'{er}')


    def date_first(self):
        """
        Actualiza la variable con la fecha más baja posible
        """
        self.lower_date.set(LOWER_DATE)


    def hoy(self):
        """
        Actualiza la variable con la fecha de hoy
        """
        d1 = datetime.today().strftime('%d/%m/%Y')
        self.upper_date.set(d1)


class Child_show_text:

    def __init__(self, master, title: str, text_body: str):
        """
        Presenta un texto aclaratorio del programa en una ventana nueva
        """
        self.master = master
        self.slave = tk.Toplevel(master)
        self.show(title, text_body)


    def show(self, title, text_body):
        """
        Dibuja la ventana
        """
        self.slave.title(title)
        frm_10 = tk.Frame(self.slave)
        vScrollbar_1 = tk.Scrollbar(frm_10, orient=tk.VERTICAL)
        txt_1 = tk.Text(frm_10, background='Black', foreground='White',
                             yscrollcommand=vScrollbar_1.set,
                             width=70, height=25, wrap=tk.WORD,
                             relief=tk.GROOVE, spacing2=1)
        vScrollbar_1.pack(side=tk.RIGHT,fill=tk.Y, expand=0)
        txt_1.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        vScrollbar_1.config(command=txt_1.yview)
        frm_10.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES,
                    padx=2, pady=2)
        txt_1.insert(tk.END, text_body)
        txt_1.config(state=tk.DISABLED)
        self.slave.grab_set()
        self.slave.focus_set()
        self.slave.wait_window()


    def terminar(self):
        """
        cierra la ventana
        """
        self.slave.destroy()
        self.master.lift()
