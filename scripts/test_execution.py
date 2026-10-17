"""Integration regressions: portability, output defaults and registered resources."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml

from exporting import export_figure
from plotting import read_data,plot_line_with_band
from settings import load_settings

ROOT=Path(__file__).resolve().parents[1]


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path.cwd())
        self.base=Path(self.temp.name)
        self.csv=self.base/'ftir_sample.csv';self.csv.write_text('wavenumber,absorbance\n3000,1\n2000,2\n1000,1.5\n',encoding='utf8')
        self.task={'data':{'path':self.csv.name,'x':'wavenumber','y':'absorbance'}}

    def tearDown(self):plt.close('all');self.temp.cleanup()

    def config(self,task=None):
        path=self.base/'task.yaml';path.write_text(yaml.safe_dump(task or self.task),encoding='utf8')
        return load_settings(path)

    def test_spectral_recommendation_uses_existing_library(self):
        c=self.config();self.assertEqual(c['theme'],'user:blue-magenta');self.assertEqual(c['template'],'spectrum')
        data=read_data(self.csv,c['data'],band=False);f=plot_line_with_band(data,c)
        self.assertTrue(f.axes[0].xaxis_inverted());self.assertIn(f.axes[0].lines[0].get_marker(),[None,'None'])

    def test_explicit_choices_override_domain(self):
        self.task.update(theme='user:peach-teal',palette='blue-red',template='line')
        c=self.config();self.assertEqual((c['theme'],c['palette'],c['template']),('user:peach-teal','blue-red','line'))

    def test_unknown_domain_borrows_an_existing_theme(self):
        self.task.update(purpose='A new research field',theme='user:mist-blue-rose')
        self.assertEqual(self.config()['theme'],'user:mist-blue-rose')

    def test_missing_theme_is_rejected(self):
        self.task['theme']='user:not-registered'
        with self.assertRaisesRegex(ValueError,'主题不在'):self.config()

    def test_missing_palette_is_rejected(self):
        self.task['palette']='user:not-registered'
        with self.assertRaisesRegex(ValueError,'配色不在'):self.config()

    def test_outside_palette_colour_is_rejected(self):
        self.task['appearance']={'colors':['#123456']}
        with self.assertRaisesRegex(ValueError,'系列颜色'):self.config()

    def test_three_formats_same_input_name_and_no_overwrite(self):
        f,a=plt.subplots(layout='constrained');a.plot([0,1],[0,1])
        c={'theme':'paper','palette':'blue-red'}
        paths=export_figure(f,data_path=self.base/'样品 A.csv',workspace=self.base,config=c)
        self.assertEqual({p.parent.name for p in paths},{'png','svg','pdf'})
        self.assertTrue(all(p.stem=='样品 A' and p.is_file() for p in paths))
        again=export_figure(f,data_path=self.base/'样品 A.csv',workspace=self.base,config=c,formats=['png'])
        self.assertEqual(again[0].stem,'样品 A_2')

    def test_separate_workspaces_use_same_installed_script(self):
        source=self.base/'actual_input.csv';source.write_text('x,y\n0,1\n1,2\n2,1.5\n',encoding='utf8')
        config=self.base/'external-task.yaml';config.write_text(yaml.safe_dump({'theme':'user:red-cyan','data':{'path':str(source),'x':'x','y':'y'}}),encoding='utf8')
        for name in ['workspace_A','workspace_B']:
            space=self.base/name;space.mkdir()
            subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/render.py'),'--config',str(config)],cwd=space,check=True,capture_output=True,text=True,encoding='utf8')
            for ext in ['png','svg','pdf']:self.assertTrue((space/'sci_plots'/ext/f'actual_input.{ext}').is_file())
            report=json.loads((space/'sci_plots/actual_input.layout-checks.json').read_text(encoding='utf8'))
            self.assertTrue(report['passed'])
            resolved=yaml.safe_load((space/'sci_plots/actual_input.resolved-config.yaml').read_text(encoding='utf8'))
            self.assertEqual(resolved['output']['directory'],str(space/'sci_plots'))

    def test_export_rejects_a_missing_resource_selection(self):
        f,a=plt.subplots()
        with self.assertRaisesRegex(ValueError,'theme 和 palette'):export_figure(f,workspace=self.base)

    def test_workspace_and_data_override_determine_output_name(self):
        source=self.base/'替换数据.csv';source.write_text('x,y\n0,1\n1,2\n2,1.5\n',encoding='utf8')
        config=self.base/'override.yaml';config.write_text(yaml.safe_dump({'theme':'user:red-cyan','template':'line','data':{'path':'unused.csv','x':'x','y':'y'}}),encoding='utf8')
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/render.py'),'--workspace',str(self.base),'--config','override.yaml','--data',source.name],
                       cwd=ROOT,check=True,capture_output=True,text=True,encoding='utf8')
        for ext in ['png','svg','pdf']:self.assertTrue((self.base/'sci_plots'/ext/f'替换数据.{ext}').is_file())


if __name__=='__main__':unittest.main()
