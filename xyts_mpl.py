# -*- coding: latin-1 -*
"""
Definiciones
subplot, es el área de dibujo dentro de una figura
"""
import matplotlib.pyplot as mpl
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class Mpl_config(object):
    """
    Opciones de dibujo que puede controlar el usuario
    __defaults es un gráfico de largo=14.23, alto=10.66 cm (5.6, 4.2 inches),
        los tamaños de los fuentes
    es posible que deban ser ajustados si se cambia el tamaño del gráfico
    """

    __defaults={'figsize':(5.6, 4.2),'linewidth':0.8, 'marker':'.',
                'markersize':4, 'xycolors':['b', 'r', 'g', 'c', 'm', 'k', 'y'],
                'fontsize_title':10, 'fontsize_axis_label':9,
                'fontsize_ticks':8, 'fontsize_legend':8}


    def __init__(self, dct={}):
        self._d = dict(Mpl_config.__defaults)
        for k, v in dct.items():
            if type(self._d[k]) != type(v):
                raise ValueError('valor erroneo para {}'.format(k))
            self._d[k] = v


    def defaults(self):
        self._d = dict(Mpl_config.__defaults)


    def get(self, k):
        return self._d[k]


    def set(self, k, v=None):
        if v is None:
            self._d[k]=Mpl_config.__defaults[k]
        else:
            if type(self._d[k]) != type(v):
                raise ValueError('valor erroneo para {}'.format(k))
            self._d[k] = v


def plt1_xy(x,y, stitle, sxlabel, sylabel, dst):
    """
    Dibuja un subplot con una serie
    x,y son 2 listas de valores float de la misma longitud
    stitle título del gráfico (use \n for multiple lines)
    sxlabel, sylabel es el nombre de los ejes x y
    dst directorio y nombre del ficnero de destino .png
    """
    assert len(x)==len(y), 'x e y deben tener el mismo número de elementos'

    fig = mpl.figure()

    mpl.plot(x, y)
    mpl.title(stitle)
    mpl.xlabel(sxlabel)
    mpl.ylabel(sylabel)

    # Tweak spacing to prevent clipping of ylabel
    mpl.grid(True)
    #mpl.subplots_adjust(left=0.15)

    #Save figure
    fig.savefig(dst)

    mpl.close('all')


def plt1_xy_varias(x,y, legends,  stitle, sxlabel, sylabel, dst):
    """
    Dibuja un subplot con una serie o varias series
    x: lista en que cada elemento es una lista de objetos float
    y: lista en que cada elemento es una lista de objetos float
    legends: lista texto leyendas
    sxlabel, saylabel: es el nombre de los ejes x y
    stitle: string title del gráfico (use \n for multiple lines)
    dst directorio y nombre del ficnero de destino .png
    """

    assert len(x) == len(y), 'x e y deben tener el mismo número de elementos'
    assert len(x) == len(legends), 'x y legends deben tener el mismo' +\
    ' número de elementos'

    fig = mpl.figure()

    for x1, y1, legend1 in zip(x, y, legends):
        assert len(x1) == len(y1), 'x1 e y1 deben tener el mismo' +\
        ' número de elementos'
        mpl.plot(x1, y1, label=legend1)
        mpl.title(stitle)
        mpl.xlabel(sxlabel)
        mpl.ylabel(sylabel)

    mpl.legend(loc='best', framealpha=0.5)
    mpl.tight_layout()
    mpl.grid(True)

    # Tweak spacing to prevent clipping of ylabel
    # mpl.subplots_adjust(left=0.15)

    # Save figure
    fig.savefig(dst)

    mpl.close('all')


def plt1_ty_varias(x, y, legends,  stitle, sylabel, dst, cfg=None):
    """
    esta funcion es un alias de la plt1_nst
    se crea para mantener la compatibilidad con versiones anteriores del módulo
    """
    if cfg is None:
        plt1_nst(x,y, legends,  stitle, sylabel, dst)
    else:
        plt1_nst(x,y, legends,  stitle, sylabel, dst, cfg)


