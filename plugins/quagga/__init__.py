import logging, interfaces, os
from StringIO import StringIO
from datetime import datetime

class Quagga(interfaces.IOpenMesherConfigPlugin):
    def activate(self):
        self._register('quagga/zebra.conf')
        self._register('quagga/ripd.conf')
    
    def setupargs(self, parser):
        parser.add_argument('--password', action='store', help='Specify quagga password')
        parser.add_argument('--enable-password', action='store', help='Specify quagga enable password')
    
    def process(self, mesh, cliargs = None):
        logging.debug('Generating Quagga config...')
        self._quaggafiles = {}
        
        for router in mesh.links:
            self._files[router] = {}
            configtime = datetime.strftime(datetime.now(), '%A, %d %B %Y %H:%M:%S -0800')
            if cliargs.password and cliargs.enable_password:
                zpw = cliargs.password
                zepw = cliargs.enable_password
            elif cliargs.password and not cliargs.enable_password:
                zpw = cliargs.password
                zepw = cliargs.password
            elif cliargs.enable_password and not cliargs.password:
                zp = cliargs.enable_password
                zepw = cliargs.enable_password
            else:
                logging.warn("You did not provide a password or enable password for quagga, using the default 'secret123' for router %s" %(router))
                zpw = 'secret123'
                zepw = 'secret123'
            
            self._files[router]['/quagga/zebra.conf'] = self._templates['quagga/zebra.conf'].render(
                gentime=configtime,
                password=zpw,
                enablepassword=zepw,
                router=router,
            )
            
            self._files[router]['/quagga/ripd.conf'] = self._templates['quagga/ripd.conf'].render(
                gentime=configtime,
                password=zpw,
                enablepassword=zepw,
                router=router,
                links=mesh.links[router]
            )

