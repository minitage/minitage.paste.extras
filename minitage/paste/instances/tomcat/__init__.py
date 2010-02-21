# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


__docformat__ = 'restructuredtext en'

import os
import stat
import getpass
import pwd
import grp
import re
import ConfigParser
import subprocess
import sys
import shutil
import xml.dom.minidom
import pkg_resources

from distutils.dir_util import copy_tree

from minitage.paste.instances import common, ssl
from minitage.core.common import remove_path, which, search_latest
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S
special_chars_re = re.compile('[-._@|{(\[|)\]}]', re_flags)
running_user = getpass.getuser()
version = '6.0.24'

class Template(common.Template):

    summary = 'Template for creating a tomcat instance'
    _template_dir = 'template'
    use_cheetah = True
    pg_present = False
    required_templates = ['minitage.instances.env']
    tomcat_vars = [
            templates.var('catalina_home', 'Path to the tomcat install',  default = ''),
            templates.var('tomcat_instance', 'tomcat instance name(without spaces or special chars', default = ''),
            templates.var('user', 'Default user',  default = common.running_user),
            templates.var('password', 'Default user password', default = 'secret'),
            templates.var('host', 'Host to listen on', default = 'localhost'),
            templates.var('ajp_port', 'Port to listen to for ajp connection', default = '8009'),
            templates.var('ssl_port', 'Port to listen to for ssl connection', default = '8443'),
            templates.var('tomcat_port', 'Port to listen to for tomcat', default = '8005'),
            templates.var('http_port', 'Port to listen to for http connection', default = '8080'),
            templates.var('admin_user', 'Tomcat administrator', default = running_user),
            templates.var('admin_password', 'Tomcat administrator password', default = 'secret'),
        ]

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['running_user'] = running_user
        vars['catalina_base'] = os.path.join(
            vars['sys'],
            'var',
            'data',
            'tomcat',
            vars['tomcat_instance'],
        )

    def post(self, command, output_dir, vars):
        # symlink conf, and logs directories inside $sys
        print
        print
        dirs = [os.path.join(vars['sys'], 'bin'),
                os.path.join(vars['sys'], 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)

        conf = os.path.join(
            vars['sys'],
            'var', 'data',
            'tomcat',
            vars['tomcat_instance'],
            'conf'
        )
        logs = os.path.join(
            vars['sys'],
            'var', 'data',
            'tomcat',
            vars['tomcat_instance'],
            'logs'
        )
        dconf = os.path.join(
            vars['sys'],
            'etc',
            'tomcat',
            vars['tomcat_instance']
        )
        dlogs = os.path.join(
            vars['sys'],
            'var',
            'log',
            'tomcat',
            vars['tomcat_instance'],
        )
        for p in dlogs, dconf:
            if os.path.exists(p):
                remove_path(p)
        os.symlink(conf, dconf)
        os.symlink(logs, dlogs)
        keysp = os.path.join(
            os.path.dirname(conf),
            'keys'
        )
        if not os.path.exists(keysp):
            os.makedirs(keysp)
        ssl.generate_prefixed_ssl_bundle(vars, vars['tomcat_instance'])
        README = '\n\n%s' % (
            "Installation is now finished.\n"
            "------------------------------\n"
            "\n"
            " * You can find an init script to lunach your tomcat instance in %s/etc/init.d/%s_%s.%s.\n"
            " * Your CATALINA_BASE is installed in %s.\n"
            " * wrappers for various tomcat script have been isntalled in %s/bin.\n"
            "    * %s\n"
            " * logs are in %s/var/log/tomvat/cas\n"
            " * symlinks for the configuration directory have been made into %s/etc.\n"
            "\n" % (
                vars['sys'],
                vars['project'],
                vars['project'],
                vars['tomcat_instance'],
                os.path.dirname(conf),
                vars['sys'],
                ',  '.join (
                    [a
                     for a in os.listdir(os.path.join(vars['sys'], 'bin'))
                     if 'tomcat_%s' % vars['tomcat_instance'] in a]
                ),
                vars['sys'],
                vars['sys'],
            )
        )

        for app in ['ROOT', 'manager', 'host-manager']:
            o = os.path.join(vars['catalina_home'], 'webapps', app)
            d = os.path.join(vars['catalina_base'], 'webapps', app)
            msg =  " * Copying %s application from %s.\n" % (app, o)
            README += msg
            copy_tree(o, d)
        if vars['inside_minitage']:
            README += '\n%s' % (
                "Please verify that tomcat-%s is in your minibuild's dependencies\n"
                "---------------------------------------------------------------------\n"
                "If not, please add it and run the following commands:\n"
                " minimerge -v tomcat-%s\n"
                " source %s/share/minitage/minitage.env\n"
                " $MT/paster create -t minitage.instances.env %s\n"
                "\n" % (version, version, vars['sys'], vars['project'])
            )
        readmep = os.path.join(vars['path'], 'README.tomcat.%s' % vars['tomcat_instance'])
        print README
        print "Those informations have been saved in %s" % readmep
        open(readmep, 'w').write(README)

        self.write_config(vars)

    def read_vars(self, command=None):
        vars = templates.Template.read_vars(self, command)
        print '!' * 80
        print ' Think to add a tomcat minibuild to your minibuild as dependency'
        print ' before trying to run this paster.'
        print '!' * 80
        myname = special_chars_re.sub('', command.args[0])
        for i, var in enumerate(vars[:]):
            if var.name in ['tomcat_instance']:
                vars[i].default = myname
            if var.name in ['catalina_home']:
                if os.path.exists(
                    os.path.join(sys.prefix, 'etc', 'minimerge.cfg')
                ):
                    vars[i].default = os.path.join(
                        sys.prefix,
                        'dependencies',
                        'tomcat-%s' % version,
                        'parts',
                        'part'
                    )
        return vars

    def write_config(self, vars):
        path = get_tomcat_config_path(self, vars)
        config = ConfigParser.ConfigParser()
        if os.path.exists(path):
            config.read(path)
        # set a number of parameters
        s = vars['tomcat_instance']
        if not config.has_section(s):
            config.add_section(s)
        for opt in self.tomcat_vars:
            config.set(s, opt.name, vars.get(opt.name, ''))
        fic = open(path, 'w')
        config.write(fic)
        fic.flush()
        fic.close()

def get_tomcat_config_path(self, vars):
    path = os.path.join(
        vars['sys'],
        'var', 'data', 'tomcat', 'tomcats.cfg'
    )
    return path

Template.required_templates = ['minitage.instances.env']
gid = pwd.getpwnam(running_user)[3]
#group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + Template.tomcat_vars + ssl.SSL_VARS


class TomcatAppBaseTemplate(common.Template):

    required_templates = []
    webapp_type = 'tomcat_webapp'
    summary = 'Template for creating a %s application inside a tomcat' % webapp_type

    def __init__(self, *args, **kwargs):
        self.vars =  common.Template.vars + [\
                      templates.var(
                          'tomcat_instance',
                          'tomcat instance to drop the instance inside',
                          default = ''),
                      templates.var('webapp_name',
                                    'tomcat instance to drop the instance inside',
                                    default = self.webapp_type),
                     ]
        common.Template.__init__(self, *args, **kwargs)

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['webapp_type'] = self.webapp_type
        path = get_tomcat_config_path(self, vars)
        config = ConfigParser.ConfigParser()
        if os.path.exists(path):
            config.read(path)
            for o in  config.options(vars['tomcat_instance']):
                vars[o] = config.get(vars['tomcat_instance'], o)
        else:
            print 'Please install a tomcat instance named "%s" prior to run this paster.' % vars['tomcat_instance']
            print '   EG: %s create -t minitage.instances.tomcat %s tomcat_instance=%s'  % (
                sys.argv[0],
                vars['project'] ,
                vars['tomcat_instance']
            )
            sys.exit(-1)

    def post(self, command, output_dir, vars):
        # symlink conf, and logs directories inside $sys
        print
        README = '\n\n%s' % (
            "Installation is now finished.\n"
            "------------------------------\n"
        )
        if vars['inside_minitage']:
            README += '\n%s' % (
                "Please verify that tomcat-%s is in your minibuild's dependencies\n"
                "---------------------------------------------------------------------\n"
                "If not, please add it and run the following commands:\n"
                " minimerge -v tomcat-%s\n"
                " source %s/share/minitage/minitage.env\n"
                " $MT/paster create -t minitage.instances.env %s\n"
                "\n" % (version, version, vars['sys'], vars['project'])
            )
        README += '%s'% (
                "\n-------------------------------------------------------------------------------------------------------\n"
            " * %s is installed under %s"
            "\n-------------------------------------------------------------------------------------------------------\n"
            ""% (
                self.webapp_type.upper(),
                os.path.join(vars['sys'],
                            'var',
                            'tomcat',
                            vars['tomcat_instance'],
                            'webapps', vars['webapp_name']
                           )
            )
        )
        readmep = os.path.join(vars['path'], 'README.tomcat.%s' % (self.webapp_type))
        print README
        print "Those informations have been savec in %s" % readmep
        open(readmep, 'w').write(README)

    def read_vars(self, command=None):
        vars = templates.Template.read_vars(self, command)
        print '!' * 80
        print ' Think to add a tomcat minibuild to your minibuild as dependency'
        print ' before trying to run this paster.'
        print '!' * 80
        myname = special_chars_re.sub('', command.args[0])
        for i, var in enumerate(vars[:]):
            if var.name in ['tomcat_instance']:
                vars[i].default = myname
        return vars

# vim:set et sts=4 ts=4 tw=0:
