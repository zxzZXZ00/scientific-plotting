"""Fresh, editable Matplotlib reconstruction. All numerical series are synthetic.

Run: python reproduce.py
The original article image is used only for the separate comparison preview.
No source pixels are embedded in the reconstruction itself.
"""
from pathlib import Path
import csv
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
import numpy as np
import yaml

BASE = Path(__file__).resolve().parent
SERIES = []


def gauss(x, center, width, height):
    return height * np.exp(-0.5 * ((x-center)/width)**2)


def record(panel, name, x, y):
    SERIES.extend((panel, name, float(a), float(b)) for a,b in zip(x,y))


def draw_figure():
    SERIES.clear()
    theme = yaml.safe_load((BASE/'theme.yaml').read_text(encoding='utf-8'))
    colors = yaml.safe_load((BASE/'palette.yaml').read_text(encoding='utf-8'))['colors']
    red, cyan, green, purple = [colors[k] for k in ['red','cyan','green','purple']]
    plt.style.use(BASE/'style.mplstyle')
    output=theme['defaults']['output']
    fig = plt.figure(figsize=(output['width_in'],output['height_in']))
    axes = {}

    def panel(name, box):
        ax = fig.add_axes(box)
        ax.set_gid(name)
        axes[name] = ax
        # Letters are outside the plotting box, with dedicated top margin.
        ax.text(-.13,1.055,name,transform=ax.transAxes,fontsize=10,
                fontweight='bold',va='bottom',gid='panel-letter')
        ax.tick_params(pad=2)
        return ax

    def line(ax, name, x, y, color, **kwargs):
        ax.plot(x,y,color=color,**kwargs)
        record(ax.get_gid(),name,x,y)

    # a: narrow gas chromatography peak.
    a=panel('a',[.075,.775,.125,.17])
    x=np.linspace(0,500,501); y=gauss(x,83,6.5,6.7)
    line(a,'H2 demo',x,y,red)
    a.set(xlim=(0,500),ylim=(-1,8),xticks=[0,200,400],yticks=[0,3,6],
          xlabel='Time (s)',ylabel=r'GC signal of H$_2$ (mV)')

    # b: one continuous frame with a compressed vertical scale.
    # Transform only the measured/demo vertices, then join adjacent samples:
    # this preserves the straight segment convention visible in the reference.
    b=panel('b',[.29,.775,.675,.17])
    b.texts[0].set_position((-.06,1.055))
    raw=np.array([-50.,0.,100.,200.,1000.,2000.,3000.,3800.])
    display=np.array([-.08,0.,.23,.40,.47,.68,.89,1.05])
    def forward(values):
        return np.interp(values,raw,display)
    def inverse(values):
        return np.interp(values,display,raw)
    b.set_yscale('function',functions=(forward,inverse))
    times=[]; high=[]; low=[]
    for cycle in range(10):
        t=np.array([cycle*10,cycle*10+5,cycle*10+10],dtype=float)
        yh=np.array([0,1850+90*np.sin(cycle),3250+100*np.cos(cycle)])
        yl=np.array([0,44+4*np.cos(cycle),87+7*np.sin(cycle)])
        b.plot(t,yh,'o-',color=red,ms=3.2,lw=.75)
        b.plot(t,yl,'o-',color=cyan,ms=3.2,lw=.75)
        times.extend(t);high.extend(yh);low.extend(yl)
    record('b','BOC-MS demo',times,high);record('b','1L-BOC demo',times,low)
    b.set(xlim=(-3,103),ylim=(-30,3800),yticks=[0,100,1000,2000,3000],
          xticks=np.arange(0,101,10),xlabel='Time (h)',ylabel=r'H$_2$ evolution (µmol)')
    b.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    b.text(.012,.87,'BOC-MS',color=red,transform=b.transAxes,fontsize=6)
    b.text(.012,.74,'1L-BOC',color=cyan,transform=b.transAxes,fontsize=6)
    break_y=float((forward(450.)-forward(-30.))/(forward(3800.)-forward(-30.)))
    for xx in [0,1]:
        for shift in [-.012,.012]:
            b.plot([xx-.007,xx+.007],[break_y+shift-.012,break_y+shift+.012],
                   transform=b.transAxes,color='.35',lw=.65,clip_on=False)

    # c: EPR, labels occupy a genuinely empty area.
    c=panel('c',[.075,.405,.125,.255])
    x=np.linspace(1.97,2.04,450)
    y=.68 + .024*np.sin(500*x)*np.exp(-((x-2.005)/.018)**2)
    y += -.20*(x-2.005)/.0035*np.exp(-.5*((x-2.005)/.0035)**2)
    line(c,'1L-BOC demo',x,y,red)
    line(c,'BOC-MS demo',x,np.full_like(x,.23),cyan)
    c.set(xlim=(1.97,2.04),ylim=(0,1.05),xticks=[1.98,2,2.02],yticks=[],xlabel='g value',ylabel='Intensity (a.u.)')
    c.text(.57,.80,'1L-BOC',color=red,transform=c.transAxes,fontsize=6)
    c.text(.54,.30,'BOC-MS',color=cyan,transform=c.transAxes,fontsize=6)

    # d: stacked spectra and editable chemical structure schematics.
    d=panel('d',[.265,.405,.335,.255])
    x=np.linspace(59,118,1800)
    peaks=[62.5,69.5,73.2,76.5,78.2,84.5,88,91.8,95.4,96.4,106.2,116.5]
    spectra=[('0 h',red,.64,[.29,.29,.04,.25,.01,0,0,0,0,0,0,.08]),
             ('45 h',cyan,.40,[.16,.15,.14,.14,.11,0,.16,.06,0,0,.08,.12]),
             ('90 h',green,.08,[.08,.12,.27,.21,.09,0,.27,.08,.07,.06,.12,.07])]
    for name,color,offset,heights in spectra:
        y=np.full_like(x,offset)+.003*np.sin(x*5)
        for center,height in zip(peaks,heights):
            y+=gauss(x,center,.12,height)
        line(d,name+' demo',x,y,color,lw=.65)
        label_y={'0 h':.48,'45 h':.23,'90 h':.12}[name]
        d.text(.86,label_y,name,transform=d.transAxes,color=color,fontsize=6)
        active=[(p,h) for p,h in zip(peaks,heights) if h>.05]
        d.scatter([p for p,h in active],[offset+h+.025 for p,h in active],
                  s=9,marker='v' if name=='45 h' else 'D',color=purple,zorder=4,linewidths=0)
    d.set(xlim=(59,118),ylim=(.02,1.08),xticks=[60,80,100],yticks=[],
          xlabel=r'δ $^{13}$C (p.p.m.)',ylabel='Intensity (a.u.)')
    for left in [.36,.55,.74]:
        # Approximate molecular insets, not exact molecular artwork.
        box=d.inset_axes([left,.67,.17,.23])
        box.set(xlim=(-1.7,1.7),ylim=(-1.7,1.7));box.set_xticks([]);box.set_yticks([])
        for spine in box.spines.values(): spine.set(color='#E6BD42',linestyle=(0,(2,2)),linewidth=.6)
        angles=np.linspace(0,2*np.pi,6)
        box.plot(np.cos(angles),np.sin(angles),color='.3',lw=.45)
        box.text(-1.3,1.15,'HO',fontsize=3.3);box.text(.65,-1.35,'OH',fontsize=3.3)
        box.text(.70,.85,'O',fontsize=3.3)
        box.set_gid('d-molecule')

    # e: oscillating DOS lines, synthetic but shape-matched.
    e=panel('e',[.66,.405,.135,.255])
    x=np.linspace(-2.6,4.7,600)
    yr=.1+gauss(x,-1.65,.43,.46)+gauss(x,-.8,.28,.42)+gauss(x,3.45,.3,.22)+gauss(x,4.5,1,.2)
    yr=np.where((x>.1)&(x<2.4),.03,yr)
    yc=.06+sum(gauss(x,p,.12,h) for p,h in [(-2.3,.45),(-1.8,.35),(-1.5,.23),(-1,.21),(-.6,.18),(.1,.16),(1.2,.2),(2.7,.45),(3,.43),(3.4,.2)])
    line(e,'1L-BOC demo',x,yr,red);line(e,'1L-MS demo',x,yc,cyan)
    e.set(xlim=(-2.6,4.7),ylim=(-.01,1),xticks=[-2,0,2,4],yticks=[],xlabel='Energy (eV)',ylabel='DOS (1/eV)')
    e.text(.60,.87,'1L-BOC',color=red,transform=e.transAxes,fontsize=6)
    e.text(.60,.74,'1L-MS',color=cyan,transform=e.transAxes,fontsize=6)

    # f: sparse hollow markers; no marker per interpolated sample.
    f=panel('f',[.85,.405,.135,.255])
    for name,color,start,slope,marker in [('1L-BOC',red,-.46,1.03,'s'),('1L-MS',cyan,-.49,.98,'s')]:
        xx=np.linspace(start,.45,23);yy=slope*(xx-start)
        line(f,name+' primary demo',xx,yy,color,lw=.5,marker=marker,ms=2.7,mfc='none',mec=color,mew=.35,markevery=2,alpha=.65)
    xx=np.linspace(-.05,.64,20)
    for shift,color in [(0,cyan),(.02,'#E6C65A')]:
        line(f,'low-slope demo',xx,.23*(xx+.05)+shift,color,lw=.5,marker='^',ms=2.5,mfc='none',mew=.35,markevery=2)
    f.set(xlim=(-.7,.75),ylim=(-.06,1.08),xticks=[-.6,-.3,0,.3,.6],yticks=[],
          xlabel='Energy (eV versus NHE)',ylabel=r'1/C$^2$ (cm$^4$ F$^{-2}$)')
    f.xaxis.label.set_fontsize(6)
    f.text(.04,.83,'1L-BOC',color=red,transform=f.transAxes,fontsize=6)
    f.text(.60,.25,'1L-MS',color=cyan,transform=f.transAxes,fontsize=6)

    # g: photovoltage spectra; explicit data-to-frame clearance.
    g=panel('g',[.075,.075,.205,.24])
    x=np.linspace(300,600,500)
    for name,color,y in [('BOC-MS',red,18+gauss(x,402,28,215)+gauss(x,430,55,35)),
                         ('1L-BOC',cyan,13+gauss(x,398,22,65)),
                         ('1L-MS',green,gauss(x,412,27,4)+.9*np.sin(x/6))]:
        line(g,name+' demo',x,y,color)
    g.set(xlim=(300,600),ylim=(-24,300),xticks=[350,400,450,500,550],yticks=[0,50,100,150,200,250,300],
          xlabel='Wavelength (nm)',ylabel='Photovoltage (mV)')
    for yy,label,color in [(.86,'BOC-MS',red),(.72,'1L-BOC',cyan),(.58,'1L-MS',green)]:
        g.text(.67,yy,label,color=color,transform=g.transAxes,fontsize=6)

    # h: one physical frame, secondary tick labels use the same plotting box.
    h=panel('h',[.37,.075,.225,.24])
    x=np.linspace(300,800,500)
    for name,color,y in [('BOC-MS',green,.94/(1+np.exp((x-438)/15))+.34*np.exp(-((x-585)/135)**2)),
                         ('1L-BOC',cyan,.93/(1+np.exp((x-445)/19))+.35*np.exp(-(x-460)/185)/(1+np.exp(-(x-440)/20))),
                         ('1L-MS',cyan,.47*np.exp(-(x-300)/620)+.055)]:
        line(h,name+' demo',x,y,color)
    xp=np.array([320,340,360,380,400,420,450,470,500,550,600,700])
    yp=np.array([.87,.88,.9,.92,.87,.55,.22,.09,.035,.015,.005,.005])
    h.errorbar(xp,yp,yerr=[.04,.04,.04,.04,.04,.04,.04,.04,.03,.01,.01,.01],fmt='o',ms=2.4,color=red,elinewidth=.55,capsize=1)
    record('h','quantum yield scaled demo',xp,yp*45)
    h.set(xlim=(300,800),ylim=(-.07,1.05),xticks=[400,500,600,700],yticks=[0,.5,1],
          xlabel='Wavelength (nm)',ylabel='Absorbance (a.u.)')
    sec=h.secondary_yaxis('right',functions=(lambda y:y*45,lambda y:y/45))
    sec.set_yticks([0,20,40]);sec.set_ylabel('Quantum yield (%)',fontsize=7,labelpad=5)
    sec.tick_params(labelsize=6.5,pad=2,width=.5,length=2)
    sec.spines['right'].set_visible(False)
    for yy,label,color in [(.92,'BOC-MS',green),(.80,'1L-BOC',cyan),(.68,'1L-MS',cyan),(.53,'PHE quantum yield',red)]:
        h.text(.49,yy,label,color=color,transform=h.transAxes,fontsize=5.8)

    # i: editable energy-band diagram, deliberately schematic.
    i=panel('i',[.73,.065,.25,.26]);i.axis('off');i.set(xlim=(0,1),ylim=(0,1))
    i.texts[0].set_position((-.13,.94))
    i.annotate('',xy=(.13,.98),xytext=(.13,.08),arrowprops={'arrowstyle':'->','color':'.55','lw':1.2})
    i.text(.015,.5,'Energy (V versus NHE)',rotation=90,va='center',fontsize=6.5)
    for y,label in [(.70,r'H$^+$/H$_2$'),(.49,r'O$_2$/H$_2$O'),(.35,r'·OH/H$_2$O')]:
        i.plot([.10,.72],[y,y],ls=(0,(2,2)),color=cyan,lw=.5)
        i.text(.08,y+.025,label,ha='left',fontsize=5.3)
    for x0,y0,w,hh,label,color in [(.34,.77,.22,.10,'CB',cyan),(.34,.21,.22,.10,'VB',cyan),(.72,.54,.17,.18,'', '#0086BB')]:
        i.add_patch(Rectangle((x0,y0),w,hh,facecolor=color,edgecolor='none'))
        if label:i.text(x0+w/2,y0+hh/2,label,ha='center',va='center',color='white',fontsize=6)
    i.annotate('',xy=(.45,.76),xytext=(.45,.33),arrowprops={'arrowstyle':'->','color':'#F49AAA','lw':1})
    i.annotate('',xy=(.78,.76),xytext=(.54,.91),arrowprops={'arrowstyle':'->','color':'#F49AAA','lw':1.2})
    for xx,yy,sym in [(.45,.94,'−'),(.80,.79,'−'),(.45,.17,'+')]:
        i.add_patch(Circle((xx,yy),.045,color='#E98FA9' if sym=='−' else '#B881BB',alpha=.8,lw=0))
        i.text(xx,yy,sym,color='white',ha='center',va='center',fontsize=6)
    i.text(.75,.43,'MoS$_2$\nmonolayer',color=cyan,ha='center',fontsize=5.5)
    i.text(.43,.015,'Bi$_{12}$O$_{17}$Cl$_2$\nmonolayer',color=cyan,ha='center',fontsize=5.5)
    i.text(.88,.91,r'H$_2$',color=red,fontsize=5.5)
    i.text(.91,.64,r'H$_2$O',color=red,fontsize=5.5)
    i.text(.74,.26,'Ascorbic acid',color=purple,fontsize=5.4)
    i.text(.77,.08,'Oxidized\nproducts',color=purple,fontsize=5.4)
    i.annotate('',xy=(.94,.94),xytext=(.98,.65),
               arrowprops={'arrowstyle':'->','color':red,'lw':.6,'connectionstyle':'arc3,rad=-.5'})
    i.annotate('',xy=(.75,.09),xytext=(.74,.25),
               arrowprops={'arrowstyle':'->','color':purple,'lw':.6,'connectionstyle':'arc3,rad=.5'})
    t=np.linspace(0,1,80)
    i.plot(.19+.21*t,.62-.13*t+.025*np.sin(t*8*np.pi),color='#E6C12D',lw=1)
    return fig