def plt1_nst(x, y, legends, stitle, sylabel, dst, cfg=None, view=False):
    """
    Dibuja un gráfico en que se pueden representar 1 a n series temporales
        en el mismo subplot
    x: lista en que cada elemento es una lista de objetos datetime
    y: lista en que cada elemento es una lista de objetos float
    legends: lista con los textos de las leyendas de cada serie
    stitle: string title del gráfico (use \n for multiple lines)
    sylabel: text label eje y
    dst directorio y nombre del ficnero de destino .png
    cfg: object Mpl_config.
    """
    assert len(x) == len(y), 'x e y deben tener el mismo número de elementos'
    assert len(x) == len(legends), \
    'x y legends deben tener el mismo número de elementos'

    from itertools import cycle

    if cfg is None:
        cfg = Mpl_config()

    mpl.rcParams['font.size'] = cfg.get('fontsize_ticks')

    colors = cycle(cfg.get('xycolors'))

    fig = mpl.figure(figsize=cfg.get('figsize'))
    ax = fig.add_subplot(111)

    # ejes y ticks
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(top='off', right='off')
    ax.set_ylabel(sylabel, fontsize=cfg.get('fontsize_axis_label'))
    ax.tick_params(which='major', labelsize=cfg.get('fontsize_ticks'))
    ax.get_xaxis().set_tick_params(direction='out')

    # eje x tixk labeles
    xmin, xmax=__minmax(x)
    fmt=__myDateFmt(xmin, xmax)
    ax.xaxis.set_major_formatter(fmt)

    for x1, y1, legend1 in zip(x, y, legends):
        assert len(x1)==len(y1), \
        'x1 e y1 deben tener el mismo número de elementos'
        mpl.plot(x1, y1, color=next(colors), label=legend1,
                 linewidth=cfg.get('linewidth'),
            marker=cfg.get('marker'),
            markersize=cfg.get('markersize'))
        mpl.title(stitle, fontsize=cfg.get('fontsize_title'))
        mpl.ylabel(sylabel, fontsize=cfg.get('fontsize_axis_label'))
        mpl.tick_params(axis='both', which='major',
                        labelsize=cfg.get('fontsize_ticks'))

    # mpl.subplots_adjust(bottom=0.16, top=0.87)

    fig.autofmt_xdate()

    if len(legends) > 1:
        mpl.legend(loc='best', framealpha=0.5,
                   fontsize=cfg.get('fontsize_legend'))
    mpl.tight_layout()
    mpl.grid(True)

    if view:
        mpl.show()

    fig.savefig(dst)
    mpl.close('all')
    mpl.rcdefaults()


def plt2_nst(xu, yu, legendsu,  ylabelu, xl,  yl,  legendsl,  ylabell,
             stitle, dst, cfg=None, view=False):
    """
    Dibuja un gráfico con dos subplots superpuestos. El superior es el
        principal y ocupa 2/3 de la altura de la figura. El inferior es
        secundario y ocupa 1/3 de la altura de la figura
    xu: lista en que cada elemento es una lista de objetos datetime que se
        dibujan en el subplot superior
    yu: lista en que cada elemento es una lista de objetos float que se
        dibujan en el subplot superior
    legendsu: lista texto leyendas en el subplot inferior
    ylabelu: text label eje y
    xl, yl, legendsl, ylabell: idem para subplot inferior
    stitle: string title del gráfico (use \n for multiple lines)
    dst: nombre fichero destino (debe invluir la extensión png)
    cfg: object Mpl_config
    view: se muestra en pantalla
    """
    assert len(xu) == len(yu) == len(legendsu), \
    'xu, yu, legendsu deben tener el mismo número de elementos'
    assert len(xl) == len(yl) == len(legendsl), \
    'xl, yl, legendsl deben tener el mismo número de elementos'

    from itertools import cycle

    if cfg is None:
        cfg = Mpl_config()

    mpl.rcParams['font.size'] = cfg.get('fontsize_ticks')

    fig = mpl.figure(figsize=cfg.get('figsize'))

    # subplots
    mpl.subplots_adjust(hspace=0.1)
    ax1 = mpl.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = mpl.subplot2grid((3, 1), (2, 0), sharex=ax1)

    # axis labels and tick labels
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.tick_params(top='off', right='off')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.tick_params(top='off', right='off')
    ax1.set_ylabel(ylabelu, fontsize=cfg.get('fontsize_axis_label'))
    ax2.set_ylabel(ylabell, fontsize=cfg.get('fontsize_axis_label'))
    ax1.tick_params(axis='both', which='major')
    ax2.tick_params(axis='both', which='major')

    # eje x2 tixk labeles
    xmin, xmax=__minmax(xu)
    fmt = __myDateFmt(xmin, xmax)
    ax2.xaxis.set_major_formatter(fmt)

    ax1.grid(True)
    ax2.grid(True)

    mpl.suptitle(stitle, fontsize=cfg.get('fontsize_title'))
    mpl.subplots_adjust(bottom=0.16, top=0.87)

    fig.autofmt_xdate()

    # dibula los datos subplot superior
    colors = cycle(cfg.get('xycolors'))
    ax1.get_xaxis().set_tick_params(direction='out')
    for x1, y1, legend1 in zip(xu, yu, legendsu):
        assert len(x1)==len(y1), \
        'x1 y1 en subplot superior\ndeben tener el mismo número de elementos'
        ax1.plot(x1, y1, color=next(colors), label=legend1,
                 linewidth=cfg.get('linewidth'),
            marker=cfg.get('marker'),
            markersize=cfg.get('markersize'))
        if len(legendsu) > 1:
            ax1.legend(loc='best', framealpha=0.5,
                       fontsize=cfg.get('fontsize_legend'))

    # dibula los datos subplot inferior
    colors = cycle(cfg.get('xycolors'))
    ax2.locator_params(axis='y', nbins=5)
    ax2.get_xaxis().set_tick_params(direction='out')
    for x1, y1, legend1 in zip(xl, yl, legendsl):
        assert len(x1) == len(y1), \
        'x1 y1 en subplot inferior\ndeben tener el mismo número de elementos'
        markerline, _, _ = ax2.stem(x1, y1, markerfmt=' ', basefmt=' ',
                                    label=legend1, use_line_collection=True)
        markerline.set_markerfacecolor('none')
        ax2.legend(loc='upper left', framealpha=0.5,
                   fontsize=cfg.get('fontsize_legend'))  # antes loc='best'
        ymin, ymax=ax2.get_ylim()
        if ymin < 0.:
            ax2.set_ylim((0,ymax))

    if view:
        mpl.show()

    fig.savefig(dst)
    mpl.close('all')
    mpl.rcdefaults()


