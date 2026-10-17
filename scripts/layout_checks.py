"""Renderer-based export gate; checks geometry, not scientific correctness."""
import json
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath
from matplotlib.text import Text


def inspect_figure(fig, full_frame=True):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    px=fig.dpi/72
    errors=[];warnings=[];excluded=set();frames=[]
    for ax in fig.axes:
        for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not min(limits)<=tick.get_loc()<=max(limits):
                    excluded.update([tick.label1,tick.label2])
        if ax.axison and ax.name=='rectilinear':
            if full_frame and not all(s.get_visible() for s in ax.spines.values()):
                errors.append({'kind':'open_frame','axes':fig.axes.index(ax)})
            frames.append((ax,ax.bbox))
    for ax,bounds in getattr(fig,'_scientific_frames',[]):
        from matplotlib.transforms import Bbox
        corners=ax.transData.transform(np.array(bounds).reshape(2,2))
        frames.append((ax,Bbox.from_extents(*corners.min(axis=0),*corners.max(axis=0))))

    texts=[]
    for t in fig.findobj(match=Text):
        if t in excluded or not t.get_visible() or not t.get_text().strip():continue
        box=t.get_window_extent(renderer)
        if not np.isfinite(box.extents).all():continue
        texts.append((t,box))
        if box.x0 < -.25*px or box.y0 < -.25*px or box.x1 > fig.bbox.width+.25*px or box.y1 > fig.bbox.height+.25*px:
            errors.append({'kind':'text_outside_canvas','text':t.get_text()})
    for i,(a,ab) in enumerate(texts):
        for b,bb in texts[i+1:]:
            overlap_x=min(ab.x1,bb.x1)-max(ab.x0,bb.x0)
            overlap_y=min(ab.y1,bb.y1)-max(ab.y0,bb.y0)
            if overlap_x>.3*px and overlap_y>.3*px:
                errors.append({'kind':'text_overlap','texts':[a.get_text(),b.get_text()]})

    errorbar_artists=getattr(fig,'_scientific_errorbar_artists',[])
    for artist in errorbar_artists:
        bounds=artist.get_path().transformed(artist.get_transform()).get_extents()
        clip=artist.get_clip_path()
        clipping=clip.get_fully_transformed_path().get_extents() if clip is not None else artist.get_clip_box()
        if artist.get_clip_on() and clipping is not None:
            stroke=artist.get_linewidth()*px
            if (bounds.width<.1*px and clipping.width<stroke+1 or
                    bounds.height<.1*px and clipping.height<stroke+1):
                errors.append({'kind':'errorbar_clip_too_narrow'})

    for ax,frame in frames:
        segments=[]
        artists=list(ax.lines)+list(ax.patches)
        if ax.axison:artists += [s for s in ax.spines.values() if s.get_visible()]
        for artist in artists:
            if not artist.get_visible() or artist is ax.patch:continue
            if hasattr(artist,'get_edgecolor') and np.asarray(artist.get_edgecolor()).size==4 and artist.get_edgecolor()[3]==0:continue
            path=artist.get_path().transformed(artist.get_transform())
            previous=None;start=None
            for vertices,code in path.iter_segments(curves=False,simplify=False):
                point=np.array(vertices[-2:])
                if code==MPath.MOVETO:previous=point;start=point;continue
                if code==MPath.CLOSEPOLY:point=start
                if previous is not None:
                    if abs(point[0]-previous[0])<.15*px:
                        segments.append(('v',point[0],min(point[1],previous[1]),max(point[1],previous[1])))
                    elif abs(point[1]-previous[1])<.15*px:
                        segments.append(('h',point[1],min(point[0],previous[0]),max(point[0],previous[0])))
                previous=point
        for side,kind,position,lo,hi in [('left','v',frame.x0,frame.y0,frame.y1),('right','v',frame.x1,frame.y0,frame.y1),
                                          ('bottom','h',frame.y0,frame.x0,frame.x1),('top','h',frame.y1,frame.x0,frame.x1)]:
            hits=[s for s in segments if s[0]==kind and abs(s[1]-position)<=3*px and
                  min(s[3],hi)-max(s[2],lo)>.8*(hi-lo)]
            if len(hits)>1:
                errors.append({'kind':'duplicate_frame_edge','side':side,'count':len(hits)})
            elif not hits and full_frame:
                errors.append({'kind':'missing_frame_edge','side':side})

    # Legends can hide lines even when all text boxes are separate.
    for ax in fig.axes:
        legend=ax.get_legend()
        if legend is None or not legend.get_visible():continue
        box=legend.get_window_extent(renderer)
        if box.x0<ax.bbox.x0 or box.y0<ax.bbox.y0 or box.x1>ax.bbox.x1 or box.y1>ax.bbox.y1:
            errors.append({'kind':'legend_outside_frame'})
        for line in ax.lines:
            if line.get_visible() and line.get_path().transformed(line.get_transform()).intersects_bbox(box,filled=False):
                warnings.append({'kind':'legend_over_data','series':line.get_label()})
    for ax,legend_bounds,frame_bounds in getattr(fig,'_scientific_legend_regions',[]):
        x0,y0,x1,y1=legend_bounds;fx0,fy0,fx1,fy1=frame_bounds
        if min(x0,x1)<min(fx0,fx1) or max(x0,x1)>max(fx0,fx1) or min(y0,y1)<min(fy0,fy1) or max(y0,y1)>max(fy0,fy1):
            errors.append({'kind':'legend_outside_frame'})
    for ax,artists,bounds in getattr(fig,'_scientific_legends',[]):
        corners=ax.transData.transform(np.array(bounds).reshape(2,2))
        lo=corners.min(axis=0);hi=corners.max(axis=0)
        for artist in artists:
            box=artist.get_window_extent(renderer)
            if box.x0<lo[0]-.1*px or box.y0<lo[1]-.1*px or box.x1>hi[0]+.1*px or box.y1>hi[1]+.1*px:
                errors.append({'kind':'legend_outside_frame','artist':getattr(artist,'get_text',lambda:'symbol')()})
    return {'passed':not errors,'errors':errors,'warnings':warnings,
            'checked_text_objects':len(texts),'checked_frames':len(frames),
            'checked_errorbar_segments':len(errorbar_artists),
            'limits':'Does not establish data accuracy, semantic equivalence, or every visual collision; inspect PNG too.'}


def validate_figure(fig,report_path,full_frame=True):
    report=inspect_figure(fig,full_frame=full_frame)
    target=Path(report_path);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if not report['passed']:
        raise ValueError('排版检查未通过，停止导出；详见 '+str(target)+': '+str(report['errors'][:4]))
    return report
