import io
import tkinter as tk


class TextBoxRedirect(io.StringIO):
    """
    Redirects stdout to a tkinter Text widget.
    """

    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def write(self, text):
        self.textbox.config(state="normal")
        self.textbox.insert(tk.END, text)
        self.textbox.config(state="disabled")
        self.textbox.see(tk.END)
        # Automatically scroll to the end of the output

    def flush(self):
        pass  # Overridden to comply with `io.StringIO`
