import math
import struct


def _normalize_and_dedupe(vertices, edge_pairs, max_edges=8000):
    """Centers the mesh at (0,0,0), scales largest dimension to ~3.2 units, and compacts edges."""
    if not vertices:
        return list(), list()

    xs = [x for x, y, z in vertices]
    ys = [y for x, y, z in vertices]
    zs = [z for x, y, z in vertices]

    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0

    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1e-6)
    scale = 3.2 / span

    unique_edges = set()
    for a, b in edge_pairs:
        if a != b:
            pair = (a, b) if a < b else (b, a)
            unique_edges.add(pair)

    edge_list = list(unique_edges)
    if len(edge_list) > max_edges:
        step = max(1, len(edge_list) // max_edges)
        edge_list = edge_list[::step]

    used_indices = sorted({idx for pair in edge_list for idx in pair})
    remap = {old_idx: new_idx for new_idx, old_idx in enumerate(used_indices)}

    nodes = list()
    for old_idx in used_indices:
        x, y, z = vertices[old_idx]
        nodes.append({
            "x": round((x - cx) * scale, 4),
            "y": round((y - cy) * scale, 4),
            "z": round((z - cz) * scale, 4),
        })

    formatted_edges = [f"{remap.get(a)}-{remap.get(b)}" for a, b in edge_list]
    return nodes, formatted_edges


def _extract_feature_edges(vertices, triangles, angle_deg=28.0):
    """Keeps boundary edges and sharp creases where adjacent face normals exceed angle_deg."""
    cos_thresh = math.cos(math.radians(angle_deg))
    edge_normals = dict()

    for i0, i1, i2 in triangles:
        x0, y0, z0 = vertices[i0]
        x1, y1, z1 = vertices[i1]
        x2, y2, z2 = vertices[i2]

        ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
        vx, vy, vz = x2 - x0, y2 - y0, z2 - z0

        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        length = math.hypot(nx, ny, nz)
        if length < 1e-12:
            continue
        normal = (nx / length, ny / length, nz / length)

        for a, b in ((i0, i1), (i1, i2), (i2, i0)):
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            bucket = edge_normals.get(key)
            if bucket is None:
                edge_normals[key] = [normal]
            else:
                bucket.append(normal)

    feature_edges = list()
    for key, normals in edge_normals.items():
        if len(normals) == 1:
            feature_edges.append(key)
        else:
            n0 = normals[0]
            n1 = normals[1]
            dot = n0[0] * n1[0] + n0[1] * n1[1] + n0[2] * n1[2]
            if dot < cos_thresh:
                feature_edges.append(key)

    return feature_edges if feature_edges else list(edge_normals.keys())


def parse_obj(file_path):
    """Parses Wavefront .obj into sharp CAD silhouette edges."""
    vertices = list()
    triangles = list()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            tag = parts.pop(0) if parts else ""
            if tag == "v" and len(parts) >= 3:
                vx, vy, vz = float(parts.pop(0)), float(parts.pop(0)), float(parts.pop(0))
                vertices.append((vx, vy, vz))
            elif tag == "f" and len(parts) >= 3:
                idxs = list()
                for token in parts:
                    v_str = token.split("/").pop(0)
                    if v_str:
                        v_idx = int(v_str)
                        idxs.append(v_idx - 1 if v_idx > 0 else len(vertices) + v_idx)
                # Fan-triangulate n-gons so dihedral angle filtering works on quads/polygons
                root = idxs[0]
                for i in range(1, len(idxs) - 1):
                    triangles.append((root, idxs[i], idxs[i + 1]))

    feature_edges = _extract_feature_edges(vertices, triangles)
    return _normalize_and_dedupe(vertices, feature_edges)


def parse_stl(file_path):
    """Parses Binary and ASCII .stl files into sharp CAD silhouette edges."""
    with open(file_path, "rb") as f:
        _header = f.read(80)
        count_bytes = f.read(4)
        is_binary = False
        tri_count = 0

        if len(count_bytes) == 4:
            (tri_count,) = struct.unpack("<I", count_bytes)
            f.seek(0, 2)
            file_size = f.tell()
            expected_size = 84 + (tri_count * 50)
            if file_size == expected_size:
                is_binary = True

    vertex_map = dict()
    vertices = list()
    triangles = list()

    def get_vertex_idx(x, y, z):
        key = (round(x, 5), round(z, 5), round(y, 5))
        idx = vertex_map.get(key)
        if idx is None:
            idx = len(vertices)
            vertex_map[key] = idx
            vertices.append(key)
        return idx

    if is_binary:
        with open(file_path, "rb") as f:
            f.seek(84)
            for _ in range(tri_count):
                data = f.read(50)
                if len(data) < 50:
                    break
                _nx, _ny, _nz, v1x, v1y, v1z, v2x, v2y, v2z, v3x, v3y, v3z, _attr = struct.unpack("<12fH", data)
                i0 = get_vertex_idx(v1x, v1y, v1z)
                i1 = get_vertex_idx(v2x, v2y, v2z)
                i2 = get_vertex_idx(v3x, v3y, v3z)
                triangles.append((i0, i1, i2))
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tri_verts = list()
            for raw_line in f:
                line = raw_line.strip()
                if line.startswith("vertex "):
                    parts = line.split()
                    if len(parts) >= 4:
                        _kw, sx, sy, sz = parts.pop(0), parts.pop(0), parts.pop(0), parts.pop(0)
                        idx = get_vertex_idx(float(sx), float(sy), float(sz))
                        tri_verts.append(idx)
                        if len(tri_verts) == 3:
                            triangles.append(tuple(tri_verts))
                            tri_verts = list()

    feature_edges = _extract_feature_edges(vertices, triangles)
    return _normalize_and_dedupe(vertices, feature_edges)


def parse_step(file_path, angle_deg=28.0):
    """Tessellates .stp / .step CAD solids and extracts sharp silhouette creases via trimesh."""
    try:
        import numpy as np
        import trimesh
    except ImportError as exc:
        raise RuntimeError("Install STEP support first: pip install trimesh cascadio") from exc

    loaded = trimesh.load(file_path, force="mesh", tol_linear=1.2, tol_angular=0.4)
    if isinstance(loaded, trimesh.Scene):
        meshes = list(loaded.geometry.values())
        if not meshes:
            return list(), list()
        mesh = trimesh.util.concatenate(meshes)
    else:
        mesh = loaded

    mesh.merge_vertices()
    vertices = [(float(x), float(z), float(y)) for x, y, z in mesh.vertices]

    # Filter interior edges by dihedral angle and keep open boundary edges
    thresh = np.deg2rad(angle_deg)
    sharp_mask = mesh.face_adjacency_angles > thresh
    sharp_edges = mesh.face_adjacency_edges[sharp_mask]

    # Find boundary edges (edges appearing only once across all faces)
    all_edges = np.sort(mesh.edges, axis=1)
    unique_e, counts = np.unique(all_edges, axis=0, return_counts=True)
    boundary_edges = unique_e[counts == 1]

    combined = np.vstack((sharp_edges, boundary_edges)) if len(boundary_edges) else sharp_edges
    edge_pairs = [(int(a), int(b)) for a, b in combined] if len(combined) else [(int(a), int(b)) for a, b in mesh.edges_unique]

    return _normalize_and_dedupe(vertices, edge_pairs)


def load_mesh_file(file_path):
    """Dispatches .obj, .stl, .stp, or .step files and returns (nodes, edges)."""
    lower = file_path.lower()
    if lower.endswith(".obj"):
        return parse_obj(file_path)
    if lower.endswith(".stl"):
        return parse_stl(file_path)
    if lower.endswith((".stp", ".step")):
        return parse_step(file_path)
    raise ValueError("Unsupported CAD mesh extension. Expected .obj, .stl, .stp, or .step.")
