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
import subprocess
import sys
import shutil
import xml.dom.minidom
import pkg_resources

from distutils.dir_util import copy_tree

from minitage.paste.instances import common, tomcat
from minitage.core.common import remove_path, which, search_latest
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S
running_user = getpass.getuser()

def get_hudson_version():
    version_file = pkg_resources.resource_filename(
        'minitage.paste.instances.hudson',
        'template/var/data/tomcat/'
        '+tomcat_instance+/webapps/+webapp_name+/META-INF/'
        'maven/org.jvnet.hudson.main/hudson-war/pom.xml')
    doc = xml.dom.minidom.parse(version_file)
    for node in doc.getElementsByTagName('parent'):
        for gnode in node.getElementsByTagName('groupId'):
            if gnode.firstChild.nodeValue == 'org.jvnet.hudson.main':
                return node.getElementsByTagName('version')[0].firstChild.nodeValue


hudson_version = get_hudson_version()

class Template(tomcat.TomcatAppBaseTemplate):

    summary = 'Template for creating a HUDSON(v%s) application in an existing running tomcat instance' % hudson_version
    webapp_type = 'hudson'
    _template_dir = 'template'
    use_cheetah = True

    def __init__(self, *args, **kwargs):
        tomcat.TomcatAppBaseTemplate.__init__(self, *args, **kwargs)
        self.vars += [templates.var('hudson_irc_support', 'hudson irc support (true or false)', default = 'true'),
                       templates.var('hudson_irc_server', 'hudson irc server to join', default = 'irc.freenode.net'),
                       templates.var('hudson_irc_port', 'hudson irc server port', default = '6667'),
                       templates.var('hudson_irc_nick', 'hudson irc nickname', default = 'hudson'),
                       templates.var('hudson_irc_channels', 'comma separated list of channels to join ', default = '#hudson-test'),
                       templates.var('hudson_email_from', 'comma separated list of channels to join ', default = 'hudson <foo@localhost>'),
                       templates.var('hudson_url', 'Hudson accessible url for notificiation (mails, irc)', default = 'http://foo:8080/hudson')
                      ]

    def read_vars(self, command=None):
        vars = tomcat.TomcatAppBaseTemplate.read_vars(self, command)
        myname = tomcat.special_chars_re.sub('', command.args[0])
        for i, var in enumerate(vars[:]):
            if var.name in ['hudson_email_from']:
                vars[i].default = '%s <%s@localhost>' % (myname, myname)
            if var.name in ['hudson_irc_nick']:
                vars[i].default = myname
            if var.name in ['hudson_irc_channels']:
                vars[i].default = '#%s' % (myname)
        return vars                     

    def pre(self, command, output_dir, vars):
        tomcat.TomcatAppBaseTemplate.pre(self, command, output_dir, vars)
        vars['hudson_email_from'] = vars['hudson_email_from'].replace('<', '&lt;').replace('>', '&gt;')
        vars['hudson_home'] = os.path.join(
            vars['sys'], 'var', 'data', 'hudson',
            vars['tomcat_instance'], vars['webapp_name']
        )

    def post(self, command, output_dir, vars):
        tomcat.TomcatAppBaseTemplate.post(self, command, output_dir, vars)
        # symlink conf, and logs directories inside $sys
        README = '%s'% (
            "-------------------------------------------------------------------------------------------------------\n"
            " * hudson home has been set in web.xml with value: %s!\n"
            "-------------------------------------------------------------------------------------------------------\n"
        % (vars['hudson_home']) )
        readmep = os.path.join(vars['path'], 'README.tomcat.%s_%s' % (self.webapp_type, vars['webapp_name']))
        print README
        print "Those informations have been savec in %s" % readmep
        open(readmep, 'w').write(README)

# vim:set et sts=4 ts=4 tw=0:
