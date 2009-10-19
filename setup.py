#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from setuptools import setup, find_packages
import os
import sys
import glob

args = {}

if os.name == 'nt':
    import py2exe
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
            return 0
        return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL

    args['windows'] = [{
        'script': os.path.join('bin', 'neso'),
        'icon_resources': [(1, os.path.join('share', 'pixmaps', 'neso', 'neso.ico'))],
    }]
    args['options'] = {
        'py2exe': {
            'optimize': 0,
            'bundle_files': 3, #don't bundle because gtk doesn't support it
            'packages': [
                'encodings',
                'gtk',
                'pygtk',
                'pytz',
                'atk',
                'pango',
                'pangocairo',
                'cairo',
                'ConfigParser',
                'xmlrpclib',
                'xml',
                'decimal',
                'mx.DateTime',
                'logging.handlers',
                'psycopg2',
                'zipfile',
                'sqlite3',
                'relatorio',
                'csv',
                'lxml',
                'pydoc',
                'DAV',
                'pydot',
                'BeautifulSoup',
                'vobject',
                'ldap',
                'pkg_resources',
            ],
        }
    }
    args['zipfile'] = None

execfile(os.path.join('neso', 'version.py'))

dist = setup(name=PACKAGE,
    version=VERSION,
    description='Tryton client/server',
    author='B2CK',
    author_email='info@b2ck.com',
    url=WEBSITE,
    download_url='http://downloads.tryton.org/' + \
            VERSION.rsplit('.', 1)[0] + '/',
    packages=find_packages(),
    scripts=['bin/neso'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Spanish',
        'Programming Language :: Python',
        'Topic :: Office/Business',
    ],
    license='GPL-3',
    install_requires=[
        'tryton >= 1.4.0',
        'trytond >= 1.4.0',
    ],
    **args
)

if os.name == 'nt':
    def find_gtk_dir():
        for directory in os.environ['PATH'].split(';'):
            if not os.path.isdir(directory):
                continue
            for file in ('gtk-demo.exe', 'gdk-pixbuf-query-loaders.exe'):
                if os.path.isfile(os.path.join(directory, file)):
                    return os.path.dirname(directory)
        return None

    def find_makensis():
        for directory in os.environ['PATH'].split(';'):
            if not os.path.isdir(directory):
                continue
            path = os.path.join(directory, 'makensis.exe')
            if os.path.isfile(path):
                return path
        return None

    import fnmatch
    def findFiles(topDir, pattern):
        for dirpath, dirnames, filenames in os.walk(topDir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, pattern):
                    yield os.path.join(dirpath, filename)

    if 'py2exe' in dist.commands:
        import shutil
        gtk_dir = find_gtk_dir()

        dist_dir = dist.command_obj['py2exe'].dist_dir

        from py_compile import compile
        for i in ('tryton', 'trytond'):
            if os.path.isdir(os.path.join(dist_dir, i)):
                shutil.rmtree(os.path.join(dist_dir, i))
            shutil.copytree(os.path.join(os.path.dirname(__file__), i),
                    os.path.join(dist_dir, i))
            for j in ('.hg', 'dist', 'build', i + '.egg-info'):
                if os.path.isdir(os.path.join(dist_dir, i, j)):
                    shutil.rmtree(os.path.join(dist_dir, i, j))
            for j in ('.hgtags', '.hgignore'):
                if os.path.isfile(os.path.join(dist_dir, i, j)):
                    os.remove(os.path.join(dist_dir, i, j))
            for file in glob.iglob(os.path.join(dist_dir, i, '*.exe')):
                os.remove(file)
            for file in findFiles(os.path.join(dist_dir, i), '*.py'):
                if file.endswith('__tryton__.py'):
                    continue
                print "byte-compiling %s to %s" % (file,
                        file[len(dist_dir) + len(os.sep):] + \
                        (__debug__ and 'c' or 'o'))
                compile(file, None, file[len(dist_dir) + len(os.sep):] + \
                        (__debug__ and 'c' or 'o'), True)
                os.remove(file)
        for j in ('.hg', 'dist', 'build', i + '.egg-info'):
            for dir in glob.iglob(os.path.join(dist_dir, 'trytond', 'trytond',
                    'modules', '*', j)):
                shutil.rmtree(dir)
        for j in ('.hgtags', '.hgignore'):
            for file in glob.iglob(os.path.join(dist_dir, 'trytond', 'trytond',
                    'modules', '*', j)):
                os.remove(file)

        if os.path.isdir(os.path.join(dist_dir, 'etc')):
            shutil.rmtree(os.path.join(dist_dir, 'etc'))
        shutil.copytree(os.path.join(gtk_dir, 'etc'),
            os.path.join(dist_dir, 'etc'))

        from subprocess import Popen, PIPE
        query_loaders = Popen(os.path.join(gtk_dir,'bin','gdk-pixbuf-query-loaders'),
            stdout=PIPE).stdout.read()
        query_loaders = query_loaders.replace(gtk_dir.replace(os.sep, '/') + '/', '')
        loaders = open(os.path.join(dist_dir, 'etc', 'gtk-2.0', 'gdk-pixbuf.loaders'), 'w')
        loaders.writelines([line + "\n" for line in query_loaders.split(os.linesep)])
        loaders.close()

        if os.path.isdir(os.path.join(dist_dir, 'lib')):
            shutil.rmtree(os.path.join(dist_dir, 'lib'))
        shutil.copytree(os.path.join(gtk_dir, 'lib'),
            os.path.join(dist_dir, 'lib'))

        for file in glob.iglob(os.path.join(gtk_dir, 'bin', '*.dll')):
            if os.path.isfile(file):
                shutil.copy(file, dist_dir)

        for lang in ('de', 'es', 'fr'):
            if os.path.isdir(os.path.join(dist_dir, 'share', 'locale', lang)):
                shutil.rmtree(os.path.join(dist_dir, 'share', 'locale', lang))
            shutil.copytree(os.path.join(gtk_dir, 'share', 'locale', lang),
                os.path.join(dist_dir, 'share', 'locale', lang))

        if os.path.isdir(os.path.join(dist_dir, 'share', 'themes', 'MS-Windows')):
            shutil.rmtree(os.path.join(dist_dir, 'share', 'themes', 'MS-Windows'))
        shutil.copytree(os.path.join(gtk_dir, 'share', 'themes', 'MS-Windows'),
            os.path.join(dist_dir, 'share', 'themes', 'MS-Windows'))

        makensis = find_makensis()
        if makensis:
            from subprocess import Popen
            Popen([makensis, "/DVERSION=" + VERSION,
                str(os.path.join(os.path.dirname(__file__),
                    'setup.nsi'))]).wait()
