import numpy as np
import pandas as pd
import timeit
import datetime as dt
import re

# Функції для профілювання часу виконання
def profile_execution(func, repeats=5):
    """Вимірює час виконання функції"""
    time_taken = timeit.timeit(func, number=repeats) / repeats
    return time_taken * 1000  # Повертає час у мілісекундах

# Завантаження та підготовка даних через pandas
def load_data_pandas():
    # Завантаження даних
    df = pd.read_csv("household_power_consumption.txt", sep=';', 
                    parse_dates={'datetime': ['Date', 'Time']},
                    dayfirst=True,
                    na_values=['?'])
    
    # Видалення рядків з відсутніми значеннями
    df = df.dropna()
    
    return df

# Завантаження та підготовка даних через numpy
def load_data_numpy():
    # Визначення типів даних для колонок
    types = [("Date", "U10"), ("Time", "U8"), ("Global_active_power", "f8"), 
             ("Global_reactive_power", "f8"), ("Voltage", "f8"), 
             ("Global_intensity", "f8"), ("Sub_metering_1", "f8"), 
             ("Sub_metering_2", "f8"), ("Sub_metering_3", "f8")]
    
    # Завантаження даних
    data = np.genfromtxt("household_power_consumption.txt", delimiter=';', 
                         dtype=types, names=True, 
                         missing_values=['?'], 
                         encoding='utf-8',
                         deletechars='')
    
    # Видалення рядків з NaN
    mask = ~np.isnan(data['Global_active_power'])
    for field in ['Global_reactive_power', 'Voltage', 'Global_intensity', 
                  'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']:
        mask = mask & ~np.isnan(data[field])
    
    data = data[mask]
    
    return data

# Функції для завдань з використанням pandas
def task1_pandas(df):
    """Обрати всі записи, у яких загальна активна споживана потужність перевищує 5 кВт."""
    return df[df['Global_active_power'] > 5]

def task2_pandas(df):
    """Обрати всі записи, у яких вольтаж перевищую 235 В."""
    return df[df['Voltage'] > 235]

def task3_pandas(df):
    """Обрати всі записи, у яких сила струму лежить в межах 19-20 А,
    для них виявити ті, у яких пральна машина та холодильних
    споживають більше, ніж бойлер та кондиціонер."""
    filtered_df = df[(df['Global_intensity'] >= 19) & (df['Global_intensity'] <= 20)]
    return filtered_df[filtered_df['Sub_metering_2'] > filtered_df['Sub_metering_3']]

def task4_pandas(df):
    """Обрати випадковим чином 500000 записів (без повторів елементів вибірки),
    для них обчислити середні величини усіх 3-х груп споживання електричної енергії."""
    # Перевірка, чи достатньо записів
    sample_size = min(500000, len(df))
    sample_df = df.sample(n=sample_size, replace=False)
    
    # Обчислення середніх значень
    mean_values = {
        'Sub_metering_1': sample_df['Sub_metering_1'].mean(),
        'Sub_metering_2': sample_df['Sub_metering_2'].mean(),
        'Sub_metering_3': sample_df['Sub_metering_3'].mean()
    }
    
    return mean_values

def task5_pandas(df):
    """Обрати ті записи, які після 18-00 споживають понад 6 кВт за хвилину в середньому,
    серед відібраних визначити ті, у яких основне споживання електроенергії у вказаний
    проміжок часу припадає на пральну машину, сушарку, холодильник та освітлення (група 2 є найбільшою),
    а потім обрати кожен третій результат із першої половини та кожен четвертий результат із другої половини."""
    
    # Конвертація datetime в pandas, якщо вже не зроблено
    if 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
    
    # Вибір записів після 18:00
    evening_df = df[df['datetime'].dt.hour >= 18]
    
    # Вибір записів, що споживають понад 6 кВт
    high_power_df = evening_df[evening_df['Global_active_power'] > 6]
    
    # Вибір записів, де група 2 є найбільшою
    group2_df = high_power_df[(high_power_df['Sub_metering_2'] > high_power_df['Sub_metering_1']) & 
                             (high_power_df['Sub_metering_2'] > high_power_df['Sub_metering_3'])]
    
    # Розділення на дві половини
    half_idx = len(group2_df) // 2
    first_half = group2_df.iloc[:half_idx]
    second_half = group2_df.iloc[half_idx:]
    
    # Вибір кожного третього запису з першої половини
    selected_first = first_half.iloc[::3]
    
    # Вибір кожного четвертого запису з другої половини
    selected_second = second_half.iloc[::4]
    
    # Об'єднання результатів
    result = pd.concat([selected_first, selected_second])
    
    return result

