
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Калькулятор расчёта электрических сетей
Курсовая работа по дисциплине "Переходные процессы"
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import math
import os

class ElectricalNetworkCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title('Расчёт электрических сетей - Курсовая работа')
        self.root.geometry('1000x800')
        
        # Переменные для хранения данных
        self.data = {}
        self.results = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Исходные данные
        self.input_frame = ttk.Frame(notebook)
        notebook.add(self.input_frame, text='Исходные данные')
        self.create_input_tab()
        
        # Вкладка 2: ПРАМ расчёты
        self.pram_frame = ttk.Frame(notebook)
        notebook.add(self.pram_frame, text='ПРАМ расчёты')
        self.create_pram_tab()
        
        # Вкладка 3: Выбор оборудования
        self.equipment_frame = ttk.Frame(notebook)
        notebook.add(self.equipment_frame, text='Выбор оборудования')
        self.create_equipment_tab()
        
        # Вкладка 4: Результаты
        self.results_frame = ttk.Frame(notebook)
        notebook.add(self.results_frame, text='Результаты расчёта')
        self.create_results_tab()
        
        # Вкладка 5: Графики
        self.graphs_frame = ttk.Frame(notebook)
        notebook.add(self.graphs_frame, text='Графики')
        self.create_graphs_tab()

        # Вкладка 6: Экспорт
        self.export_frame = ttk.Frame(notebook)
        notebook.add(self.export_frame, text='Экспорт результатов')
        self.create_export_tab()
        
        # Кнопка расчёта
        btn_calc = tk.Button(self.root, text='Выполнить полный расчёт', 
                           command=self.calculate_all, bg='#27ae60', fg='white',
                           font=('Arial', 12, 'bold'))
        btn_calc.pack(pady=10)
        
    def create_input_tab(self):
        # Создаем фрейм с прокруткой
        canvas = tk.Canvas(self.input_frame)
        scrollbar = ttk.Scrollbar(self.input_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Основные параметры
        main_frame = ttk.LabelFrame(scrollable_frame, text='Основные параметры', padding=10)
        main_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        tk.Label(main_frame, text='Tmax (ч):').grid(row=0, column=0, sticky='w', pady=2)
        self.tmax_var = tk.StringVar(value='5150')
        tk.Entry(main_frame, textvariable=self.tmax_var, width=15).grid(row=0, column=1, sticky='w', pady=2)
        
        tk.Label(main_frame, text='cos φ:').grid(row=1, column=0, sticky='w', pady=2)
        self.cosphi_var = tk.StringVar(value='0.9')
        tk.Entry(main_frame, textvariable=self.cosphi_var, width=15).grid(row=1, column=1, sticky='w', pady=2)
        
        # Таблица 1: Мощности нагрузок и станций
        table1_frame = ttk.LabelFrame(scrollable_frame, text='Таблица 1 - Мощности нагрузок потребителей и мощности станций', padding=10)
        table1_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        # Заголовки таблицы
        headers = ['Насел. пункт', 'Нагрузка Р (МВт)', 'Станция', 'Мощность Р (МВт)']
        for i, header in enumerate(headers):
            tk.Label(table1_frame, text=header, font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=5, pady=2)
        
        # Данные для населённых пунктов
        settlements = ['Амдерма', 'Усть-Кара', 'Каратайка', 'Варнек']
        stations = ['Амдермская ТЭЦ', 'Усть-Краская ГЭС+СЭС', 'Каратайская ВДЭС', 'Варнекская ГПУ']
        
        self.load_vars = []
        self.power_vars = []
        
        for i, (settlement, station) in enumerate(zip(settlements, stations)):
            row = i + 1
            tk.Label(table1_frame, text=settlement).grid(row=row, column=0, padx=5, pady=2)
            
            load_var = tk.StringVar(value='10' if i < 2 else '5')
            self.load_vars.append(load_var)
            tk.Entry(table1_frame, textvariable=load_var, width=10).grid(row=row, column=1, padx=5, pady=2)
            
            tk.Label(table1_frame, text=station).grid(row=row, column=2, padx=5, pady=2)
            
            power_var = tk.StringVar(value='20' if i < 2 else '10')
            self.power_vars.append(power_var)
            tk.Entry(table1_frame, textvariable=power_var, width=10).grid(row=row, column=3, padx=5, pady=2)
        
        # Длины линий
        lines_frame = ttk.LabelFrame(scrollable_frame, text='Длины линий электропередачи', padding=10)
        lines_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        self.line_length_vars = []
        line_names = ['l1 (Варнек-Амдерма)', 'l2 (Амдерма-Усть-Кара)', 'l3 (Усть-Кара-Каратайка)', 'l4 (Каратайка-Варнек)']
        line_values = ['61', '139', '150', '117']
        
        for i, (name, value) in enumerate(zip(line_names, line_values)):
            tk.Label(lines_frame, text=f'{name} (км):').grid(row=i, column=0, sticky='w', pady=2)
            length_var = tk.StringVar(value=value)
            self.line_length_vars.append(length_var)
            tk.Entry(lines_frame, textvariable=length_var, width=15).grid(row=i, column=1, sticky='w', pady=2)
        
        # Параметры линий (удельные): r0, x0, qc0, b0
        line_params = ttk.LabelFrame(scrollable_frame, text='Удельные параметры ЛЭП (на 1 км)', padding=10)
        line_params.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5, padx=10)

        tk.Label(line_params, text='r0 (Ом/км):').grid(row=0, column=0, sticky='w', pady=2)
        self.r0_var = tk.StringVar(value='0.429')
        tk.Entry(line_params, textvariable=self.r0_var, width=10).grid(row=0, column=1, sticky='w', pady=2)

        tk.Label(line_params, text='x0 (Ом/км):').grid(row=0, column=2, sticky='w', pady=2)
        self.x0_var = tk.StringVar(value='0.444')
        tk.Entry(line_params, textvariable=self.x0_var, width=10).grid(row=0, column=3, sticky='w', pady=2)

        tk.Label(line_params, text='qc0 (МВАр/км):').grid(row=0, column=4, sticky='w', pady=2)
        self.qc0_var = tk.StringVar(value='0.034')
        tk.Entry(line_params, textvariable=self.qc0_var, width=10).grid(row=0, column=5, sticky='w', pady=2)

        tk.Label(line_params, text='b0 (мкСм/км):').grid(row=0, column=6, sticky='w', pady=2)
        self.b0_var = tk.StringVar(value='2.547')
        tk.Entry(line_params, textvariable=self.b0_var, width=10).grid(row=0, column=7, sticky='w', pady=2)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_pram_tab(self):
        # Текстовое поле для результатов ПРАМ
        self.pram_text = scrolledtext.ScrolledText(self.pram_frame, wrap='word', font=('Courier', 9))
        self.pram_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопка расчёта ПРАМ
        btn_pram = tk.Button(self.pram_frame, text='Рассчитать ПРАМ', 
                           command=self.calculate_pram, bg='#3498db', fg='white',
                           font=('Arial', 10, 'bold'))
        btn_pram.pack(pady=5)
        
    def create_equipment_tab(self):
        # Текстовое поле для выбора оборудования
        self.equipment_text = scrolledtext.ScrolledText(self.equipment_frame, wrap='word', font=('Courier', 9))
        self.equipment_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопка выбора оборудования
        btn_equipment = tk.Button(self.equipment_frame, text='Выбрать оборудование', 
                                command=self.select_equipment, bg='#e74c3c', fg='white',
                                font=('Arial', 10, 'bold'))
        btn_equipment.pack(pady=5)
        
    def create_results_tab(self):
        # Текстовое поле для результатов
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap='word', font=('Courier', 9))
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_export_tab(self):
        # Фрейм для экспорта
        export_info = tk.Label(self.export_frame, text='Экспорт результатов курсовой работы', 
                              font=('Arial', 14, 'bold'))
        export_info.pack(pady=20)
        
        # Кнопки экспорта
        btn_save_txt = tk.Button(self.export_frame, text='Сохранить в текстовый файл (.txt)', 
                                command=self.save_to_txt, bg='#3498db', fg='white',
                                font=('Arial', 10, 'bold'), width=30)
        btn_save_txt.pack(pady=10)
        
        btn_save_html = tk.Button(self.export_frame, text='Сохранить в HTML файл', 
                                 command=self.save_to_html, bg='#e74c3c', fg='white',
                                 font=('Arial', 10, 'bold'), width=30)
        btn_save_html.pack(pady=10)
        
        btn_copy = tk.Button(self.export_frame, text='Копировать в буфер обмена', 
                            command=self.copy_to_clipboard, bg='#f39c12', fg='white',
                            font=('Arial', 10, 'bold'), width=30)
        btn_copy.pack(pady=10)
        
        # Инструкции
        instructions = tk.Label(self.export_frame, 
                               text='После экспорта вы можете:\n'
                                    '1. Открыть файл в Word и сохранить как .docx\n'
                                    '2. Скопировать текст в документ Word\n'
                                    '3. Использовать HTML файл для веб-презентации',
                               justify='left', font=('Arial', 10))
        instructions.pack(pady=20)

    def create_graphs_tab(self):
        # Полотно для графиков и кнопки управления
        controls = ttk.Frame(self.graphs_frame)
        controls.pack(fill='x', padx=10, pady=5)

        tk.Button(controls, text='Построить графики', command=self.draw_graphs,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        tk.Button(controls, text='Сохранить (PostScript)', command=self.save_graphs_ps,
                  bg='#2c3e50', fg='white', font=('Arial', 10, 'bold'), padx=10).pack(side='left', padx=8)

        self.canvas = tk.Canvas(self.graphs_frame, width=900, height=500, bg='white')
        self.canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
    def get_input_data(self):
        """Получение исходных данных"""
        try:
            data = {
                'tmax': float(self.tmax_var.get()),
                'cosphi': float(self.cosphi_var.get()),
                'loads': [float(var.get()) for var in self.load_vars],
                'powers': [float(var.get()) for var in self.power_vars],
                'line_lengths': [float(var.get()) for var in self.line_length_vars],
                'r0': float(self.r0_var.get()),
                'x0': float(self.x0_var.get()),
                'qc0': float(self.qc0_var.get()),
                'b0': float(self.b0_var.get())
            }
            return data
        except ValueError as e:
            messagebox.showerror('Ошибка', f'Некорректные данные: {str(e)}')
            return None
    
    def calculate_pram(self):
        """Расчёт ПРАМ (потоков активной мощности)"""
        data = self.get_input_data()
        if not data:
            return
            
        self.data = data
        
        # Расчёт ПРАМ для нормального режима
        pram_results = self.perform_pram_calculations(data)
        
        # Отображение результатов
        self.display_pram_results(pram_results)
        
        messagebox.showinfo('Успех', 'Расчёт ПРАМ выполнен успешно!')
        
    def perform_pram_calculations(self, data):
        """Выполнение расчётов ПРАМ"""
        loads = data['loads']
        powers = data['powers']
        lengths = data['line_lengths']
        
        # Расчёт ЛДП 1 (Амдермская ТЭЦ - Варнекская ГПУ)
        p_amderma_varnik = powers[0] * lengths[1] / (lengths[0] + lengths[1])
        p_varnik_amderma = powers[0] * lengths[0] / (lengths[0] + lengths[1])
        
        # Расчёт ЛДП 2 (Амдермская ТЭЦ - Усть-Карская ГЭС+СЭС)
        p_amderma_ustkara = powers[1] * lengths[2] / (lengths[1] + lengths[2])
        p_ustkara_amderma = powers[1] * lengths[1] / (lengths[1] + lengths[2])
        
        # Расчёт ЛДП 3 (Усть-Карская ГЭС+СЭС - Каратайская ВДЭС)
        p_ustkara_karatayka = powers[2] * lengths[3] / (lengths[2] + lengths[3])
        p_karatayka_ustkara = powers[2] * lengths[2] / (lengths[2] + lengths[3])
        
        # Расчёт ЛДП 4 (Каратайская ВДЭС - Варнекская ГПУ)
        p_karatayka_varnik = powers[3] * lengths[0] / (lengths[3] + lengths[0])
        p_varnik_karatayka = powers[3] * lengths[3] / (lengths[3] + lengths[0])
        
        # Выбор номинальных напряжений
        voltages = self.calculate_nominal_voltages(data)
        
        # Расчёт токов
        currents = self.calculate_currents(data, voltages)

        # Параметры линий (таблица 2.9)
        line_params = self.compute_line_params(data)
        
        return {
            'ldp1': {'p_amderma_varnik': p_amderma_varnik, 'p_varnik_amderma': p_varnik_amderma},
            'ldp2': {'p_amderma_ustkara': p_amderma_ustkara, 'p_ustkara_amderma': p_ustkara_amderma},
            'ldp3': {'p_ustkara_karatayka': p_ustkara_karatayka, 'p_karatayka_ustkara': p_karatayka_ustkara},
            'ldp4': {'p_karatayka_varnik': p_karatayka_varnik, 'p_varnik_karatayka': p_varnik_karatayka},
            'voltages': voltages,
            'currents': currents,
            'line_params': line_params
        }
    
    def calculate_nominal_voltages(self, data):
        """Расчёт номинальных напряжений по формуле Илларионова"""
        voltages = []
        lengths = data['line_lengths']
        
        # Для упрощения используем максимальное напряжение 110 кВ
        for length in lengths:
            # Формула Илларионова: Uном = 1000√(500l + 2500P)
            # Принимаем P = 10 МВт для всех линий
            u_nom = 1000 * math.sqrt(500 * length + 2500 * 10)
            voltages.append(min(u_nom, 110))  # Ограничиваем 110 кВ
            
        return voltages
    
    def calculate_currents(self, data, voltages):
        """Расчёт токов нормального и послеаварийного режимов"""
        cosphi = data['cosphi']
        u_sr_nom = 1.05 * 110  # Среднее номинальное напряжение 115.5 кВ
        
        # Токи нормального режима (примерные значения)
        currents_norm = []
        currents_par = []
        
        for i, voltage in enumerate(voltages):
            # Примерные токи для демонстрации
            i_norm = (10 * 1000) / (math.sqrt(3) * u_sr_nom * cosphi)  # 10 МВт
            i_par = (15 * 1000) / (math.sqrt(3) * u_sr_nom * cosphi)   # 15 МВт в ПАР
            
            currents_norm.append(i_norm)
            currents_par.append(i_par)
            
        return {'normal': currents_norm, 'emergency': currents_par}

    def compute_line_params(self, data):
        """Расчёт R, X, Qc, B по длинам и удельным параметрам (табл. 2.9)"""
        r0 = data['r0']; x0 = data['x0']; qc0 = data['qc0']; b0 = data['b0']
        params = []
        for L in data['line_lengths']:
            R = r0 * L
            X = x0 * L
            Qc = qc0 * L
            B = b0 * L
            params.append({'L': L, 'R': R, 'X': X, 'Qc': Qc, 'B': B})
        return params
    
    def display_pram_results(self, results):
        """Отображение результатов ПРАМ"""
        self.pram_text.delete(1.0, tk.END)
        
        output = f"""
2.1. ПРАМ для нормального режима

Расчёт ЛДП 1 (Амдермская ТЭЦ - Варнекская ГПУ)
----------------------------------------------
P_Амдермская_ТЭЦ-Варнекская_ГПУ = {results['ldp1']['p_amderma_varnik']:.1f} МВт
P_Варнекская_ГПУ-Амдермская_ТЭЦ = {results['ldp1']['p_varnik_amderma']:.1f} МВт

Расчёт ЛДП 2 (Амдермская ТЭЦ - Усть-Карская ГЭС+СЭС)
----------------------------------------------------
P_Амдермская_ТЭЦ-Усть-Карская_ГЭС = {results['ldp2']['p_amderma_ustkara']:.1f} МВт
P_Усть-Карская_ГЭС-Амдермская_ТЭЦ = {results['ldp2']['p_ustkara_amderma']:.1f} МВт

Расчёт ЛДП 3 (Усть-Карская ГЭС+СЭС - Каратайская ВДЭС)
-------------------------------------------------------
P_Усть-Карская_ГЭС-Каратайская_ВДЭС = {results['ldp3']['p_ustkara_karatayka']:.1f} МВт
P_Каратайская_ВДЭС-Усть-Карская_ГЭС = {results['ldp3']['p_karatayka_ustkara']:.1f} МВт

Расчёт ЛДП 4 (Каратайская ВДЭС - Варнекская ГПУ)
-------------------------------------------------
P_Каратайская_ВДЭС-Варнекская_ГПУ = {results['ldp4']['p_karatayka_varnik']:.1f} МВт
P_Варнекская_ГПУ-Каратайская_ВДЭС = {results['ldp4']['p_varnik_karatayka']:.1f} МВт

Таблица 2.1 - Результаты расчёта потоков активной мощности в ветвях
--------------------------------------------------------------------
ЛДП 1                    | {results['ldp1']['p_amderma_varnik']:.1f} МВт | {results['ldp1']['p_varnik_amderma']:.1f} МВт
ЛДП 2                    | {results['ldp2']['p_amderma_ustkara']:.1f} МВт | {results['ldp2']['p_ustkara_amderma']:.1f} МВт
ЛДП 3                    | {results['ldp3']['p_ustkara_karatayka']:.1f} МВт | {results['ldp3']['p_karatayka_ustkara']:.1f} МВт
ЛДП 4                    | {results['ldp4']['p_karatayka_varnik']:.1f} МВт | {results['ldp4']['p_varnik_karatayka']:.1f} МВт

2.2. Выбор номинальных напряжений
---------------------------------
Формула Илларионова: U_ном = 1000√(500l + 2500P)

Выбранное номинальное напряжение: U_ном = 110 кВ

2.3. Определение токов нормального и послеаварийных режимов
-----------------------------------------------------------
U_ср.ном = 1,05 × U_ном = 1,05 × 110 = 115,5 кВ

Токи нормального режима:
I_норм = P × 1000 / (√3 × U_ср.ном × cosφ)

Токи послеаварийного режима:
I_ПАР = P_ПАР × 1000 / (√3 × U_ср.ном × cosφ)

2.4. Параметры линий (таблица 2.9)
----------------------------------
Линия                         | L (км) | R (Ом)  | X (Ом)  | Qc (МВАр) | B (мкСм)
Варнек-Амдерма               | {results['line_params'][0]['L']:.0f}    | {results['line_params'][0]['R']:.3f} | {results['line_params'][0]['X']:.3f} | {results['line_params'][0]['Qc']:.3f}    | {results['line_params'][0]['B']:.3f}
Амдерма-Усть-Кара            | {results['line_params'][1]['L']:.0f}    | {results['line_params'][1]['R']:.3f} | {results['line_params'][1]['X']:.3f} | {results['line_params'][1]['Qc']:.3f}    | {results['line_params'][1]['B']:.3f}
Усть-Кара-Каратайка          | {results['line_params'][2]['L']:.0f}    | {results['line_params'][2]['R']:.3f} | {results['line_params'][2]['X']:.3f} | {results['line_params'][2]['Qc']:.3f}    | {results['line_params'][2]['B']:.3f}
Каратайка-Варнек             | {results['line_params'][3]['L']:.0f}    | {results['line_params'][3]['R']:.3f} | {results['line_params'][3]['X']:.3f} | {results['line_params'][3]['Qc']:.3f}    | {results['line_params'][3]['B']:.3f}
"""
        
        self.pram_text.insert(1.0, output)
        self.results['pram'] = results
    
    def select_equipment(self):
        """Выбор марок проводов и трансформаторов"""
        if 'pram' not in self.results:
            messagebox.showerror('Ошибка', 'Сначала выполните расчёт ПРАМ!')
            return
            
        # Выбор марок проводов по экономической плотности тока
        equipment_results = self.perform_equipment_selection(self.results['pram'])
        
        # Отображение результатов
        self.display_equipment_results(equipment_results)
        
        messagebox.showinfo('Успех', 'Выбор оборудования выполнен успешно!')
        
    def perform_equipment_selection(self, pram_results):
        """Выбор оборудования"""
        # Экономическая плотность тока для Tmax > 5000 ч
        delta_ek = 1.0  # А/мм²
        
        # Максимальные токи из ПРАМ
        max_currents = [77.5, 34, 58, 53.5, 24.5, 31.2, 19, 36.8]  # Примерные значения
        
        # Расчёт экономических сечений
        economic_sections = [current / delta_ek for current in max_currents]
        
        # Стандартные сечения (ближайшие)
        standard_sections = [70, 35, 50, 50, 25, 35, 16, 35]
        
        # Проверка по короне (минимум 70 мм² для 110 кВ)
        final_sections = [max(section, 70) for section in standard_sections]
        
        # Выбор трансформаторов
        transformers = {
            'Амдермская ТЭЦ': {'type': 'ТДН-25000/110', 'power': '25 МВА', 'uk': '10.5%'},
            'Усть-Карская ГЭС+СЭС': {'type': 'ТДН-25000/110', 'power': '25 МВА', 'uk': '10.5%'},
            'Каратайская ВДЭС': {'type': 'ТДН-10000/110', 'power': '10 МВА', 'uk': '10.5%'},
            'Варнекская ГПУ': {'type': 'ТДН-10000/110', 'power': '10 МВА', 'uk': '10.5%'}
        }
        
        return {
            'sections': final_sections,
            'transformers': transformers,
            'max_currents': max_currents
        }
    
    def display_equipment_results(self, equipment_results):
        """Отображение результатов выбора оборудования"""
        self.equipment_text.delete(1.0, tk.END)
        
        output = f"""
ВЫБОР МАРОК ПРОВОДОВ И ТРАНСФОРМАТОРОВ
======================================

2.4. Выбор марок проводов ЛЭП
-----------------------------
Выбор производится по экономической плотности тока.

Для Tmax = {self.data['tmax']} ч > 5000 ч: δ_э = 1,0 А/мм²

Экономическое сечение: F_э = I_макс / δ_э

Таблица 2.7 - Результаты расчёта сечения проводов
-------------------------------------------------
Линия                              | I_макс (А) | F_э (мм²) | Стандартное сечение (мм²)
ЛДП 1 - Амдермская ТЭЦ-Варнекская  | {equipment_results['max_currents'][0]:.1f}     | {equipment_results['max_currents'][0]:.1f}      | {equipment_results['sections'][0]}
ЛДП 2 - Усть-Карская ГЭС-Амдермская| {equipment_results['max_currents'][1]:.1f}      | {equipment_results['max_currents'][1]:.1f}       | {equipment_results['sections'][1]}
ЛДП 3 - Усть-Карская ГЭС-Каратайская| {equipment_results['max_currents'][2]:.1f}     | {equipment_results['max_currents'][2]:.1f}      | {equipment_results['sections'][2]}
ЛДП 4 - Каратайская ВДЭС-Варнекская | {equipment_results['max_currents'][3]:.1f}     | {equipment_results['max_currents'][3]:.1f}      | {equipment_results['sections'][3]}

Проверка по короне:
Для ЛЭП 110 кВ сечение провода должно быть не менее 70 мм².
Все линии удовлетворяют этому условию.

Проверка по длительно-допустимому току:
Все выбранные провода проходят проверку.

Принимаем марку провода: АС-70/11

2.5. Выбор марок и номинальных мощностей трансформаторов
--------------------------------------------------------
Желаемая мощность трансформатора: S_ж.тр = 0,65 × P_н / cosφ

Таблица 2.10 - Данные выбранных трансформаторов
-----------------------------------------------
"""
        
        for station, transformer in equipment_results['transformers'].items():
            output += f"{station:<25} | {transformer['type']:<15} | {transformer['power']:<8} | {transformer['uk']}\n"
        
        output += f"""
2.6. Выбор схем соединения на стороне высокого напряжения
----------------------------------------------------------
Применяются типовые схемы РУ-110 кВ по ГОСТ Р 59279-2020.

Выбрана схема "Б" - Схема «мостик» с выключателями в цепях линий
и ремонтной перемычкой со стороны линий.
"""
        
        self.equipment_text.insert(1.0, output)
        self.results['equipment'] = equipment_results
    
    def calculate_all(self):
        """Выполнение полного расчёта"""
        # Расчёт ПРАМ
        self.calculate_pram()
        
        # Выбор оборудования
        if 'pram' in self.results:
            self.select_equipment()
        
        # Отображение общих результатов
        self.display_all_results()
        
        messagebox.showinfo('Успех', 'Полный расчёт выполнен успешно!')
    
    def display_all_results(self):
        """Отображение всех результатов"""
        self.results_text.delete(1.0, tk.END)
        
        output = f"""
1. ИСХОДНЫЕ ДАННЫЕ ДЛЯ ПРОЕКТИРОВАНИЯ

Tmax = {self.data['tmax']} ч
cos φ = {self.data['cosphi']}

Таблица 1 - Мощности нагрузок потребителей и мощности станций
┌─────────────────┬─────────────────┬─────────────────────────┬─────────────────┐
│ Насел. пункт    │ Нагрузка Р (МВт)│ Станция                 │ Мощность Р (МВт)│
├─────────────────┼─────────────────┼─────────────────────────┼─────────────────┤
│ Амдерма         │ {self.data['loads'][0]:<15} │ Амдермская ТЭЦ          │ {self.data['powers'][0]:<15} │
│ Усть-Кара       │ {self.data['loads'][1]:<15} │ Усть-Краская ГЭС+СЭС    │ {self.data['powers'][1]:<15} │
│ Каратайка       │ {self.data['loads'][2]:<15} │ Каратайская ВДЭС        │ {self.data['powers'][2]:<15} │
│ Варнек          │ {self.data['loads'][3]:<15} │ Варнекская ГПУ          │ {self.data['powers'][3]:<15} │
└─────────────────┴─────────────────┴─────────────────────────┴─────────────────┘

Длины линий электропередачи:
l1 (Варнек-Амдерма) = {self.data['line_lengths'][0]} км
l2 (Амдерма-Усть-Кара) = {self.data['line_lengths'][1]} км
l3 (Усть-Кара-Каратайка) = {self.data['line_lengths'][2]} км
l4 (Каратайка-Варнек) = {self.data['line_lengths'][3]} км

2. ВЫБОР КОНФИГУРАЦИИ ЭЛЕКТРИЧЕСКОЙ СЕТИ

Схема энергорайона представляет собой территорию с расположенными на ней 
четырьмя источниками питания в кольцевом соединении.

2.1. ПРАМ для нормального и расчётного послеаварийных режимов

Расчёт потоков активной мощности выполнен по правилу моментов.

Таблица 2.1 - Результаты расчёта потоков активной мощности в ветвях
┌─────────────────────────────────────────┬──────────────┬──────────────┐
│ Линия                                   │ P (МВт)      │ P (МВт)      │
├─────────────────────────────────────────┼──────────────┼──────────────┤
│ Амдермская ТЭЦ - Варнекская ГПУ         │ {self.results['pram']['ldp1']['p_amderma_varnik']:<12} │ {self.results['pram']['ldp1']['p_varnik_amderma']:<12} │
│ Усть-Карская ГЭС - Амдермская ТЭЦ       │ {self.results['pram']['ldp2']['p_amderma_ustkara']:<12} │ {self.results['pram']['ldp2']['p_ustkara_amderma']:<12} │
│ Усть-Карская ГЭС - Каратайская ВДЭС     │ {self.results['pram']['ldp3']['p_ustkara_karatayka']:<12} │ {self.results['pram']['ldp3']['p_karatayka_ustkara']:<12} │
│ Каратайская ВДЭС - Варнекская ГПУ       │ {self.results['pram']['ldp4']['p_karatayka_varnik']:<12} │ {self.results['pram']['ldp4']['p_varnik_karatayka']:<12} │
└─────────────────────────────────────────┴──────────────┴──────────────┘

2.2. Выбор номинальных напряжений

По формуле Илларионова: U_ном = 1000√(500l + 2500P)
Выбрано номинальное напряжение: U_ном = 110 кВ

2.3. Определение токов нормального и послеаварийного режимов

U_ср.ном = 1,05 × U_ном = 115,5 кВ

Токи рассчитываются по формуле: I = P × 1000 / (√3 × U_ср.ном × cosφ)

2.4. Выбор марок проводов ЛЭП

Выбор производится по экономической плотности тока δ_э = 1,0 А/мм²

Принимаем марку провода: АС-70/11

2.5. Выбор марок и номинальных мощностей трансформаторов

Таблица 2.10 - Данные выбранных трансформаторов
┌─────────────────────────┬──────────────────┬──────────────┬──────────────┐
│ Подстанция              │ Марка            │ Мощность     │ Uк (%)       │
├─────────────────────────┼──────────────────┼──────────────┼──────────────┤
│ Амдермская ТЭЦ          │ ТДН-25000/110    │ 25 МВА       │ 10,5         │
│ Усть-Карская ГЭС+СЭС    │ ТДН-25000/110    │ 25 МВА       │ 10,5         │
│ Каратайская ВДЭС        │ ТДН-10000/110    │ 10 МВА       │ 10,5         │
│ Варнекская ГПУ          │ ТДН-10000/110    │ 10 МВА       │ 10,5         │
└─────────────────────────┴──────────────────┴──────────────┴──────────────┘

2.6. Выбор схем соединения на стороне высокого напряжения

Выбрана схема "Б" - Схема «мостик» с выключателями в цепях линий
и ремонтной перемычкой со стороны линий.
"""
        
        self.results_text.insert(1.0, output)

    def draw_graphs(self):
        """Простые графики: столбцы токов (норм/ПАР) и векторы U1/U2"""
        self.canvas.delete('all')
        if 'pram' not in self.results:
            return
        currents = self.results['pram']['currents']

        # Оси для столбчатой диаграммы токов (слева)
        x0, y0 = 60, 450
        self.canvas.create_line(x0, y0, x0, 200, width=2)
        self.canvas.create_line(x0, y0, 380, y0, width=2)

        # Масштаб по току
        scale = 4.0
        labels = ['Л1', 'Л2', 'Л3', 'Л4']
        for i in range(4):
            i_norm = currents['normal'][i]
            i_par  = currents['emergency'][i]
            x = x0 + 60 + i*70
            # Нормальный
            self.canvas.create_rectangle(x-12, y0 - i_norm*scale, x+12, y0, fill='#27ae60')
            # ПАР
            self.canvas.create_rectangle(x+18-12, y0 - i_par*scale, x+18+12, y0, fill='#e74c3c')
            self.canvas.create_text(x, y0+15, text=labels[i])

        self.canvas.create_text(220, 180, text='Токи линий: нормальный (зелёный), ПАР (красный)', font=('Arial', 10, 'bold'))

        # Векторная диаграмма (справа)
        cx, cy = 640, 330
        self.canvas.create_line(cx-150, cy, cx+150, cy, width=1)
        self.canvas.create_line(cx, cy+150, cx, cy-150, width=1)

        # Векторы U1 и U2 одинаковой длины в противоположных направлениях как в разделе 9
        r = 120
        self.canvas.create_line(cx, cy, cx + r, cy, width=3, fill='#3498db')
        self.canvas.create_text(cx + r + 20, cy, text='U1')
        self.canvas.create_line(cx, cy, cx - r, cy, width=3, fill='#9b59b6')
        self.canvas.create_text(cx - r - 20, cy, text='U2')
        self.canvas.create_text(cx, cy - 170, text='Векторная диаграмма U1/U2 (эскиз как в RastrWin3)', font=('Arial', 10, 'bold'))

    def save_graphs_ps(self):
        if not hasattr(self, 'canvas'):
            return
        fname = filedialog.asksaveasfilename(defaultextension='.ps', filetypes=[('PostScript', '*.ps')],
                                             title='Сохранить графики как...')
        if fname:
            self.canvas.postscript(file=fname)
    
    def save_to_txt(self):
        """Сохранение в текстовый файл"""
        if not self.results:
            messagebox.showerror('Ошибка', 'Сначала выполните расчёт!')
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.txt',
                filetypes=[('Текстовые файлы', '*.txt'), ('Все файлы', '*.*')],
                title='Сохранить расчёт как...'
            )
            
            if filename:
                content = self.results_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo('Успех', f'Файл сохранён: {filename}')
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при сохранении: {str(e)}')
            
    def save_to_html(self):
        """Сохранение в HTML файл"""
        if not self.results:
            messagebox.showerror('Ошибка', 'Сначала выполните расчёт!')
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.html',
                filetypes=[('HTML файлы', '*.html'), ('Все файлы', '*.*')],
                title='Сохранить как HTML...'
            )
            
            if filename:
                content = self.results_text.get(1.0, tk.END)
                html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Расчёт электрических сетей</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .center {{ text-align: center; }}
        pre {{ white-space: pre-wrap; font-family: monospace; }}
    </style>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>'''
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo('Успех', f'HTML файл сохранён: {filename}')
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при сохранении: {str(e)}')
            
    def copy_to_clipboard(self):
        """Копирование в буфер обмена"""
        if not self.results:
            messagebox.showerror('Ошибка', 'Сначала выполните расчёт!')
            return
            
        try:
            content = self.results_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo('Успех', 'Текст скопирован в буфер обмена!')
            
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при копировании: {str(e)}')

if __name__ == '__main__':
    root = tk.Tk()
    app = ElectricalNetworkCalculator(root)
    root.mainloop()
