import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import json
import os
import sys

INVENTORY_FILE_PATH = r"template.json"
VERSION = "1.1"

class Application:
    def __init__(self):
        self._window = tk.Tk()
        self._window.title("RJ45-InventoPy")
        self._window.protocol("WM_DELETE_WINDOW", self._confirm_quit_without_saving)
        self._window.resizable(False, False)
        self._data = None
        self._filepath = None
        self._text_vars = {}

    def load_data(self, filepath):
        self._filepath = filepath
        try:
            with open(self._filepath, 'r') as file:
                self._data = json.load(file)
        except (OSError, FileNotFoundError):
            self._display_error_message()
            exit()
        
    def save_data(self, filepath):
        try:
            with open(filepath, 'w') as file:
                json.dump(self._data, file, indent=4)
            return 1
        except (OSError, FileNotFoundError):
            self._display_error_message()
            return 0
    
    def _display_error_message(self):
        msgbox.showerror("Error", "Server is not accessible.\n\nPlease check your network connection and try again.\nIf the problem persists, contact your network administrator.", type=msgbox.OK)

    def _display_help_message(self):
        msgbox.showinfo("Help", f"RJ45-InventoPy\nv{VERSION}\n\nClick to add or remove 1.\nShift+Click to add or remove 10.\nDon't forget to save your changes.\n\n© Dylan TAILDEMAN - 2024", type=msgbox.OK)

    def _update_value(self, length, color, incr):
        self._data[length][color] += incr
        if self._data[length][color] < 0: self._data[length][color] = 0
        self._update_textvariable(length, color)
        self._update_total(length)

    def _update_textvariable(self, length, color):
        var = self._text_vars[length][color]
        var.set(str(self._data[length][color]))

    def _update_total(self, length):
        total = sum(self._data[length].values())
        self._text_vars[length]['total'].set(f"{total}")

    def _create_elements(self, frame, length, color):
        decrease = ttk.Button(master=frame, text="-", width=3)
        decrease.pack(side=tk.LEFT)
        decrease.bind("<Button-1>", lambda event: self._update_value(length, color, -1))
        decrease.bind("<Shift-Button-1>", lambda event: self._update_value(length, color, -10))
        
        ttk.Label(
            master=frame,
            textvariable=self._text_vars[length][color],
            width=5,
            background=color,
            anchor='center'
        ).pack(side=tk.LEFT)
        
        increase = ttk.Button(master=frame, text="+", width=3)
        increase.pack(side=tk.LEFT, padx=(0, 5))
        increase.bind("<Button-1>", lambda event: self._update_value(length, color, 1))
        increase.bind("<Shift-Button-1>", lambda event: self._update_value(length, color, 10))

    def _draw_table(self):
        for length, values in self._data.items():
            frame = ttk.Frame(master=self._window, padding=(5, 5))
            frame.pack(side=tk.TOP, fill=tk.X)

            # Initialize dictionary for textvars
            self._text_vars[length] = {}
            
            ttk.Label(master=frame, text=f"{length}: >", width=10, anchor="e", padding=(0, 0, 10, 0)).pack(side=tk.LEFT)
            
            # Calculating total
            total = sum(values.values())
            self._text_vars[length]['total'] = tk.StringVar(value=f"{total}")
            ttk.Label(
                master=frame, 
                textvariable=self._text_vars[length]['total'], 
                width=10, 
                anchor="center"
            ).pack(side=tk.LEFT)
            
            # Create labels and buttons for each color
            for color in values.keys():
                self._text_vars[length][color] = tk.StringVar(value=str(values.get(color, 0)))
                label_frame = ttk.Frame(master=frame)
                label_frame.pack(side=tk.LEFT)
                self._create_elements(label_frame, length, color)
                
        # Save & Quit and Quit without Saving buttons
        control_frame = ttk.Frame(master=self._window, padding=(5, 5))
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="?", width=3, command=self._display_help_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save & Quit", command=self._save_and_quit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Quit without Saving", command=self._confirm_quit_without_saving).pack(side=tk.RIGHT, padx=5)
    
    def _save_and_quit(self):
        if self.save_data(self._filepath):
            self._window.destroy()
    
    def _confirm_quit_without_saving(self):
        if msgbox.askyesno(title = "Quit without Saving", message = "Your changes won't be saved.\nAre you sure you want to quit?", icon="warning"):
            self._window.destroy()
    
    def run(self):
        """
        Start the Tkinter window mainloop.
        """
        self._draw_table()
        self._window.mainloop()

if __name__ == "__main__":
    app = Application()
    app.load_data(INVENTORY_FILE_PATH)
    app.run()