import requests
from tkinter import Tk, Toplevel, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

image_window_visible = False
loading = False

def get_random_dog_image():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        return response.json()['message']
    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка при запросе к API: {e}")
        return None

def show_image():
    global loading
    if loading:  # предотвращаем повторное нажатие
        return
    loading = True
    button_load.config(text="Загрузка...", state="disabled")
    progress_simulate(0)
    window.after(2000, load_image_process)

def progress_simulate(step):
    if step <= 100:
        button_load.config(text=f"Загрузка... {step}%")
        window.after(30, progress_simulate, step + 5)

def load_image_process():
    global loading
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

            global image_window_visible
            if not image_window_visible:
                top_level_window.deiconify()
                image_window_visible = True

            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Собака {notebook.index('end') + 1}")
            label = ttk.Label(tab, image=img)
            label.image = img
            label.pack(padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    button_load.config(text="Загрузить собаку", state="normal")
    loading = False

def clear_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)
    global image_window_visible
    if image_window_visible:
        top_level_window.withdraw()
        image_window_visible = False
    messagebox.showinfo("Очистка", "Все вкладки удалены.")

def toggle_image_window():
    global image_window_visible
    if image_window_visible:
        top_level_window.withdraw()
        image_window_visible = False
        toggle_button.config(text="Показать изображения")
    else:
        top_level_window.deiconify()
        image_window_visible = True
        toggle_button.config(text="Скрыть изображения")

# === Интерфейс ===
window = Tk()
window.title("Панель управления собаками")
window.resizable(True, False)

main_frame = ttk.Frame(window, padding="5")
main_frame.pack(fill='x')

button_load = ttk.Button(main_frame, text="Загрузить собаку", command=show_image)
button_load.pack(side='left', padx=5)

ttk.Button(main_frame, text="Очистить всё", command=clear_tabs).pack(side='left', padx=5)

ttk.Label(main_frame, text="Ширина:").pack(side='left', padx=(10, 0))
width_spinbox = ttk.Spinbox(main_frame, from_=200, to=500, increment=50, width=5)
width_spinbox.set(300)
width_spinbox.pack(side='left', padx=(0, 10))

ttk.Label(main_frame, text="Высота:").pack(side='left', padx=(10, 0))
height_spinbox = ttk.Spinbox(main_frame, from_=200, to=500, increment=50, width=5)
height_spinbox.set(300)
height_spinbox.pack(side='left', padx=(0, 10))

toggle_button = ttk.Button(main_frame, text="Показать изображения", command=toggle_image_window)
toggle_button.pack(side='left', padx=10)

top_level_window = Toplevel(window)
top_level_window.title("Галерея собак")
top_level_window.withdraw()

notebook = ttk.Notebook(top_level_window)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

window.mainloop()
