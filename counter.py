import tkinter as tk

window = tk.Tk()
window.title("counter")
window.geometry("300x200")

count = 0

label =tk.Label(window, text="0", font=("Arial", 40))
label.pack(pady=20)

def add():
    global count
    count += 1
    label.config(text=count)

def subtract():
        global count
        if count > 0:count -= 1
        label.config(text=count) 

def resets():
      global count
      count =0
      label.config(text=count)

tk.Button(window, text="+", font=("Arial", 18), command=add).pack(pady=5)        
tk.Button(window, text="-", font=("Arial", 18), command=subtract).pack(pady=5)  
tk.Button(window, text="Reset", font=("Arial", 18), command=resets).pack(pady=5)


window.mainloop()