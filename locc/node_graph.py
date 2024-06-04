import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem, QInputDialog, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsItem, QMenu, QPushButton, QLabel
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QLineF

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, label, radius=20):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.setBrush(QBrush(QColor("lightblue")))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setPos(x, y)

        self.text = QGraphicsTextItem(label, self)
        self.text.setPos(-self.text.boundingRect().width() / 2, -self.text.boundingRect().height() / 2)

        print(f"Node created at ({x}, {y}) with label '{label}'")

    def mouseDoubleClickEvent(self, event):
        # Prompt for a new label when the node is double-clicked
        label, ok = QInputDialog.getText(None, "Rename Node", "Enter new node label:", text=self.text.toPlainText())
        if ok:
            self.text.setPlainText(label)
            self.text.setPos(-self.text.boundingRect().width() / 2, -self.text.boundingRect().height() / 2)
            print(f"Node renamed to '{label}'")

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete Node")
        action = menu.exec_(event.screenPos())
        if action == delete_action:
            if self.scene():
                print(f"Node at ({self.pos().x()}, {self.pos().y()}) with label '{self.text.toPlainText()}' deleted")
                self.scene().parent().remove_node(self, self.scene())
            else:
                print("Node is not associated with any scene.")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.scene().parent().update_edges()
        return super().itemChange(change, value)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, node1, node2):
        super().__init__()
        self.node1 = node1
        self.node2 = node2
        self.setPen(QPen(Qt.black, 2))
        self.update_position()

    def update_position(self):
        line = QLineF(self.node1.scenePos(), self.node2.scenePos())
        self.setLine(line)

class NodeGraphView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setSceneRect(-400, -300, 800, 600)  # Center the scene rectangle around (0,0)
        print("NodeGraphView initialized with scene rect (-400, -300, 800, 600)")
        self.nodes = []
        self.edges = []

    def mouseDoubleClickEvent(self, event):
        pos = self.mapToScene(event.pos())
        print(f"Mouse double-clicked at ({pos.x()}, {pos.y()})")
        items = self.scene.items(pos)
        if items:
            for item in items:
                if isinstance(item, NodeItem):
                    item.mouseDoubleClickEvent(event)
                    return
        label, ok = QInputDialog.getText(self, "Node Label", "Enter node label:")
        if ok:
            node = NodeItem(pos.x(), pos.y(), label)
            self.scene.addItem(node)
            self.nodes.append(node)
            node.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
            self.update_edges()
            print(f"Node added to scene at ({pos.x()}, {pos.y()}) with label '{label}'")

    def update_edges(self):
        # Remove old edges
        for edge in self.edges:
            self.scene.removeItem(edge)
        self.edges.clear()

        # Create new edges
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                edge = EdgeItem(self.nodes[i], self.nodes[j])
                self.scene.addItem(edge)
                self.edges.append(edge)

    def remove_node(self, node, scene):
        if node in self.nodes:
            self.nodes.remove(node)
            scene.removeItem(node)
            self.update_edges()
        else:
            print("Node is not in the list of nodes.")

class NodeGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Graph GUI")
        self.setGeometry(100, 100, 1000, 600)  # Increased width for control panel

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)

        # Add QLabel widget for user directions
        self.directions_label = QLabel("Instructions:\n"
                                       "1. Double-click on the canvas to create a new node.\n"
                                       "2. Double-click on a node to rename it.\n"
                                       "3. Right-click on a node to delete it.\n"
                                       "4. Use the 'Measure' button to change the color of a selected node to red.\n"
                                       "5. Nodes can be moved around by dragging.")
        main_layout.addWidget(self.directions_label)

        # Add a horizontal layout for the graph view and control panel
        graph_layout = QHBoxLayout()
        main_layout.addLayout(graph_layout)

        self.graph_view = NodeGraphView()
        graph_layout.addWidget(self.graph_view)

        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        
        # Add buttons to control panel
        self.measure_button = QPushButton("Measure")
        self.measure_button.clicked.connect(self.measure_node)
        control_layout.addWidget(self.measure_button)

        control_layout.addStretch()
        graph_layout.addWidget(self.control_panel)

        print("NodeGraphApp initialized")

    def measure_node(self):
        selected_items = self.graph_view.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, NodeItem):
                item.setBrush(QBrush(QColor("red")))
                print(f"Node at ({item.pos().x()}, {item.pos().y()}) with label '{item.text.toPlainText()}' measured (color changed to red)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NodeGraphApp()
    window.show()
    print("Application started")
    sys.exit(app.exec_())