def check_boundaries(fig):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer()
    outside=[]
    for artist in fig.findobj(matplotlib.text.Text):
        if not artist.get_visible() or not artist.get_text().strip(): continue
        box=artist.get_window_extent(renderer)
        if box.x0 < 0 or box.y0 < 0 or box.x1 > fig.bbox.width or box.y1 > fig.bbox.height:
            outside.append(artist.get_text())
    # Check the bounding rectangles of all visible, nonempty text elements.
    texts=[]
    for artist in fig.findobj(matplotlib.text.Text):
        if artist.get_visible() and artist.get_text().strip():
            texts.append((artist.get_text(),artist.get_window_extent(renderer)))
    overlaps=[]
    for j,(s,a) in enumerate(texts):
        for t,b in texts[j+1:]:
            if min(a.x1,b.x1)-max(a.x0,b.x0)>1 and min(a.y1,b.y1)-max(a.y0,b.y0)>1:
                overlaps.append([s,t])
    data_hits=[]
    # Scope: explicit panel annotations against Line2D paths in data panels.
    # This does not certify every marker/patch intersection or scientific fidelity.
    for ax in fig.axes:
        if ax.get_gid() in {'i','d-molecule'}: continue
        for text in ax.texts:
            if text.get_gid()=='panel-letter': continue
            box=text.get_window_extent(renderer).expanded(1.03,1.10)
            if not ax.bbox.contains(box.x0,box.y0): continue
            for line in ax.lines:
                path=line.get_transform().transform_path(line.get_path())
                if path.intersects_bbox(box,filled=False):
                    data_hits.append([ax.get_gid(),text.get_text()]);break
    return {'canvas_pixels':[int(fig.bbox.width),int(fig.bbox.height)],
            'text_outside_canvas':outside,'text_rectangle_overlaps':overlaps,
            'annotation_line_intersections':data_hits}


if __name__=='__main__':
    import sys
    root=next(p for p in BASE.parents if (p/'scripts/exporting.py').is_file())
    sys.path.insert(0,str(root/'scripts'))
    from exporting import export_figure
    output=yaml.safe_load((BASE/'theme.yaml').read_text(encoding='utf-8'))['defaults']['output']
    fig=draw_figure()
    targets=export_figure(fig,stem='red-cyan-reference',dpi=output['dpi'],
                         transparent=output['transparent'],
                         config={'theme':'user:red-cyan','palette':'user:red-cyan'})
    plt.close(fig)
    for target in targets:print(target)
