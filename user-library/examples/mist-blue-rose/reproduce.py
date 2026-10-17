"""Rebuild supplied PDF vector geometry as editable Matplotlib paths.

No raster screenshots are placed in the rebuilt figure. Molecular raster insets
are replaced by explicitly approximate, editable sphere schematics.
"""
from pathlib import Path
import re
import json
import xml.etree.ElementTree as ET
import sys

import numpy as np
import pymupdf as fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Circle, Rectangle
from matplotlib.transforms import Affine2D

BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'scripts/layout_checks.py').is_file())
sys.path.insert(0,str(ROOT/'scripts'))
from layout_checks import validate_figure
from exporting import export_figure, output_root
NS='{http://www.w3.org/1999/xlink}'
plt.rcParams.update({'font.family':'Arial','font.style':'normal','svg.fonttype':'none',
                     'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic',
                     'mathtext.default':'regular'})


def rebuilt_labels(page,clip):
    """Group source spans into complete labels before changing font or size."""
    lines=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            box=fitz.Rect(line['bbox']);centre=(box.tl+box.br)/2
            if fitz.Rect(clip).contains(centre):
                lines.append(dict(line,spans=list(line['spans'])))
    # Some PDFs store the final superscript as a separate extraction line.
    # Attach only those small fragments to the geometrically nearest label.
    fragments=[l for l in lines if max(s['size'] for s in l['spans'])<5 or
               ''.join(s['text'] for s in l['spans']).startswith('−2 h')]
    for fragment in fragments:
        fb=fitz.Rect(fragment['bbox']);candidates=[]
        for target in lines:
            if target is fragment or target in fragments:continue
            if np.linalg.norm(np.array(target['dir'])-fragment['dir'])>.05:continue
            tb=fitz.Rect(target['bbox'])
            distance=np.hypot(max(tb.x0-fb.x1,fb.x0-tb.x1,0),max(tb.y0-fb.y1,fb.y0-tb.y1,0))
            if distance<4:candidates.append((distance,target))
        if candidates:
            target=min(candidates,key=lambda p:p[0])[1]
            target['spans'].extend(fragment['spans'])
            target['bbox']=tuple(fitz.Rect(target['bbox'])|fb)
            lines.remove(fragment)
    for line in lines:
        spans=line['spans'];direction=np.array(line['dir']);normal=np.array([-direction[1],direction[0]])
        size=max(s['size'] for s in spans)
        main=next(s for s in spans if s['size']>=size*.95)
        base=np.dot(main['origin'],normal)
        spans.sort(key=lambda s:np.dot(s['origin'],direction))
        pieces=[]
        for span in spans:
            value=span['text'].replace('\u00a0',' ')
            if span['size']<size*.82:
                operator='_' if np.dot(span['origin'],normal)>base else '^'
                value=value.replace('−','-').replace('–','-')
                pieces.append('$'+operator+'{'+r'\mathrm{'+value+'}'+'}$')
            elif value in ['j','k','R','χ'] and 'italic' in span['font'].lower():
                pieces.append('$'+('\\chi' if value=='χ' else value)+'$')
            else:pieces.append(value)
        text=''.join(pieces).strip()
        flat=''.join(s['text'] for s in spans)
        if flat.startswith('jHER'):
            match=re.search(r'=\s*([−–-]?\d+)',flat)
            text=(r'$j_{\mathrm{HER}}' + ((' = '+match.group(1).replace('−','-').replace('–','-')) if match else '')
                  +r'\ (\mathrm{mA}\ \mathrm{cm}^{-2})$')
        if flat.startswith('TOF'):
            text=r'TOF (mM m$_{\mathrm{Pd}}^{-2}$ h$^{-1}$)'
        if flat.startswith('FT('):text=r'FT($k^2\chi(k)$) (Å$^{-3}$)'
        # Common compounds must share one base for simultaneous sub/superscripts.
        text=text.replace('$'+'_{\\mathrm{Pd}}'+'$$'+'^{\\mathrm{-2}}'+'$',
                          r'$_{\mathrm{Pd}}^{-2}$')
        box=fitz.Rect(line['bbox'])
        yield {'text':text,'xy':((box.x0+box.x1)/2,(box.y0+box.y1)/2),
               'rotation':-np.degrees(np.arctan2(direction[1],direction[0])),
               'size':size*1.15,'color':'#%06x'%main['color'],
               'weight':'bold' if 'bold' in main['font'].lower() or 'semibold' in main['font'].lower() else 'normal'}


