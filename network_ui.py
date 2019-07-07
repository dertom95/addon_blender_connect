import bpy

class Test_PT_Panel(bpy.types.Panel):
    bl_idname = "Test_PT_Panel"
    bl_label = "Test panel"
    bl_category = "Test Addon"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.operator("view3d.cursor_center",text="Center 3D cursor")

class BCONNECT_PT_panel(bpy.types.Panel):
    bl_idname = "BCONNECT_PT_panel"
    bl_label = "Blender Connect"
    bl_category = "BConnect"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.operator("bconnect.control",text="start network").mode="start"        
        row.operator("bconnect.control",text="stop network").mode="stop"        
        row = layout.row()
        row.operator("bconnect.control",text="test").mode="test"        
