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

def streamlit_vhi_app():
    st.set_page_config(layout="wide")
    st.title("VHI Аналіз Рослинності в Україні")

    # Завантаження даних
    if 'province_data' not in st.session_state:
        with st.spinner('Завантаження даних...'):
            files = download_all_provinces()
            st.session_state.province_data = read_all_provinces()

    # Sidebar для фільтрів
    col1, col2 = st.columns([1, 3])

    with col1:
        # Правильне отримання років
        years = sorted(set(int(year) for df in st.session_state.province_data.values() for year in df['Рік']))
        
        # Dropdown для вибору області
        selected_province = st.selectbox(
            "Оберіть область", 
            options=list(st.session_state.province_data.keys())
        )

        # Dropdown для вибору індексу
        selected_index = st.selectbox(
            "Оберіть індекс", 
            options=['VHI', 'VCI', 'TCI']
        )

        # Роки та тижні
        year_range = st.slider(
            "Виберіть інтервал років", 
            min_value=min(years), 
            max_value=max(years), 
            value=(min(years), max(years))
        )

        # Решта коду залишається без змін
        week_range = st.slider(
            "Виберіть інтервал тижнів", 
            min_value=1, 
            max_value=52, 
            value=(1, 52)
        )

        # Checkbox для сортування
        ascending = st.checkbox("Сортувати за зростанням")
        descending = st.checkbox("Сортувати за спаданням")

        # Кнопка скидання
        if st.button("Скинути фільтри"):
            st.experimental_rerun()

    with col2:
        # Фільтрація даних
        province_df = st.session_state.province_data[selected_province]
        filtered_df = province_df[
            (province_df['Рік'] >= year_range[0]) & 
            (province_df['Рік'] <= year_range[1]) & 
            (province_df['Тиждень'] >= week_range[0]) & 
            (province_df['Тиждень'] <= week_range[1])
        ]

        # Сортування
        if ascending and not descending:
            filtered_df = filtered_df.sort_values(by=selected_index)
        elif descending and not ascending:
            filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)

        # Вкладки
        tab1, tab2 = st.tabs(["Таблиця", "Графіки"])

        with tab1:
            st.dataframe(filtered_df)

        with tab2:
            # Графіки
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Перший графік: часовий ряд для обраної області
            ax1.plot(filtered_df['Тиждень'], filtered_df[selected_index], marker='o')
            ax1.set_title(f'{selected_index} для {selected_province}')
            ax1.set_xlabel('Тиждень')
            ax1.set_ylabel(selected_index)

            # Другий графік: порівняння з іншими областями
            for province, df in st.session_state.province_data.items():
                province_filtered = df[
                    (df['Рік'] >= year_range[0]) & 
                    (df['Рік'] <= year_range[1]) & 
                    (df['Тиждень'] >= week_range[0]) & 
                    (df['Тиждень'] <= week_range[1])
                ]
                ax2.plot(province_filtered['Тиждень'], province_filtered[selected_index], label=province)
            
            ax2.set_title(f'Порівняння {selected_index} по областях')
            ax2.set_xlabel('Тиждень')
            ax2.set_ylabel(selected_index)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            plt.tight_layout()
            st.pyplot(fig)

def main():
    streamlit_vhi_app()

if __name__ == "__main__":
    main()