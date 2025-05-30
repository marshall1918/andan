# для фільтру
import numpy as np
# для серверу
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup, Select, Button, Div
from bokeh.plotting import figure, curdoc
# для запуску
import subprocess

# ініціалізація глобальних змінних
noise_global = None
noise_global_mean = None
noise_global_covariance = None

# ініціалізація параметрів
init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_covariance = 0.1
show_noise = True
init_filter_window_size = 10
t = np.linspace(0, 10, 10000)

# генерація гармонічного сигналу
def generate_harmonic(amplitude, frequency, phase, t):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)

# генерація шуму
def generate_noise(noise_mean, noise_covariance, t):
    noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
    return noise

# генерація гармонійний сигнал із додатковим шумом
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise, noise=None):
    global noise_global
    global noise_global_mean
    global noise_global_covariance
    y = generate_harmonic(amplitude, frequency, phase, t)
    if noise is not None:
        return y + noise
    else:
        if noise_global is None or len(noise_global) != len(t) or noise_mean != noise_global_mean or noise_covariance != noise_global_covariance:
            noise_global = generate_noise(noise_mean, noise_covariance, t)
            noise_global_mean = noise_mean
            noise_global_covariance = noise_covariance
        if show_noise:
            return y + noise_global
        else:
            return y

# Moving average filter function - ковзаюче середнє
def moving_average_filter(signal, window_size):
    filtered_signal = np.zeros_like(signal)
    for i in range(len(signal)):
        if i < window_size:
            filtered_signal[i] = np.mean(signal[:i+1])
        else:
            filtered_signal[i] = np.mean(signal[i-window_size+1:i+1])
    return filtered_signal

# Hann filter function
# signal - це вхідний сигнал, до якого застосовується фільтр.
# window_size - розмір вікна фільтра.
def hann_filter(signal, window_size):
    hann = np.hanning(window_size) # створює вікно Ханна
    hann = hann / sum(hann)  # Normalization

    # згладити вхідний сигнал signal за допомогою вікна Ханна.
    filtered_signal = np.convolve(signal, hann, mode='same')
    # Параметр mode='same' означає, що вихідний сигнал буде такого ж розміру, як і вхідний.
    return filtered_signal

# функція вибору типу фільтру: або ковзаюче середнє або фільтр Ханна
def filtered_harmonic_with_noise(filter_type, filter_window_size, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    if filter_type == 'Moving Average':
        y_filtered = moving_average_filter(y, filter_window_size)
    elif filter_type == 'Hann Filter':
        y_filtered = hann_filter(y, filter_window_size)
    return y_filtered

# створення базового об'єкта ColumnDataSource для кожного сигналу, data - параметр об'єкта
source_harmonic            = ColumnDataSource(data={'x': t, 'y': generate_harmonic(init_amplitude, init_frequency, init_phase, t)})
source_harmonic_with_noise = ColumnDataSource(data={'x': t, 'y': harmonic_with_noise(init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_covariance, True)})
source_filtered            = ColumnDataSource(data={'x': t, 'y': filtered_harmonic_with_noise('Moving Average', init_filter_window_size, init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_covariance, True)})

# оновлення даних
def update_data(attrname, old, new):
    amplitude = slider_amplitude.value
    frequency = slider_frequency.value
    phase = slider_phase.value
    noise_mean = slider_noise_mean.value
    noise_covariance = slider_noise_covariance.value
    filter_type = select_filter_type.value
    filter_window_size = int(slider_filter_window_size.value)
    show_noise = 0 in checkbox_show_noise.active

    # генерація звичайної гармоніки
    harmonic_signal = generate_harmonic(amplitude, frequency, phase, t)

    # генерація гармоніки з шумом
    harmonic_with_noise_signal = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)

    # побудова фільтру для гармоніки з шумом
    filtered_signal = filtered_harmonic_with_noise(filter_type, filter_window_size, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)

    # оновлення даних
    source_harmonic.data            = {'x': t, 'y': harmonic_signal}
    source_harmonic_with_noise.data = {'x': t, 'y': harmonic_with_noise_signal}
    source_filtered.data            = {'x': t, 'y': filtered_signal}

