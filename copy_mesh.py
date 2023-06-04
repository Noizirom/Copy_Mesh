import numpy as np
from . object_utils import *




class CopyMesh:
    copy_mesh = None
    info = None
    #
    def __init__(self, object, name, copy_vert_groups=False, copy_vert_group_wts=False, copy_shape_keys=False, copy_shape_key_frame=False, copy_uv=False, collection=None, keep_origin=True) -> None:
        self.object = object
        self.name = name
        self.copy_vert_groups = copy_vert_groups
        self.copy_vert_group_wts = copy_vert_group_wts
        self.copy_shape_keys = copy_shape_keys
        self.copy_shape_key_frame = copy_shape_key_frame
        self.copy_uv = copy_uv
        self.collection = collection
        self.keep_origin = keep_origin
        self.__create()
    #
    def __create(self) -> None:
        self.info = selected_face_to_new(self.object)
        self.copy_mesh = create_ob(self.name, verts=np.add(self.info["NEW"]["VERTS"], np.array(self.object.location)), edges=[], faces=self.info["NEW"]["FACES"], collection=self.collection)
        if self.copy_vert_groups:
            self.__copy_vert_groups()
        if self.copy_shape_keys:
            self.__copy_shape_keys()
        if self.copy_uv:
            # self.__copy_uv()
            pass
        co = get_co(self.copy_mesh)
        origin = np.array(self.object.location)
        if not self.keep_origin:
            new_origin = centroid(co)
            new_co = np.subtract(co, new_origin)
            set_co(self.copy_mesh, new_co)
            self.copy_mesh.location = new_origin
        if self.keep_origin:
            co = np.subtract(co, origin)
            set_co(self.copy_mesh, co)
            self.copy_mesh.location = origin
        return
    #
    def __copy_vert_groups(self):
        verts = self.info["OLD"]["VERTS"]
        converter = self.info["CONVERSION"]
        vert_group_data = get_vertex_groups_idxs(self.object)
        set_copy_vertex_groups_idxs(self.copy_mesh, verts, converter, vert_group_data)
        if self.copy_vert_group_wts:
            weights = get_vertex_groups_wts(self.object)
            set_copy_vertex_groups_wts(self.copy_mesh, verts, weights)
        return
    #
    def __copy_shape_keys(self):
        key_block_data = get_shape_keys(self.object)
        keys = np.array([k for k in key_block_data.keys()])
        for sk in keys:
            data = key_block_data[sk]
            shape_key = self.copy_mesh.shape_key_add(from_mix=True)
            shape_key.name = sk
            shape_key.interpolation = data["interpolation"]
            shape_key.relative_key = data["relative_key"]
            shape_key.value = data["value"]
            shape_key.slider_min = data["slider_min"]
            shape_key.slider_max = data["slider_max"]
            shape_key.vertex_group = data["vertex_group"]
            if self.copy_shape_key_frame:
                shape_key.frame = data["frame"]
            for i, co in enumerate(data["co"][self.info["OLD"]["VERTS"]]):
                shape_key.data[i].co = co
        return
    #
    def __copy_uv(self):
        # TODO: arange uv points better
        __layer = self.object.data.uv_layers
        __count = len(__layer)
        names = [i.name for i in __layer]
        for uv in range(__count):
            try:
                co = get_uv_co(self.object, uv=uv)[self.info["OLD"]["VERTS"]]
                nl = self.copy_mesh.data.uv_layers.new(name=names[uv])
                layer = self.copy_mesh.data.uv_layers[uv]
                for i, v in enumerate(co):
                    layer.uv[i].vector = v
            except Exception as e:
                print(f"{e} <> {uv} : {names[uv]}")
            finally:
                continue
        return









