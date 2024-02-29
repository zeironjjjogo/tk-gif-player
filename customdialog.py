import tkinter as tk
from tkinter import simpledialog

class AskNewFileProperty(simpledialog.Dialog):
    def __init__(self, parent: tk.Misc | None = None, title: str | None = None) -> None:
        self.result = False
        super().__init__(parent, title)

    def body(self, master: tk.Frame) -> None:
        self.ask_name = tk.Entry(master, width=27)

        self.ask_width = tk.Entry(master, width=7)
        self.ask_height = tk.Entry(master, width=7)
        self.show_err = tk.Label(master, width=33, fg="red")

        self.ask_width.insert(0, "256")
        self.ask_height.insert(0, "256")

        tk.Label(master, text="ファイル名", width=7).grid(column=0, row=0)
        self.ask_name.grid(column=1, row=0, columnspan=3)

        tk.Label(master, text="サイズ", width=7).grid(column=0, row=1)
        self.ask_width.grid(column=1, row=1)
        tk.Label(master, text="x", width=7).grid(column=2, row=1)
        self.ask_height.grid(column=3, row=1)

        self.show_err.grid(column=0, row=2, columnspan=4)

    def apply(self) -> None:
        name = self.ask_name.get()
        width = int(self.ask_width.get())
        height = int(self.ask_height.get())

        self.result = name, (width, height)

    def validate(self) -> bool:
        if len(self.ask_name.get()) == 0:
            self.show_err.configure(text="ファイル名を入力してください。")
            return False
        
        elif len(self.ask_width.get()) == 0 or len(self.ask_height.get()) == 0:
            self.show_err.configure(text="サイズを入力してください。")
            return False
        
        try:
            x = int(self.ask_width.get())
            y = int(self.ask_height.get())

        except ValueError as error:
            self.show_err.configure(text="サイズは半角数字のみで入力してください。")
            return False
        
        return True

    def get(self) -> tuple[str, tuple[int, int]]:
        return self.result


class AskNewFps(simpledialog.Dialog):
    def __init__(self, parent: tk.Misc | None = None, title: str | None = None) -> None:
        self.result = False
        super().__init__(parent, title)

    def body(self, master: tk.Frame) -> None:
        self.ask_fps = tk.Entry(master)
        self.show_err = tk.Label(master, fg="red")
        
        tk.Label(master, text="fps").grid(column=0, row=0)
        self.ask_fps.grid(column=1, row=0)
        self.show_err.grid(column=0, row=1, columnspan=2)

    def apply(self) -> None:
        self.result = float(self.ask_fps.get())

    def validate(self) -> bool:
        if len(fps := self.ask_fps.get()) == 0:
            self.show_err.configure(text="数値を入力して下さい。")
            return False
        
        try:
            fps = float(fps)

        except ValueError as error:
            self.show_err.configure(text="数字以外が含まれています。")
            return False
        
        return True

    def get(self) -> float:
        return self.result