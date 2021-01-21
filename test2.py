# type: ignore
# pylint: skip-file
# flake8: noqa
from panda3d.core import *
from panda3d.egg import *

import direct.directbase.DirectStart
loadPrcFileData('', 'notify-level spam\ndefault-directnotify-level info')
props = WindowProperties()
props.setCursorHidden(True)
props.setMouseMode(WindowProperties.M_relative)
base.win.requestProperties(props)

base.run()
