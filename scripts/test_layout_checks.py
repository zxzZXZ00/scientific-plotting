"""Regression cases based on user-reported layout errors."""
import unittest
import tempfile
import json
from pathlib import Path as FilePath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from layout_checks import inspect_figure, validate_figure


class LayoutChecks(unittest.TestCase):
    def tearDown(self):plt.close('all')

    def test_separate_formula_fragments_overlap(self):
        f,a=plt.subplots();a.text(.4,.5,'j');a.text(.4,.5,'(mA cm)')
        self.assertIn('text_overlap',[e['kind'] for e in inspect_figure(f)['errors']])

    def test_complete_math_label_is_valid(self):
        f,a=plt.subplots(layout='constrained')
        a.set_ylabel(r'$j$ (mA cm$^{-2}$)');a.plot([0,1],[1,2])
        self.assertTrue(inspect_figure(f)['passed'])

    def test_outside_text(self):
        f,a=plt.subplots();f.text(-.1,.5,'Outside')
        self.assertIn('text_outside_canvas',[e['kind'] for e in inspect_figure(f)['errors']])

    def test_extra_rectangle_is_rejected(self):
        f,a=plt.subplots();a.add_patch(Rectangle((0,0),1,1,transform=a.transAxes,fill=False))
        self.assertIn('duplicate_frame_edge',[e['kind'] for e in inspect_figure(f)['errors']])

    def test_nearby_parallel_border_is_rejected(self):
        f,a=plt.subplots();a.add_patch(Rectangle((.004,0),.996,1,transform=a.transAxes,fill=False))
        self.assertIn('duplicate_frame_edge',[e['kind'] for e in inspect_figure(f)['errors']])

    def test_inverted_y_frame_is_valid(self):
        f,a=plt.subplots();a.axis('off');a.set_ylim(1,0)
        a.add_patch(Rectangle((0,0),1,1,fill=False))
        f._scientific_frames=[(a,(0,0,1,1))]
        self.assertTrue(inspect_figure(f)['passed'])

    def test_thin_errorbar_clip_is_rejected(self):
        f,a=plt.subplots()
        stem=PathPatch(Path([[.5,.3],[.5,.7]]),fill=False,lw=.5)
        a.add_patch(stem)
        stem.set_clip_path(Rectangle((.49999,.2),.00002,.6,transform=a.transData))
        f._scientific_errorbar_artists=[stem]
        self.assertIn('errorbar_clip_too_narrow',[e['kind'] for e in inspect_figure(f)['errors']])

    def test_export_gate_raises_and_keeps_diagnostics(self):
        f,a=plt.subplots();a.text(.5,.5,'A');a.text(.5,.5,'B')
        with tempfile.TemporaryDirectory(dir=FilePath.cwd()) as folder:
            report=FilePath(folder)/'layout-checks.json'
            with self.assertRaises(ValueError):validate_figure(f,report)
            self.assertFalse(json.loads(report.read_text(encoding='utf-8'))['passed'])

    def test_legend_outside_frame_is_rejected(self):
        f,a=plt.subplots();a.plot([0,1],[0,1],label='Data')
        a.legend(loc='upper left',bbox_to_anchor=(1.01,1))
        self.assertIn('legend_outside_frame',[e['kind'] for e in inspect_figure(f)['errors']])


if __name__=='__main__':unittest.main()
