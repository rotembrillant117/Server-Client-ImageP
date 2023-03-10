import customtkinter as tk
from tkinter import messagebox
from client import handle_request
import os
from constants import IMG_EXTENSIONS, VID_EXTENSIONS, GS, PB


class GuiApp(tk.CTk):
    """
    A simple Gui app that can run client.py
    """

    def __init__(self):
        super().__init__()
        tk.set_appearance_mode("dark")
        tk.set_default_color_theme("dark-blue")
        self.geometry("500x350")

        # Tab menu
        self.tabview = tk.CTkTabview(self, width=250)
        self.tabview.pack(pady=20, padx=20)
        self.tabview.add(GS)
        self.tabview.add(PB)
        self.tabview.tab(GS).grid_columnconfigure(0, weight=1)
        self.tabview.tab(PB).grid_columnconfigure(0, weight=1)
        self.send_to_server_btn = tk.CTkButton(self.tabview, text="Send", command=self.get_input)
        self.send_to_server_btn.grid(row=4, column=0, padx=20, pady=20)

        # Gray-Scale
        self.gs_menu = tk.CTkOptionMenu(self.tabview.tab(GS), dynamic_resizing=False,
                                                        values=[".mp4 file", "Image File"])
        self.gs_menu.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.gs_entry = tk.CTkEntry(self.tabview.tab(GS), placeholder_text="File Path")
        self.gs_entry.grid(row=1, column=0, padx=20, pady=(20, 10))

        # Pyramid-Blending
        self.pb_entry_1 = tk.CTkEntry(self.tabview.tab(PB), placeholder_text="First Image Path")
        self.pb_entry_1.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.pb_entry_2 = tk.CTkEntry(self.tabview.tab(PB), placeholder_text="Second Image Path")
        self.pb_entry_2.grid(row=2, column=0, padx=20, pady=(20, 10))

    def get_input(self):
        """
        This function gets the current tab that is selected
        :return:
        """
        cur_tab = self.tabview.get()
        if cur_tab == GS:
            self.handle_gray_scale()
        else:
            self.handle_pyr_blend()

    def handle_gray_scale(self):
        """
        This function handles a Gray-Scale request
        :return:
        """
        cur_menu = self.gs_menu.get()
        if cur_menu == ".mp4 file":
            expected_extensions = VID_EXTENSIONS
        else:
            expected_extensions = IMG_EXTENSIONS
        file_info = self.get_file_info(self.gs_entry.get())
        if not self.check_file_info(file_info, expected_extensions):
            messagebox.showinfo(title="Error", message="Invalid File")
            return
        handle_request(GS, [file_info])

    def handle_pyr_blend(self):
        """
        This function handels a Pyramid Blending request
        :return:
        """
        file_info_1 = self.get_file_info(self.pb_entry_1.get())
        file_info_2 = self.get_file_info(self.pb_entry_2.get())
        if not self.check_file_info(file_info_1, IMG_EXTENSIONS) or \
                not self.check_file_info(file_info_2, IMG_EXTENSIONS):
            messagebox.showinfo(title="Error", message="Invalid File")
            return
        handle_request(PB, [file_info_1, file_info_2])

    def get_file_info(self, file_path):
        """
        This function retrieves file information
        :param file_path: the path to the file
        :return:
        """
        if not os.path.isfile(file_path):
            return []
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(file_name)
        return [file_path, file_extension, file_size]

    def check_file_info(self, file_info, expected_extensions):
        """
        This function checks the validity of the file information
        :param file_info:
        :param expected_extensions:
        :return:
        """
        if len(file_info) != 3:
            return False
        if file_info[1] not in expected_extensions:
            return False
        return True

if __name__ == '__main__':
    app = GuiApp()
    app.mainloop()


