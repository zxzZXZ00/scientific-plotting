"""Approximate editable reconstruction of PNAS Figure 2.

Raster reference: numerical values were visually estimated, not original data.
Panels A and H are explicitly simplified biological flow schematics.
"""
from pathlib import Path
import csv
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, FancyArrowPatch, Polygon
from matplotlib.ticker import FixedLocator, NullLocator
from matplotlib.lines import Line2D

BASE=Path(__file__).resolve().parent
OUT=BASE
ROOT=next(p for p in BASE.parents if (p/'scripts/layout_checks.py').is_file())
sys.path.insert(0,str(ROOT/'scripts'))
from layout_checks import validate_figure
from exporting import export_figure
plt.style.use(ROOT/'user-library/styles/peach-teal.mplstyle')
plt.rcParams.update({'font.family':'Arial','font.style':'normal','axes.labelsize':9,
                     'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic',
                     'mathtext.default':'regular'})
ORANGE='#F19E65';TEAL='#7FBFBB';OFILL='#F6C5A1';TFILL='#C1DFD9'
DATA=[]

def series_legend(ax):
    # Reference legends use line + circle, without the error-bar whiskers.
    handles=[Line2D([],[],color=col,marker='o',mfc=fill,mec=col,ms=3.5,lw=.8)
             for col,fill in [(ORANGE,OFILL),(TEAL,TFILL)]]
    ax.legend(handles,['M. a 321','M. a 3fk'],loc='upper left',ncol=2,
              fontsize=6.5,handlelength=1.25,columnspacing=.8,handletextpad=.45,
              borderaxespad=.6)


