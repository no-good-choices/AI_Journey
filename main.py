import sys
import os
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QSplitter, QFrame, QLabel, QListWidget,
    QStatusBar, QPushButton, QFileDialog, QSlider, QCheckBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
import rag_engine_2

VIEWPORT_HTML = """<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background-color: #161616; user-select: none; }
  canvas { display: block; width: 100vw; height: 100vh; cursor: grab; }
  canvas:active { cursor: grabbing; }
  #hud { position: absolute; top: 12px; left: 14px; color: #6B8BA4; font-family: monospace; font-size: 12px; pointer-events: none; line-height: 1.5; }
</style>
</head>
<body>
<div id="hud">TSIATA CAD KERNEL // ORBIT: DRAG | ZOOM: SCROLL<br>ACTIVE NODE: <span id="hud-node" style="color:#38BDF8;">tsiata_hypercar_root</span></div>
<canvas id="view3d"></canvas>
<script>
const canvas = document.getElementById('view3d');
const ctx = canvas.getContext('2d');
function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
window.addEventListener('resize', resize);
resize();

let assemblies = {
  chassis_system: {
    explodeVec: { x: 0, y: 0, z: 0 },
    nodes: [
      {x: -1.6, y: -0.2, z: -0.65}, {x: 1.6, y: -0.2, z: -0.65}, {x: 1.6, y: 0.25, z: -0.65}, {x: -1.6, y: 0.25, z: -0.65},
      {x: -1.6, y: -0.2, z: 0.65},  {x: 1.6, y: -0.2, z: 0.65},  {x: 1.6, y: 0.25, z: 0.65},  {x: -1.6, y: 0.25, z: 0.65}
    ],
    edges: ["0-1","1-2","2-3","3-0","4-5","5-6","6-7","7-4","0-4","1-5","2-6","3-7"]
  },
  powertrain_unit: {
    explodeVec: { x: -0.8, y: -0.7, z: 0 },
    nodes: [
      {x: -1.2, y: -0.1, z: -0.35}, {x: -0.2, y: -0.1, z: -0.35}, {x: -0.2, y: 0.2, z: -0.35}, {x: -1.2, y: 0.2, z: -0.35},
      {x: -1.2, y: -0.1, z: 0.35},  {x: -0.2, y: -0.1, z: 0.35},  {x: -0.2, y: 0.2, z: 0.35},  {x: -1.2, y: 0.2, z: 0.35}
    ],
    edges: ["0-1","1-2","2-3","3-0","4-5","5-6","6-7","7-4","0-4","1-5","2-6","3-7"]
  },
  aero_surfaces: {
    explodeVec: { x: 0, y: 0.9, z: 0 },
    nodes: [
      {x: 2.1, y: -0.25, z: -0.75}, {x: 2.1, y: -0.25, z: 0.75}, {x: 0.4, y: 0.65, z: -0.50}, {x: 0.4, y: 0.65, z: 0.50},
      {x: -1.9, y: 0.55, z: -0.75}, {x: -1.9, y: 0.55, z: 0.75}, {x: -2.1, y: 0.85, z: -0.85}, {x: -2.1, y: 0.85, z: 0.85}
    ],
    edges: ["0-1","0-2","1-3","2-3","2-4","3-5","4-5","4-6","5-7","6-7"]
  }
};

let rotX = 0.35, rotY = -0.65, zoom = 1.0, explodeFactor = 0.0, autoRotate = true;
let selectedNode = "tsiata_hypercar_root";
let isDragging = false, lastX = 0, lastY = 0;

canvas.addEventListener('mousedown', e => { isDragging = true; lastX = e.clientX; lastY = e.clientY; });
window.addEventListener('mouseup', () => isDragging = false);
window.addEventListener('mousemove', e => {
  if (!isDragging) return;
  rotY += (e.clientX - lastX) * 0.008;
  rotX += (e.clientY - lastY) * 0.008;
  lastX = e.clientX; lastY = e.clientY;
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  zoom = Math.max(0.3, Math.min(4.0, zoom * (e.deltaY > 0 ? 0.92 : 1.08)));
}, { passive: false });

window.setSelectedNode = name => { selectedNode = name; document.getElementById('hud-node').textContent = name; };
window.setExplodeFactor = val => { explodeFactor = val; };
window.setAutoRotate = flag => { autoRotate = flag; };
window.loadCustomBlueprint = (name, nodes, edges) => {
  assemblies[name] = { explodeVec: { x: 0, y: 0.5, z: 0 }, nodes: nodes, edges: edges };
  window.setSelectedNode(name);
};

function project(pt) {
  let cosY = Math.cos(rotY), sinY = Math.sin(rotY);
  let x1 = pt.x * cosY + pt.z * sinY;
  let z1 = pt.z * cosY - pt.x * sinY;
  let cosX = Math.cos(rotX), sinX = Math.sin(rotX);
  let y2 = pt.y * cosX - z1 * sinX;
  let z2 = z1 * cosX + pt.y * sinX;
  let scale = Math.min(canvas.width, canvas.height) * 0.18 * zoom;
  let p = 5 / (5 + z2);
  return { x: x1 * scale * p + canvas.width / 2, y: -y2 * scale * p + canvas.height / 2 };
}

function drawGrid() {
  ctx.strokeStyle = '#202020';
  ctx.lineWidth = 1;
  for (let i = -3; i <= 3; i++) {
    let p1 = project({x: i, y: -0.4, z: -3}), p2 = project({x: i, y: -0.4, z: 3});
    ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
    let p3 = project({x: -3, y: -0.4, z: i}), p4 = project({x: 3, y: -0.4, z: i});
    ctx.beginPath(); ctx.moveTo(p3.x, p3.y); ctx.lineTo(p4.x, p4.y); ctx.stroke();
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  if (autoRotate && !isDragging) rotY += 0.006;
  let showAll = (selectedNode === "tsiata_hypercar_root" || selectedNode === "assembly_manifest.json");
  for (const [name, part] of Object.entries(assemblies)) {
    let isSel = (name === selectedNode);
    ctx.strokeStyle = isSel ? '#38BDF8' : (showAll ? '#0A5C96' : '#2A3B4C');
    ctx.lineWidth = isSel ? 2.8 : 1.6;
    let pts = part.nodes.map(n => project({
      x: n.x + part.explodeVec.x * explodeFactor,
      y: n.y + part.explodeVec.y * explodeFactor,
      z: n.z + part.explodeVec.z * explodeFactor
    }));
    part.edges.forEach(e => {
      let pair = Array.isArray(e) ? e : e.split('-').map(Number);
      let p1 = pts.at(pair.at(0)), p2 = pts.at(pair.at(1));
      if (p1 && p2) { ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke(); }
    });
  }
  requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>"""


