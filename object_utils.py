import bpy
import numpy as np

###################
# MATH
###################

def centroid(co):
    if not isinstance(co, np.ndarray):
        co = np.array(co)
    return co.mean(0)


###################
# COLLECTIONS
###################


def if_collection_exists(Name):
    if bpy.data.collections.get(Name):
        return True
    return False


def get_collection(Name, collection=None):
    if not Name:
        return
    try:
        if if_collection_exists(Name):
            return bpy.data.collections.get(Name)
        coll = bpy.data.collections.new(Name)
        if collection==None:
            collection = bpy.context.collection
        collection.children.link(coll)
        return coll
    except Exception as e:
        print(e)
        return


###################
# OBJECT
###################


def new_mesh(Name, verts=[], edges=[], faces=[]):
    mesh = bpy.data.meshes.new(Name)
    mesh.from_pydata(verts, edges, faces)
    return mesh


def new_object(Name, mesh_data):
    ob = bpy.data.objects.new(Name, mesh_data)
    return ob


def link_ob(ob, collection=None):
    if not collection:
        collection = bpy.context.collection
    collection.objects.link(ob)
    return ob


def create_ob(Name, verts=[], edges=[], faces=[], collection=None):
    mesh_data = new_mesh(Name, verts, edges, faces)
    ob = new_object(Name, mesh_data)
    link_ob(ob, collection=collection)
    return ob


def get_co(ob):
    vt = ob.data.vertices
    ct = len(vt)
    co = np.empty(ct*3)
    vt.foreach_get('co', co)
    return co.reshape((ct, 3))


def set_co(ob, co):
    vt = ob.data.vertices
    co = co.ravel()
    vt.foreach_set('co', co)
    return 


def get_selected_verts(ob):
    vt = ob.data.vertices
    ct = len(vt)
    sel = np.zeros(ct, bool)
    vt.foreach_get('select', sel)
    return sel


def get_face_select(ob):
    faces = ob.data.polygons
    ct = len(faces)
    co = np.empty(ct, bool)
    faces.foreach_get('select', co)
    return co


def get_face_verts(ob):
    return np.array([np.array(i.vertices[:]) for i in ob.data.polygons], dtype=object)


def old_new_vert_dict(verts):
    return {o: n for n, o in enumerate(verts)}


def selected_face_to_new(ob):
    sel = get_face_select(ob)
    selected = get_face_verts(ob)[sel]
    verts = np.arange(len(ob.data.vertices))[get_selected_verts(ob)]
    s = selected.copy()
    new = old_new_vert_dict(verts)
    for f in range(selected.shape[0]):
        ct = selected[f].shape[0]
        n = np.empty(ct).astype(int)
        for i in range(ct):
            n[i] = new[selected[f][i]]
        s[f] = n
    return {"OLD": {"VERTS": verts, "FACES": selected}, "NEW": {"VERTS": get_co(ob)[verts], "FACES": s}, "CONVERSION": new}

###################
# UV
###################

def get_uv_co(ob, uv=0):
    layer = ob.data.uv_layers[uv]
    ct = len(layer.uv)
    co = np.empty(ct*2)
    layer.uv.foreach_get("vector", co)
    return co.reshape((ct, 2))


def set_uv_co(ob, co, uv=0):
    layer = ob.data.uv_layers[uv]
    layer.uv.foreach_set("vector", co.ravel())
    return

###################
# SHAPE KEYS
###################

