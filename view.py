import tkinter as tk

from controller import Controller

class View():

    icon_images: dict[str, tk.PhotoImage]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("GIFプレイヤー")
        self.root.protocol("WM_DELETE_WINDOW", self.event_destroy)

        self.controller = Controller()
        
        self.init_icons()

        menu = tk.Menu(self.root, tearoff=False)
        file_menu = tk.Menu(menu, tearoff=False)
        self.edit_menu = tk.Menu(menu, tearoff=False)
        config_menu = tk.Menu(menu, tearoff=False)

        menu.add_cascade(label="ファイル(F)", menu=file_menu, underline=5)
        menu.add_cascade(label="編集(E)", menu=self.edit_menu, underline=3)
        menu.add_cascade(label="設定(S)", menu=config_menu, underline=3)

        file_menu.add_command(label="gifを新規作成", image=self.icon_images["new"], compound=tk.LEFT, command=self.event_create, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="gifを開く", image=self.icon_images["open"], compound=tk.LEFT, command=self.event_open, accelerator="Ctrl+O")
        file_menu.add_command(label="画像を開く", image=self.icon_images["ins"], compound=tk.LEFT, command=self.event_insert, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="gifを保存", image=self.icon_images["save"], compound=tk.LEFT, command=self.event_save, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="現在のフレームをエクスポート", command=self.event_export)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.event_destroy)

        event_up = tk.Event()
        event_down = tk.Event()

        event_up.keysym = "Up"
        event_down.keysym = "Down"

        self.edit_menu.add_command(label="一層上へ", command=lambda :self.event_replace(event_up), accelerator="Alt+UpArrow")
        self.edit_menu.add_command(label="一層下へ", command=lambda :self.event_replace(event_down), accelerator="Alt+DownArrow")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="フレームを削除", image=self.icon_images["del"], compound=tk.LEFT, command=self.event_delete, accelerator="Delete")

        config_menu.add_cascade(label="フレームレート", command=self.event_change_fps)

        self.root.config(menu=menu)



        self.n_frames_fmt = "フレーム数: {}"
        self.size_fmt = "サイズ: {} x {}"
        self.fps_fmt = "{}fps"



        self.root_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, showhandle=True)


        self.player_frm = tk.Frame(self.root_pane)

        self.canvas = tk.Canvas(self.player_frm, bg="black")
        self.playbtn = tk.Button(self.player_frm, image=self.icon_images["play"], width=40, command=self.event_play)
        self.stopbtn = tk.Button(self.player_frm, image=self.icon_images["stop"], width=20, command=self.event_stop)
        self.n_frames_lab = tk.Label(self.player_frm, relief=tk.SUNKEN, text=self.n_frames_fmt.format(1))
        self.size_lab = tk.Label(self.player_frm, relief=tk.SUNKEN, text=self.size_fmt.format(1,1))
        self.fps_lab = tk.Label(self.player_frm, relief=tk.SUNKEN, text=self.fps_fmt.format(24.00))


        self.listbox_frm = tk.Frame(self.root_pane)

        self.listbox = tk.Listbox(self.listbox_frm)
        self.listbox_scroll = tk.Scrollbar(self.listbox_frm, command=self.listbox.yview, orient=tk.VERTICAL)
        self.listbox.configure(yscrollcommand=self.listbox_scroll.set)



        self.root_pane.pack(expand=True, fill=tk.BOTH)


        self.root_pane.add(self.player_frm)

        self.canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.playbtn.pack(side=tk.LEFT)
        self.stopbtn.pack(side=tk.LEFT)
        self.n_frames_lab.pack(fill=tk.Y, side=tk.LEFT)
        self.size_lab.pack(fill=tk.Y, side=tk.LEFT)
        self.fps_lab.pack(fill=tk.Y, side=tk.LEFT)
        tk.Label(self.player_frm, relief=tk.SUNKEN).pack(expand=True, fill=tk.BOTH, side=tk.LEFT)


        self.root_pane.add(self.listbox_frm)

        self.listbox.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        self.listbox_scroll.pack(fill=tk.Y, side=tk.LEFT)



        self.root.bind("<space>", self.event_play)
        self.root.bind("<Delete>", self.event_delete)
        self.root.bind("<Control-KeyPress>", self.ctrl_bind)
        self.listbox.bind("<Button-3>", lambda event: self.edit_menu.post(event.x_root, event.y_root))
        self.listbox.bind("<Alt-KeyPress>", self.alt_bind)
        self.listbox.bind("<<ListboxSelect>>", self.event_listbox_selected)

        self.init_canvas()
        self.bind_sync_func()

    def init_canvas(self) -> None:
        self.controller.init_canvas(self.canvas)

    def init_icons(self) -> None:
        self.icon_images = self.controller.get_icons()

    def bind_sync_func(self) -> None:
        self.controller.bind_sync_func(self.set_listbox_selection)

    def set_listbox_selection(self, index: int) -> None:
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def set_labels(self, title: str | None = None, n_frames: int | None = None, size: tuple[int, int] | None = None, fps: float | None = None) -> None:
        if title:
            self.root.title(title)

        if n_frames:
            self.n_frames_lab.configure(text=self.n_frames_fmt.format(n_frames))

        if size:
            self.size_lab.configure(text=self.size_fmt.format(size[0], size[1]))

        if fps:
            self.fps_lab.configure(text=self.fps_fmt.format(fps))

    def ctrl_bind(self, event: tk.Event) -> None:
        if (key := event.keysym) == "n":
            self.event_create()

        elif key == "o":
            self.event_open()

        elif key == "O":
            self.event_insert()

        elif key == "S":
            self.event_save()

    def alt_bind(self, event: tk.Event) -> None:
        if (key := event.keysym) in ("Up", "Down"):
            self.event_replace(event)

    def event_create(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("set"):
            filename, size = self.controller.create_gif()

            self.set_labels(title=filename, n_frames=0, size=size)
            self.listbox.delete(0, tk.END)

    def event_open(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("set"):
            n_frames, filename, framenames, size = self.controller.open_gif()

            self.set_labels(title=filename, n_frames=n_frames, size=size)
            self.listbox.delete(0, tk.END)

            for framename in framenames:
                self.listbox.insert(tk.END, framename)

    def event_insert(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("ins"):
            n_frames, filenames = self.controller.ins_images()

            self.set_labels(n_frames=n_frames)

            for filename in filenames:
                self.listbox.insert(tk.END, filename)

    def event_save(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("save"):
            self.controller.save_gif()

    def event_export(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("save"):
            index = self.listbox.curselection()[0]
            name = self.listbox.get(index)
            self.controller.export_frame(index, name)

    def event_play(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("play"):
            self.controller.animation("play")
            self.playbtn.configure(image=self.icon_images["pause"])

        elif self.controller.is_transfer_to_state("stop"):
            self.controller.animation("pause")
            self.playbtn.configure(image=self.icon_images["play"])

    def event_stop(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("stop"):
            self.controller.animation("stop")
            self.playbtn.configure(image=self.icon_images["play"])
        
        else:
            self.controller.display_frame(0)
        
        self.set_listbox_selection(0)

    def event_listbox_selected(self, event: tk.Event = None) -> None:
        index = self.listbox.curselection()[0]

        self.controller.display_frame(index)

    def event_replace(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("edit"):
            index = self.listbox.curselection()[0]

            ins_index = self.controller.replace_frame(index, event.keysym)

            title = self.listbox.get(index)

            self.listbox.delete(index)

            self.listbox.insert(ins_index, title)
            self.set_listbox_selection(ins_index)
            self.listbox.event_generate("<<ListboxSelect>>")

    def event_delete(self, event: tk.Event = None) -> None:
        if self.controller.is_transfer_to_state("edit"):
            index = self.listbox.curselection()[0]
            n_frames = self.controller.delete_frame(index)

            self.set_labels(n_frames=n_frames)
            self.listbox.delete(index)

            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)

    def event_change_fps(self) -> None:
        new_fps = self.controller.set_fps()

        self.set_labels(fps=new_fps)
        
    def event_destroy(self) -> None:
        print("destroy")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    View(root)
    root.mainloop()