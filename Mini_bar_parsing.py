import requests
from tkinter import Tk, Toplevel, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

# Глобальная переменная для отслеживания состояния окна с изображениями
image_window_visible = False


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
    # Меняем цвет индикатора на желтый (загрузка)
    status_indicator.config(background='yellow')
    window.update()

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

            # Показываем окно с изображениями при первом запросе
            global image_window_visible
            if not image_window_visible:
                top_level_window.deiconify()
                image_window_visible = True

            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Изображение {notebook.index('end') + 1}")
            label = ttk.Label(tab, image=img)
            label.image = img
            label.pack(padx=10, pady=10)

            # Меняем цвет индикатора на зеленый (успех)
            status_indicator.config(background='green')

        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
            # Меняем цвет индикатора на красный (ошибка)
            status_indicator.config(background='red')


def clear_tabs():
    """Удаляет все вкладки из Notebook."""
    for tab in notebook.tabs():
        notebook.forget(tab)

    # Скрываем окно с изображениями после очистки
    global image_window_visible
    if image_window_visible:
        top_level_window.withdraw()
        image_window_visible = False

    messagebox.showinfo("Очистка", "Все вкладки успешно удалены.")
    # Возвращаем индикатор в исходное состояние
    status_indicator.config(background='lightgray')


def toggle_image_window():
    """Показывает/скрывает окно с изображениями"""
    global image_window_visible
    if image_window_visible:
        top_level_window.withdraw()
        image_window_visible = False
        toggle_button.config(text="Показать изображения")
    else:
        top_level_window.deiconify()
        image_window_visible = True
        toggle_button.config(text="Скрыть изображения")


# --- Главное окно (компактная панель) ---
window = Tk()
window.title("Панель управления парсинга")
window.resizable(True, False)  # Запрещаем изменение высоты окна

# Основной фрейм для всех элементов в одну строку
main_frame = ttk.Frame(window, padding="5")
main_frame.pack(fill='x')

# Индикатор статуса (меняет цвет)
status_indicator = ttk.Label(main_frame, width=3, background='lightgray', relief='solid')
status_indicator.pack(side='left', padx=5)

# Кнопка загрузки изображения
button_load = ttk.Button(main_frame, text="Загрузить данные", command=show_image)
button_load.pack(side='left', padx=5)

# Кнопка очистки вкладок
button_clear = ttk.Button(main_frame, text="Очистить всё", command=clear_tabs)
button_clear.pack(side='left', padx=5)

# Настройки размеров
ttk.Label(main_frame, text="Ширина:").pack(side='left', padx=(10, 0))
width_spinbox = ttk.Spinbox(main_frame, from_=200, to=500, increment=50, width=5)
width_spinbox.set(300)
width_spinbox.pack(side='left', padx=(0, 10))

ttk.Label(main_frame, text="Высота:").pack(side='left', padx=(10, 0))
height_spinbox = ttk.Spinbox(main_frame, from_=200, to=500, increment=50, width=5)
height_spinbox.set(300)
height_spinbox.pack(side='left', padx=(0, 10))

# Кнопка показа/скрытия окна с изображениями
toggle_button = ttk.Button(main_frame, text="Показать изображения", command=toggle_image_window)
toggle_button.pack(side='left', padx=10)

# --- Окно для вкладок (изначально скрыто) ---
top_level_window = Toplevel(window)
top_level_window.title("Галерея собак")
top_level_window.withdraw()  # Скрываем окно при запуске

notebook = ttk.Notebook(top_level_window)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

# Центрируем главное окно в верхней части экрана
window.update_idletasks()
x = (window.winfo_screenwidth() - window.winfo_width()) // 2
y = 10
window.geometry(f"+{x}+{y}")

window.mainloop()