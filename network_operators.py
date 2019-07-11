import bpy
from . BConnectNetwork import StartNetwork,StopNetwork,AddListener,Publish

class Test_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.cursor_center"
    bl_label = "Simple Operator"
    bl_description = "Center 3D Cursor"

    def execute(self,context):
        bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}


class BCONNECT_OT_control(bpy.types.Operator):
    bl_idname = "bconnect.control"
    bl_label = "control the blender connect network"
    bl_description = "control the blender connect network"

    mode : bpy.props.StringProperty()

    def caller(self,topic,data):
        print("CALLER:%s %s"%(topic,data))

    def execute(self,context):
        print("type:%s" % self.mode)
        if self.mode == "start":
            StartNetwork()
        elif self.mode == "stop":
            StopNetwork()
        elif self.mode == "test":
            AddListener(b"runtime",self.caller)

        bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}        



