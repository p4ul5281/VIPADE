import tkinter as tk

# colors (hex codes)
BG = "#1b314b"       # deep purple background
HEADER = "#7c3aed"   # bright purple
LIST_BG = "#312e81"  # list background
GREEN = "#22C55e"
RED = "#ef4444"
ORANGE = "#f59e0b"
PINK = "#ec4899"

window = tk.Tk()
window.title("my to-do list")
window.geometry("380x560")
window.configure(bg=BG)

header = tk.Label(window, text="my to-do list", font=("Arial", 22, "bold"), bg=HEADER, fg="white", pady=14)
header.pack(fill="x")

entry = tk.Entry(window, font=("Arial", 14), bg="white", fg="#222", relief="flat", justify="center")
entry.pack(pady=15, padx=20, ipady=8, fill="x")

listbox = tk.Listbox(window, font=("Arial", 14), bg=LIST_BG, fg="white", selectbackground=PINK, selectforeground="white", height=10, relief="flat", highlightthickness=0, activestyle="none")
listbox.pack(padx=20, fill="x")
info = tk.Label(window, text="0 tasks", font=("Arial", 11), bg=BG, fg="#a5b4fc")
info.pack(pady= 8)

def update_count():
    info.config(text=f"{listbox.size()} tasks")

def add_task():
    task = entry.get()
    if task != "":
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
        update_count()

def delete_task():
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected[0])
        update_count()

def done_task():
    selected = listbox.curselection()
    if selected:
        i=selected[0]
        text = listbox.get(i)  
        if not text.startswitch("✔ "):
            listbox.delete(i)
            listbox.insert(i, "✔ " + text)
            listbox.itemconfig(i, fg="#86efac")

def make_button(text, color, command):
    tk.Button(window, text=text, command=command, bg=color, fg="white", font=("Arial", 13,"bold"),relief="flat", cursor="hand2",activebackground=color, width=18).pack(pady=4)

make_button("Add Task",GREEN, add_task)
make_button("Mark as Done",ORANGE, done_task)
make_button("Delete Task",RED, delete_task)

window.bind("<Return>", lambda event: add_task())

window.mainloop()
