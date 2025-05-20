import os
from setuptools import setup, find_packages
setupdir = os.path.abspath(
    os.path.dirname(__file__)
)
os.chdir(setupdir)

name='minitage.paste.extras'
version = '1.12'

def read(rnames):
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name=name,
    version=version,
    description='Extension for minitage.paste allowing users to have some server instaces configured on top of projects sponsored by Makina Corpus',
    download_url='http://distfiles.minitage.org/public/externals/minitage/',
    long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n'
    ),
    classifiers=[
        "Framework :: Django",
        "Framework :: Pylons",
        "Framework :: Paste",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3" ,
        "Framework :: Buildout",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='PasteScripts minitage',
    author='Makina Corpus',
    author_email='freesoftware@makina-corpus.com',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['minitage', 'minitage.paste', 'minitage.paste.instances'],
    include_package_data=True,
    zip_safe=False,
    install_requires = [
                        'PasteScript',
                        'ZopeSkel',
                        'zc.buildout',
                        'pyopenssl',
                        'iniparse',
                        'Cheetah',
                        'minitage.core',
                        'minitage.paste>=1.0.36'],
    #tests_require = ['zope.testing'],
    # merged into django 'minitage.geodjango = minitage.paste.projects.geodjango:Template',
    entry_points = {
        'paste.paster_create_template' : [
            'minitage.instances.tomcat = minitage.paste.instances.tomcat:Template',
            'minitage.instances.cas = minitage.paste.instances.cas:Template',
            'minitage.instances.hudson = minitage.paste.instances.hudson:Template',
            'minitage.instances.openldap = minitage.paste.instances.openldap:Template',

        ]
    },
)

