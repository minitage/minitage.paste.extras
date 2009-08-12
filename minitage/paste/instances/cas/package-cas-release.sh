#!/usr/bin/env bash

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

cd $(dirname $0)
release=http://www.ja-sig.org/downloads/cas/cas-server-3.3.3-release.tar.gz
tgz=$(basename $release)
name=$(basename $tgz .tar.gz)
[[ ! -f $tgz ]] && wget $release
tar xzf $tgz
cd ${name//-release/}
rm -rf ../release
mkdir ../release
unzip -qqd ../release/  modules/cas-server-webapp-*.war
cp modules/cas-server-*jar ../release/WEB-INF/lib/
cd ..
cp template/var/data/tomcat/cas/webapps/cas/WEB-INF/cas.properties_tmpl release/WEB-INF/cas.properties_tmpl
cp template/var/data/tomcat/cas/webapps/cas/WEB-INF/classes/log4j.properties_tmpl  release/WEB-INF/classes/log4j.properties_tmpl
rm  release/WEB-INF/cas.properties release/WEB-INF/classes/log4j.properties
rm -rf template/var/data/tomcat/cas/webapps/cas/
cp -rf release  template/var/data/tomcat/cas/webapps/cas/

# vim:set et sts=4 ts=4 tw=80:
