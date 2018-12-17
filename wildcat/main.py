import sys
import os
import time
import logging
import traceback
import ctypes
from PySide2.QtWidgets import QApplication
from .wildcat import MainWindow

def _log_uncaught_exceptions(ex_cls, ex, tb):
    logging.debug(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
    logging.debug(''.join(traceback.format_tb(tb)))
    logging.debug('{0}: {1}\n'.format(ex_cls, ex))


def run_app():
    """Main entry point for starting application"""
    # fix to allow icon to show up in Windows
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # logging
    save_dir = os.path.abspath(os.path.expanduser('~/Desktop'))
    save_path = os.path.join(save_dir, 'error.log')
    logging.basicConfig(level=logging.DEBUG, filename=save_path,
                        filemode='w')

    sys.excepthook = _log_uncaught_exceptions

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())