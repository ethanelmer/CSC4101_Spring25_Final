import tkinter as tk
from tkinter import scrolledtext, messagebox
from lexer import Lexer
from parser import Parser, ParserError

class ParserGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Recursive Descent Parser")

        # Text area
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=15)
        self.text_area.pack(padx=10, pady=10)

        # Buttons frame
        button_frame = tk.Frame(master)
        button_frame.pack()

        parse_button = tk.Button(button_frame, text="Parse", command=self.on_parse)
        parse_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(button_frame, text="Clear", command=self.on_clear)
        clear_button.pack(side=tk.LEFT, padx=5)

    def on_parse(self):
        source_code = self.text_area.get("1.0", tk.END)
        try:
            lexer = Lexer(source_code)
            parser = Parser(lexer)
            parser.parse()
            messagebox.showinfo("Result", "Parsing succeeded! No errors.")
        except (ParserError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def on_clear(self):
        self.text_area.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
