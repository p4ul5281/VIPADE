import tkinter as tk 

window = tk.Tk()
window.title("calculator")
window.geometry("300x400")

entry1 = tk.Entry(window, font=("Arial", 16))
entry1.pack(pady=10)

entry2 = tk.Entry(window, font=("Arial", 16))
entry2.pack(pady=10)

result = tk.Label(window, text="Result:", font=("Arial", 18))
result.pack(pady=10)

def add():
    try:
        a = float(entry1.get())
        b = float(entry2.get())
        result.config(text=f"Result: {a + b:,.15g}")
    except ValueError:
        result.config(text="Enter two numbers")

def subtract():
    try:
        a = float(entry1.get())
        b = float(entry2.get())
        result.config(text=f"Result: {a - b:g:,.15g}")
    except ValueError:
        result.config(text="Enter two numbers")
    
def multiply():
    try:
        a = float(entry1.get())
        b = float(entry2.get())
        result.config(text=f"Result: {a * b:,.15g}")
    except ValueError:
        result.config(text="Enter two numbers")

def divide():
    try:
        a = float(entry1.get())
        b = float(entry2.get())
        if b == 0:
            result.config(text="Cannot divide by zero")
        else:
            result.config(text=f"Result: {a / b:g:,.15g}")
    except ValueError:
        result.config(text="Enter two numbers")

frame = tk.Frame(window)
frame.pack(pady=10)

tk.Button(frame, text="+", width=4, command=add).pack(side="left", padx=3)
tk.Button(frame, text="-", width=4, command=subtract).pack(side="left", padx=3)
tk.Button(frame, text="*", width=4, command=multiply).pack(side="left", padx=3)
tk.Button(frame, text="/", width=4, command=divide).pack(side="left", padx=3)

window.mainloop()