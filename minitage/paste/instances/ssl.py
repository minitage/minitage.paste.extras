
import os
import sys
import getpass

from minitage.paste.instances import common

from OpenSSL.crypto import TYPE_RSA, TYPE_DSA, Error, PKey, PKeyType
from OpenSSL.crypto import X509, X509Type, X509Name, X509NameType
from OpenSSL.crypto import X509Req, X509ReqType
from OpenSSL.crypto import X509Extension, X509ExtensionType
from OpenSSL.crypto import load_certificate, load_privatekey
from OpenSSL.crypto import FILETYPE_PEM, FILETYPE_ASN1, FILETYPE_TEXT
from OpenSSL.crypto import dump_certificate, load_certificate_request
from OpenSSL.crypto import dump_certificate_request, dump_privatekey

from paste.script import templates
running_user = getpass.getuser()

def dump_write(content, dump_path):
    f = open(dump_path, 'w')
    f.write(content)
    f.close()

def set_x509(kw, xname = None):
    if not xname:
        # XXX There's no other way to get a new X509Name yet.
        xname = X509().get_subject()

    xname.countryName = kw['C']
    xname.stateOrProvinceName = kw['ST']
    xname.localityName = kw['L']
    xname.organizationName = kw['O']
    xname.organizationalUnitName = kw['OU']
    xname.emailAddress = kw['emailAddress']
    xname.commonName = kw['CN']

    return xname

def set_x509_serv(xname=None, vars = None):
    kw = {
         'C':'FR',
         'ST':'StateServ',
         'L':'NantesServ',
         'O':'OrgServ',
         'OU':'UnitServ',
         'emailAddress':'dj.coin@laposte.net',
         }
    kw['CN'] = vars.get('host', 'servcas')
    for var in kw:
        key = 'ssl_server_%s' % var
        if key in vars:
            kw[var] = vars[key]
    return set_x509(kw, xname)

def set_x509_ca(xname=None, vars = None):
    kw = {
        'C':'FR',
        'ST':'StateCA',
        'L':'TownCa',
        'O':'OrgCA',
        'OU':'UnitCA',
        'emailAddress':'foo@foo.com',
    }
    kw['CN'] = vars.get('host', 'localhost')
    for var in kw:
        key = 'ssl_ca_%s' % var
        if key in vars:
            kw[var] = vars[key]
    return set_x509(kw, xname)

def generate_prefixed_ssl_bundle(vars, name):
    spath = os.path.join(vars['sys'], 'etc' , 'ssl')
    make_certificate(
        os.path.join(spath, 'certs', '%s-ca.crt' % (name)),
        os.path.join(spath, 'private', '%s-ca.key' % (name)),
        os.path.join(spath, 'certs', '%s-server.crt' % (name)),
        os.path.join(spath, 'private', '%s-server.key' % (name)),
        vars=vars
    )

def make_certificate(
    ca_crt_path = 'ca.crt',
    ca_key_path = 'ca.key',
    server_crt_path = 'server.crt',
    server_key_path  = 'server.key',
    vars=None):

    # make the certificat of CA
    # need passphrase ?
    ca_key = PKey()
    ca_key.generate_key(TYPE_RSA, 1024)
    dump_write(dump_privatekey(FILETYPE_PEM, ca_key),
               ca_key_path)

    # MAKE THE CA SELF-SIGNED CERTIFICATE
    cert =  X509()
    sub = cert.get_subject()
    set_x509_ca(sub, vars=vars)

    #FORMAT : YYYYMMDDhhmmssZ
    after =  '20200101000000Z'
    before = '20090101000000Z'
    cert.set_notAfter(after)
    cert.set_notBefore(before)

    cert.set_serial_number(1)
    cert.set_pubkey(ca_key)
    cert.set_issuer(cert.get_subject())

    cert.sign(ca_key,"MD5")
    dump_write(dump_certificate(FILETYPE_PEM, cert),
               ca_crt_path)
    print "Generated CA certificate in %s" % ca_crt_path

    # MAKE THE SERVER CERTIFICATE
    s_key = PKey()
    s_key.generate_key(TYPE_RSA, 1024)
    dump_write(dump_privatekey(FILETYPE_PEM, s_key),
               server_key_path)
    s_cert = X509()
    s_sub = s_cert.get_subject()
    set_x509_serv(s_sub, vars=vars)

    #FORMAT : YYYYMMDDhhmmssZ
    after =  '20200101000000Z'
    before = '20090101000000Z'
    s_cert.set_notAfter(after)
    s_cert.set_notBefore(before)

    s_cert.set_serial_number(2)
    s_cert.set_pubkey(s_key)
    s_cert.set_issuer(cert.get_subject())

    s_cert.sign(ca_key,"MD5")
    dump_write(dump_certificate(FILETYPE_PEM, s_cert),
               server_crt_path)
    print "Generated Server certificate in %s" % server_crt_path
    for p in [ca_key_path, server_key_path]:
        os.chmod(p, 0600)




SSL_VARS = [
    templates.var('ssl_ca_C', 'SSL Ca Country', default = 'FR'),
    templates.var('ssl_ca_L', 'SSL Ca town', default = 'Paris'),
    templates.var('ssl_ca_ST', 'SSL Ca state', default = 'CaState'),
    templates.var('ssl_ca_O', 'SSL Ca Organization', default = 'organizationCorp'),
    templates.var('ssl_ca_OU', 'SSL Ca Unit', default = 'SpecialUnit'),
    templates.var('ssl_ca_emailAddress', 'SSL Ca email', default = '%s@localhost'%running_user),
    templates.var('ssl_server_C', 'SSL Server Country', default = 'FR'),
    templates.var('ssl_server_L', 'SSL Server town', default = 'Paris'),
    templates.var('ssl_server_ST', 'SSL Server state', default = 'ServerState'),
    templates.var('ssl_server_O', 'SSL Server Organization', default = 'organizationCorp'),
    templates.var('ssl_server_OU', 'SSL Server Unit', default = 'SpecialUnit'),
    templates.var('ssl_server_emailAddress', 'SSL Server email',
                  default = '%s@localhost' % ( running_user)
                 ),
]
