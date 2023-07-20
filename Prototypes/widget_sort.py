import customtkinter as ctk


class MainScreen(ctk.CTk):
    def __init__(self):

        super().__init__()

        self.option = ctk.CTkComboBox(self,
                                      values=["Ascending", "Descending"],
                                      command=self.sort_change,
                                      width=100)
        self.labela = ctk.CTkLabel(self,
                                   text="A",
                                   width=100
                                   )
        self.labelb = ctk.CTkLabel(self,
                                   text="B",
                                   width=100
                                   )
        self.labelc = ctk.CTkLabel(self,
                                   text="C",
                                   width=100
                                   )
        self.labeld = ctk.CTkLabel(self,
                                   text="D",
                                   width=100
                                   )
        self.format_asc()

    def format_asc(self):
        self.option.grid(row=0, column=0)
        self.labela.grid(row=1, column=0)
        self.labelb.grid(row=1, column=1)
        self.labelc.grid(row=1, column=2)
        self.labeld.grid(row=1, column=3)

    def format_desc(self):
        self.option.grid(row=0, column=0)
        self.labela.grid(row=1, column=3)
        self.labelb.grid(row=1, column=2)
        self.labelc.grid(row=1, column=1)
        self.labeld.grid(row=1, column=0)

    def sort_change(self, choice):
        if choice == "Ascending":
            self.format_asc()
        else:
            self.format_desc()


gui = MainScreen()
gui.mainloop()
