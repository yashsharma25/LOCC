import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem, QInputDialog, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsItem, QMenu, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
import random

class NodeProperties(QObject):
    properties_changed = pyqtSignal()

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, label, view, radius=20):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.setBrush(QBrush(QColor("lightblue")))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setPos(x, y)
        self.view = view
        self.properties = NodeProperties()  # Create properties object
        self.properties.properties_changed.connect(self.update_properties)

        self.text = QGraphicsTextItem(label, self)
        self.text.setPos(-self.text.boundingRect().width() / 2, -self.text.boundingRect().height() / 2)

        self.childNode = None  # Reference to the duplicated node
        self.parentNode = None  # Reference to the original node

        print(f"Node created at ({x}, {y}) with label '{label}' in view {view.objectName()}")

    def setChildNode(self, node):
        self.childNode = node
        node.setParentNode(self)
        node.update_properties()

    def setParentNode(self, node):
        self.parentNode = node

    def mouseDoubleClickEvent(self, event):
        # Prompt for a new label when the node is double-clicked
        label, ok = QInputDialog.getText(None, "Rename Node", "Enter new node label:", text=self.text.toPlainText())
        if ok:
            self.text.setPlainText(label)
            self.text.setPos(-self.text.boundingRect().width() / 2, -self.text.boundingRect().height() / 2)
            self.properties.properties_changed.emit()
            print(f"Node renamed to '{label}'")

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete Node")
        
        if self.view.objectName() == "View_Right":
            duplicate_action = menu.addAction("Duplicate Node to Left View")

        action = menu.exec_(event.screenPos())
        
        if action == delete_action:
            if self.scene():
                print(f"Node at ({self.pos().x()}, {self.pos().y()}) with label '{self.text.toPlainText()}' deleted")
                self.view.remove_node(self, self.scene())
            else:
                print("Node is not associated with any scene.")
        
        elif action == duplicate_action:
            self.view.duplicate_node_to_left_view(self)

    def update_properties(self):
        if self.childNode:
            self.childNode.setPos(self.pos())
            self.childNode.text.setPlainText(self.text.toPlainText())
            self.childNode.setBrush(self.brush())
        if self.parentNode:
            self.parentNode.setPos(self.pos())
            self.parentNode.text.setPlainText(self.text.toPlainText())
            self.parentNode.setBrush(self.brush())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            scene_rect = self.scene().sceneRect()
            radius = self.rect().width() / 2
            
            # Check boundaries of the node's view's scene
            if new_pos.x() - radius < scene_rect.left():
                new_pos.setX(scene_rect.left() + radius)
            elif new_pos.x() + radius > scene_rect.right():
                new_pos.setX(scene_rect.right() - radius)
            if new_pos.y() - radius < scene_rect.top():
                new_pos.setY(scene_rect.top() + radius)
            elif new_pos.y() + radius > scene_rect.bottom():
                new_pos.setY(scene_rect.bottom() - radius)

            # Ensure the node does not move to another view's scene
            view_rect = self.view.viewport().rect()
            mapped_pos = self.view.mapFromScene(new_pos)
            if not view_rect.contains(mapped_pos):
                # Clamp position to the view's bounds
                if mapped_pos.x() < 0:
                    new_pos.setX(self.view.mapToScene(0, 0).x() + radius)
                elif mapped_pos.x() > view_rect.width():
                    new_pos.setX(self.view.mapToScene(view_rect.width(), 0).x() - radius)
                if mapped_pos.y() < 0:
                    new_pos.setY(self.view.mapToScene(0, 0).y() + radius)
                elif mapped_pos.y() > view_rect.height():
                    new_pos.setY(self.view.mapToScene(0, view_rect.height()).y() - radius)

            # Propagate position change to connected node
            if self.childNode and change != QGraphicsItem.ItemPositionChange:  # Added condition to prevent recursion
                self.childNode.setPos(new_pos)
            if self.parentNode and change != QGraphicsItem.ItemPositionChange:  # Added condition to prevent recursion
                self.parentNode.setPos(new_pos)

            # Update edges
            self.view.update_edges()
            
            return new_pos
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(f"View_{id(self)}")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setSceneRect(-400, -300, 800, 600)  # Center the scene rectangle around (0,0)
        print(f"{self.objectName()} initialized with scene rect (-400, -300, 800, 600)")
        self.nodes = []
        self.edges = []
        # Connect node properties changed signal to update connected nodes
        self.connections = {}

    def mouseDoubleClickEvent(self, event):
        if self.objectName() == "View_Right":  # Only allow adding nodes in View_Right
            pos = self.mapToScene(event.pos())
            print(f"Mouse double-clicked at ({pos.x()}, {pos.y()}) in {self.objectName()}")
            items = self.scene.items(pos)
            if items:
                for item in items:
                    if isinstance(item, NodeItem):
                        item.mouseDoubleClickEvent(event)
                        return
            label, ok = QInputDialog.getText(self, "Qubit Label", "Enter qubit label:")
            if ok:
                if self.objectName() == "View_Left" and len(self.nodes) >= 2:
                    QMessageBox.warning(self, "Limit Exceeded", "Local View (pair-wise) can only be used for 2 qubits at a time. Please remove a qubit from Local View to add a different qubit.")
                    return
                node = NodeItem(pos.x(), pos.y(), label, self)
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
            # Remove connections
            if node in self.connections:
                del self.connections[node]
            for left_node, right_node in list(self.connections.items()):
                if right_node == node:
                    del self.connections[left_node]
            self.update_edges()
        else:
            print("Node is not in the list of nodes.")
    
    def duplicate_node_to_left_view(self, node):
        main_window = self.parentWidget().parentWidget()
        left_view = main_window.graph_view_1
        if len(left_view.nodes) >= 2:
            QMessageBox.warning(self, "Limit Exceeded", "Local View (pair-wise) can only be used for 2 nodes at a time. Please remove a node from Local View to add a different node.")
            return
        new_pos = QPointF(-node.pos().x(), node.pos().y())  # Adjust the position as needed
        new_node = NodeItem(new_pos.x(), new_pos.y(), node.text.toPlainText(), left_view)
        left_view.scene.addItem(new_node)
        left_view.nodes.append(new_node)
        new_node.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        left_view.update_edges()
        print(f"Node duplicated to left view at ({new_pos.x()}, {new_pos.y()}) with label '{node.text.toPlainText()}'")

        # Set parent-child relationship
        node.setChildNode(new_node)
        # Store the connection
        self.connections[node] = new_node

    def update_connected_node(self):
        sender_node = self.sender()
        for node in self.nodes:
            if node is not sender_node and node.view is not sender_node.view:
                if node.text.toPlainText() == sender_node.text.toPlainText():
                    node.update_properties()

class NodeGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Quantum Tool - Quantum Measurement and Entanglement Entropy")
        self.setGeometry(100, 100, 1200, 600)  # Increased width for two graph views

        # Set fixed size to disable resizing
        self.setFixedSize(1200, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)

        # Add QLabel widget for user directions
        self.directions_label = QLabel("Instructions:\n"
                                       "1. Double-click on the Global View canvas to create a new qubit.\n"
                                       "2. Double-click on an existing qubit to rename it.\n"
                                       "3. Right-click on a qubit to delete it.\n"
                                       "4. Right-click on a qubit in the Global View to duplicate it to the Local View.\n"
                                       "5. Use the 'Measure' button to measure the selected qubit (for now this is represented by qubit turning red).\n"
                                       "6. Use the 'Change Measurement Basis' button to change the basis of measurement of a selected qubit (for now this is represented as qubit turning green).\n"
                                       "7. Qubits can be moved around canvas by dragging.")
        main_layout.addWidget(self.directions_label)

        # Add a horizontal layout for the two graph views
        graph_layout = QHBoxLayout()
        main_layout.addLayout(graph_layout)

        # Add View_Left
        view_left_layout = QVBoxLayout()
        self.label_left = QLabel("Local View (pair-wise)")
        self.label_left.setAlignment(Qt.AlignCenter)
        view_left_layout.addWidget(self.label_left)
        self.graph_view_1 = NodeGraphView()
        self.graph_view_1.setObjectName("View_Left")
        view_left_layout.addWidget(self.graph_view_1)
        graph_layout.addLayout(view_left_layout)

        # Add View_Right
        view_right_layout = QVBoxLayout()
        self.label_right = QLabel("Global View (bi-partite, tri-partite, etc.)")
        self.label_right.setAlignment(Qt.AlignCenter)
        view_right_layout.addWidget(self.label_right)
        self.graph_view_2 = NodeGraphView()
        self.graph_view_2.setObjectName("View_Right")
        view_right_layout.addWidget(self.graph_view_2)
        graph_layout.addLayout(view_right_layout)

        # Add a control panel below the graph views
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)

        self.measure_button = QPushButton("Measure")
        self.measure_button.clicked.connect(self.measure_node)
        control_layout.addWidget(self.measure_button)

        self.basis_button = QPushButton("Change Measurement Basis")
        self.basis_button.clicked.connect(self.change_basis)
        control_layout.addWidget(self.basis_button)

        control_layout.addStretch()

        print("NodeGraphApp initialized")

    def change_basis(self):
        selected_items_1 = self.graph_view_1.scene.selectedItems()
        selected_items_2 = self.graph_view_2.scene.selectedItems()
        for item in selected_items_1 + selected_items_2:
            if isinstance(item, NodeItem):
                item.setBrush(QBrush(QColor("green")))
                print(f"Node at ({item.pos().x()}, {item.pos().y()}) with label '{item.text.toPlainText()}' measurement basis was changed (color changed to green)")

    def measure_node(self):
        # Measure node in both views
        selected_items_1 = self.graph_view_1.scene.selectedItems()
        selected_items_2 = self.graph_view_2.scene.selectedItems()

        for item in selected_items_1 + selected_items_2:
            if isinstance(item, NodeItem):
                item.setBrush(QBrush(QColor("red")))
                print(f"Node at ({item.pos().x()}, {item.pos().y()}) with label '{item.text.toPlainText()}' measured (color changed to red)")
                # Display pop-up
                msg_box = QMessageBox()
                msg_box.setWindowTitle("New Local EE")
                x = random.uniform(0,1) # for now it's just a random number, need to implement actual logic later
                msg_box.setText(f"New Local EE: {x}")
                msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NodeGraphApp()
    window.show()
    print("Application started")
    sys.exit(app.exec_())
