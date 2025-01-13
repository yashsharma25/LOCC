from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, 
    QVBoxLayout, QWidget, QMessageBox, QLabel, QLineEdit, QSizePolicy, QHBoxLayout, QComboBox, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtWidgets import QFileDialog

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Set up the main window
        self.setWindowTitle("Quantum State Input and Operations")
        # self.setGeometry(100, 100, 600, 600)
        self.setGeometry(100, 60, 700, 950)
        self.setFixedSize(self.width(), self.height())
        self.fixed_width = 50

        # Create a scroll area and set it as the central widget
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll_area)

        # Create a widget for the scroll area and set its layout
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        self.layout = QVBoxLayout(scroll_widget)

        self.layout.setContentsMargins(10,10,10,10)

        # Alternatively, you can add a QSpacerItem to the layout
        spacer = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.layout.addItem(spacer)

        self.download_button = QPushButton("Download Template")
        self.download_button.clicked.connect(self.download_template)
        self.layout.addWidget(self.download_button, alignment=Qt.AlignCenter)

        self.upload_button = QPushButton("Upload Template")
        self.upload_button.clicked.connect(self.upload_template)
        self.layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        table_h_layout = QHBoxLayout()

        # Create a table widget for amplitude and basis state input
        self.table = QTableWidget(0, 2)  # Initially zero rows, 2 columns
        self.table.setHorizontalHeaderLabels(["Amplitude", "Basis State"])

        self.table.setFixedSize(300,200)
        table_h_layout.addWidget(self.table, alignment=Qt.AlignCenter)

        add_remove_v_layout = QVBoxLayout()
        add_remove_v_layout.setSpacing(5)  # Set spacing to 5 pixels (or any small value)
        add_remove_v_layout.setContentsMargins(0,0,0,0)

        # Add buttons to add/remove rows
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.add_row_button.setFixedSize(100,30)
        add_remove_v_layout.addWidget(self.add_row_button, alignment=Qt.AlignCenter)

        self.remove_row_button = QPushButton("Remove Row")
        self.remove_row_button.clicked.connect(self.remove_row)
        self.remove_row_button.setFixedSize(100,30)
        add_remove_v_layout.addWidget(self.remove_row_button, alignment=Qt.AlignCenter)
        
        table_h_layout.addLayout(add_remove_v_layout)
        self.layout.addLayout(table_h_layout)

        # Function Buttons Layout
        self.function_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.function_buttons_layout)

        # Dictionary of allowed functions with formatted strings
        self.allowed_functions = {
            'SQRT': 'np.sqrt()',
            'PI': 'np.pi',
            'SIN': 'np.sin()',
            'COS': 'np.cos()',
            'EXP': 'np.exp()',
        }

        # Add function buttons
        for func_name, func_str in self.allowed_functions.items():
            button = QPushButton(func_name)
            button.clicked.connect(lambda _, f=func_str: self.insert_function(f))
            self.function_buttons_layout.addWidget(button)

        # Add a button to create the quantum state
        self.create_state_button = QPushButton("Create Quantum State")
        self.create_state_button.clicked.connect(self.handle_create_state)
        self.create_state_button.setFixedSize(200,30)
        self.layout.addWidget(self.create_state_button, alignment=Qt.AlignCenter)

        party_h_layout = QHBoxLayout()
        party_h_layout.setSpacing(0)
        party_h_layout.setContentsMargins(0, 0, 275, 0)


        self.num_parties_label = QLabel("Number of parties (k):")
        self.num_parties_input = QLineEdit()
        self.num_parties_input.setFixedWidth(self.fixed_width)
        party_h_layout.addWidget(self.num_parties_label)
        party_h_layout.addWidget(self.num_parties_input)
        self.layout.addLayout(party_h_layout)
        
        # input for number of qudits per party
        qudits_h_layout = QHBoxLayout()
        qudits_h_layout.setSpacing(0)
        qudits_h_layout.setContentsMargins(0, 0, 100, 0)

        self.num_qudits_label = QLabel("Number of qudits for each party (comma-separated):")
        self.num_qudits_input = QLineEdit()
        self.num_qudits_input.setFixedWidth(self.fixed_width)
        qudits_h_layout.addWidget(self.num_qudits_label)
        qudits_h_layout.addWidget(self.num_qudits_input)
        self.layout.addLayout(qudits_h_layout)

        # Input for dimension
        dim_h_layout = QHBoxLayout()
        dim_h_layout.setSpacing(0)
        dim_h_layout.setContentsMargins(0, 0, 300, 0)

        self.dim_label = QLabel("Dimension of qudits:")
        self.dim_input = QLineEdit()
        self.dim_input.setFixedWidth(self.fixed_width)
        dim_h_layout.addWidget(self.dim_label)
        dim_h_layout.addWidget(self.dim_input)
        self.layout.addLayout(dim_h_layout)

        # Button to generate state description label
        self.generate_button = QPushButton("Generate State Descriptor and K Party")
        self.generate_button.clicked.connect(self.handle_generate_state_desc_label_and_k_party)
        self.generate_button.setFixedSize(300,30)
        self.layout.addWidget(self.generate_button, alignment=Qt.AlignCenter)

        # Alternatively, you can add a QSpacerItem to the layout
        spacer_new = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.layout.addItem(spacer_new)

        self.layout.addWidget(QLabel("LOCC Operation Creator"), alignment=Qt.AlignCenter)
        
        # Conditional operation entries
        cond_text = QLabel("Leave the condition entry empty if the step is NOT a CONDITIONAL OPERATION.")
        cond_text.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(cond_text)

        locc_table_h_layout = QHBoxLayout()

        # Create a table widget for amplitude and basis state input
        self.locc_table = QTableWidget(0,5)  # Initially zero rows, 5 columns
        self.locc_table.setHorizontalHeaderLabels(["operation", "operator", "party index", "qudit index", "condition"])

        self.locc_table.setFixedSize(505, 200)
        locc_table_h_layout.addWidget(self.locc_table, alignment=Qt.AlignLeft)

        locc_add_remove_v_layout = QVBoxLayout()
        locc_add_remove_v_layout.setSpacing(5)  # Set spacing to 5 pixels (or any small value)
        locc_add_remove_v_layout.setContentsMargins(0,0,0,0)

        # Add buttons to add/remove rows
        self.locc_add_row_button = QPushButton("Add Row")
        self.locc_add_row_button.clicked.connect(self.locc_add_row)
        self.locc_add_row_button.setFixedSize(100,30)
        locc_add_remove_v_layout.addWidget(self.locc_add_row_button, alignment=Qt.AlignCenter)

        self.locc_remove_row_button = QPushButton("Remove Row")
        self.locc_remove_row_button.clicked.connect(self.locc_remove_row)
        self.locc_remove_row_button.setFixedSize(100,30)
        locc_add_remove_v_layout.addWidget(self.locc_remove_row_button, alignment=Qt.AlignCenter)
        
        locc_table_h_layout.addLayout(locc_add_remove_v_layout)
        self.layout.addLayout(locc_table_h_layout)

        # locc operation type Buttons Layout
        self.locc_op_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.locc_op_buttons_layout)

        # Dictionary of allowed functions with formatted strings
        self.locc_allowed_ops = {
            'M': 'measurement',
            'C': 'condition',
            'D': 'default'
        }

        # Add function buttons
        for func_name, func_str in self.locc_allowed_ops.items():
            button = QPushButton(func_name)
            button.clicked.connect(lambda _, f=func_str: self.locc_insert_operation(f))
            self.locc_op_buttons_layout.addWidget(button)

        # locc operator type Buttons Layout
        self.locc_operator_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.locc_operator_buttons_layout)

        # Dictionary of allowed functions with formatted strings
        self.locc_allowed_operators = {
            'XGate': 'XGate',
            'HGate': 'HGate',
            'CXGate': 'CXGate'
        }

        # Add function buttons
        for func_name, func_str in self.locc_allowed_operators.items():
            button = QPushButton(func_name)
            button.clicked.connect(lambda _, f=func_str: self.locc_insert_operator(f))
            self.locc_operator_buttons_layout.addWidget(button)

        # Add a button to create the quantum state
        self.create_locc_protocol = QPushButton("Create LOCC Protocol")
        self.create_locc_protocol.clicked.connect(self.handle_create_locc_protocol)
        self.create_locc_protocol.setFixedSize(200,30)
        self.layout.addWidget(self.create_locc_protocol, alignment=Qt.AlignCenter)

        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout.addSpacerItem(self.spacer)

        layout_execution_type = QHBoxLayout()
        execution_type_label = QLabel("Localisable Entanglement Metric:")
        layout_execution_type.addWidget(execution_type_label)
        
        self.select_execution_type = QComboBox()
        self.select_execution_type.addItems(["select execution type...", "upper bound", "lower bound"])
        layout_execution_type.addWidget(self.select_execution_type)
        self.layout.addLayout(layout_execution_type)

        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.handle_execute)
        self.layout.addWidget(execute_button)

    # TODO: add custom gate input functionality
    def handle_add_custom_operator(self):
        print()

    def download_template(self):
        template_content = """
    num_parties: 
    num_qudits: 
    dim: 
    table:
    Amplitude,Basis State
    ,
    locc_table:
    operation,operator,party index,qudit index,condition
    """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Template", "template.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                file.write(template_content)
            QMessageBox.information(self, "Success", "Template downloaded successfully!")

    def upload_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Template", "", "Text Files (*.txt)")
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                data = file.readlines()
            
            # Initialize state for parsing
            current_section = None
            table_data = []
            locc_table_data = []

            for line in data:
                stripped_line = line.strip()

                # Skip empty lines
                if not stripped_line:
                    continue

                # Detect section headers or key-value pairs
                if ":" in stripped_line:
                    key, value = stripped_line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle fields
                    if key == "num_parties":
                        self.num_parties_input.setText(value)
                    elif key == "num_qudits":
                        self.num_qudits_input.setText(value)
                    elif key == "dim":
                        self.dim_input.setText(value)
                    elif key == "table":
                        current_section = "table"
                        table_data = []  # Reset table data
                    elif key == "locc_table":
                        current_section = "locc_table"
                        locc_table_data = []  # Reset locc table data
                else:
                    # Collect table data based on the current section
                    if current_section == "table":
                        table_data.append(stripped_line)
                    elif current_section == "locc_table":
                        locc_table_data.append(stripped_line)

            # Populate the tables
            if table_data:
                self.populate_table(self.table, table_data)
            if locc_table_data:
                self.populate_table(self.locc_table, locc_table_data)

            QMessageBox.information(self, "Success", "Fields populated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload template: {e}")


    def populate_table(self, table_widget, data):
        # Clear any existing content
        table_widget.clear()

        # First line is assumed to be column labels
        column_labels = data[0].split(",")
        table_widget.setColumnCount(len(column_labels))
        table_widget.setHorizontalHeaderLabels(column_labels)

        # Populate rows starting from the second line
        row_data = data[1:]  # Skip the first line (column labels)
        table_widget.setRowCount(len(row_data))
        for row_index, row in enumerate(row_data):
            columns = row.split(",")
            for col_index, value in enumerate(columns):
                table_widget.setItem(row_index, col_index, QTableWidgetItem(value))


    def insert_function(self, func_str):
        # Get the currently selected cell in the table
        row = self.table.currentRow()
        col = self.table.currentColumn()

        if row >= 0 and col == 0:  # Ensure we're in the "Amplitude" column
            current_item = self.table.item(row, col)
            if current_item is None:
                current_item = QTableWidgetItem()
                self.table.setItem(row, col, current_item)
            
            # Insert function text into the selected cell
            current_text = current_item.text()
            if func_str.endswith("()"):
                func_text = func_str[:-1] + ")"  # Ensure we have empty parentheses for cursor placement
            else:
                func_text = func_str
            new_text = f"{current_text}{func_text}"

            current_item.setText(new_text)

            # Place cursor inside the parentheses (e.g., "np.sqrt(|)")
            cursor_position = len(new_text) - 1  # Index of the character before the closing parenthesis
            self.table.editItem(current_item)  # Enter editing mode
            current_item.setText(new_text)  # Update with the new text
            self.table.setCurrentCell(row, col)
            self.table.cellWidget(row, col).setFocus()  # Set focus back to the item

            # Move cursor into the parentheses for immediate editing
            self.table.cellWidget(row, col).setCursorPosition(cursor_position)

    def handle_execute(self):
        try:
            execution_type = self.select_execution_type.currentText()
            if execution_type == "select execution type...":
                raise ValueError("Please select execution type")
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        
        # self.controller.generate_manim_video("Hello, Manim!")
        self.controller.perform_operation("execute_protocol", execution_type)

    
    def locc_insert_operator(self, func_str):
        # Get the currently selected cell in the table
        row = self.locc_table.currentRow()
        col = self.locc_table.currentColumn()

        if row >= 0 and col == 1:  # Ensure we're in the "operator" column
            current_item = self.locc_table.item(row, col)
            if current_item is None:
                current_item = QTableWidgetItem()
                self.locc_table.setItem(row, col, current_item)
            
            # Insert function text into the selected cell
            # current_text = current_item.text()
            current_text = ""
            func_text = func_str
            new_text = f"{current_text}{func_text}"
            current_item.setText(new_text)

    def locc_insert_operation(self, func_str):
        # Get the currently selected cell in the table
        row = self.locc_table.currentRow()
        col = self.locc_table.currentColumn()

        if row >= 0 and col == 0:  # Ensure we're in the "operation type" column
            current_item = self.locc_table.item(row, col)
            if current_item is None:
                current_item = QTableWidgetItem()
                self.locc_table.setItem(row, col, current_item)
            
            # Insert function text into the selected cell
            # current_text = current_item.text()
            current_text = ""
            func_text = func_str
            new_text = f"{current_text}{func_text}"
            current_item.setText(new_text)

    def handle_create_state(self):
        res = self.get_table_data()
        amplitude_list = res[0]
        basis_state_list = res[1]
        self.controller.perform_operation("create_quantum_state", amplitude_list, basis_state_list)
    
    def handle_create_locc_protocol(self):
        # each row in the locc table represents a locc operation
        for row in range(self.locc_table.rowCount()):
            operation_item = self.locc_table.item(row, 0)
            operator_item = self.locc_table.item(row, 1)
            party_index_item = self.locc_table.item(row, 2)
            qudit_index_item = self.locc_table.item(row, 3)
            condition_entry_info = self.locc_table.item(row, 4)
            if operation_item is None or not operation_item.text():
                raise ValueError(f"Missing operation in row {row}.")
            if operator_item is None or not operator_item.text():
                raise ValueError(f"Missing operator in row {row}.")
            if party_index_item is None or not party_index_item.text():
                raise ValueError(f"Missing party index in row {row}.")
            if qudit_index_item is None or not qudit_index_item.text():
                raise ValueError(f"Missing qudit index in row {row}.")
            
            operation_str = operation_item.text()
            operator_str = operator_item.text()

            party = party_index_item.text()
            if not party.isdigit():
                raise ValueError(f"Invalid party index '{party}' in row {row}. Must be digits only.")
            
            qudit = qudit_index_item.text()
            if not qudit.isdigit():
                raise ValueError(f"Invalid qudit index '{qudit}' in row {row}. Must be digits only.")
            
            condition = None
            if operation_str == "conditional":
                cond_info_list = list(map(int, self.condition_entry_info.text().split(',')))
                condition = (cond_info_list[0], cond_info_list[1], cond_info_list[2]) # party, qudit, result
            self.controller.perform_operation("save_locc_operation", int(party), int(qudit), operation_str, operator_str, condition)

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
    
    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def locc_add_row(self):
        row_position = self.locc_table.rowCount()
        self.locc_table.insertRow(row_position)
    
    def locc_remove_row(self):
        current_row = self.locc_table.currentRow()
        if current_row >= 0:
            self.locc_table.removeRow(current_row)

    def handle_generate_state_desc_label_and_k_party(self):
        self.controller.perform_operation("generate_state_desc_label_and_k_party", self.num_parties_input, self.num_qudits_input, self.dim_input)

    def display_message(self, message):
        # Display a message to the user
        QMessageBox.information(self, "Information", message)

    def locc_get_table_data(self):
        # each row in the locc table represents a locc operation
        for row in range(self.locc_table.rowCount()):
            operation_item = self.locc_table.item(row, 0)
            operator_item = self.locc_table.item(row, 1)
            party_index_item = self.locc_table.item(row, 2)
            qudit_index_item = self.locc_table.item(row, 3)
            condition_entry_info = self.locc_table.item(row, 4)
            if operation_item is None or not operation_item.text():
                raise ValueError(f"Missing operation in row {row}.")
            if operator_item is None or not operator_item.text():
                raise ValueError(f"Missing operator in row {row}.")
            if party_index_item is None or not party_index_item.text():
                raise ValueError(f"Missing party index in row {row}.")
            if qudit_index_item is None or not qudit_index_item.text():
                raise ValueError(f"Missing qudit index in row {row}.")
            
            operation_str = operation_item.text()
            operator_str = operator_item.text()

            party = party_index_item.text()
            if not party.isdigit():
                raise ValueError(f"Invalid party index '{party}' in row {row}. Must be digits only.")
            
            qudit = qudit_index_item.text()
            if not qudit.isdigit():
                raise ValueError(f"Invalid qudit index '{qudit}' in row {row}. Must be digits only.")
            
            condition = None
            if operation_str == "conditional":
                cond_info_list = list(map(int, self.condition_entry_info.text().split(',')))
                condition = (cond_info_list[0], cond_info_list[1], cond_info_list[2]) # party, qudit, result
        self.controller.perform_operation("save_locc_step", int(party), int(qudit), operation_str, operator_str, condition)
    
    def get_table_data(self):
        # Allowed functions for user input
        allowed_functions = {
            'np': np,
            'sqrt': np.sqrt,
            'pi': np.pi,
            'sin': np.sin,
            'cos': np.cos,
            'exp': np.exp,
            'j': 1j,
            'I': 1j,
        }

        amplitude_list = []
        basis_state_list = []

        for row in range(self.table.rowCount()):
            amplitude_item = self.table.item(row, 0)
            basis_state_item = self.table.item(row, 1)
            if amplitude_item is None or not amplitude_item.text():
                raise ValueError(f"Missing amplitude in row {row}.")
            if basis_state_item is None or not basis_state_item.text():
                raise ValueError(f"Missing basis state in row {row}.")
            
            amplitude_str = amplitude_item.text()
            print(amplitude_str)
            amplitude = eval(amplitude_str, {"__builtins__": {}}, allowed_functions)

            basis_state = basis_state_item.text()
            if not basis_state.isdigit():
                raise ValueError(f"Invalid basis state '{basis_state}' in row {row}. Must be digits only.")

            amplitude_list.append(amplitude)
            basis_state_list.append(basis_state)

        return (amplitude_list, basis_state_list)