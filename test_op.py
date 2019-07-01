import bpy

class Test_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.cursor_center"
    bl_label = "Simple Operator"
    bl_description = "Center 3D Cursor"

    def execute(self,context):
        bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}
