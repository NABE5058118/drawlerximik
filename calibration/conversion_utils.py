import numpy as np
from scipy.optimize import curve_fit

def mm_to_steps(mm, axis):
    """
    Конвертирует миллиметры в шаги для заданной оси (X, Y, Z).
    Настройте под ваше калибровочное уравнение.
    """
    if axis == 'X':
        return int(mm * 10.0)  # Пример: 10 шагов на мм
    elif axis == 'Y':
        return int(mm * 10.0)
    elif axis == 'Z':
        return int(mm * 100.0)  # Пример: 100 шагов на мм для Z
    return 0

def steps_to_mm(steps, axis):
    """
    Обратное преобразование: шаги в мм.
    """
    if axis == 'X':
        return steps / 10.0
    elif axis == 'Y':
        return steps / 10.0
    elif axis == 'Z':
        return steps / 100.0
    return 0

def fit_calibration_model(points_mm, points_steps):
    """
    Подгоняет модель калибровки по точкам (мм → шаги).
    """
    def linear(x, a, b):
        return a * x + b

    x_mm = np.array([p[0] for p in points_mm])
    y_mm = np.array([p[1] for p in points_mm])
    x_steps = np.array([p[0] for p in points_steps])
    y_steps = np.array([p[1] for p in points_steps])

    popt_x, _ = curve_fit(linear, x_mm, x_steps)
    popt_y, _ = curve_fit(linear, y_mm, y_steps)

    return popt_x, popt_y  # [a, b] для X и Y