import requests
from tkinter import messagebox
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO

def get_random_dog_image():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        data = response.json()
        print(data)
        print(data['message'])
        print(data['status'])
        return data['message']
    except Exception as e:
        mb.showerror("Ошибка", f"Ошибка при запросе к API: {e}")
        return None


def show_image():
    status_label.config(text="Загрузка...")
    image_url = get_random_dog_image()
    if image_url:
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img_size = (int(width_spinbox.get()), int(height_spinbox.get()))
            img.thumbnail(img_size)
            img = ImageTk.PhotoImage(img)
            # new_window = Toplevel(window)
            # new_window.title("Случайное изображение пёсика")
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Изображение № {notebook.index('end') + 1}")
            lb = ttk.Label(tab, image=img)
            lb.pack(padx=10, pady=10)
            lb.image = img
            status_label.config(text="")
        except requests.RequestException as e:
            mb.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
    progress.stop()


def progress():
    progress['value'] = 0
    progress.start(30)
    window.after(3000, lambda: [progress.stop(), show_image()])


def clear_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)
    messagebox.showinfo("Очистка", "Все вкладки успешно удалены.")

window = Tk()
window.title("Картинки с собачками")
window.geometry("240x240")

status_label = ttk.Label(window, text="")
status_label.pack(padx=10, pady=5)

# label = ttk.Label()
# label.pack(padx=10, pady=10)

button_frame = ttk.Frame(window)
button_frame.pack(pady=10)

button = ttk.Button(text="Загрузить изображение", command=progress)
button.pack(padx=10, pady=10)

button_clear = ttk.Button(button_frame, text="Очистить вкладки", command=clear_tabs)
button_clear.pack(side='left', padx=5)

progress = ttk.Progressbar(mode='determinate', length=300)
progress.pack(padx=10, pady=10)

size_frame = ttk.Frame(window)
size_frame.pack(pady=10)

width_label = ttk.Label(text="Ширина:")
width_label.pack(side='left', padx=(10, 0))
width_spinbox = ttk.Spinbox(from_=200, to=500, increment=50, width=5)
width_spinbox.pack(side='left', padx=(0, 10))
width_spinbox.set(300)

height_label = ttk.Label(text="Высота:")
height_label.pack(side='left', padx=(10, 0))
height_spinbox = ttk.Spinbox(from_=200, to=500, increment=50, width=5)
height_spinbox.pack(side='left', padx=(0, 10))
height_spinbox.set(300)

top_level_window = Toplevel(window)
top_level_window.title("Изображения пёсиков")

notebook = ttk.Notebook(top_level_window)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

window.mainloop()