# Функції для завдань з використанням numpy
def task1_numpy(data):
    """Обрати всі записи, у яких загальна активна споживана потужність перевищує 5 кВт."""
    return data[data['Global_active_power'] > 5]

def task2_numpy(data):
    """Обрати всі записи, у яких вольтаж перевищую 235 В."""
    return data[data['Voltage'] > 235]

def task3_numpy(data):
    """Обрати всі записи, у яких сила струму лежить в межах 19-20 А,
    для них виявити ті, у яких пральна машина та холодильних
    споживають більше, ніж бойлер та кондиціонер."""
    intensity_mask = (data['Global_intensity'] >= 19) & (data['Global_intensity'] <= 20)
    filtered_data = data[intensity_mask]
    return filtered_data[filtered_data['Sub_metering_2'] > filtered_data['Sub_metering_3']]

def task4_numpy(data):
    """Обрати випадковим чином 500000 записів (без повторів елементів вибірки),
    для них обчислити середні величини усіх 3-х груп споживання електричної енергії."""
    # Перевірка, чи достатньо записів
    sample_size = min(500000, len(data))
    
    # Вибір випадкових індексів без повторень
    indices = np.random.choice(len(data), size=sample_size, replace=False)
    sample_data = data[indices]
    
    # Обчислення середніх значень
    mean_values = {
        'Sub_metering_1': np.mean(sample_data['Sub_metering_1']),
        'Sub_metering_2': np.mean(sample_data['Sub_metering_2']),
        'Sub_metering_3': np.mean(sample_data['Sub_metering_3'])
    }
    
    return mean_values

def task5_numpy(data):
    """Обрати ті записи, які після 18-00 споживають понад 6 кВт за хвилину в середньому,
    серед відібраних визначити ті, у яких основне споживання електроенергії у вказаний
    проміжок часу припадає на пральну машину, сушарку, холодильник та освітлення (група 2 є найбільшою),
    а потім обрати кожен третій результат із першої половини та кожен четвертий результат із другої половини."""
    
    # Конвертація часу в години
    hours = np.array([int(t.split(':')[0]) for t in data['Time']])
    
    # Вибір записів після 18:00
    evening_mask = hours >= 18
    evening_data = data[evening_mask]
    
    # Вибір записів, що споживають понад 6 кВт
    high_power_mask = evening_data['Global_active_power'] > 6
    high_power_data = evening_data[high_power_mask]
    
    # Вибір записів, де група 2 є найбільшою
    group2_mask = (high_power_data['Sub_metering_2'] > high_power_data['Sub_metering_1']) & \
                  (high_power_data['Sub_metering_2'] > high_power_data['Sub_metering_3'])
    group2_data = high_power_data[group2_mask]
    
    # Розділення на дві половини
    half_idx = len(group2_data) // 2
    first_half = group2_data[:half_idx]
    second_half = group2_data[half_idx:]
    
    # Вибір кожного третього запису з першої половини
    selected_first = first_half[::3]
    
    # Вибір кожного четвертого запису з другої половини
    selected_second = second_half[::4]
    
    # Об'єднання результатів
    result = np.concatenate((selected_first, selected_second))
    
    return result

