import tkinter as tk
from gui.code_smell_detector_gui import CodeSmellDetectorGUI


class CodeSmileGUI:
    """
    Application controller for initializing and running the GUI.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.gui = CodeSmellDetectorGUI(self.root)

    def run(self):
        """
        Runs the GUI application.
        """
        self.root.mainloop()


if __name__ == "__main__":
    app = CodeSmileGUI()
    app.run()
