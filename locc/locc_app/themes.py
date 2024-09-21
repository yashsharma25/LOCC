def get_light_mode_stylesheet():
    return """
    QWidget {
        background-color: white;
        color: black;
    }
    QPushButton {
        background-color: lightgray;
        color: black;
    }
    QLineEdit {
        background-color: white;
        color: black;
    }
    QLabel {
        color: black;
    }
    QScrollArea {
        background-color: white;
    }
    QSlider::groove:horizontal {
        background: lightgray;
    }
    QSlider::handle:horizontal {
        background: darkgray;
    }
    """

def get_dark_mode_stylesheet():
    return """
    QWidget {
        background-color: #2E2E2E;
        color: white;
    }
    QPushButton {
        background-color: #444444;
        color: white;
    }
    QLineEdit {
        background-color: #555555;
        color: white;
    }
    QLabel {
        color: white;
    }
    QScrollArea {
        background-color: #2E2E2E;
    }
    QSlider::groove:horizontal {
        background: #555555;
    }
    QSlider::handle:horizontal {
        background: #777777;
    }
    """
