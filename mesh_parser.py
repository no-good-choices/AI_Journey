import struct


def _normalize_and_dedupe(vertices, edge_pairs, max_edges=6000):
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


def parse_obj(file_path):
    """Parses Wavefront .obj vertices ('v') and faces ('f') into viewport nodes and edges."""
    vertices = list()
    edge_pairs = list()

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
                count = len(idxs)
                for i in range(count):
                    a = idxs.pop(0)
                    idxs.append(a)
                    b = idxs.pop(0)
                    idxs.insert(0, b)
                    edge_pairs.append((a, b))

    return _normalize_and_dedupe(vertices, edge_pairs)


def parse_stl(file_path):
    """Parses both Binary and ASCII .stl files into viewport nodes and edges."""
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
    edge_pairs = list()

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
                edge_pairs.extend(((i0, i1), (i1, i2), (i2, i0)))
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
                            i0, i1, i2 = tri_verts
                            edge_pairs.extend(((i0, i1), (i1, i2), (i2, i0)))
                            tri_verts = list()

    return _normalize_and_dedupe(vertices, edge_pairs)


def parse_step(file_path):
    """Tessellates .stp / .step CAD solids via trimesh + cascadio into viewport nodes and edges."""
    try:
        import trimesh
    except ImportError as exc:
        raise RuntimeError("Install STEP support first: pip install trimesh cascadio") from exc

    # Coarse angular/linear deflection keeps large assemblies like a V8 engine fast
    loaded = trimesh.load(file_path, force="mesh", tol_linear=1.5, tol_angular=0.5)
    if isinstance(loaded, trimesh.Scene):
        meshes = list(loaded.geometry.values())
        if not meshes:
            return list(), list()
        mesh = trimesh.util.concatenate(meshes)
    else:
        mesh = loaded

    vertices = [(float(x), float(z), float(y)) for x, y, z in mesh.vertices]
    edge_pairs = [(int(a), int(b)) for a, b in mesh.edges_unique]
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
