# -*- coding: latin-1 -*
from xml.etree.ElementTree import parse, Element
import littleLogging as logging


dbtypes = ('ms_access', 'sqlite')


class Project(object):

    XML_FILE_INI = 'xyts.xml'
    ROOT_ELEMENT_NAME = 'xyts'
    PROJECT_ELEMENT_NAME = 'project'

    def __init__(self, element: Element, check: bool=True):
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

        tree = parse(xml_file)
        root = tree.getroot()

        if root.tag != Project.ROOT_ELEMENT_NAME:
            raise ValueError(f'El elemento raiz en {xml_file} debe ser ' +\
                             f'{Project.ROOT_ELEMENT_NAME}')

        elements = root.findall(Project.PROJECT_ELEMENT_NAME)
        if not elements:
            raise ValueError(f'El fichero {xml_file} no tiene elementos ' +\
                             f'{Project.PROJECT_ELEMENT_NAME}')
        projects = []
        for i, element in enumerate(elements):
            try:
                prj = Project(element)
                projects.append(prj)
            except Exception:
                logging.append(f'El project {i:d} está mal formado',
                               toScreen=False)
        return projects


    @staticmethod
    def check(prj_node: Element):
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
        def element_get(element: Element, path2: str, required: bool=True,
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


    def element_get(self, path2: str, attrib: str = None) -> Element:
        """
        devuelve el subelemento de self.p en path2 o uno de sus
            atributos
        """
        if attrib is None:
            return self.p.find(path2)
        else:
            return self.p.find(path2).get(attrib)


    def elements_get(self, path2: str) -> Element:
        """
        devuelve los subelementos de self.p en path2
        """
        return self.p.findall(path2)


    def element_with_atribb_get(self, path2: str, attrib: str,
                                attrib_value: str) -> Element:
        """
        devuelve el subelementos de self.p en path2 cuyo atributo attrib
            tiene el valor attrib_value
        """
        for element in self.p.findall(path2):
            if element.get(attrib) == attrib_value:
                return element
        return None


    def exists_element(self, path2: str) ->bool:
        """
        devuelve True si path2 es un subelemento de self.p
        """
        e = self.p.find(path2)
        if e:
            return True
        return False


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


    def col_get(self, sql_type: str, col_type: str ) -> int:
        """
        devuelve el texto del elemento col con type col_type en el elemento
        sql con type sql_type
        """
        esql = self.p.sql_get(sql_type)


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


    def __check1(self):
        """
        Para eliminar
        comprueba que la estructura de datos está bien formada
        comprobando que no lanza ninguna excepcion al ejecutar todos los
        metodos _get de la clase Project
        """
        import inspect
        import types

        methodList = [n for n, v in \
                      inspect.getmembers(self, inspect.ismethod) \
                      if isinstance(v, types.MethodType)]

        for methodName in methodList:
            if methodName.endswith('_get'):
                func = getattr(self, methodName)
                _ = func()


    @staticmethod
    def xml_tree_as_str():
        """
        Para eliminar
        crea un xml tree con la estructura que necesita el programa para ser
            ejecutado
        los contenidos son de ejemplo
        el nombre del primer tag esta definido como Project.__root_tag
        cada proyecto se identifica con un tag de nombre Project.__project_tag
            que cuelga
        directamente del primer tag
        el resto de tags que se crean son despues chequeados con los getter
            de la clase
        """
        from xml.etree.ElementTree import Element, SubElement, Comment \
        , tostring

        top = Element(Project.__root_tag)

        #tag project: cada proyecto tiene 3 tags file, graf y sql
        project=SubElement(top, Project.__project_tag,
                           name="Project description", type="1")

        #tag file
        sube = SubElement(project, 'file', name="{0:03d}_{1}")
        sube.append(Comment('name es un molde (formado por elementos {} )' +\
                            'para el nombre del fichero los valores se' +\
                            ' toman de la select de tipo master'))
        sube_1 = SubElement(sube, 'col')
        sube_1.append(Comment('hay tantos tag col como elementos {} ' +\
                              'en name. Es la num de columna del select' +\
                              ' master'))
        sube_1.text = '1'

        sube_1 = SubElement(sube, 'col')
        sube_1.text = '2'

        #tag graf
        sube = SubElement(project, 'graf', type="XY")

        sube_1 = SubElement(sube, 'axis_name')
        sube_1.append(Comment('lista con los nombres de 3 ejes: X, Y ' +\
                              'superior, Y inferior'))
        sube_1.text = "[' ', 'm s.n.m.', 'P dmm/d']"

        sube_1 = SubElement(sube, 'polcrv')
        sube_1.append(Comment('lista de 2 elementos con el tipo de ' +\
                              'grafico en cada subplot'))
        sube_1.text = "['LINEAR','BARS']"

        #tag sql master
        sube=SubElement(project, 'sql', type="master",  bdd="path2some.mdb",
                        select="some valid sql select" )
        sube.append(Comment('la select debe contener las columas implicadas' +\
                    ' en el nombre del fichero una columna con el id del' +\
                    ' elemento a representar, la fecha de la medida y el' +\
                    ' valor de la medida. Tambien debe contener una clasula' +\
                    ' WHERE del tipo IPA2.FECHA&gt;#_lower_bound_date_#' +\
                    ' AND IPA2.FECHA&lt;#_upper_bound_date_#, donde' +\
                    ' #_lower_bound_date_# y #_upper_bound_date_# son' +\
                    ' moldes que se sustituyen con las fechas que se' +\
                    ' indican en la interfaz'))

        sube_1 = SubElement(sube, 'titul',  line="1", text="Piezometro {}")
        sube_1.append(Comment('titulo del grafico en la linea line text' +\
                              ' es el molde para la linea 1'))

        sube_2=SubElement(sube_1, 'col')
        sube_2.append(Comment('num de columna en el select para la linea' +\
                              ' de titulo, tiene que haber tantos tag col' +\
                              ' como moldes en la linea de titulo, si 0' +\
                              ' indica el num de grafico'))
        sube_2.text = "0"

        sube_1 = SubElement(sube, 'cod',  col="3")
        sube_1.append(Comment('num python de columna en la select para la' +\
                              ' id del elemento que se va a representar'))

        sube_1 = SubElement(sube, 'x',  col="4")
        sube_1.append(Comment('num de columna en la select para la serie' +\
                              ' que se represenat en el eje X. Debe ser de' +\
                              ' tipo fecha'))

        sube_1 = SubElement(sube, 'y',  col="5")
        sube_1.append(Comment('num de columna en la select para la serie' +\
                              ' que se represenat en el eje Y. Debe ser' +\
                              ' de tipo float o int'))

        #tag sql upper_relation
        sube = SubElement(project, 'sql', type="upper_relation",
                          bdd="path2some.mdb",
                          select='SELECT COD1,COD2 FROM IPA1_SELF WHERE' +\
                          ' COD1="{}"')
        sube.append(Comment('en el tag sql upper_relation (opcional) se' +\
                            ' escribe la select establece la relacion' +\
                            ' entre los codigos de puntos de la select' +\
                            ' master con otros puntos que completan su' +\
                            ' informacion, similar a la que se indica' +\
                            ' en el ejemplo'))

        sube_1=SubElement(sube, 'current', col="1")
        sube_1.append(Comment('columna del codigo del punto principal' +\
                              ' en la select'))

        sube_1=SubElement(sube, 'others', col="2")
        sube_1.append(Comment('columna del codigo de el/los punto' +\
                              ' relacionado con el principal en la select'))

        sube_1=SubElement(sube, 'sql', type='distancia', bdd="path2some.mdb",
                          select="SELECT X_UTM,Y_UTM FROM IPA1 WHERE" +\
                          " COD='{}' OR COD='{}'")
        sube_1.append(Comment('define una select que devuelve las' +\
                              ' coordenadas de los puntos que se' +\
                              ' representan en el subplot 1'))

        #tag sql upper
        sube=SubElement(project, 'sql', type="upper",  bdd="path2some.mdb",
                        select="SELECT IPA2.COD,IPA2.FECHA,IPA1.Z-IPA2.PNP" +\
                        " AS CNP FROM IPA1 IPA1 INNER JOIN IPA2 ON" +\
                        " IPA1.COD=IPA2.COD WHERE IPA1.COD='{}' ORDER" +\
                        " BY IPA2.FECHA" )
        sube.append(Comment('el tag sql upper (solo obligatorio si esta' +\
                            ' definido el tag upper_relation) devuelve los' +\
                            ' datos de los puntos que se representan en el' +\
                            ' subplot 1, similar a la que se indica en' +\
                            ' el ejemplo'))

        sube_1 = SubElement(sube, 'cod', col="1")
        sube_1.append(Comment('columna del codigo de el/los puntos cuyos' +\
                              ' datos se representan'))

        sube_1 = SubElement(sube, 'x',  col="2")
        sube_1.append(Comment('num de columna en la select para la serie' +\
                              ' que se represenat en el eje X. Debe ser' +\
                              ' de tipo fecha'))

        sube_1 = SubElement(sube, 'y',  col="3")
        sube_1.append(Comment('num de columna en la select para la serie' +\
                              ' que se represenat en el eje Y. Debe ser' +\
                              ' de tipo float o int'))

        #tag sql lower_relation
        sube = SubElement(project, 'sql', type="lower_relation",
                          bdd="path2some.mdb",
                          select='SELECT IDIPA1,IDINM FROM IPA1_INM' +\
                          ' WHERE IDIPA1="{}"')
        sube.append(Comment('en el tag sql lower_relation (opcional) se' +\
                            ' escribe la select establece la relacion entre' +\
                            ' los codigos de puntos de la select master' +\
                            ' con los puntos relacionados que se' +\
                            ' representan en el subplot 2, similar a' +\
                            ' la que se indica en el ejemplo'))

        sube_1 = SubElement(sube, 'current', col="1")
        sube_1.append(Comment('columna del codigo del punto del subplot 1'))

        sube_1 = SubElement(sube, 'others', col="2")
        sube_1.append(Comment('columna del codigo del punto relacionado' +\
                              ' que se representa en el subplot 2'))

        #tag sql lower
        sube = SubElement(project, 'sql', type="lower",  bdd="path2some.mdb",
                          select="SELECT IDINM,FECHA,P FROM P WHERE" +\
                          " IDINM=&quot;{}&quot; AND FECHA&gt;=#{}# AND" +\
                          " FECHA&lt;=#{}# AND P&gt;0 ORDER BY FECHA")
        sube.append(Comment('en el tag sql lower (solo obligatorio si' +\
                            ' esta definido el tag lower_relation) se' +\
                            ' escribe la select que devuelve los datos del' +\
                            ' subplot 2. Obligatoriamente debe tener tres' +\
                            ' moldes; uno para el codigo del elemento que' +\
                            ' se representa y los otros 2 para el rango de' +\
                            ' fechas que se representa, similar a la que' +\
                            ' se indica en el ejemplo'))

        sube_1 = SubElement(sube, 'cod', col="1")
        sube_1.append(Comment('columna del codigo de el/los punto cuyos' +\
                              ' datos se representan'))

        sube_1 = SubElement(sube, 'x',  col="2")
        sube_1.append(Comment('columna en la select para la serie que se' +\
                              ' represenat en el eje X. Debe ser de' +\
                              ' tipo fecha'))

        sube_1 = SubElement(sube, 'y',  col="3")
        sube_1.append(Comment('columna en la select para la serie que se' +\
                              ' represenat en el eje Y. Debe ser de tipo' +\
                              ' float o int'))

        #tag sql upper_locations
        sube = SubElement(project, 'sql', type="upper_locations",
                          bdd="path2some.mdb",
                          select="SELECT COD,X_UTM,Y_UTM FROM IPA1" +\
                          " WHERE COD='{}'")
        sube.append(Comment('en el tag sql upper_locations (opcional) se' +\
                            ' escribe la select que permite escribir las' +\
                            ' coordenadas de los puntos que se representan' +\
                            ' en el plot principal'))

        #tag sql lower_locations
        sube = SubElement(project, 'sql', type="lower_locations",
                          bdd="path2some.mdb",
                          select="SELECT COD,XUTM,YUTM FROM ESTACIONES" +\
                          " WHERE COD={0:d}" )
        sube.append(Comment('en el tag sql lower_locations (opcional) se' +\
                            ' escribe la select que permite escribir las' +\
                            ' coordenadas de los puntos que se' +\
                            ' representan en el plot inferior'))

        a = tostring(top, encoding="iso-8859-1" )
        return a