def __write_title_tag(title, f):
    """
    write tag title
    si el titulo del grafico tiene más de una linea en mathplotlib es un str
        con \n
    """
    titles=title.split('\n')
    for item in titles:
        f.write("\t<title>{}</title>\n".format(item))


def __write_plt_tag(xu, yu, legendsu,  ylabelu, plot_number, f):
    """
    write tag plot_01 en f
    """
    f.write("\t<plot_{0:d} Y_axis='{1}'>\n".format(plot_number, ylabelu))
    for x, y, legend in zip(xu, yu, legendsu):
        assert len(x) == len(y), \
        'x y en subplot superior\ndeben tener el mismo número de elementos'
        f.write("\t\t<serie name='{}'>\n".format(legend))
        f.write("\t\t<![CDATA[\n")
        for x1,y1 in zip(x,y):
            f.write("\t\t{0}/{1}/{2}\t{3:0.2f}\n".format(x1.day, x1.month,
                    x1.year,y1))
        f.write("\t\t]]>\n")
        f.write("\t\t</serie>\n")
    f.write("\t</plot_{0:d}>\n".format(plot_number))


def plt1_nst_2_xml(xu, yu, legendsu,  ylabelu, stitle, dst):
    """
    graba los datos que se pasan a la función plt1_nst en formato xml
    dst. nombre del fichero xml (el directorio debe existir)
    """
    f=open(dst,'w')

    f.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")

    f.write("<XY>\n")
    __write_title_tag(stitle, f)
    __write_plt_tag(xu, yu, legendsu,  ylabelu, 1, f)
    f.write("</XY>")

    f.close()


def plt2_nst_2_xml(xu, yu, legendsu,  ylabelu, xl,  yl,  legendsl,  ylabell,
                   stitle, dst):
    """
    graba los datos que se pasan a la función plt2_nst en formato xml
    dst. nombre del fichero xml (el directorio debe existir)
    """
    assert len(xu) == len(yu) == len(legendsu), \
    'x, y, legends deben tener el mismo número de elementos'

    f=open(dst,'w')
    f.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")

    f.write("<XY>\n")
    __write_title_tag(stitle, f)
    __write_plt_tag(xu, yu, legendsu,  ylabelu, 1, f)
    __write_plt_tag(xl, yl, legendsl,  ylabell, 2, f)
    f.write("</XY>")

    f.close()


def __minmax(series):
    """
    series es una lista de 1 o varias series
    a su vez cada serie es una lista
    """
    xmin = min(series[0])
    xmax = max(series[0])
    for item in series[1::]:
        xmin = min(xmin, min(item))
        xmax = max(xmax, max(item))
    return xmin, xmax


def __myDateFmt(xmin, xmax):
    """
    en función de los valores min y max de los valores que se presentan
    en el eje x se devuelve el fmt del eje
    """
    from matplotlib.dates import DateFormatter
    d=xmax-xmin
    d=d.days
    if d <= 7:
        return DateFormatter('%d/%m/%Y %H:%M')
    elif d > 7 and d <= 1825:
        return DateFormatter('%d/%m/%Y')
    elif d > 1825 and d <= 7300:
        return DateFormatter('%m/%Y')
    else:
        return DateFormatter('%Y')
