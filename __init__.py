bl_info = {
    "name": "Blender Connect",
    "description": "Connect to a special ZMQ-Node for communicating with the outer world",
    "author": "Thomas Trocha",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }

import bpy

from . test_op import Test_OT_Operator
from . test_panel import Test_PT_Panel
from . network import PubSubNetwork,StartNetwork

StartNetwork()

classes =(Test_OT_Operator, Test_PT_Panel)

register, unregister = bpy.utils.register_classes_factory(classes)
    