# функція скидання всіх повзунків до початкових значень
def reset_sliders():
    slider_amplitude.value = init_amplitude
    slider_frequency.value = init_frequency
    slider_phase.value = init_phase
    slider_noise_mean.value = init_noise_mean
    slider_noise_covariance.value = init_noise_covariance
    slider_filter_window_size.value = init_filter_window_size
    checkbox_show_noise.active = [0]  # оновлення checkbox

# поле для графіку функції (plot)
plot = figure(height=500, width=1900,
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 10], y_range=[-2, 2], x_axis_label='Time', y_axis_label='Amplitude')

# стилі
plot.title.text_font_size = "16pt"  # розмір для загаловку
plot.xaxis.axis_label_text_font_size = "14pt"  # розмір по X
plot.yaxis.axis_label_text_font_size = "14pt"  # розмір по Y

# додавання заголовку до графіку
plot_title = Div(text="<h1 style='text-align:center;color:blue;'>Harmonic Signal with Noise</h1>", width=1000)
# додавання додаткового тексту
description_text = Div(text="<p style='text-align:center;color:black;'>This plot displays a harmonic signal with optional noise. You can adjust the parameters using the sliders and select different types of filters and plot styles. All this can be implemented using the library BOKEH</p>", width=1200)

# слайдери
slider_amplitude  = Slider(title="Amplitude", value=init_amplitude, start=0.1, end=10.0, step=0.1, height=50, width=300)
slider_frequency  = Slider(title="Frequency", value=init_frequency, start=0.1, end=10.0, step=0.1, height=50, width=300)
slider_phase      = Slider(title="Phase", value=init_phase, start=0.0, end=2 * np.pi, step=0.1, height=50, width=300)
slider_noise_mean = Slider(title="Noise Mean", value=init_noise_mean, start=-1.0, end=1.0, step=0.1, height=50, width=300)
slider_noise_covariance = Slider(title="Noise Covariance", value=init_noise_covariance, start=0.0, end=1.0, step=0.1, height=50, width=300)
select_filter_type      = Select(title="Filter Type", value='Moving Average', options=['Moving Average', 'Hann Filter'], height=50, width=300)
slider_filter_window_size = Slider(title="Filter Window Size", value=init_filter_window_size, start=1, end=500, step=1, height=50, width=300)

# чекбокс
checkbox_show_noise = CheckboxGroup(labels=["Show Noise"], active=[0], height=50, width=300)

# виклик слайдерів
for w in [slider_amplitude, slider_frequency, slider_phase, slider_noise_mean, slider_noise_covariance, slider_filter_window_size]:
    w.on_change('value', update_data)

# виклик чекбоксу
checkbox_show_noise.on_change('active', update_data)

# виклик випадаючого списку
select_filter_type.on_change('value', update_data)

# словник з кольорів
colors = {'harmonic': 'green', 'original': 'red', 'filtered': 'blue'}
# побудова сигналу
plot.line('x', 'y', source=source_harmonic_with_noise, line_width=2, color=colors['original'], legend_label='Harmonic Signal with Noise')

plot.line('x', 'y', source=source_harmonic, line_width=2, color=colors['harmonic'], legend_label='Harmonic Signal')
plot.line('x', 'y', source=source_filtered, line_width=2, color=colors['filtered'], legend_label='Filtered Signal')

# визначення кнопки Reset типом danger
button_reset = Button(label="Reset", button_type="danger")
button_reset.on_click(reset_sliders)

# інтерактивні елементи
inputs = column(
    row(slider_amplitude, slider_frequency, slider_phase),
    row(slider_noise_mean, slider_noise_covariance, select_filter_type),
    row(slider_filter_window_size, checkbox_show_noise, button_reset),
    width=300
)

layout = column(plot_title, description_text, row(plot, width=1900), inputs)

# add_root - додати модель як корінь цього документа
# дозволяє додавати елементи до документа, такі як графіки, таблиці, візуалізації та інші компоненти Bokeh
curdoc().add_root(layout)
curdoc().title = "Harmonic Signal with Noise"

# запуск Bokeh серверу за допомогою subprocess
subprocess.call(["bokeh", "serve", "--show", __file__])