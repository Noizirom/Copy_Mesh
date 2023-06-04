import bpy
from . copy_mesh import CopyMesh
from . object_utils import get_collection
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.props import (StringProperty,
                       BoolProperty,
                       FloatProperty,
                       PointerProperty
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Function
# ------------------------------------------------------------------------


#Create the Copy Face Object
def copy_object(self, context):
    ob = context.object
    copy_ob = CopyMesh(
                        ob, 
                        context.scene.copy_mesh.obj_name, 
                        copy_vert_groups=context.scene.copy_mesh.add_vg_bool, 
                        copy_vert_group_wts=context.scene.copy_mesh.add_vg_wts_bool, 
                        copy_shape_keys=context.scene.copy_mesh.add_sk_bool, 
                        copy_shape_key_frame=context.scene.copy_mesh.add_sk_frame_bool, 
                        copy_uv=False, 
                        collection=get_collection(context.scene.copy_mesh.coll_name),
                        keep_origin=context.scene.copy_mesh.keep_origin_bool)
   

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class FC_Properties(PropertyGroup):

    add_vg_bool: BoolProperty(
        name="Copy Vertex Groups",
        description="Copy Vertex Groups",
        default = False
        )

    add_vg_wts_bool: BoolProperty(
        name="Copy Vertex Group Weights",
        description="Copy Vertex Groups Weights",
        default = False
        )

    add_sk_bool: BoolProperty(
        name="Copy Shape Keys",
        description="Copy Shape Keys",
        default = False
        )

    add_sk_frame_bool: BoolProperty(
        name="Copy Shape Key Frames",
        description="Copy Shape Key Frames",
        default = False
        )

    keep_origin_bool: BoolProperty(
        name="Use Object Origin",
        description="Use object origin or place origin at center of copy mesh",
        default = True
        )

    use_coll_bool: BoolProperty(
        name="Use Object Custom Collection",
        description="Use collection other than object collection to store copy mesh",
        default = False
        )

    obj_name: StringProperty(
        name="name",
        description="Enter the Object Name",
        default="Object",
        maxlen=1024,
        )

    coll_name: StringProperty(
        name="collection",
        description="Enter the Object Collection",
        default="",
        maxlen=1024,
        )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class OBJECT_OT_copy_mesh(Operator):
    """Create a new Object from selected faces"""
    bl_idname = "mesh.copy_mesh"
    bl_label = "Add Copy Mesh"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        copy_object(self, context)
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class OBJECT_PT_CopyMeshPanel(Panel):
    bl_idname = "object.copy_mesh_panel"
    bl_label = "Copy Mesh"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Copy_Mesh"
    
    @classmethod
    def poll(self,context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        copymesh = scene.copy_mesh

        layout.prop(copymesh, "add_vg_bool")
        (layout.prop(copymesh, "add_vg_wts_bool") if context.scene.copy_mesh.add_vg_bool else None)
        layout.prop(copymesh, "add_sk_bool")
        (layout.prop(copymesh, "add_sk_frame_bool") if context.scene.copy_mesh.add_sk_bool else None)
        layout.prop(copymesh, "keep_origin_bool")
        layout.prop(copymesh, "use_coll_bool")
        (layout.prop(copymesh, "coll_name") if context.scene.copy_mesh.use_coll_bool else None)
        layout.prop(copymesh, "obj_name")
        layout.operator("mesh.copy_mesh")
        layout.separator()



# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    FC_Properties,
    OBJECT_OT_copy_mesh,
    OBJECT_PT_CopyMeshPanel,
)



def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.copy_mesh = PointerProperty(type=FC_Properties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.copy_mesh


if __name__ == "__main__":
    register()