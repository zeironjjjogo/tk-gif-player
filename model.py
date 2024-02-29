from pathlib import Path
from PIL import Image, ImageOps, ImageTk
from tkinter import Canvas, PhotoImage
from time import sleep
from threading import Thread
from typing import Literal
from configparser import ConfigParser

class Model():

    images: list[Image.Image]
    frames: list[ImageTk.PhotoImage]
    size: tuple[int, int]
    n_frames: int
    current_frame: int
    before: int | None
    stop_request: int

    canvas: Canvas
    fps: float

    def __init__(self) -> None:
        self.images = []
        self.frames = []
        self.size = (0, 0)
        self.n_frames = 0
        self.current_frame = 0
        self.stop_request = 0
        self.before = None

    def init_canvas(self, canvas: Canvas) -> None:
        self.canvas = canvas

    def bind_sync_func(self, func: object) -> None:
        self.bound_func = func

    def get_icons(self) -> dict[str, PhotoImage]:
        c = ConfigParser()
        c.read("./icons.ini", encoding="utf-8")
        icons = c.items("icons")

        ret_dict: dict[str, PhotoImage] = {}

        for name, value in icons:
            ret_dict[name] = PhotoImage(data=value)

        return ret_dict

    def clear_configure(self) -> None:
        self.images = []
        self.frames = []
        self.size = (0, 0)
        self.n_frames = 0
        self.current_frame = 0
        self.stop_request = 0
        self.before = None

    def set_fps(self, fps: float) -> None:
        self.fps = fps

    def get_n_frames(self) -> int:
        return self.n_frames
    
    def get_canvas_size(self) -> tuple[int, int]:
        return self.canvas.winfo_width(), self.canvas.winfo_height()

    def create_gif(self, size: tuple[int, int]) -> None:
        self.clear_configure()

        self.size = size

    def load_gif(self, path: Path) -> tuple[tuple[int, int], list[str]]:
        image = Image.open(path)

        self.clear_configure()

        self.size = image.size

        frames_name: list[str] = []

        for i in range(image.n_frames):
            image.seek(i)
            croped = image.crop()

            self.ins_frame(i, croped)

            frames_name.append(f"{path.stem}_{i}")

        self.display_frame(0)

        return image.size, frames_name
    
    def ins_image(self, index: int | Literal["end"], path: Path) -> None:
        image = Image.open(path)

        image = self.adjust_image(image)

        self.ins_frame(index, image)

    def adjust_image(self, image: Image.Image) -> Image.Image:
        width_prod, height_prod = image.width / self.size[0], image.height / self.size[1]

        scale = width_prod if width_prod > height_prod else height_prod

        image = ImageOps.scale(image, 1 / scale)
        image = ImageOps.pad(image, self.size)

        return image
    
    def ins_frame(self, index: int | Literal["end"], image: Image.Image) -> None:
        if index == "end":
            index = self.n_frames

        self.images.insert(index, image)
        self.frames.insert(index, ImageTk.PhotoImage(image=image))
        self.n_frames += 1
        
    def del_frame(self, index: int) -> None:
        del self.images[index]
        del self.frames[index]
        self.n_frames -= 1

    def save_frame(self, index: int, path: Path) -> None:
        image = self.images[index]
        image.save(path)

    def save_as_gif(self, path: Path) -> None:
        images = self.images
        topimg = images.pop(0)
        topimg.save(path, save_all=True, append_images=images, optimize=False, loop=0, comment="test")

    def start_loop(self):
        thread = Thread(target=self.loop_gif, daemon=True)
        thread.start()

    def loop_gif(self) -> None:
        index = self.current_frame

        while self.stop_request == 0:
            self.display_frame(index)
            
            self.bound_func(self.current_frame)

            sleep(1 / self.fps)

            if index < self.n_frames - 1:
                index += 1

            else:
                index = 0
        
        if self.stop_request == 0:
            raise ValueError("Invaild request. (Not 1 or 2)")

        elif self.stop_request == 1:
            self.display_frame(0)

        elif self.stop_request == 2:
            pass

        else:
            raise ValueError("Invaild request. (Not 1 or 2)")

    def request_stop(self, stop: Literal[0, 1, 2]) -> None:
        self.stop_request = stop

    def display_frame(self, index: int) -> None:
        w, h = self.get_canvas_size()

        before = self.before
        self.before = self.canvas.create_image(w/2, h/2, image=self.frames[index])
        self.canvas.delete(before)

        self.current_frame = index

    def replace_frame(self, index: int, ins_index: int) -> None:
        image = self.images[index]

        self.del_frame(index)

        self.ins_frame(ins_index, image)