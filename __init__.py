found_blender = False
try:
    import bpy
    from . network_operators import BCONNECT_OT_control
    from . network_ui import BCONNECT_PT_panel
    found_blender = True
except:
    pass

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



if found_blender:
    class BlenderConnectSettings(bpy.types.PropertyGroup):
        log_network : bpy.props.BoolProperty(name="log the textual network-traffic")

    classes =(BCONNECT_OT_control, BCONNECT_PT_panel,BlenderConnectSettings)

    defRegister, defUnregister = bpy.utils.register_classes_factory(classes)

def register():
    defRegister()
    bpy.types.World.blender_connect_settings = bpy.props.PointerProperty(type=BlenderConnectSettings)

def unregister():
    defUnregister()
    del bpy.types.World.blender_connect_settings
    