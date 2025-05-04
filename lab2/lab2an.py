import urllib.request
import pandas as pd
import os
import datetime
import numpy as np
import re
import streamlit as st
import matplotlib.pyplot as plt

def create_directory(dir_name='vhi_data'):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def download_vhi_data(province_id, year1=1981, year2=2024, dir_name='vhi_data'):
    create_directory(dir_name)
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_id}&year1={year1}&year2={year2}&type=Mean"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{dir_name}/vhi_id_{province_id}_{now}.csv"

    try:
        vhi_url = urllib.request.urlopen(url)
        out = open(file_name, 'wb')
        out.write(vhi_url.read())
        out.close()
        return file_name
    except Exception as e:
        st.error(f"Помилка при завантаженні даних для області {province_id}: {e}")
        return None

def read_vhi_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        content = re.sub(r'<[^>]+>', '', content)
        lines = content.split('\n')
        start_line = 0
        for i, line in enumerate(lines):
            if 'year' in line.lower() and 'week' in line.lower():
                start_line = i
                break

        if start_line == 0:
            for i, line in enumerate(lines):
                if re.search(r'\d{4}', line):
                    start_line = i
                    break

        temp_file = file_path + '.temp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            if 'year' not in lines[start_line].lower() or 'week' not in lines[start_line].lower():
                f.write("year,week,SMN,SMT,VCI,TCI,VHI,%Area_VHI_LESS_15,%Area_VHI_LESS_35\n")

            for line in lines[start_line:]:
                if line.strip():
                    cleaned_line = re.sub(r'\s+', ',', line.strip())
                    cleaned_line = re.sub(r'^,+|,+$', '', cleaned_line)
                    cleaned_line = re.sub(r',+', ',', cleaned_line)
                    f.write(cleaned_line + '\n')

        try:
            df = pd.read_csv(temp_file, index_col=False)
        except pd.errors.EmptyDataError:
            st.error(f"Файл {file_path} не містить даних після очищення.")
            return None
        except pd.errors.ParserError:
            df = pd.read_csv(temp_file, index_col=False, sep=',', header=0,
                             names=["year", "week", "SMN", "SMT", "VCI", "TCI", "VHI",
                                    "%Area_VHI_LESS_15", "%Area_VHI_LESS_35"])

        try:
            os.remove(temp_file)
        except:
            pass

        df.columns = [col.strip() for col in df.columns]
        df = df[pd.to_numeric(df['year'], errors='coerce').notna()]
        df = df.dropna(subset=['year', 'week'])

        df['year'] = df['year'].astype(int)
        df['week'] = df['week'].astype(int)

        for col in ['SMN', 'SMT', 'VCI', 'TCI', 'VHI', '%Area_VHI_LESS_15', '%Area_VHI_LESS_35']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        column_mapping = {
            'year': 'Рік',
            'week': 'Тиждень',
            'SMN': 'SMN',
            'SMT': 'SMT',
            'VCI': 'VCI',
            'TCI': 'TCI',
            'VHI': 'VHI',
            '%Area_VHI_LESS_15': 'Площа_VHI_менше_15',
            '%Area_VHI_LESS_35': 'Площа_VHI_менше_35'
        }

        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})

        return df

    except Exception as e:
        st.error(f"Помилка при читанні CSV-файлу {file_path}: {e}")
        return None

def change_province_ids(old_id):
    province_map = {
        1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька", 
        5: "Житомирська", 6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська", 
        9: "Київська", 10: "Кіровоградська", 11: "Луганська", 12: "Львівська", 
        13: "Миколаївська", 14: "Одеська", 15: "Полтавська", 16: "Рівенська", 
        17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська", 
        21: "Хмельницька", 22: "Черкаська", 23: "Чернівецька", 24: "Чернігівська", 
        25: "Республіка Крим"
    }
    return province_map.get(old_id, f"Невідома область: {old_id}")

def download_all_provinces(year1=1981, year2=2024):
    data_dir = create_directory()
    files = {}

    for province_id in range(1, 26):
        file_path = download_vhi_data(province_id, year1, year2, data_dir)
        if file_path:
            files[province_id] = file_path

    return files

def read_all_provinces(data_dir='vhi_data'):
    province_data = {}

    try:
        for file_name in os.listdir(data_dir):
            if file_name.startswith('vhi_id_') and file_name.endswith('.csv'):
                province_id = int(file_name.split('_')[2])
                file_path = os.path.join(data_dir, file_name)

                df = read_vhi_data(file_path)
                if df is not None and 'VHI' in df.columns:
                    province_name = change_province_ids(province_id)
                    province_data[province_name] = df
    except Exception as e:
        st.error(f"Помилка при зчитуванні всіх файлів: {e}")

    return province_data


def get_vhi_for_year(province_data, province_name, year):
    """
    Повертає ряд VHI для вказаної області за вказаний рік
    """
    if province_name not in province_data:
        print(f"Дані для області '{province_name}' не знайдено.")
        return None
    
    df = province_data[province_name]
    result = df[df['Рік'] == year][['Тиждень', 'VHI']].copy()
    
    if result.empty:
        print(f"Немає даних VHI для області '{province_name}' за {year} рік.")
        return None
    
    print(f"\nДані VHI для області {province_name} за {year} рік:")
    print(result.to_string(index=False))
    return result