def draw():
    DATA.clear()
    fig=plt.figure(figsize=(7.15,6.55),dpi=240)
    def panel(letter,box,axis=True):
        a=fig.add_axes(box)
        a.text(-.027/box[2],1.04,letter,transform=a.transAxes,fontsize=11,va='bottom')
        a.set_gid(letter)
        if not axis:a.axis('off');a.set(xlim=(0,1),ylim=(0,1))
        else:
            for spine in a.spines.values():spine.set_visible(True)
            a.tick_params(labelsize=7,pad=2)
            a.xaxis.set_minor_locator(NullLocator());a.yaxis.set_minor_locator(NullLocator())
        return a
    a=panel('A',[.055,.76,.49,.19],False)
    for y in [.40,.67]:
        for x in np.linspace(.04,.55,13):
            a.add_patch(Ellipse((x,y),.031,.085,facecolor='#A9DAE4',edgecolor='#93C9D8',lw=.35))
    for x in np.linspace(.04,.55,13):
        a.plot([x,x-.005,x+.005,x],[.45,.5,.56,.62],color='#D2B9DF',lw=.5)
    for x,name,color in [(.20,'glf',TEAL),(.43,'glk',ORANGE)]:
        a.add_patch(Polygon([(x-.04,.38),(x-.035,.67),(x+.04,.69),(x+.035,.4)],facecolor='#A9C4BA',edgecolor='#77958A',lw=.5))
        a.annotate('',xy=(x,.25),xytext=(x,.82),arrowprops={'arrowstyle':'->','color':color,'lw':1})
        a.text(x+.045,.80,name,color=color,fontsize=7,fontstyle='italic')
    a.text(.17,.92,'D-Glucose',fontsize=7)
    a.text(.13,.18,'D-Glucose-6P',fontsize=7)
    a.text(.10,.02,'Metabolic pathway',fontsize=7,bbox={'facecolor':'#E6F0EB','edgecolor':'none','pad':2})
    for y,name,color in [(.70,'glf',TEAL),(.23,'glk',ORANGE)]:
        a.add_patch(Rectangle((.65,y-.05),.33,.28,fill=False,edgecolor=color,linestyle='--',lw=.6))
        a.add_patch(FancyArrowPatch((.67,y+.05),(.94,y+.05),arrowstyle='simple',mutation_scale=12,color=color,lw=0))
        a.text(.74,y+.15,name,fontsize=7,color=color,fontstyle='italic')
    b=panel('B',[.615,.76,.085,.19])
    b.bar([0,1],[1.12,1.09],yerr=[.19,.10],color=[TFILL,OFILL],edgecolor=[TEAL,ORANGE],width=.55,
          linewidth=.6,capsize=2,error_kw={'lw':.5,'ecolor':'#9BAAA6'})
    b.set(ylim=(0,1.5),xticks=[0,1],xticklabels=['glf','glk'],yticks=[0,.5,1,1.5],ylabel='Relative expression level')
    c=panel('C',[.79,.76,.185,.19])
    t=np.array([0,10,20,30,45,60]);yo=np.array([0,.075,.23,.26,.27,.245]);yt=np.array([0,.15,.25,.255,.27,.255])
    for name,y,col,fill in [('M. a 321',yo,ORANGE,OFILL),('M. a 3fk',yt,TEAL,TFILL)]:
        c.errorbar(t,y,yerr=[0,.025,.03,.015,.02,.015],color=col,marker='o',mfc=fill,mec=col,ms=3,lw=.8,capsize=2,elinewidth=.5,label=name)
        DATA.extend(['C',name,float(x),float(z)] for x,z in zip(t,y))
    c.set(xlim=(-2,62),ylim=(-.02,.4),xticks=[0,20,40,60],yticks=[0,.2,.4],xlabel='Time (h)',ylabel='OD')
    series_legend(c)
    d=panel('D',[.065,.435,.225,.235]);rng=np.random.default_rng(20261015)
    for j,(col,fill,means,offset) in enumerate([(ORANGE,OFILL,[2.95,2.7,3.4,3.45],-.17),(TEAL,TFILL,[2.9,3.12,3.9,4.5],.17)]):
        samples=[m+np.array([-.14,-.05,0,.06,.13])*(1.5 if i==0 and j==1 else .6) for i,m in enumerate(means)]
        bp=d.boxplot(samples,positions=np.arange(4)+offset,widths=.25,patch_artist=True,showfliers=False,
                     boxprops={'facecolor':fill,'edgecolor':col,'lw':.6},medianprops={'color':col,'lw':.7},
                     whiskerprops={'color':col,'lw':.5},capprops={'color':col,'lw':.5})
        DATA.extend(['D','group'+str(j),float(i),float(v)] for i,vals in enumerate(samples) for v in vals)
    d.set(xlim=(-.5,3.5),ylim=(0,6),xticks=[0,1,2,3],xticklabels=[24,34,48,58],yticks=[0,2,4,6],xlabel='Time (h)',ylabel=r'CH$_4$ yield (mmol/OD)')
    d.legend(handles=[Rectangle((0,0),1,1,facecolor=OFILL,edgecolor=ORANGE),Rectangle((0,0),1,1,facecolor=TFILL,edgecolor=TEAL)],
             labels=['M. a 321','M. a 3fk'],loc='upper left',ncol=2,fontsize=6.5,handlelength=.9,columnspacing=.7)
    for x,y in [(1,3.5),(2,4.5),(3,5)]:
        d.plot([x-.24,x+.24],[y,y],color='.25',lw=.5);d.text(x,y+.06,'***',ha='center',fontsize=7)
    e=panel('E',[.395,.435,.225,.235])
    t=np.array([0,10,20,30,45,55]);y1=np.array([13.6,13.8,13.85,13.4,13.65,13.8]);y2=np.array([14,13.5,11.85,11.2,10.2,9.7])
    for name,y,col,fill in [('M. a 321',y1,ORANGE,OFILL),('M. a 3fk',y2,TEAL,TFILL)]:
        e.errorbar(t,y,yerr=.35,color=col,marker='o',mfc=fill,mec=col,ms=3,lw=.8,capsize=2,elinewidth=.5,label=name)
        DATA.extend(['E',name,float(x),float(z)] for x,z in zip(t,y))
    e.axhline(13.9,color='.2',ls=':',lw=.8)
    e.set(xlim=(-2,62),ylim=(8,16),xticks=[0,20,40,60],yticks=[8,12,16],xlabel='Time (h)',ylabel='Glucose concentration (mM)')
    series_legend(e)
    for letter,box,col,values,yticks,ylabel in [
        ('F',[.70,.435,.10,.235],ORANGE,[1.1,0,17.4,.4,7.4,.1,0],[0,10,20],r'Intensity ($10^5$)'),
        ('G',[.875,.435,.10,.235],TEAL,[.15,.18,4.7,1.25,4.4,1.1,6.2],[0,3,6],r'Intensity ($10^6$)')]:
        ax=panel(letter,box);mass=np.arange(12,19)
        ax.vlines(mass,0,values,color=col,lw=1.1)
        ax.set(xlim=(11.5,18.5),ylim=(0,20 if letter=='F' else 6.8),xticks=[12,14,16,18],yticks=yticks,xlabel='m/z',ylabel=ylabel)
        for x,y in zip(mass,values):
            if y>.5:ax.text(x,y+.2,str(x),ha='center',fontsize=6,color=col)
        DATA.extend([letter,'spectrum',float(x),float(z)] for x,z in zip(mass,values))
    h=panel('H',[.055,.055,.92,.28],False)
    # Editable simplified pathway, not a claimed chemical-structure reconstruction.
    for x,y,label in [(.09,.73,'Glu'),(.09,.24,'G6P'),(.29,.24,'F6P'),(.29,.73,'FBP'),(.49,.73,'Pyr'),(.49,.24,'AcCoA'),(.67,.73,'Cit'),(.88,.73,'Icit'),(.88,.24,'Succ'),(.71,.08,'Mal'),(.65,.27,'Oxa')]:
        angles=np.linspace(0,2*np.pi,7)
        h.plot(x+.032*np.cos(angles),y+.065*np.sin(angles),color='.3',lw=.6)
        h.scatter([x-.016,x+.016],[y-.02,y+.02],s=14,color=TEAL,alpha=.55,edgecolors='none')
        h.text(x,y-.12,label,ha='center',fontsize=6.5,color=ORANGE)
    for start,end,col in [((.09,.61),(.09,.37),ORANGE),((.13,.24),(.24,.24),ORANGE),((.29,.37),(.29,.61),ORANGE),
                          ((.34,.73),(.44,.73),ORANGE),((.49,.60),(.49,.37),ORANGE),((.54,.24),(.64,.61),'#EEA9B5'),
                          ((.72,.73),(.83,.73),'#EEA9B5'),((.88,.60),(.88,.37),'#EEA9B5'),((.83,.20),(.76,.10),'#EEA9B5')]:
        h.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':col,'lw':1})
    for spine in h.spines.values():spine.set_visible(True)
    h.add_patch(Rectangle((0,0),1,1,fill=False,edgecolor='#BBBBBB',lw=.6))
    h.text(.02,.97,'Simplified pathway schematic',fontsize=6,va='top',color='.4')
    return fig


if __name__=='__main__':
    f=draw()
    targets=export_figure(f,stem='peach-teal-reference',dpi=240,
                         config={'theme':'user:peach-teal','palette':'user:peach-teal'})
    plt.close(f)
    with (targets[0].parent.parent/(targets[0].stem+'.estimated-data.csv')).open('w',encoding='utf-8',newline='') as file:
        w=csv.writer(file);w.writerow(['panel','series','x','y']);w.writerows(DATA)
    for target in targets:print(target)
