# завдання 1
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
# завдання 2
from scipy.signal import butter, filtfilt

# Визначення всіх змінних
# Початкові значення кожного параметру
init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_covariance = 0.1
show_noise = True

# Генерація часового ряду
sampling_frequency = 1000
t = np.linspace(0, 10, sampling_frequency * 10)

# Початковий колір графіку
current_color = 'red'

# Параметри фільтру
order = 4
init_cutoff_frequency = 3.0

noise_global = None
noise_global_mean = None
noise_global_covariance = None


# Функція генерації гармоніки
def generate_harmonic(amplitude, frequency, phase, t):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)


# Функція генерації шуму
def generate_noise(noise_mean, noise_covariance, t):
    noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
    return noise


# Функція для гармоніки з шумом
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise, noise=None):
    global noise_global
    global noise_global_mean
    global noise_global_covariance
    y = generate_harmonic(amplitude, frequency, phase, t)
    if noise is not None:
        return y + noise
    else:
        if noise_global is None or len(noise_global) != len(
                t) or noise_mean != noise_global_mean or noise_covariance != noise_global_covariance:
            noise_global = generate_noise(noise_mean, noise_covariance, t)
            noise_global_mean = noise_mean
            noise_global_covariance = noise_covariance
        if show_noise:
            return y + noise_global
        else:
            return y


# Функція для відфільтрованої гармоніки
def filtered_harmonic_with_noise(cutoff_frequency, amplitude, frequency, phase, noise_mean, noise_covariance,
                                 show_noise):
    y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    # Фільтрація сигналу
    nyquist = 0.5 * sampling_frequency
    normal_cutoff = cutoff_frequency / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y_filtered = filtfilt(b, a, y)
    return y_filtered


# Створення головного вікна та елементів інтерфейсу
fig, ax = plt.subplots(figsize=(20, 7.7))
plt.subplots_adjust(left=0.15, bottom=0.55)
plt.figtext(0.52, 0.9, 'Graphs', ha='center', va='center', fontsize=16)
ax.set_xlabel('Time')
ax.set_ylabel('Amplitude')
# Додавання сітки
plt.grid(True)

# Слайдери для параметрів
ax_amplitude = plt.axes([0.2, 0.4, 0.65, 0.03])
ax_frequency = plt.axes([0.2, 0.35, 0.65, 0.03])
ax_phase = plt.axes([0.2, 0.3, 0.65, 0.03])
ax_noise_mean = plt.axes([0.2, 0.25, 0.65, 0.03])
ax_noise_covariance = plt.axes([0.2, 0.2, 0.65, 0.03])
ax_cutoff_frequency = plt.axes([0.2, 0.15, 0.65, 0.03])

slider_amplitude = Slider(ax_amplitude, 'Amplitude', 0.1, 10.0, valinit=init_amplitude, color=current_color)
slider_frequency = Slider(ax_frequency, 'Frequency', 0.1, 10.0, valinit=init_frequency, color=current_color)
slider_phase = Slider(ax_phase, 'Phase', 0.0, 2 * np.pi, valinit=init_phase, color=current_color)
slider_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=init_noise_mean, color=current_color)
slider_noise_covariance = Slider(ax_noise_covariance, 'Noise Covariance', 0.0, 1.0, valinit=init_noise_covariance,
                                 color=current_color)
slider_cutoff_frequency = Slider(ax_cutoff_frequency, 'Cutoff Frequency', 0.1, 10.0, valinit=init_cutoff_frequency,
                                 color=current_color)


# оновлення даних
def update(val):
    amplitude = slider_amplitude.val
    frequency = slider_frequency.val
    phase = slider_phase.val
    noise_mean = slider_noise_mean.val
    noise_covariance = slider_noise_covariance.val
    cutoff_frequency = slider_cutoff_frequency.val

    # Початковий графік гармоніки
    y_harmonic = generate_harmonic(amplitude, frequency, phase, t)
    line_harmonic.set_ydata(y_harmonic)

    # Гармоніки гармоніки з накладеним шумом
    y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    line.set_ydata(y)

    # Фільтрація та оновлення відфільтрованої гармоніки
    y_filtered = filtered_harmonic_with_noise(cutoff_frequency, amplitude, frequency, phase, noise_mean,
                                              noise_covariance, show_noise)
    line_filtered.set_ydata(y_filtered)

    fig.canvas.draw_idle()


slider_amplitude.on_changed(update)
slider_frequency.on_changed(update)
slider_phase.on_changed(update)
slider_noise_mean.on_changed(update)
slider_noise_covariance.on_changed(update)
slider_cutoff_frequency.on_changed(update)


# функція для чекбоксу
def toggle_noise(label):
    global show_noise
    show_noise = not show_noise
    update(None)


# ітерактивний елемент - чекбокс
rax = plt.axes([0.8, 0.1, 0.1, 0.04])
check = CheckButtons(rax, ['Show Noise'], [True])
check.on_clicked(toggle_noise)

# масив доступних кольорів
colors = ['red', 'green', 'blue', 'purple']


# функція для зміни кольору
def change_color(event):
    # збереження даних у глобальних зміннах
    global current_color
    global colors

    # Знаходження індексу поточного кольору в списку кольорів
    current_index = colors.index(current_color)

    # Обчислення індексу наступного кольору
    next_index = (current_index + 1) % len(colors)

    # Оновлення поточного кольору
    current_color = colors[next_index]

    # Зміна кольору для графіків і легенди
    line.set_color(current_color)
    line_harmonic.set_color(colors[(next_index + 1) % len(colors)])  # Кольори для гармоніки змінюються в іншому порядку
    line_filtered.set_color(
        colors[(next_index + 2) % len(colors)])  # Кольори для відфільтрованого сигналу змінюються в іншому порядку
    ax.legend().get_texts()[0].set_color(colors[next_index])  # Зміна кольору тексту в легенді

    fig.canvas.draw_idle()


# інтерактивний елемент для зміни кольору
button_color = Button(plt.axes([0.6, 0.1, 0.1, 0.04]), 'Change Color')
button_color.on_clicked(change_color)


# функція для скидання параметрів
def reset_parameters(event):
    slider_amplitude.reset()
    slider_frequency.reset()
    slider_phase.reset()
    slider_noise_mean.reset()
    slider_noise_covariance.reset()
    slider_cutoff_frequency.reset()
    update(None)


# інтерактивний елемент для скидання всіх параметрів
button_reset = Button(plt.axes([0.7, 0.1, 0.1, 0.04]), 'Reset')
button_reset.on_clicked(reset_parameters)

# ПОБУДОВА

# Початковий графік гармоніки
y = generate_harmonic(init_amplitude, init_frequency, init_phase, t)
line_harmonic, = ax.plot(t, y, lw=2, color='green', label='Harmonic Signal')

# Початковий графік
y_with_noise = harmonic_with_noise(init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_covariance,
                                   show_noise)
line, = ax.plot(t, y_with_noise, lw=2, color=current_color, label='Original Signal')

# Відфільтрований графік
y_filtered = filtered_harmonic_with_noise(init_cutoff_frequency, init_amplitude, init_frequency, init_phase,
                                          init_noise_mean, init_noise_covariance, show_noise)
line_filtered, = ax.plot(t, y_filtered, lw=2, color='blue', alpha=0.5, label='Filtered Signal')

# Легенда
ax.legend()

# Побудова
plt.show()