def find_extremes(province_data, province_names, years):
    """
    Знаходить екстремуми (мін і макс), середнє та медіану VHI 
    для вказаних областей і років
    """
    results = []
    
    for province_name in province_names:
        if province_name not in province_data:
            print(f"Дані для області '{province_name}' не знайдено.")
            continue
            
        df = province_data[province_name]
        df_years = df[df['Рік'].isin(years)]
        
        if df_years.empty:
            print(f"Немає даних для області '{province_name}' за вказані роки.")
            continue
            
        vhi_min = df_years['VHI'].min()
        vhi_max = df_years['VHI'].max()
        vhi_mean = df_years['VHI'].mean()
        vhi_median = df_years['VHI'].median()
        
        results.append({
            'Область': province_name,
            'Мінімальний VHI': vhi_min,
            'Максимальний VHI': vhi_max,
            'Середній VHI': vhi_mean,
            'Медіана VHI': vhi_median
        })
        
        print(f"\nСтатистика VHI для області {province_name} за роки {years}:")
        print(f"Мінімальний VHI: {vhi_min:.2f}")
        print(f"Максимальний VHI: {vhi_max:.2f}")
        print(f"Середній VHI: {vhi_mean:.2f}")
        print(f"Медіана VHI: {vhi_median:.2f}")
    
    return pd.DataFrame(results)

def get_vhi_for_years_range(province_data, province_names, year_start, year_end):
    """
    Повертає ряд VHI за вказаний діапазон років для вказаних областей
    """
    results = {}
    
    for province_name in province_names:
        if province_name not in province_data:
            print(f"Дані для області '{province_name}' не знайдено.")
            continue
            
        df = province_data[province_name]
        mask = (df['Рік'] >= year_start) & (df['Рік'] <= year_end)
        result = df.loc[mask, ['Рік', 'Тиждень', 'VHI']].copy()
        
        if result.empty:
            print(f"Немає даних VHI для області '{province_name}' за період {year_start}-{year_end}.")
            continue
            
        results[province_name] = result
        
        print(f"\nДані VHI для області {province_name} за період {year_start}-{year_end}:")
        print(result.to_string(index=False))
    
    return results

def find_extreme_droughts_simple(province_data, threshold_percent=20, vhi_threshold=15, min_weeks=3):
    """
    Спрощена версія: знаходить роки, коли більше threshold_percent% областей
    мали екстремальні посухи, виводить лише роки та назви областей
    """
    all_years = set()
    for df in province_data.values():
        all_years.update(df['Рік'].unique())
    all_years = sorted(all_years)
    
    drought_years = []
    
    for year in all_years:
        affected_provinces = []
        
        for province_name, df in province_data.items():
            year_data = df[df['Рік'] == year]
            
            if not year_data.empty:
                drought_weeks = year_data[year_data['VHI'] < vhi_threshold]
                if len(drought_weeks) >= min_weeks:
                    affected_provinces.append(province_name)
        
        total_provinces = len(province_data)
        threshold_count = total_provinces * threshold_percent / 100
        
        if len(affected_provinces) > threshold_count:
            drought_years.append({
                'Рік': year,
                'Області': affected_provinces
            })
    
    if not drought_years:
        print(f"\nНе знайдено років, коли більше {threshold_percent}% областей "
              f"зазнавали екстремальних посух.")
        return None
    
    print(f"\nРоки, коли більше {threshold_percent}% областей мали екстремальні посухи:")
    print("--------------------------------------------------")
    
    for entry in drought_years:
        print(f"\nРік: {entry['Рік']}")
        print("Уражені області:")
        for province in entry['Області']:
            print(f"- {province}")
    
    return drought_years

# Приклад використання функцій:
if __name__ == "__main__":
    # Завантажуємо дані (якщо ще не завантажені)
    data_dir = create_directory()
    files = download_all_provinces(1981, 2024)
    province_data = read_all_provinces(data_dir)
    
    if not province_data:
        print("Не вдалося завантажити дані. ")
    else:
        # 1. Отримати VHI для області за вказаний рік
        print("\n=== Завдання 1: Ряд VHI для області за вказаний рік ===")
        vhi_year = get_vhi_for_year(province_data, "Київська", 2020)
        
        # 2. Пошук екстремумів для вказаних областей і років
        print("\n=== Завдання 2: Пошук екстремумів для вказаних областей і років ===")
        extremes = find_extremes(
            province_data, 
            ["Київська", "Львівська", "Одеська"], 
            [2018, 2019, 2020]
        )
        
        # 3. Ряд VHI за вказаний діапазон років для вказаних областей
        print("\n=== Завдання 3: Ряд VHI за діапазон років для вказаних областей ===")
        vhi_range = get_vhi_for_years_range(
            province_data, 
            ["Київська", "Харківська"], 
            2015, 2020
        )
        
        # 4. Пошук років з екстремальними посухами
        print("\n=== Завдання 4: Пошук років з екстремальними посухами ===")
        droughts = find_extreme_droughts_simple(province_data, threshold_percent=20)