def evaluate_and_report(pandas_df, numpy_data):
    # Створюємо словник для зберігання результатів
    results = {
        'pandas': {},
        'numpy': {},
        'convenience': {}  # Оцінка зручності виконання операцій
    }
    
    # Завдання 1: Обрати всі записи з потужністю > 5 кВт
    print("Завдання 1: Обрати записи з потужністю > 5 кВт")
    results['pandas']['task1'] = profile_execution(lambda: task1_pandas(pandas_df))
    results['numpy']['task1'] = profile_execution(lambda: task1_numpy(numpy_data))
    results['convenience']['task1'] = {'pandas': 5, 'numpy': 4}  # Суб'єктивна оцінка за 5-бальною шкалою
    
    print(f"Pandas час виконання: {results['pandas']['task1']:.3f} мс")
    print(f"NumPy час виконання: {results['numpy']['task1']:.3f} мс")
    print(f"Співвідношення Pandas/NumPy: {results['pandas']['task1'] / results['numpy']['task1']:.2f}")
    
    # Завдання 2: Обрати всі записи з вольтажем > 235 В
    print("\nЗавдання 2: Обрати записи з вольтажем > 235 В")
    results['pandas']['task2'] = profile_execution(lambda: task2_pandas(pandas_df))
    results['numpy']['task2'] = profile_execution(lambda: task2_numpy(numpy_data))
    results['convenience']['task2'] = {'pandas': 5, 'numpy': 4}
    
    print(f"Pandas час виконання: {results['pandas']['task2']:.3f} мс")
    print(f"NumPy час виконання: {results['numpy']['task2']:.3f} мс")
    print(f"Співвідношення Pandas/NumPy: {results['pandas']['task2'] / results['numpy']['task2']:.2f}")
    
    # Завдання 3: Обрати записи з силою струму 19-20 А і співвідношенням груп споживачів
    print("\nЗавдання 3: Обрати записи з силою струму 19-20 А і певним співвідношенням груп")
    results['pandas']['task3'] = profile_execution(lambda: task3_pandas(pandas_df))
    results['numpy']['task3'] = profile_execution(lambda: task3_numpy(numpy_data))
    results['convenience']['task3'] = {'pandas': 5, 'numpy': 3}
    
    print(f"Pandas час виконання: {results['pandas']['task3']:.3f} мс")
    print(f"NumPy час виконання: {results['numpy']['task3']:.3f} мс")
    print(f"Співвідношення Pandas/NumPy: {results['pandas']['task3'] / results['numpy']['task3']:.2f}")
    
    # Завдання 4: Випадковий вибір 500000 записів і обчислення середніх
    print("\nЗавдання 4: Випадковий вибір 500000 записів і обчислення середніх")
    results['pandas']['task4'] = profile_execution(lambda: task4_pandas(pandas_df))
    results['numpy']['task4'] = profile_execution(lambda: task4_numpy(numpy_data))
    results['convenience']['task4'] = {'pandas': 5, 'numpy': 4}
    
    print(f"Pandas час виконання: {results['pandas']['task4']:.3f} мс")
    print(f"NumPy час виконання: {results['numpy']['task4']:.3f} мс")
    print(f"Співвідношення Pandas/NumPy: {results['pandas']['task4'] / results['numpy']['task4']:.2f}")
    
    # Завдання 5: Складне завдання з фільтрацією за часом і значеннями
    print("\nЗавдання 5: Складне завдання з фільтрацією за часом і значеннями")
    results['pandas']['task5'] = profile_execution(lambda: task5_pandas(pandas_df))
    results['numpy']['task5'] = profile_execution(lambda: task5_numpy(numpy_data))
    results['convenience']['task5'] = {'pandas': 5, 'numpy': 2}
    
    print(f"Pandas час виконання: {results['pandas']['task5']:.3f} мс")
    print(f"NumPy час виконання: {results['numpy']['task5']:.3f} мс")
    print(f"Співвідношення Pandas/NumPy: {results['pandas']['task5'] / results['numpy']['task5']:.2f}")
    
    # Підсумковий звіт
    print("\n" + "="*50)
    print("ПІДСУМКОВИЙ ЗВІТ")
    print("="*50)
    
    for task in range(1, 6):
        task_key = f'task{task}'
        pandas_time = results['pandas'][task_key]
        numpy_time = results['numpy'][task_key]
        pandas_convenience = results['convenience'][task_key]['pandas']
        numpy_convenience = results['convenience'][task_key]['numpy']
        
        faster = "Pandas" if pandas_time < numpy_time else "NumPy"
        ratio = pandas_time / numpy_time if pandas_time > numpy_time else numpy_time / pandas_time
        
        print(f"\nЗавдання {task}:")
        print(f"  Pandas: {pandas_time:.3f} мс, зручність: {pandas_convenience}/5")
        print(f"  NumPy: {numpy_time:.3f} мс, зручність: {numpy_convenience}/5")
        print(f"  Швидший варіант: {faster} (в {ratio:.2f} рази)")
    
    # Загальні висновки
    print("\n" + "="*50)
    print("ЗАГАЛЬНІ ВИСНОВКИ")
    print("="*50)
    
    pandas_avg_time = sum(results['pandas'].values()) / len(results['pandas'])
    numpy_avg_time = sum(results['numpy'].values()) / len(results['numpy'])
    
    pandas_avg_convenience = sum(results['convenience'][f'task{i}']['pandas'] for i in range(1, 6)) / 5
    numpy_avg_convenience = sum(results['convenience'][f'task{i}']['numpy'] for i in range(1, 6)) / 5
    
    print(f"Середній час виконання Pandas: {pandas_avg_time:.3f} мс")
    print(f"Середній час виконання NumPy: {numpy_avg_time:.3f} мс")
    print(f"Середня оцінка зручності Pandas: {pandas_avg_convenience:.1f}/5")
    print(f"Середня оцінка зручності NumPy: {numpy_avg_convenience:.1f}/5")
    
    if pandas_avg_time < numpy_avg_time:
        print("\nЗагалом Pandas працює швидше для цих завдань.")
    else:
        print("\nЗагалом NumPy працює швидше для цих завдань.")
    
    print("\nВисновки про зручність використання структур даних:")
    print("1. Pandas зручніший для складних операцій фільтрації та індексації.")
    print("2. Pandas має вбудовану підтримку дат і часу, що робить роботу з часовими рядами простішою.")
    print("3. NumPy вимагає більше коду для виконання складних фільтрацій.")
    print("4. Pandas має кращу підтримку роботи з відсутніми даними.")
    print("5. NumPy кращий для низькорівневих операцій з великими масивами чисел.")
    
    print("\nРекомендації щодо використання:")
    print("- Використовуйте Pandas для аналізу даних з складними умовами вибору, часовими рядами та відсутніми значеннями.")
    print("- Використовуйте NumPy для низькорівневих числових операцій, де важлива продуктивність і робота з однорідними даними.")

# Головна функція
def main():
    print("Завантаження даних...")
    
    # Вимірювання часу завантаження даних
    pandas_load_time = profile_execution(load_data_pandas)
    numpy_load_time = profile_execution(load_data_numpy)
    
    print(f"Час завантаження даних через Pandas: {pandas_load_time:.3f} мс")
    print(f"Час завантаження даних через NumPy: {numpy_load_time:.3f} мс")
    
    # Завантаження даних для подальшого використання
    pandas_df = load_data_pandas()
    numpy_data = load_data_numpy()
    
    print(f"\nРозмір даних Pandas: {len(pandas_df)} рядків")
    print(f"Розмір даних NumPy: {len(numpy_data)} рядків")
    
    # Проведення аналізу та порівняння
    evaluate_and_report(pandas_df, numpy_data)

if __name__ == "__main__":
    main()
