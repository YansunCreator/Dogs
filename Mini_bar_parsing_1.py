import threading
import requests
from tkinter import Tk, Toplevel, messagebox
from tkinter import ttk, Button, Label
from PIL import Image, ImageTk
from io import BytesIO

# ---- состояния ----
image_window_visible = False
downloading = False
download_complete = False
progress_value = 0
images_refs = []  # чтобы PhotoImage не очищались сборщиком мусора

# --- функции сетевые / UI ---
def get_random_dog_image():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random', timeout=10)
        response.raise_for_status()
        return response.json().get('message')
    except requests.RequestException as e:
        return None, e

def start_download():
    """Запускает поток загрузки и прогресс-обновление."""
    global downloading, download_complete, progress_value
    if downloading:
        return
    downloading = True
    download_complete = False
    progress_value = 0

    # кнопка в состояние загрузки
    load_button.config(text="Загрузка... 0%", state="disabled", bg="#f0ad4e", activebackground="#f0ad4e")
    progressbar['value'] = 0
    progress_tick()  # запустить анимацию прогресса

    # Запускаем поток, который загрузит картинку
    t = threading.Thread(target=download_thread, daemon=True)
    t.start()

def download_thread():
    """Фоновый поток — скачивает картинку и по завершении вызывает on_download_success/error в главном потоке."""
    try:
        # получаем URL
        response = requests.get('https://dog.ceo/api/breeds/image/random', timeout=10)
        response.raise_for_status()
        url = response.json().get('message')
        if not url:
            raise RuntimeError("Не удалось получить URL изображения")

        # скачиваем само изображение
        resp = requests.get(url, stream=True, timeout=15)
        resp.raise_for_status()
        img_data = BytesIO(resp.content)
        pil_img = Image.open(img_data)

        # передаем обработку в главный поток (UI)
        window.after(0, on_download_success, pil_img)
    except Exception as e:
        window.after(0, on_download_error, e)

def on_download_success(pil_img):
    """Вызывается в главном потоке при успешной загрузке."""
    global downloading, download_complete, image_window_visible
    download_complete = True

    # подгоняем изображение под размер
    try:
        target = (int(width_spinbox.get()), int(height_spinbox.get()))
    except Exception:
        target = (300, 300)
    pil_img.thumbnail(target)

    tk_img = ImageTk.PhotoImage(pil_img)
    images_refs.append(tk_img)  # держим ссылку

    # показать окно с вкладками при первом изображении
    if not image_window_visible:
        top_level_window.deiconify()
        image_window_visible = True

    tab = ttk.Frame(notebook)
    notebook.add(tab, text=f"Собака {notebook.index('end') + 1}")
    lbl = Label(tab, image=tk_img)
    lbl.image = tk_img
    lbl.pack(padx=6, pady=6)

    # финализируем прогресс — поставить 100% и показать Готово
    progressbar['value'] = 100
    load_button.config(text="✅ Готово", bg="#4CAF50", activebackground="#4CAF50")
    # сброс кнопки через 1.5 секунды
    window.after(1500, reset_after_finish)

    downloading = False

def on_download_error(err):
    """Обработка ошибок загрузки (в главном потоке)."""
    global downloading
    downloading = False
    progressbar['value'] = 0
    load_button.config(text="Загрузить собаку", state="normal", bg=default_button_bg)
    messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{err}")

def progress_tick():
    """Анимирует прогресс-полосу, пока идет загрузка."""
    global progress_value
    if download_complete:
        progressbar['value'] = 100
        return
    # увеличиваем значение (имитация прогресса). Не доходить до 100, чтобы завершение выглядело плавно.
    progress_value = min(98, progress_value + 2)
    progressbar['value'] = progress_value
    # обновляем текст кнопки с процентом
    load_button.config(text=f"Загрузка... {progress_value}%")
    # повторяем через 80 мс
    window.after(80, progress_tick)

def reset_after_finish():
    """Возвращает кнопку и прогресс в исходное состояние."""
    progressbar['value'] = 0
    load_button.config(text="Загрузить собаку", state="normal", bg=default_button_bg)
    global download_complete
    download_complete = False

def clear_tabs():
    """Удаляет все вкладки и прячет окно."""
    for tab in notebook.tabs():
        notebook.forget(tab)
    global image_window_visible
    if image_window_visible:
        top_level_window.withdraw()
        image_window_visible = False
    messagebox.showinfo("Очистка", "Все вкладки успешно удалены.")
    progressbar['value'] = 0

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

# ---- GUI ----
window = Tk()
window.title("Панель управления собаками")
window.resizable(True, False)

main_frame = ttk.Frame(window, padding=5)
main_frame.pack(fill='x')

# тонкий progressbar под панелью (будет заполняться по ширине)
progressbar = ttk.Progressbar(window, mode='determinate', maximum=100)
progressbar.pack(fill='x', padx=6, pady=(4, 6), ipady=0)  # ipady=1 делает полосу тонкой

# Размещаем кнопки и контролы над полосой (панель компактнее, прогресс ниже)
# Кнопка загрузки — обычная tkinter.Button, чтобы можно было легко менять bg
load_button = Button(main_frame, text="Загрузить собаку", command=start_download)
load_button.pack(side='left', padx=6)

clear_button = ttk.Button(main_frame, text="Очистить всё", command=clear_tabs)
clear_button.pack(side='left', padx=6)

ttk.Label(main_frame, text="Ширина:").pack(side='left', padx=(10, 0))
width_spinbox = ttk.Spinbox(main_frame, from_=200, to=800, increment=50, width=6)
width_spinbox.set(300)
width_spinbox.pack(side='left', padx=(4, 8))

ttk.Label(main_frame, text="Высота:").pack(side='left', padx=(4, 0))
height_spinbox = ttk.Spinbox(main_frame, from_=200, to=800, increment=50, width=6)
height_spinbox.set(300)
height_spinbox.pack(side='left', padx=(4, 8))

toggle_button = ttk.Button(main_frame, text="Показать изображения", command=toggle_image_window)
toggle_button.pack(side='left', padx=8)

# Запоминаем стандартный цвет кнопки (понадобится для восстановления)
window.update_idletasks()
default_button_bg = load_button.cget('bg')

# --- окно для вкладок (скрытое изначально) ---
top_level_window = Toplevel(window)
top_level_window.title("Галерея собак")
top_level_window.withdraw()
notebook = ttk.Notebook(top_level_window)
notebook.pack(expand=True, fill='both', padx=8, pady=8)

# Центрируем главное окно по ширине и чуть выше экрана
window.update_idletasks()
x = (window.winfo_screenwidth() - window.winfo_width()) // 2
y = 10
window.geometry(f"+{x}+{y}")

window.mainloop()
