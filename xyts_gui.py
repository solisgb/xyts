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
    GUI con tkinter. No tiene ningún método público
    """

    def __init__(self, master):
        """
        Se dibula la gui
        """
        try:
            # geometría
            self.master = master
            self.master.title(TITLE_WINDOW)
            self.master.geometry(f'{WIDTH:d}x{HEIGHT:d}+' +\
                                 f'{XOFFSET:d}+{YOFFSET:d}')
            self.master.maxsize(WIDTH, HEIGHT)
            self.master.protocol('WM_DELETE_WINDOW', self.__exitMethod)

            self.fname = FILE_PROJECTS

            # variables específicas
            # lista de objetos Project en el fichero xyts_gui.FILE_PROJECTS
            self.projects = []
            # índice del proyecto seleccionado en self.projects
            self.selected_project: int = TKINTNULL
            # nombre del proyecto seleccionado
            self.selected_project_show = tk.StringVar()
            # directorio de resultados
            self.path_out = tk.StringVar()
            # indicador del número de gráfico grabados
            self.icount = tk.IntVar()
            # número total de gráficos potenciales en el proyecto
            self.ngraf = tk.IntVar()
            # indicador de grabar los datos representados [0, 1]
            self.dataToFile = tk.IntVar(value=1)
            # indicador de grabar solo el primer gráfico
            self.only_master = tk.IntVar()
            # indicador de grabar solo el gráfico superior
            self.upperPlotOnly = tk.IntVar()
            # indicador de grabar el fichero de localizaciones de los puntos
            self.grabar_localizaciones = tk.IntVar()
            # fecha inicial en las select
            self.lower_date = tk.StringVar()
            # fecha final en las select
            self.upper_date = tk.StringVar()
            # pausar la ejecución en el gráfico número n
            self.stop_from_graph = tk.IntVar(value=0)
            # siguiente pausa cada m gráficos
            self.stop_graph_step = tk.IntVar(value=0)

            self.__read_last_action()

            # widgets
            self.__cuerpo_put()
            self.__action_buttons_put()
            self.master.mainloop()

        except:
            a = format_exc()
            logging.append(a, toScreen=False)
            tk.messagebox.showerror(self.__module__, a)
            self.__exitMethod()


    def __cuerpo_put(self):
        """
        lee el fichero xyts.xml y muestra la lista de proyectos disponibles
        """

        # nuevo grupo de widgets
        frm_g0 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE, pady=3)

        frm_01 = tk.Frame(frm_g0)
        tk.Label(frm_01, text= 'Proyectos', pady=5) \
        .pack(side=tk.TOP, anchor=tk.CENTER)
        frm_01.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, expand=tk.NO)

        # list box para proyectos disponibles
        frm_01 = tk.Frame(frm_g0,borderwidth=2, relief=tk.SUNKEN)
        v_scrollbar_05_01 = tk.Scrollbar(frm_01, orient=tk.VERTICAL)
        self.listbox_05_01 = tk.Listbox(frm_01,selectmode=tk.BROWSE,
                yscrollcommand=v_scrollbar_05_01.set,
                width=45, height=9)
        self.__cargar_lista_proyectos_en_listbox()
        self.listbox_05_01.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.listbox_05_01.bind("<Button-3>", self.__ver_proyecto)
        v_scrollbar_05_01.pack(side=tk.RIGHT, fill=tk.Y)
        v_scrollbar_05_01.config(command=self.listbox_05_01.yview)
        frm_01.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        frm_01 = tk.Frame(frm_g0)
        h_scrollbar_07_01 = tk.Scrollbar(frm_01, orient=tk.HORIZONTAL)
        h_scrollbar_07_01.pack(side=tk.TOP, fill=tk.X)
        h_scrollbar_07_01.config(command=self.listbox_05_01.xview)
        frm_01.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        frm_g0.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)

        frm_01 = tk.Frame(self.master,borderwidth=2)
        tk.Button(frm_01, text="Seleccionar", padx=5, pady=2,
                  command=self.__select_project) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_01, text="Ver selección", padx=5, pady=2,
                  command=self.__ver_proyecto) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        tk.Button(frm_01, text="Quitar selección", padx=5, pady=2,
                  command=self.__deSelectProyecto) \
                  .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, padx=1)
        frm_01.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)

        # nuevo grupo de widgets
        frm_g0 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE, pady=3)

        frm_10 = tk.Frame(frm_g0)
        tk.Label(frm_10, text = "Projecto seleccionado: ", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm_10, textvariable = self.selected_project_show, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_10 = tk.Frame(frm_g0)
        tk.Label(frm_10,
                 text = "Rango de fechas. Fecha inferior",
                 pady=2).pack(side=tk.LEFT, anchor=tk.W)
        self.edlb=tk.Entry(frm_10,textvariable=self.lower_date, width=10,
                           state=tk.DISABLED).pack(side=tk.LEFT)
        tk.Label(frm_10, text = "Fecha superior", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        self.edub = tk.Entry(frm_10,textvariable=self.upper_date, width=10,
                             state=tk.DISABLED).pack(side=tk.LEFT)
        tk.Button(frm_10,text="Validar", padx=1, pady=1,
                  command=self.validar_lub_date) \
                  .pack(side=tk.LEFT,anchor=tk.W, padx=4)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_10 = tk.Frame(frm_g0)
        self.ckb1=tk.Checkbutton(frm_10,
                                 text="Gráfico superior, solo serie principal",
                                 variable=self.only_master, pady=2,
                                 state=tk.DISABLED)
        self.ckb1.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb2=tk.Checkbutton(frm_10, text="Gráfico inferior deshabilitado",
                                 variable=self.upperPlotOnly, pady=2,
                                 state=tk.DISABLED)
        self.ckb2.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.ckb3=tk.Checkbutton(frm_10, text="Grabar datos",
                                 variable=self.dataToFile) \
                                 .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_10 = tk.Frame(frm_g0)
        tk.Label(frm_10,
                 text = "Pausar desde gráfico número",
                 pady=2).pack(side=tk.LEFT, anchor=tk.W)
        tk.Entry(frm_10,textvariable=self.stop_from_graph,
                 width=5, justify=tk.RIGHT).pack(side=tk.LEFT)
        tk.Label(frm_10, text = "Pausar cada", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Entry(frm_10,textvariable=self.stop_graph_step,
                 width=10, justify=tk.RIGHT).pack(side=tk.LEFT)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)

        frm_g0.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)

        # nuevo grupo de widgets
        frm_g0 = tk.Frame(self.master, borderwidth=1, relief=tk.GROOVE,
                           pady=2)
        tk.Button(frm_g0, text="Grabar en", padx=1, pady=2,
                  command=self.output_dir_set).pack(side=tk.LEFT)
        tk.Entry(frm_g0, textvariable=self.path_out, width=98) \
        .pack(side=tk.LEFT, expand=tk.YES, pady=2)
        frm_g0.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)

        frm_g0 = tk.Frame(self.master, borderwidth=2, relief=tk.GROOVE, pady=3)
        frm_10 = tk.Frame(frm_g0)
        tk.Label(frm_10, text = "En ejecución:", pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(frm_10, textvariable = self.icount, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm_10, text = '/',pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        tk.Label(frm_10, textvariable = self.ngraf, padx=8, pady=2) \
            .pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        frm_10.pack(side=tk.TOP, anchor=tk.W, expand=tk.NO)
        frm_g0.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=tk.YES)


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
                  command=self.show_log_file) \
                  .pack(side=tk.RIGHT, anchor=tk.W, fill=tk.X, padx=1)
        frm_08.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.NO)


    @staticmethod
    def __strdate2gui(str_date: str, sep: str='-') -> str:
        """
        convert a date as str from format 'yyyy-mm-dd' to 'dd/mm/yyyy'
        """
        a = str_date.split(sep)
        d1 = date(int(a[0]), int(a[1]), int(a[2]))
        return d1.strftime('%d/%m/%Y')


    @staticmethod
    def __strdate2sqlite(str_date: str, sep: str='/') -> str:
        """
        convert a date as str from format 'dd/mm/yyyy' to 'yyyy-mm-dd'
        """
        a = str_date.split(sep)
        d1 = date(int(a[2]), int(a[1]), int(a[0]))
        return d1.strftime('%Y-%m-%d')


    @staticmethod
    def __str_to_date(str_date: str, sep: str='/') -> date:
        """
        convert a date as str from format 'dd/mm/yyyy' to date
        """
        a = str_date.split(sep)
        return date(int(a[2]), int(a[1]), int(a[0]))


    def __insert_last_action(self):
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
            lower_date = GUI.__strdate2sqlite(self.lower_date.get())
            upper_date = GUI.__strdate2sqlite(self.upper_date.get())
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


    def __set_defaults(self, defaults: dict):
        self.path_out.set(defaults['path_out'])
        self.lower_date.set(defaults['lower_date'])
        self.upper_date.set(defaults['upper_date'])
        self.stop_from_graph.set(0)
        self.stop_graph_step.set(0)
        return


    def __read_last_action(self):
        """
        Escribe parámetros seleccionados de la ejecución a la salida del
            programa
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
                self.__set_defaults(defaults)
                return
        except:
            self.__set_defaults(defaults)
            return
        finally:
            con.close()
        lower_date = GUI.__strdate2gui(row['lower_date'])
        upper_date = GUI.__strdate2gui(row['upper_date'])
        self.path_out.set(row['path_out'])
        self.lower_date.set(lower_date)
        self.upper_date.set(upper_date)


    def __exitMethod(self):
        """
        acciones cuando abandono la gui
        """
        self.__insert_last_action()
        self.master.destroy()


    def __helpMenu(self):
        """
        lee el fichero de ayuda
        """
        from io import StringIO
        lines = StringIO()
        try:
            f = open(FILE_HELP, 'r')
            for line in f.readlines():
                lines.write(line)
            f.close()
        except:
            a = format_exc()
            logging.append(a, toScreen=False)
            lines.write(f'Error al leer {FILE_HELP}')

        contents=lines.getvalue()
        Child_show_text(self.master,contents,'Ayuda')


    def show_log_file(self):
        """
        muestra el contenido del fichero de log
        """
        contents = logging.get_as_str()
        Child_show_text(self.master, contents, 'Fichero log')


    def output_dir_set(self):
        """
        selecciona el directorio de resultados
        """
        from glob import glob
        from os.path import join, normpath
        from tkinter.filedialog import askdirectory

        while True:
            dst = askdirectory(initialdir=self.path_out.get(),
                               title='Seleccionar directorio',
                               parent=self.master)
            if not dst:
                return
            else:
                files = glob(join(dst, '*.*'))
                if files:
                    if tk.messagebox.askyesno('Directorio con ficheros',
                                              '¿Continuar?'):
                        break
                    else:
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
                                      .format(project.name_get()))


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
                                       .name_get())
        self.listbox_05_01.selection_clear(0, tk.END)

        if self.projects[self.selected_project] \
               .exists_element('upper_relation'):
            self.only_master.set(0)
            self.ckb1.config(state='normal')

        if self.projects[self.selected_project] \
               .exists_element('lower_relation'):
            self.upperPlotOnly.set(0)
            self.ckb2.config(state='normal')

        if self.edlb:
            self.edlb.config(state='normal')
            self.edub.config(state='normal')


    def __ver_proyecto(self):
        """
        muestra la informacion del projecto seleccionado
        """
        if self.selected_project > len(self.projects):
            return
        xml_str = self.projects[self.selected_project].pretty_xml_get()
        Child_show_text(self.master, xml_str, 'Proyecto seleccionado')


    def __deSelectProyecto(self):
        """
        deselecciona un projecto previamente seleccionado
        """
        self.ckb1.config(state='disabled')
        self.ckb2.config(state='disabled')
        self.edub.config(state='disabled')
        self.edlb.config(state='disabled')
        self.listbox_05_01.selection_clear(0, tk.END)
        self.selected_project = TKINTNULL
        i = len(self.selected_project_show.get())
        self.selected_project_show.set(i*' ')


    def __do_graphs(self):
        """
        llamada al metodo en el que se ejecutan los select y se
            graban los graficos
        """
        from glob import glob
        from os.path import isdir, join


        def volver():
            self.ngraf.set(0)
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
        if files:
            if not tk.messagebox.askyesno('Directorio con ficheros',
                                          '¿Continuar?'):
                return

        self.master.configure(cursor='watch')
        self.ngraf.set(0)
        self.icount.set(0)
        d1 = GUI.__str_to_date(self.lower_date.get())
        d2 = GUI.__str_to_date(self.upper_date.get())
        only_master = self.only_master.get()
        only_upper_graph = self.upperPlotOnly.get()
        counter = prj.xygraphs(dst, d1, d2, only_master, only_upper_graph)
        try:
            icontrol = self.stop_from_graph.get()
            for n, m in counter:
                self.icount.set(n)
                self.ngraf.set(m)
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


    def validar_lub_date(self, mostrar=1):
        """
        Validad las fecha inicial y la final de la master select
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
