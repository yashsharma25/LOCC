🚀 Getting Started

This project is a Python-based GUI application built with Manim, PyQt5, and scientific computing libraries. It supports development on macOS, Linux, and Windows.
📦 Installation Options
Option 1: Conda (Recommended)

Cross-platform and easiest if you're working with GUI apps or scientific libraries.

# Clone the repository
git clone https://github.com/yashsharma25/LOCC.git
cd your-repo

# Create environment
conda env create -f environment.yml
conda activate manim_env

If you encounter ModuleNotFoundError: No module named 'PyQt5', run:

# Ensure PyQt5 bindings are present
conda install -c conda-forge pyqt

Option 2: Pip (For Virtualenv or Minimal Setups)

Use this if you're not using Conda. Be aware that PyQt5 and some dependencies may need additional platform-specific configuration.

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

🏁 Running the App

python main.py

🧪 Developer Notes

    requirements.txt: Use for pip-based installs (e.g. Docker, CI, Heroku).

    environment.yml: Recommended for development. Ensures compatibility with GUI libraries and system-level dependencies.

    If you're contributing or debugging across platforms, prefer conda for smoother setup.