class TsiataPlatform(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSIATA ENGINEERING PLATFORM - Active 3D Render")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: #121212;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        window_splitter = QSplitter(Qt.Horizontal)

        # Left Sidebar
        self.sidebar_panel = QFrame()
        self.sidebar_panel.setStyleSheet("background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px;")
        sidebar_layout = QVBoxLayout(self.sidebar_panel)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        sidebar_title = QLabel("PROJECT BROWSER")
        sidebar_title.setStyleSheet("color: #0A5C96; font-weight: bold; font-size: 12px; border: none;")
        sidebar_layout.addWidget(sidebar_title)

        self.component_list = QListWidget()
        self.component_list.setStyleSheet("QListWidget { background-color: #1A1A1A; border: 1px solid #2D2D2D; color: #E0E0E0; font-family: monospace; } QListWidget::item { padding: 6px; } QListWidget::item:selected { background-color: #0A5C96; color: #FFFFFF; }")
        self.component_list.addItems(list(("tsiata_hypercar_root", "assembly_manifest.json", "chassis_system", "powertrain_unit", "aero_surfaces")))
        sidebar_layout.addWidget(self.component_list)

        controls_title = QLabel("ASSEMBLY CONTROLS")
        controls_title.setStyleSheet("color: #0A5C96; font-weight: bold; font-size: 11px; border: none; margin-top: 8px;")
        sidebar_layout.addWidget(controls_title)

        self.explode_label = QLabel("Explode Factor: 0%")
        self.explode_label.setStyleSheet("color: #A0A0A0; font-size: 11px; border: none;")
        sidebar_layout.addWidget(self.explode_label)

        self.explode_slider = QSlider(Qt.Horizontal)
        self.explode_slider.setRange(0, 100)
        self.explode_slider.setValue(0)
        self.explode_slider.setStyleSheet("border: none;")
        self.explode_slider.valueChanged.connect(self.on_explode_changed)
        sidebar_layout.addWidget(self.explode_slider)

        self.auto_rotate_chk = QCheckBox("Auto-Orbit Viewport")
        self.auto_rotate_chk.setChecked(True)
        self.auto_rotate_chk.setStyleSheet("color: #CCCCCC; font-size: 12px; border: none; margin-bottom: 6px;")
        self.auto_rotate_chk.toggled.connect(self.on_auto_rotate_toggled)
        sidebar_layout.addWidget(self.auto_rotate_chk)

        self.import_button = QPushButton("Import Design File...")
        self.import_button.setStyleSheet("QPushButton { background-color: #252525; border: 1px solid #3D3D3D; color: #FFFFFF; padding: 8px; font-weight: bold; border-radius: 4px; } QPushButton:hover { background-color: #0A5C96; border-color: #0F72B8; } QPushButton:pressed { background-color: #063B61; }")
        sidebar_layout.addWidget(self.import_button)

        # Right Workspace
        workspace_splitter = QSplitter(Qt.Vertical)
        self.viewport_panel = QFrame()
        self.viewport_panel.setStyleSheet("background-color: #161616; border: 1px solid #2D2D2D; border-radius: 4px;")
        viewport_layout = QVBoxLayout(self.viewport_panel)
        viewport_layout.setContentsMargins(0, 0, 0, 0)

        self.threejs_view = QWebEngineView()
        self.threejs_view.setStyleSheet("border: none; border-radius: 4px;")
        self.threejs_view.setHtml(VIEWPORT_HTML)
        viewport_layout.addWidget(self.threejs_view)

        self.info_panel = QFrame()
        self.info_panel.setStyleSheet("background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px;")
        info_layout = QVBoxLayout(self.info_panel)
        info_title = QLabel("ENGINEERING INFORMATION")
        info_title.setStyleSheet("color: #0A5C96; font-weight: bold; font-size: 12px; border: none;")
        info_layout.addWidget(info_title, alignment=Qt.AlignTop)

        self.info_text = QLabel("Select an engineering node or track structural coordinates inside the 3D viewport canvas.")
        self.info_text.setStyleSheet("color: #A0A0A0; font-size: 13px; border: none;")
        self.info_text.setWordWrap(True)
        info_layout.addWidget(self.info_text)

        workspace_splitter.addWidget(self.viewport_panel)
        workspace_splitter.addWidget(self.info_panel)
        workspace_splitter.setSizes(list((500, 200)))



        window_splitter.addWidget(self.sidebar_panel)
        window_splitter.addWidget(workspace_splitter)
        window_splitter.setSizes(list((300, 900)))
        main_layout.addWidget(window_splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #888888; background-color: #1A1A1A; border-top: 1px solid #2D2D2D;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hardware-accelerated local 3D canvas viewport initialized successfully.")

        self.component_list.itemClicked.connect(self.on_node_clicked)
        self.import_button.clicked.connect(self.on_import_button_clicked)

    def on_explode_changed(self, val):
        self.explode_label.setText(f"Explode Factor: {val}%")
        self.threejs_view.page().runJavaScript(f"setExplodeFactor({val / 100.0});")

    def on_auto_rotate_toggled(self, state):
        flag = "true" if state else "false"
        self.threejs_view.page().runJavaScript(f"setAutoRotate({flag});")

    def on_node_clicked(self, item):
        node_key = item.text().strip()
        self.status_bar.showMessage(f"Running matrix operations for node: {node_key}...")
        self.threejs_view.page().runJavaScript(f"setSelectedNode({json.dumps(node_key)});")
        computed_result_html = rag_engine_2.compute_ui_similarity(node_key)
        self.info_text.setText(computed_result_html)

    def on_import_button_clicked(self):
        self.status_bar.showMessage("Awaiting user file selection from system exploration panel...")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "TSIATA - Select Engineering Target Asset File", "", "Design Data Files (*.json *.step *.gltf *.obj);;All Files (*)"
        )
        if file_path:
            file_name = os.path.basename(file_path)
            self.component_list.addItem(file_name)
            self.status_bar.showMessage(f"Ingested asset structural file node: {file_name}")
            geometry_status = "Metadata registered (CAD mesh parser queued)."
            if file_path.lower().endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if "nodes" in data and "edges" in data:
                        nodes_json = json.dumps(data.get("nodes"))
                        edges_json = json.dumps(data.get("edges"))
                        self.threejs_view.page().runJavaScript(
                            f"loadCustomBlueprint({json.dumps(file_name)}, {nodes_json}, {edges_json});"
                        )
                        geometry_status = f"Rendered {len(data.get('nodes'))} nodes and {len(data.get('edges'))} edges in 3D viewport."
                except Exception as e:
                    geometry_status = f"JSON loaded as data node (no wireframe matrix found: {e})."
            self.info_text.setText(
                f"<b>File Import Pipeline Active</b><br>"
                f"<b>Source Location:</b> <span style='color: #0A5C96;'>{file_path}</span><br>"
                f"<b>File Size Matrix:</b> {os.path.getsize(file_path) / 1024:.2f} KB<br>"
                f"<b>Viewport Status:</b> {geometry_status}"
            )
        else:
            self.status_bar.showMessage("File import operation aborted by user.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    platform = TsiataPlatform()
    platform.show()
    sys.exit(app.exec())
