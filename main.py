import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import copy

# Ваш список точек
points = [
    [-2, 4, 0], [-2,4,1], [1,4,0], [1,4,1], [2,3,0], 
    [2,3,1], [3,1,0], [3,1,1], [3,-1,0], [3,-1,1], 
    [2,-3,0], [2,-3,1], [1,-4,0], [1,-4,1], [-2,-4,0], 
    [-2,-4,1], [-1,3,0], [-1,3,1], [-1,-3,0], [-1,-3,1], 
    [1,3,0], [1,3,1], [1,-3,0], [1,-3,1], [2,1,0], 
    [2,1,1], [2,-1,0], [2,-1,1]
]

connections = [
    (0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
    (12, 13), (14, 15), (16, 17), (18, 19), (20, 21),
    (22, 23), (24, 25), (26, 27),

    (0, 2), (1, 3), (4, 6), (5, 7), 
    (0, 14), (1, 15), (14, 12), (15, 13), 
    (12, 10), (13, 11), (10, 8), (11, 9),
    (8, 6), (9, 7), (4, 2), (5, 3),
    (16, 20), (17, 21), (20, 24), (21, 25),
    (24, 26), (25, 27), (26, 22), (27, 23),
    (22, 18), (23, 19), (18, 16), (19, 17)
    # и т.д.
]

class PointApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Points Viewer")

        # Сохранение оригинальных точек для сброса
        self.original_points = copy.deepcopy(points)
        self.current_points = copy.deepcopy(points)

        # Инициализация трансформаций
        self.scale_factor = 1.0
        self.shift_x_total = 0.0
        self.shift_y_total = 0.0
        self.shift_z_total = 0.0
        self.current_projection = None

        # Создание фигуры matplotlib
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Встраивание фигуры в Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=7)

        # Инициализация объектов для точек и линий
        self.scatter = self.ax.scatter([], [], [], c='b', s=50, label='Точки')
        self.line_collection = Line3DCollection([], colors='r', label='Соединения')
        self.ax.add_collection3d(self.line_collection)

        # Добавление легенды
        self.ax.legend(loc='upper left')

        # Первоначальная отрисовка
        self.plot_points()

        # Элементы управления для сдвига
        tk.Label(root, text="Сдвиг по X:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.shift_x = tk.DoubleVar()
        tk.Entry(root, textvariable=self.shift_x).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Сдвиг по Y:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.shift_y = tk.DoubleVar()
        tk.Entry(root, textvariable=self.shift_y).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(root, text="Сдвиг по Z:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.shift_z = tk.DoubleVar()
        tk.Entry(root, textvariable=self.shift_z).grid(row=3, column=1, padx=5, pady=5)

        tk.Button(root, text="Применить сдвиг", command=self.apply_shift).grid(row=1, column=2, padx=5, pady=5)

        # Кнопки для отображения проекций
        tk.Button(root, text="Проекция на плоскость YZ", command=self.project_yz).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(root, text="Проекция на плоскость XZ", command=self.project_xz).grid(row=3, column=2, padx=5, pady=5)
        tk.Button(root, text="Проекция на плоскость XY", command=self.project_xy).grid(row=4, column=2, padx=5, pady=5)

        # Кнопка для сброса изменений
        tk.Button(root, text="Сбросить", command=self.reset).grid(row=1, column=3, rowspan=1, padx=5, pady=5)

        # Кнопки для масштабирования
        tk.Button(root, text="Масштабировать +", command=self.scale_up).grid(row=2, column=3, padx=5, pady=5)
        tk.Button(root, text="Масштабировать -", command=self.scale_down).grid(row=3, column=3, padx=5, pady=5)

    def plot_points(self):
        """Отображение точек и соединений на 3D графике с учётом всех трансформаций."""
        self.ax.clear()
        # Настройка осей
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # Применение трансформаций к оригинальным точкам
        transformed_points = copy.deepcopy(self.original_points)

        # Применение масштабирования
        transformed_points = [[x * self.scale_factor, y * self.scale_factor, z * self.scale_factor] for x, y, z in transformed_points]

        # Применение сдвига
        transformed_points = [[x + self.shift_x_total, y + self.shift_y_total, z + self.shift_z_total] for x, y, z in transformed_points]

        # Применение проекций
        if self.current_projection == 'yz':
            transformed_points = [[0, y, z] for x, y, z in transformed_points]
        elif self.current_projection == 'xz':
            transformed_points = [[x, 0, z] for x, y, z in transformed_points]
        elif self.current_projection == 'xy':
            transformed_points = [[x, y, 0] for x, y, z in transformed_points]

        self.current_points = transformed_points

        # Извлечение координат
        if self.current_points:
            x, y, z = zip(*self.current_points)
            self.scatter = self.ax.scatter(x, y, z, c='b', s=50, label='Точки')

        # Создание списка линий
        lines = []
        for conn in connections:
            start_idx, end_idx = conn
            try:
                start_point = self.current_points[start_idx]
                end_point = self.current_points[end_idx]
                lines.append([start_point, end_point])
            except IndexError:
                print(f"Ошибка: Индекс соединения {conn} выходит за пределы списка точек.")

        # Создание Line3DCollection
        self.line_collection = Line3DCollection(lines, colors='r', linewidths=1)
        self.ax.add_collection3d(self.line_collection)

        # Установка границ осей для лучшего отображения
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_zlim([-10, 10])

        # Добавление легенды
        self.ax.legend(['Точки', 'Соединения'], loc='upper left')

        self.canvas.draw_idle()

    def apply_shift(self):
        """Применение сдвига ко всем точкам."""
        dx = self.shift_x.get()
        dy = self.shift_y.get()
        dz = self.shift_z.get()
        self.shift_x_total += dx
        self.shift_y_total += dy
        self.shift_z_total += dz
        self.plot_points()

    def project_yz(self):
        """Отображение проекции на плоскость YZ (X=0)."""
        self.current_projection = 'yz'
        self.plot_points()

    def project_xz(self):
        """Отображение проекции на плоскость XZ (Y=0)."""
        self.current_projection = 'xz'
        self.plot_points()

    def project_xy(self):
        """Отображение проекции на плоскость XY (Z=0)."""
        self.current_projection = 'xy'
        self.plot_points()

    def reset(self):
        """Сброс всех изменений к оригинальным точкам."""
        self.current_points = copy.deepcopy(self.original_points)
        self.scale_factor = 1.0
        self.shift_x_total = 0.0
        self.shift_y_total = 0.0
        self.shift_z_total = 0.0
        self.current_projection = None
        self.plot_points()

    def scale_up(self):
        """Увеличение размера модели на 10%."""
        self.scale_factor *= 1.1
        self.plot_points()

    def scale_down(self):
        """Уменьшение размера модели на 10%."""
        self.scale_factor *= 0.9
        self.plot_points()

if __name__ == "__main__":
    root = tk.Tk()
    app = PointApp(root)
    root.mainloop()