def transform(value):
    matrix=np.eye(3)
    for name,args in re.findall(r'(matrix|translate|scale|rotate)\(([^)]*)\)',value or ''):
        a=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',args)]
        t=np.eye(3)
        if name=='matrix':t=np.array([[a[0],a[2],a[4]],[a[1],a[3],a[5]],[0,0,1.]])
        elif name=='translate':t[:2,2]=[a[0],a[1] if len(a)>1 else 0]
        elif name=='scale':t[0,0]=a[0];t[1,1]=a[1] if len(a)>1 else a[0]
        elif name=='rotate':
            angle=np.deg2rad(a[0]);t[:2,:2]=[[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]
        matrix=matrix@t
    return matrix


def path_from_d(d):
    tokens=re.findall(r'[MLHVQCZmlhvqcz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',d)
    vertices=[];codes=[];i=0;cmd=None;point=np.zeros(2);start=np.zeros(2)
    while i<len(tokens):
        if tokens[i].isalpha():cmd=tokens[i];i+=1
        upper=cmd.upper();relative=cmd.islower()
        if upper=='Z':
            vertices.append(start.copy());codes.append(MPath.CLOSEPOLY);point=start.copy();cmd=None;continue
        count={'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6}[upper]
        nums=np.array([float(x) for x in tokens[i:i+count]]);i+=count
        if upper in ['H','V']:
            nxt=point.copy();axis=0 if upper=='H' else 1
            nxt[axis]=nums[0]+(point[axis] if relative else 0)
            vertices.append(nxt);codes.append(MPath.LINETO);point=nxt
        else:
            pts=nums.reshape(-1,2)+(point if relative else 0)
            vertices.extend(pts)
            codes.extend([{'M':MPath.MOVETO,'L':MPath.LINETO,'Q':MPath.CURVE3,'C':MPath.CURVE4}[upper]]*len(pts))
            point=pts[-1]
            if upper=='M':start=point.copy();cmd='l' if relative else 'L'
    return MPath(np.array(vertices),codes)


def rebuild(name,filename,clip):
    dest=output_root()
    doc=fitz.open(BASE/'source.pdf');page=doc[0]
    source_svg=page.get_svg_image(text_as_path=False)
    root=ET.fromstring(source_svg);defs={e.get('id'):e for e in root.iter() if e.get('id')}
    left,top,right,bottom=clip
    # Padding is physical space, not bbox_inches='tight' as an overlap remedy.
    margin=8
    extra=35 if name=='mist-blue-rose' else 0
    fig=plt.figure(figsize=((right-left+2*margin)/72,(bottom-top+2*margin+extra)/72),dpi=240)
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(left-margin,right+margin),ylim=(bottom+margin+extra,top-margin));ax.axis('off')
    stats={'paths':0,'text_runs':0,'font':'Arial','raster_images_reused':0,'raster_images_replaced':0}
    seen_edges=set()
    fig._scientific_errorbar_artists=[]
    fig._scientific_legends=[]

    def walk(element,parent=np.eye(3),style=None,clipbox=None):
        tag=element.tag.split('}')[-1]
        if tag in ['defs','clipPath','mask','image']:return
        current=parent@transform(element.get('transform'))
        clipref=re.search(r'url\(#([^)]*)\)',element.get('clip-path',''))
        if clipref:
            clipping=defs.get(clipref.group(1))
            if clipping is not None:
                boxes=[]
                for child in clipping:
                    if child.get('d'):
                        cp=Affine2D(current@transform(child.get('transform'))).transform_path(path_from_d(child.get('d')))
                        boxes.append(cp.get_extents())
                if boxes:
                    b=boxes[0]
                    # Hairline-sized PDF masks cause Agg to erase error-bar stems.
                    # The underlying path already describes that exact stem/cap;
                    # keep the enclosing panel clip instead of clipping it twice.
                    if b.width >= .6 and b.height >= .6:
                        newclip=(b.x0,b.y0,b.x1,b.y1)
                        clipbox=newclip if clipbox is None else (max(clipbox[0],b.x0),max(clipbox[1],b.y0),min(clipbox[2],b.x1),min(clipbox[3],b.y1))
        attrs=dict(style or {})
        for k in ['fill','stroke','stroke-width','opacity','fill-opacity','stroke-opacity','stroke-dasharray','stroke-linecap','stroke-linejoin']:
            if k in element.attrib:attrs[k]=element.get(k)
        if tag=='text':return

        if tag=='use':
            target=defs.get(element.get(NS+'href','').lstrip('#'))
            if target is not None:walk(target,current,attrs,clipbox)
            return
        if tag=='path' and element.get('d'):
            path=path_from_d(element.get('d'))
            path=Affine2D(current).transform_path(path)
            bounds=path.get_extents()
            if bounds.x1<left or bounds.x0>right or bounds.y1<top or bounds.y0>bottom:return
            stroke=attrs.get('stroke','none');fill=attrs.get('fill','#000000')
            if name=='mist-blue-rose':
                # Replace only legend primitives; never mask a whole area that
                # might contain real data, error bars, or dual-axis arrows.
                old_legend=(195<bounds.x0 and bounds.x1<223 or 442<bounds.x0 and bounds.x1<467)
                if old_legend and 375<bounds.y0 and bounds.y1<400:return
                if 206<bounds.x0 and bounds.x1<217 and 125<bounds.y0 and bounds.y1<175:return
                if 210<bounds.x0 and bounds.x1<240 and 125<bounds.y0 and bounds.y1<175 and bounds.height<1:return
                if 205<bounds.x0 and bounds.x1<215 and 286<bounds.y0 and bounds.y1<326:return
                if bounds.y0>=370 and fill=='none' and (
                    bounds.width<.02 and bounds.height>100 and any(abs(bounds.x0-v)<.1 for v in [125.368,262.961,332.288,469.881]) or
                    bounds.height<.02 and bounds.width>130 and any(abs(bounds.y0-v)<.1 for v in [372.393,493.809,372.522,493.937])):return
                if bounds.y0>=365:
                    path=Affine2D().translate(0,extra).transform_path(path)
                    if clipbox and clipbox[1]>=365:
                        clipbox=(clipbox[0],clipbox[1]+extra,clipbox[2],clipbox[3]+extra)
            if name=='blue-magenta':
                if 330<bounds.x0 and bounds.x1<422 and 204<bounds.y0 and bounds.y1<216:return
                if abs(bounds.y0-323.9283)<.02 and bounds.height<.02 and bounds.width>70:return
                if abs(bounds.x0-329.8145)<.02 and bounds.width<.02 and bounds.height>100:
                    path=MPath([[329.8145,198],[329.8145,323.9283]],[MPath.MOVETO,MPath.LINETO])
            if fill=='none' and (bounds.width<.02 and bounds.height>70 or bounds.height<.02 and bounds.width>70):
                key=tuple(np.round(path.get_extents().extents,1))
                if key in seen_edges:return
                seen_edges.add(key)
            # Stroke widths are source units times the local affine scale.
            scale=np.sqrt(abs(np.linalg.det(current[:2,:2])))
            patch=PathPatch(path,facecolor=fill,edgecolor=stroke,
                            lw=float(attrs.get('stroke-width',1))*scale,
                            alpha=float(attrs.get('opacity',1)),
                            capstyle={'square':'projecting'}.get(attrs.get('stroke-linecap'),attrs.get('stroke-linecap','butt')),
                            joinstyle=attrs.get('stroke-linejoin','miter'))
            dash=attrs.get('stroke-dasharray','none')
            if dash!='none':
                values=[float(x)*scale for x in re.findall(r'[\d.]+',dash)]
                if values:patch.set_linestyle((0,values))
            ax.add_patch(patch)
            if clipbox:
                x0,y0,x1,y1=clipbox
                patch.set_clip_path(Rectangle((x0,y0),max(0,x1-x0),max(0,y1-y0),transform=ax.transData))
            if name=='mist-blue-rose' and 335<bounds.x0<465 and 63<bounds.y0<333 and (
                    bounds.width<.02 and 3<bounds.height<30 or bounds.height<.02 and 2<bounds.width<5):
                fig._scientific_errorbar_artists.append(patch)
            stats['paths']+=1
        for child in element:walk(child,current,attrs,clipbox)
    walk(root)
    if name=='blue-magenta':
        # Original gradient columns and 3D molecular pictures are raster images.
        # Replace them with editable vector approximations, not pasted source pixels.
        bar_index=0
        for info in page.get_image_info():
            x0,y0,x1,y1=info['bbox'];w=x1-x0;h=y1-y0
            if not(left<=x0<=right and top<=y0<=bottom):continue
            if w<10:
                if bar_index==0:
                    # Remove transparent-image boundary remnants above the short ZnO bar.
                    ax.add_patch(Rectangle((335,217),67,107,facecolor='white',edgecolor='none',zorder=3))
                segments=[[(.47,'#AAAAAA')],[(.56,'#AAAAAA'),(.44,'#CC79A7')],
                          [(.56,'#AAAAAA'),(.29,'#CC79A7'),(.15,'#377EB8')]][bar_index]
                accumulated=0
                for fraction,color in segments:
                    ax.add_patch(Rectangle((x0,y1-h*(accumulated+fraction)),w,h*fraction,
                                           facecolor=color,edgecolor='#444444',lw=.25,zorder=4))
                    accumulated+=fraction
                bar_index+=1
            else:
                for row in range(6):
                    for col in range(12-row//2):
                        xx=x0+w*(.08+.075*col+.015*row);yy=y0+h*(.20+.105*row)
                        color=['#9BA5AE','#B96060','#9BA5AE','#688CB0'][(row+col)%4]
                        ax.add_patch(Circle((xx,yy),w*.022,facecolor=color,edgecolor='#666666',lw=.15,zorder=.5))
            stats['raster_images_replaced']+=1
        # Keep the composition chart closed even though the article used two sides.
        # Supplement only missing sides, using the original axes' exact ends.
        ax.plot([329.8145,403.7895,403.7895,329.8145],[198,198,323.9283,323.9283],color='black',lw=.35,zorder=5)
    for label in rebuilt_labels(page,clip):
        x,y=label['xy'];text=label['text']
        if name=='mist-blue-rose':
            if text.startswith('$j_{') and label['size']<7:continue
            if 230<x<260 and 120<y<175 and (text=='Ar' or text.startswith('CO')):continue
            if abs(label['rotation']-30)<1:continue
            if y>=365:label['xy']=(x,y+extra)
            if text in ['e','f'] and 360<y<380:label['xy']=(x,y)
            if text=='FE (%)' and y>400:label['xy']=(x,y+extra-17.5)
            if text=='TOF (mM m$_{\\mathrm{Pd}}^{-2}$ h$^{-1}$)':
                label['xy']=(x+2,y+extra-17.5)
        if name=='blue-magenta':
            if (330<x<422 and 204<y<216):continue
            if abs(label['rotation']-45)<1:continue
            if text=='Surface composition (%)':label['xy']=(x,y-4)
        ax.text(*label['xy'],label['text'],ha='center',va='center',
                fontsize=label['size'],rotation=label['rotation'],rotation_mode='anchor',
                color=label['color'],fontweight=label['weight'],zorder=6)
        stats['text_runs']+=1
    if name=='mist-blue-rose':
        for x0,y0,x1,y1 in [(125.368,372.393,262.961,528.809),(332.288,372.521,469.881,528.937)]:
            ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor='black',lw=.35,zorder=5))
        # Complete mathematical labels are rendered once, with native spacing.
        # Legend text/handles are placed together instead of retaining glyph xy.
        def legend_text(x,y,value,size=6.5):
            return ax.text(x,y,value,fontsize=size,ha='left',va='center',zorder=8)
        for y,val in [(119,0),(151,-10)]:
            group=[legend_text(202,y,rf'$j_{{\mathrm{{HER}}}}={val}\ \mathrm{{mA}}\ \mathrm{{cm}}^{{-2}}$')]
            for dy,color,ls,word in [(10,'#999999' if val==0 else 'black',':' if val==0 else '-','Ar'),
                                     (20,'#FF7DC5' if val==0 else '#D90042',':' if val==0 else '-',r'CO$_2$')]:
                group.extend(ax.plot([215,227],[y+dy,y+dy],color=color,ls=ls,lw=.8,zorder=7))
                group.append(legend_text(231,y+dy,word))
            fig._scientific_legends.append((ax,group,(125.371,61.937,262.944,182.427)))
        group=[]
        for y,val,color in zip([290,301,312,323],[-1,-5,-10,-50],['#F6B6A1','#FF8D95','#D90042','#C5689B']):
            group.extend(ax.plot([190,196],[y,y],color=color,lw=.8,zorder=7))
            group.append(legend_text(199,y,rf'$j_{{\mathrm{{HER}}}}={val}\ \mathrm{{mA}}\ \mathrm{{cm}}^{{-2}}$'))
        fig._scientific_legends.append((ax,group,(125.4,215.112,262.973,335.602)))
        for offset in [0,207]:
            group=[]
            for y,val,color,marker in [(385,0,'#595959','o'),(397,-10,'#00629F','^')]:
                group.append(legend_text(139+offset,y,rf'$j_{{\mathrm{{HER}}}}={val}\ \mathrm{{mA}}\ \mathrm{{cm}}^{{-2}}$'))
                group.extend(ax.plot(219+offset,y,marker=marker,color=color,ms=3.5,zorder=7))
                patch=Rectangle((228+offset,y-2),10,4,facecolor='#BFBFBF' if val==0 else '#71A9CE',edgecolor='none',zorder=7)
                ax.add_patch(patch);group.append(patch)
            fig._scientific_legends.append((ax,group,(125.368+offset,372.393,262.961+offset,528.809)))
        category_sets=[([154,200,245],['0.5 M\nKHCO$_3$','0.5 M\nNaClO$_4$','50 mM KHCO$_3$\n0.5 M NaClO$_4$']),
                       ([361,407,453],['50 mM NaHCO$_3$\n0.5 M NaClO$_4$','50 mM KHCO$_3$\n0.5 M NaClO$_4$','50 mM CsHCO$_3$\n0.5 M NaClO$_4$'])]
        for positions,values in category_sets:
            for x,value in zip(positions,values):
                # Split long salt names into aligned rows instead of rotation.
                value=value.replace('50 mM ','50 mM\n').replace('0.5 M NaClO','0.5 M\nNaClO')
                ax.text(x,535,value,ha='center',va='top',fontsize=7,linespacing=1.35,zorder=8)
    else:
        for x,value in [(342,'ZnO'),(367,'Cr/ZnO\n0.3'),(392,'Cr/ZnO\n1.8')]:
            ax.text(x,330,value,ha='center',va='top',fontsize=6.8,linespacing=1.35,zorder=8)
        group=[]
        for y,value,color in [(204,r'Isolated Cr$^{3+}$','#C5689B'),(214,r'Cr$_2$O$_3$ cluster','#377EB8')]:
            patch=Rectangle((333,y-2),4.5,4.5,facecolor=color,edgecolor='black',lw=.25,zorder=7)
            ax.add_patch(patch);group.append(patch)
            group.append(ax.text(340,y,value,fontsize=6.5,va='center',zorder=8))
        fig._scientific_legends.append((ax,group,(329.8145,198,403.7895,323.9283)))
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    texts=[t for t in ax.texts if t.get_text().strip()]
    boxes=[t.get_window_extent(renderer) for t in texts]
    stats['text_collisions']=[(texts[i].get_text(),texts[j].get_text())
                             for i,b in enumerate(boxes) for j in range(i+1,len(boxes))
                             if b.overlaps(boxes[j])]
    stats['text_outside_canvas']=[t.get_text() for t,b in zip(texts,boxes)
                                  if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height]
    frame_bounds=([(125.371,61.937,262.944,182.427),(330.31,61.678,471.78,182.547),
                   (125.4,215.112,262.973,335.602),(330.661,215.305,472.04,336.172),
                   (125.368,372.393,262.961,528.809),(332.288,372.521,469.881,528.937)]
                  if name=='mist-blue-rose' else
                  [(144.932,54.003,287.925,170.219),(329.712,53.337,473.128,170.025),
                   (144.604,206.89,288.372,324.073),(329.8145,198,403.7895,323.9283)])
    fig._scientific_frames=[(ax,b) for b in frame_bounds]
    fig._scientific_legend_regions=([(ax,(139,380,239,402),frame_bounds[4]),
                                   (ax,(346,380,446,402),frame_bounds[5])]
                                  if name=='mist-blue-rose' else
                                  [(ax,(333,199,400,219),frame_bounds[3])])
    targets=export_figure(fig,stem=name+'-reference',dpi=240,config={'theme':'user:'+name,'palette':'user:'+name})
    for target in targets:print(target)
    plt.close(fig)
    (dest/(targets[0].stem+'.source-checks.json')).write_text(json.dumps(stats,indent=2),encoding='utf-8')
    doc.close();print(name,stats)


if __name__=='__main__':
    rebuild('mist-blue-rose','s41557-026-02243-1.pdf',(95, 49, 525, 535))