def get_shape_keys(ob):
    shape_key_dict = {}
    if ob.data.shape_keys:
        key_blocks = ob.data.shape_keys.key_blocks
        vertices = ob.data.vertices
        count = len(key_blocks)
        vcount = len(vertices)
        co = np.empty(vcount*3)
        names = np.array([kb.name for kb in key_blocks])
        interpolations = np.array([kb.interpolation for kb in key_blocks])
        relative_keys = np.array([kb.relative_key for kb in key_blocks])
        vertex_groups = np.array([kb.vertex_group for kb in key_blocks])
        values = np.empty(count)
        slider_min = values.copy()
        slider_max = values.copy()
        frames = values.copy()
        key_blocks.foreach_get("value", values)
        key_blocks.foreach_get("slider_min", slider_min)
        key_blocks.foreach_get("slider_max", slider_max)
        key_blocks.foreach_get("frame", frames)
        for sk in range(count):
            data = key_blocks[sk].data
            sco = co.copy()
            data.foreach_get("co", sco)
            shape_key_dict.update({
                                names[sk]: {
                                "co":            sco.reshape((vcount, 3)),
                                "interpolation": interpolations[sk],
                                "relative_key":  relative_keys[sk],
                                "value":         values[sk],
                                "slider_min":    slider_min[sk],
                                "slider_max":    slider_max[sk],
                                "frame":         frames[sk],
                                "vertex_group":  vertex_groups[sk],
                                }})
    return shape_key_dict


def set_shape_keys(ob, key_block_data, use_frame=False):
    keys = np.array([k for k in key_block_data.keys()])
    for sk in keys:
        data = key_block_data[sk]
        shape_key = ob.shape_key_add(from_mix=True)
        shape_key.name = sk
        shape_key.interpolation = data["interpolation"]
        shape_key.relative_key = data["relative_key"]
        shape_key.value = data["value"]
        shape_key.slider_min = data["slider_min"]
        shape_key.slider_max = data["slider_max"]
        shape_key.vertex_group = data["vertex_group"]
        if use_frame:
            shape_key.frame = data["frame"]
        for i, co in enumerate(data["co"]):
            shape_key.data[i].co = co
    return

###################
# VERTEX GROUPS
###################

def get_vertex_groups_idxs(ob):
    vg = ob.vertex_groups
    data = {"INDICES": {}, "NAMES": []}
    if vg:
        vt = ob.data.vertices
        gct = len(vg)
        vct = len(vt)
        vg_idx_dict = {i: [] for i in range(gct)}
        vn = [v.name for v in vg]
        for v in range(vct):
            gr = vt[v].groups[:]
            if gr == []:
                continue
            else:
                for g in gr:
                    vg_idx_dict[g.group].append(v)
        data["INDICES"] = vg_idx_dict
        data["NAMES"] = vn
    return data


def get_vertex_groups_wts(ob):
    vt = ob.data.vertices
    weights = {}
    for v in vt:
        weights.update({v.index: {}})
        vg = list(v.groups[:])
        if vg:
            weights[v.index].update({"GROUP_INDEX": [], "WEIGHT": []})
            for g in vg:
                weights[v.index]["GROUP_INDEX"].append(g.group)
                weights[v.index]["WEIGHT"].append(g.weight)
    verts_with_weights = (np.where([weights[i] for i in list(weights.keys())])[0]).astype(int)
    return {"WEIGHTS": weights, "VERTS_WITH_WEIGHTS": verts_with_weights}


def set_copy_vertex_groups_idxs(ob, verts, converter, vert_group_data):
    vertex_groups = ob.vertex_groups
    groups = vert_group_data["NAMES"]
    for i, g in enumerate(groups):
        mask = np.isin(vert_group_data["INDICES"][i], verts)
        new_idx = [converter[vgi] for vgi in np.array(vert_group_data["INDICES"][i], dtype=int)[mask]]
        nvg = vertex_groups.new(name=g)
        nvg.add(new_idx, 1.0, 'REPLACE')
    return


def set_copy_vertex_groups_wts(ob, verts, weights):
    vt = ob.data.vertices
    mask = np.isin(verts, weights["VERTS_WITH_WEIGHTS"])
    for i, v in enumerate(vt):
        try:
            if mask[i]:
                v_ = verts[i]
                data = weights["WEIGHTS"][v_]
                for g in range(len(data["GROUP_INDEX"])):
                    v.groups[g].weight = data["WEIGHT"][g]
        except Exception as e:
            print(f"{e} <> {i} : {v_} >>> {data}")
        finally:
            continue
    return



