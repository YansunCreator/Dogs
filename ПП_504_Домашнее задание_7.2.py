import requests
from tkinter import Tk, Toplevel, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO


def get_random_dog_image():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        data = response.json()
        return data['message']
    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка при запросе к API: {e}")
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

            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Изображение {notebook.index('end') + 1}")
            label = ttk.Label(tab, image=img)
            label.image = img
            label.pack(padx=10, pady=10)

            status_label.config(text="")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")


def start_progress():
    progress['value'] = 0
    progress.start(30)
    window.after(3000, lambda: [progress.stop(), show_image()])


def clear_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)
    messagebox.showinfo("Очистка", "Все вкладки успешно удалены.")

window = Tk()
window.title("Поисковик изображений")

status_label = ttk.Label(window, text="")
status_label.pack(padx=10, pady=5)

button_frame = ttk.Frame(window)
button_frame.pack(pady=10)

button_load = ttk.Button(button_frame, text="Загрузить изображение", command=start_progress)
button_load.pack(side='left', padx=5)

button_clear = ttk.Button(button_frame, text="Очистить вкладки", command=clear_tabs)
button_clear.pack(side='left', padx=5)

progress = ttk.Progressbar(window, mode='determinate', length=300)
progress.pack(padx=10, pady=5)

size_frame = ttk.Frame(window)
size_frame.pack(pady=10)

width_label = ttk.Label(size_frame, text="Ширина:")
width_label.pack(side='left', padx=(10, 0))
width_spinbox = ttk.Spinbox(size_frame, from_=200, to=500, increment=50, width=5)
width_spinbox.pack(side='left', padx=(0, 10))
width_spinbox.set(300)

height_label = ttk.Label(size_frame, text="Высота:")
height_label.pack(side='left', padx=(10, 0))
height_spinbox = ttk.Spinbox(size_frame, from_=200, to=500, increment=50, width=5)
height_spinbox.pack(side='left', padx=(0, 10))
height_spinbox.set(300)

top_level_window = Toplevel(window)
top_level_window.title("Галерея собак")

notebook = ttk.Notebook(top_level_window)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

window.update_idletasks()
x = (window.winfo_screenwidth() - window.winfo_width()) // 2
y = 10
window.geometry(f"+{x}+{y}")

window.mainloop()
