from tkinter import Canvas, PhotoImage, filedialog
from pathlib import Path
from typing import Literal

from model import Model
from customdialog import AskNewFileProperty, AskNewFps


class Controller():

    model: Model

    state: list[dict[str, tuple[int, int]]]
    current_state: int

    def __init__(self) -> None:
        self.model = Model()

        self.init_state_machine()
        self.model.set_fps(24)

    def init_canvas(self, canvas: Canvas) -> None:
        self.model.init_canvas(canvas)
    
    def bind_sync_func(self, func: object) -> None:
        self.model.bind_sync_func(func)

    def init_state_machine(self) -> None:
        self.state = [
            {"set": (1, 1), "ins": (0, 0), "save": (0, 0), "play": (0, 0), "stop":(0, 0), "edit": (0, 0)}, # when none
            {"set": (1, 1), "ins": (1, 1), "save": (1, 1), "play": (1, 2), "stop":(0, 1), "edit": (1, 1)}, # when idle
            {"set": (1, 1), "ins": (1, 2), "save": (1, 2), "play": (0, 2), "stop":(1, 1), "edit": (1, 2)}, # when play
        ]

        self.current_state = 0

    def get_icons(self) -> dict[str, PhotoImage]:
        return self.model.get_icons()

    def is_transfer_to_state(self, command: Literal["set", "ins", "save", "play", "stop", "edit"]) -> bool:
        is_vailed, next_state = self.state[self.current_state][command]

        print(f"state: {command}: {self.current_state} > {next_state}")

        self.current_state = next_state

        return is_vailed

    def set_fps(self) -> float:
        fps = AskNewFps(title="fpsの変更").get()

        if not fps:
            raise TypeError("'fps' must int | float.")

        self.model.set_fps(fps)

        return fps
    
    def create_gif(self) -> tuple[str, tuple[int, int]]:
        filename, size = AskNewFileProperty(title="新しいgifファイル").get()
        
        path = Path(filename)

        if path.suffix == "":
            path = path.with_suffix(".gif")

        self.model.create_gif(size)

        self.current_path = path

        return path.name, size
    
    def open_gif(self) -> tuple[int, str, list[str], tuple[int, int]]:
        path = Path(filedialog.askopenfilename(filetypes=[("GIF", "*.gif"), ("APNG", "*.apng")]))

        size, frames_name = self.model.load_gif(path)

        n_frames = self.model.get_n_frames()

        self.current_path = path

        return n_frames, path.name, frames_name, size 
    
    def ins_images(self) -> tuple[int, list[str]]:
        filenames = filedialog.askopenfilenames()

        names: list[str] = []
        
        for filename in filenames:
            path = Path(filename)

            self.model.ins_image("end", path)

            names.append(path.name)

        n_frames = self.model.get_n_frames()

        return n_frames, names

    def save_gif(self) -> None:
        types = [
            ("GIF", "*.gif"), ("APNG", "*.apng")
        ]

        path = Path(filedialog.asksaveasfilename(defaultextension=".gif", filetypes=types, initialfile=self.current_path))

        self.model.save_as_gif(path)

    def export_frame(self, index: int, name: str) -> None:
        types = [
            ("GIF", "*.gif"), ("PNG", "*.png"), ("JPEG", ["*.jpg", "*.jpeg"])
        ]

        initialfilename = f"{name}"

        path = Path(filedialog.asksaveasfilename(defaultextension=".gif", filetypes=types, initialfile=initialfilename))

        self.model.save_frame(index, path)

    def animation(self, command: Literal["play", "stop", "pause"]) -> None:
        if command == "play":
            self.model.request_stop(0)
            self.model.start_loop()

        elif command == "stop":
            self.model.request_stop(1)

        elif command == "pause":
            self.model.request_stop(2)

    def display_frame(self, index: int) -> None:
        self.model.display_frame(index)

    def delete_frame(self, index: int) -> int:
        self.model.del_frame(index)

        n_frames = self.model.get_n_frames()

        return n_frames
    
    def replace_frame(self, index: int, to: Literal["Up", "Down"]) -> int:
        ins_index = index

        if to == "Up":
            ins_index -= 1

        elif to == "Down":
            ins_index += 1

        self.model.replace_frame(index, ins_index)

        return ins_index