import tkinter as tk

window = tk.Tk()
window.title("My First App")
window.geometry("300x200")

label = tk.Label(window, text="Hello!", font=("Arial", 16))
label.pack(pady=20)

def say_hello():
    label.config(text="Hello, Paul!")

button = tk.Button(window, text="Click me", command=say_hello)
button.pack()

window.mainloop()