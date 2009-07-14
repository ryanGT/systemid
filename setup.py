from distutils.core import setup

tests = ['systemid.tests']
modules = ['systemid.gui','systemid.testing']

setup(name='systemid',
      version='a',
      license = None,
      description='A set of tools including a wxPython GUI for system identification.',
      author='Bill Purcell',
      author_email='williamhpurcell@gmail.com',
      url = 'http://www.siue.edu/~wpurcel',
      packages=['systemid']+modules+tests,
      scripts = ['bin/sysidgui.py'],
      )
