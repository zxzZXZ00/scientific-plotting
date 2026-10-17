"""Read-only dependency/font check. Never installs packages or copies fonts."""
import importlib.metadata
import json
import os
import platform
import sys


def check_environment():
    result={'python':platform.python_version(),'executable':sys.executable,
            'platform':platform.platform(),'packages':{},'errors':[]}
    if sys.version_info < (3,12):result['errors'].append('This pinned environment requires Python 3.12 or newer; tested on 3.12.10.')
    for name in ['matplotlib','numpy','PyYAML','PyMuPDF']:
        try:result['packages'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:result['errors'].append('Missing package: '+name)
    try:
        from matplotlib import font_manager
        if os.environ.get('SCI_PLOT_ARIAL'):font_manager.fontManager.addfont(os.environ['SCI_PLOT_ARIAL'])
        result['arial']=font_manager.findfont('Arial',fallback_to_default=False)
    except (ImportError,ValueError,OSError) as exc:
        result['errors'].append('Arial is unavailable: install a licensed Arial font, or set SCI_PLOT_ARIAL to its .ttf path. '+str(exc))
    result['passed']=not result['errors']
    return result


if __name__=='__main__':
    result=check_environment();print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['passed'] else 1)
