import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QSplitter, QFrame, QLabel, QListWidget, 
    QStatusBar, QPushButton, QFileDialog
)
from PySide6.QtWebEngineWidgets import QWebEngineView

# Import your local vector matrix logic
import rag_engine_2

class TsiataPlatform(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TSIATA ENGINEERING PLATFORM - Pure 3D Engine")
        self.resize(1280, 720)
        self.setStyleSheet("QMainWindow { background-color: #121212; }")
        
        # Core Layout Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT PANEL: COMPONENT BROWSER ---
        self.sidebar_panel = QFrame()
        self.sidebar_panel.setStyleSheet("background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px;")
        sidebar_layout = QVBoxLayout(self.sidebar_panel)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        sidebar_title = QLabel("PROJECT BROWSER")
        sidebar_title.setStyleSheet("color: #0A5C96; font-weight: bold; font-size: 12px; border: none;")
        sidebar_layout.addWidget(sidebar_title)
        
        self.component_list = QListWidget()
        self.component_list.setStyleSheet("""
            QListWidget { background-color: #1A1A1A; border: 1px solid #2D2D2D; color: #E0E0E0; font-family: monospace; }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background-color: #0A5C96; color: #FFFFFF; }
        """)
        self.component_list.addItems([
            "tsiata_hypercar_root",
            "assembly_manifest.json",
            "chassis_system",
            "powertrain_unit",
            "aero_surfaces"
        ])
        sidebar_layout.addWidget(self.component_list)
        
        self.import_button = QPushButton("Import Design File...")
        self.import_button.setStyleSheet("""
            QPushButton { background-color: #252525; border: 1px solid #3D3D3D; color: #FFFFFF; padding: 8px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #0A5C96; border-color: #0F72B8; }
            QPushButton:pressed { background-color: #063B61; }
        """)
        sidebar_layout.addWidget(self.import_button)
        
        # --- RIGHT PANEL: VIEWPORT & TEXT CONSOLE ---
        workspace_splitter = QSplitter(Qt.Vertical)
        
        # 3D Graphics Viewport Slot
        self.viewport_panel = QFrame()
        self.viewport_panel.setStyleSheet("background-color: #161616; border: 1px solid #2D2D2D; border-radius: 4px;")
        viewport_layout = QVBoxLayout(self.viewport_panel)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        
        self.threejs_view = QWebEngineView()
        self.threejs_view.setStyleSheet("border: none; border-radius: 4px;")
        
        # Local rendering pipeline for the 3D structure
        local_canvas_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; overflow: hidden; background-color: #161616; }
                canvas { display: block; width: 100vw; height: 100vh; }
            </style>
        </head>
        <body>
            <canvas id="view3d"></canvas>
            <script>
                const canvas = document.getElementById('view3d');
                const ctx = canvas.getContext('2d');

                function resize() {
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                }
                window.addEventListener('resize', resize);
                resize();

                // Coordinates matrix for 3D model vertices
                let nodes = [
                    {x: -1, y: -1, z: -1}, {x: 1, y: -1, z: -1}, {x: 1, y: 1, z: -1}, {x: -1, y: 1, z: -1},
                    {x: -1, y: -1, z: 1},  {x: 1, y: -1, z: 1},  {x: 1, y: 1, z: 1},  {x: -1, y: 1, z: 1}
                ];

                // Closed structural map matching our nodes lists
                                let edges = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];


                let angleX = 0.008;
                let angleY = 0.012;

                function rotateX(node, angle) {
                    let cos = Math.cos(angle);
                    let sin = Math.sin(angle);
                    let y = node.y * cos - node.z * sin;
                    let z = node.z * cos + node.y * sin;
                    node.y = y;
                    node.z = z;
                }

                function rotateY(node, angle) {
                    let cos = Math.cos(angle);
                    let sin = Math.sin(angle);
                    let x = node.x * cos + node.z * sin;
                    let z = node.z * cos - node.x * sin;
                    node.x = x;
                    node.z = z;
                }

                function draw() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.strokeStyle = '#0A5C96';
                    ctx.lineWidth = 2;

                    let projected = [];
                    let scale = Math.min(canvas.width, canvas.height) * 0.28;
                    let cx = canvas.width / 2;
                    let cy = canvas.height / 2;

                    nodes.forEach(node => {
                        rotateX(node, angleX);
                        rotateY(node, angleY);
                        projected.push({
                            x: node.x * scale + cx,
                            y: node.y * scale + cy
                        });
                    });

                    edges.forEach(edge => {
                        let p1 = projected[edge[0]];
                        let p2 = projected[edge[1]];
                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    });

                    requestAnimationFrame(draw);
                }
                draw();
            </script>
        </body>
        </html>
        """
        self.threejs_view.setHtml(local_canvas_html)
        viewport_layout.addWidget(self.threejs_view)

        # Lower Data Panel Consolidation Window
        self.info_panel = QFrame()
        self.info_panel.setStyleSheet("background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px;")
        info_layout = QVBoxLayout(self.info_panel)
        info_title = QLabel("ENGINEERING INFORMATION")
        info_title.setStyleSheet("color: #0A5C96; font-weight: bold; font-size: 12px; border: none;")
        info_layout.addWidget(info_title, alignment=Qt.AlignTop)
        
        self.info_text = QLabel("Select an engineering node in the browser matrix to compute local vector metrics.")
        self.info_text.setStyleSheet("color: #A0A0A0; font-size: 13px; border: none;")
        self.info_text.setWordWrap(True)
        info_layout.addWidget(self.info_text)

        workspace_splitter.addWidget(self.viewport_panel)
        workspace_splitter.addWidget(self.info_panel)
        workspace_splitter.setSizes([450, 200])

        main_splitter.addWidget(self.sidebar_panel)
        main_splitter.addWidget(workspace_splitter)
        main_splitter.setSizes([300, 900])
        main_layout.addWidget(main_splitter)

        # Bottom System Status Monitor
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #888888; background-color: #1A1A1A; border-top: 1px solid #2D2D2D;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hardware-accelerated 3D viewport online. Local matrix vector loops active.")

        # Wire Up Interactive Event Hooks
        self.component_list.itemClicked.connect(self.on_node_clicked)
        self.import_button.clicked.connect(self.on_import_button_clicked)

    def on_node_clicked(self, item):
        node_key = item.text().strip()
        self.status_bar.showMessage(f"Running matrix operations for node: {node_key}...")
        computed_result_html = rag_engine_2.compute_ui_similarity(node_key)
        self.info_text.setText(computed_result_html)

    def on_import_button_clicked(self):
        self.status_bar.showMessage("Awaiting user file selection from system exploration panel...")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "TSIATA - Select Engineering Target Asset File", "", "Design Data Files (*.json *.step *.gltf);;All Files (*)"
        )
        if file_path:
            file_name = os.path.basename(file_path)
            self.component_list.addItem(file_name)
            self.status_bar.showMessage(f"✅ Ingested asset structural file node: {file_name}")
            self.info_text.setText(
                f"<b>File Import Pipeline Active</b><br><b>Source Location:</b> <span style='color: #0A5C96;'>{file_path}</span><br><b>File Size Matrix:</b> {os.path.getsize(file_path) / 1024:.2f} KB"
            )
        else:
            self.status_bar.showMessage("File import operation aborted by user.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    platform = TsiataPlatform()
    platform.show()
    sys.exit(app.exec())
