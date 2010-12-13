#!/usr/bin/env python
import datetime
from tunnelobjects import *
from StringIO import StringIO

def makedebs(mesh, include_dirs = '', restart_services = ''):
    print 'Generating deb configs...'
    dpkgfiles = {}
    for router in mesh.routers:
        dpkgfiles[router] = {}
        changelog_date = datetime.datetime.strftime(datetime.datetime.now(), '%A, %d %B %Y %H:%M:%S -0800')
        
        changelog = StringIO()
        #TODO: Need way to bump pkg version number for easier inclusion into repositories for auto-update
        changelog.write('%s (1.0) stable; urgency=low\n' %(mesh.routers[router].hostname.lower()))
        changelog.write('\n')
        changelog.write('  * OpenMesher Package for %s\n' %(mesh.routers[router].fqdn))
        changelog.write('\n')
    #       BUG: %z doesn't work for some dumb reason: http://www.aczoom.com/blog/ac/2007-02-24/strftime-in-python
    #        changelog_date = datetime.datetime.strftime(datetime.datetime.utcnow(), '%A, %d %B %Y %H:%M:%S +%z')
        changelog.write(' -- Aaron C. de Bruyn <aaron@heyaaron.com>  %s\n' %(changelog_date))
        changelog.write('\n')
        dpkgfiles[router]['/debian/changelog'] = changelog.getvalue()
        
        compat = StringIO()
        compat.write('8\n')
        dpkgfiles[router]['/debian/compat'] = compat.getvalue()
        
        control = StringIO()
        control.write('Source: %s\n' %(mesh.routers[router].hostname.lower()))
        control.write('Maintainer: Aaron C. de Bruyn <aaron@heyaaron.com>\n')
        control.write('\n')
        control.write('Package: %s\n' %(mesh.routers[router].hostname.lower()))
        control.write('Architecture: all\n')
        control.write('Depends: openvpn, quagga\n')
        control.write('Description: OpenMesher config files for %s\n' %(mesh.routers[router].fqdn))
        control.write(' This package was automatically generated by OpenMesher\n')
        control.write(' on %s\n' %(changelog_date))
        dpkgfiles[router]['/debian/control'] = control.getvalue()
        
        rules = StringIO()
        rules.write('#! /bin/sh -e\n')
        rules.write('dh_testdir\n')
        rules.write('dh_testroot\n')
        rules.write('dh_prep\n')
        rules.write('dh_installdirs\n')
        #BUG: Need to figure out which files need to be installed from various tunnelobjects.make* classes
        if 'ezri' in router.lower():
            rules.write('dh_install openvpn /etc/\n')
        else:
            for include_dir in include_dirs:
                rules.write('dh_install %s /etc/\n' %(include_dir))

        rules.write('dh_fixperms\n')
        rules.write('find -name "*.key" | xargs chmod 400\n')
        rules.write('dh_installdeb\n')
        rules.write('dh_gencontrol\n')
        rules.write('dh_md5sums\n')
        rules.write('dh_builddeb --filename=%s.deb\n' %(mesh.routers[router].hostname.lower()))
        dpkgfiles[router]['/debian/rules'] = rules.getvalue()
        
        postinst = StringIO()
        postinst.write('#!/bin/sh\n')
        for service in restart_services:
            postinst.write('if [ -x "/etc/init.d/%s" ]; then\n' %(service))
            postinst.write('        if [ -x /usr/sbin/invoke-rc.d ]; then\n')
            postinst.write('           invoke-rc.d %s restart\n' %(service))
            postinst.write('        else\n')
            postinst.write('           /etc/init.d/%s restart\n' %(service))
            postinst.write('        fi\n')
            postinst.write('fi\n')
        if not 'ezri' in router.lower():
            dpkgfiles[router]['/debian/postinst'] = postinst.getvalue()
    
    return dpkgfiles

