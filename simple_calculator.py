#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощённый калькулятор токов короткого замыкания
Без внешних зависимостей - только стандартные библиотеки Python
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import math
import os

class SimpleShortCircuitCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title('Расчёт токов короткого замыкания - Курсовая работа')
        self.root.geometry('900x700')
        
        # Переменные для хранения данных
        self.data = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Исходные данные
        self.input_frame = ttk.Frame(notebook)
        notebook.add(self.input_frame, text='Исходные данные')
        self.create_input_tab()
        
        # Вкладка 2: Результаты расчёта
        self.results_frame = ttk.Frame(notebook)
        notebook.add(self.results_frame, text='Результаты расчёта')
        self.create_results_tab()
        
        # Вкладка 3: Экспорт
        self.export_frame = ttk.Frame(notebook)
        notebook.add(self.export_frame, text='Экспорт результатов')
        self.create_export_tab()
        
        # Кнопка расчёта
        btn_calc = tk.Button(self.root, text='Выполнить расчёт', 
                           command=self.calculate, bg='#27ae60', fg='white',
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
        
        # Параметры генератора
        gen_frame = ttk.LabelFrame(scrollable_frame, text='Параметры генератора', padding=10)
        gen_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        tk.Label(gen_frame, text='Напряжение (кВ):').grid(row=0, column=0, sticky='w', pady=2)
        self.voltage_var = tk.StringVar(value='110')
        tk.Entry(gen_frame, textvariable=self.voltage_var, width=15).grid(row=0, column=1, sticky='w', pady=2)
        
        tk.Label(gen_frame, text='Мощность (МВт):').grid(row=1, column=0, sticky='w', pady=2)
        self.power_var = tk.StringVar(value='20')
        tk.Entry(gen_frame, textvariable=self.power_var, width=15).grid(row=1, column=1, sticky='w', pady=2)
        
        tk.Label(gen_frame, text='Сверхпереходное сопротивление (о.е.):').grid(row=2, column=0, sticky='w', pady=2)
        self.xd_var = tk.StringVar(value='0.22')
        tk.Entry(gen_frame, textvariable=self.xd_var, width=15).grid(row=2, column=1, sticky='w', pady=2)
        
        tk.Label(gen_frame, text='Коэффициент мощности:').grid(row=3, column=0, sticky='w', pady=2)
        self.cosphi_var = tk.StringVar(value='0.8')
        tk.Entry(gen_frame, textvariable=self.cosphi_var, width=15).grid(row=3, column=1, sticky='w', pady=2)
        
        # Параметры трансформатора
        trans_frame = ttk.LabelFrame(scrollable_frame, text='Параметры трансформатора', padding=10)
        trans_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        tk.Label(trans_frame, text='Мощность (МВА):').grid(row=0, column=0, sticky='w', pady=2)
        self.trans_power_var = tk.StringVar(value='25')
        tk.Entry(trans_frame, textvariable=self.trans_power_var, width=15).grid(row=0, column=1, sticky='w', pady=2)
        
        tk.Label(trans_frame, text='Напряжение КЗ (%):').grid(row=1, column=0, sticky='w', pady=2)
        self.uk_var = tk.StringVar(value='10.5')
        tk.Entry(trans_frame, textvariable=self.uk_var, width=15).grid(row=1, column=1, sticky='w', pady=2)
        
        # Параметры линии
        line_frame = ttk.LabelFrame(scrollable_frame, text='Параметры линии', padding=10)
        line_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        tk.Label(line_frame, text='Длина (км):').grid(row=0, column=0, sticky='w', pady=2)
        self.line_length_var = tk.StringVar(value='61')
        tk.Entry(line_frame, textvariable=self.line_length_var, width=15).grid(row=0, column=1, sticky='w', pady=2)
        
        tk.Label(line_frame, text='Удельное сопротивление (Ом/км):').grid(row=1, column=0, sticky='w', pady=2)
        self.line_res_var = tk.StringVar(value='0.429')
        tk.Entry(line_frame, textvariable=self.line_res_var, width=15).grid(row=1, column=1, sticky='w', pady=2)
        
        # Базисные величины
        base_frame = ttk.LabelFrame(scrollable_frame, text='Базисные величины', padding=10)
        base_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5, padx=10)
        
        tk.Label(base_frame, text='Базисная мощность (МВА):').grid(row=0, column=0, sticky='w', pady=2)
        self.base_power_var = tk.StringVar(value='1000')
        tk.Entry(base_frame, textvariable=self.base_power_var, width=15).grid(row=0, column=1, sticky='w', pady=2)
        
        tk.Label(base_frame, text='Базисное напряжение (кВ):').grid(row=1, column=0, sticky='w', pady=2)
        self.base_voltage_var = tk.StringVar(value='110')
        tk.Entry(base_frame, textvariable=self.base_voltage_var, width=15).grid(row=1, column=1, sticky='w', pady=2)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_results_tab(self):
        # Текстовое поле для результатов
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap='word', font=('Courier', 10))
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
        
    def calculate(self):
        try:
            # Получаем данные из полей
            voltage = float(self.voltage_var.get())
            power = float(self.power_var.get())
            xd = float(self.xd_var.get())
            cosphi = float(self.cosphi_var.get())
            trans_power = float(self.trans_power_var.get())
            uk = float(self.uk_var.get())
            line_length = float(self.line_length_var.get())
            line_res = float(self.line_res_var.get())
            base_power = float(self.base_power_var.get())
            base_voltage = float(self.base_voltage_var.get())
            
            # Выполняем расчёты
            results = self.perform_calculations(voltage, power, xd, cosphi, trans_power, uk, 
                                              line_length, line_res, base_power, base_voltage)
            
            # Сохраняем результаты
            self.data = results
            
            # Отображаем результаты
            self.display_results(results)
            
            messagebox.showinfo('Успех', 'Расчёт выполнен успешно!')
            
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при расчёте: {str(e)}')
            
    def perform_calculations(self, voltage, power, xd, cosphi, trans_power, uk, 
                           line_length, line_res, base_power, base_voltage):
        # Расчёт сверхпереходной ЭДС генератора
        sinphi = math.sqrt(1 - cosphi**2)
        generator_emf = math.sqrt(cosphi**2 + (sinphi + xd)**2) * voltage
        
        # Расчёт сопротивлений
        generator_resistance = xd * (voltage**2 / power) * (base_power / voltage**2)
        transformer_resistance = (uk / 100) * (voltage**2 / trans_power)
        line_resistance = line_res * line_length
        
        total_resistance = generator_resistance + transformer_resistance + line_resistance
        
        # Расчёт токов короткого замыкания
        three_phase_current = generator_emf / (math.sqrt(3) * total_resistance)
        two_phase_current = (math.sqrt(3) / 2) * three_phase_current
        single_phase_current = 3 * generator_emf / (3 * total_resistance)
        two_phase_ground_current = math.sqrt(3) * generator_emf / (2 * total_resistance)
        
        # Симметричные составляющие
        positive_sequence_current = three_phase_current
        negative_sequence_current = -three_phase_current
        zero_sequence_current = 0
        
        # Напряжения в месте КЗ
        positive_sequence_voltage = generator_emf - positive_sequence_current * total_resistance
        negative_sequence_voltage = -negative_sequence_current * total_resistance
        zero_sequence_voltage = -zero_sequence_current * total_resistance
        
        # Коэффициенты токораспределения
        generator_coefficient = generator_resistance / total_resistance
        transformer_coefficient = transformer_resistance / total_resistance
        line_coefficient = line_resistance / total_resistance
        
        return {
            'voltage': voltage,
            'power': power,
            'xd': xd,
            'cosphi': cosphi,
            'trans_power': trans_power,
            'uk': uk,
            'line_length': line_length,
            'line_res': line_res,
            'base_power': base_power,
            'base_voltage': base_voltage,
            'generator_emf': generator_emf,
            'generator_resistance': generator_resistance,
            'transformer_resistance': transformer_resistance,
            'line_resistance': line_resistance,
            'total_resistance': total_resistance,
            'three_phase_current': three_phase_current,
            'two_phase_current': two_phase_current,
            'single_phase_current': single_phase_current,
            'two_phase_ground_current': two_phase_ground_current,
            'positive_sequence_current': positive_sequence_current,
            'negative_sequence_current': negative_sequence_current,
            'zero_sequence_current': zero_sequence_current,
            'positive_sequence_voltage': positive_sequence_voltage,
            'negative_sequence_voltage': negative_sequence_voltage,
            'zero_sequence_voltage': zero_sequence_voltage,
            'generator_coefficient': generator_coefficient,
            'transformer_coefficient': transformer_coefficient,
            'line_coefficient': line_coefficient
        }
        
    def display_results(self, results):
        self.results_text.delete(1.0, tk.END)
        
        output = f'''МИНОБРНАУКИ РОССИИ
Федеральное государственное бюджетное образовательное учреждение высшего образования
«Самарский государственный технический университет» (ФГБОУ ВО «СамГТУ»)
филиал в г. Новокуйбышевске

Кафедра «Электроэнергетика, электротехника и автоматизация технологических процессов»

КУРСОВОЙ ПРОЕКТ
по дисциплине: Переходные процессы
на тему: Расчёт токов короткого замыкания в электроэнергетической системе

Направление подготовки: 13.03.02 Электроэнергетика и электротехника

Выполнил: студент 4 курса, группы 13-НФ21 Корытников Р.М
Руководитель: к.т.н., доцент по кафедре «ЭЭиАТП» Складчиков А.А.

Работа защищена «____» ___________ 20__ г.
Оценка ___________________

Новокуйбышевск, 2024

{'='*80}

РАСЧЁТ ТОКОВ КОРОТКОГО ЗАМЫКАНИЯ В ЭЛЕКТРОЭНЕРГЕТИЧЕСКОЙ СИСТЕМЕ

{'='*80}

1. ИСХОДНЫЕ ДАННЫЕ ДЛЯ ПРОЕКТИРОВАНИЯ

Таблица 1 - Исходные данные
┌─────────────────────────────────────────────────┬──────────────┐
│ Параметр                                        │ Значение     │
├─────────────────────────────────────────────────┼──────────────┤
│ Напряжение системы                              │ {results['voltage']} кВ      │
│ Мощность генератора                             │ {results['power']} МВт       │
│ Сверхпереходное сопротивление генератора        │ {results['xd']} о.е.        │
│ Коэффициент мощности                            │ {results['cosphi']}          │
│ Мощность трансформатора                         │ {results['trans_power']} МВА │
│ Напряжение короткого замыкания трансформатора   │ {results['uk']} %           │
│ Длина линии                                     │ {results['line_length']} км  │
│ Удельное сопротивление линии                   │ {results['line_res']} Ом/км │
│ Базисная мощность                               │ {results['base_power']} МВА │
│ Базисное напряжение                             │ {results['base_voltage']} кВ │
└─────────────────────────────────────────────────┴──────────────┘

2. РАСЧЁТ ПАРАМЕТРОВ СХЕМЫ ЗАМЕЩЕНИЯ

2.1. Расчёт сверхпереходной ЭДС генератора

Сверхпереходная ЭДС генератора рассчитывается по формуле:
E'' = √(cos²φ + (sinφ + xd'')²) × Uном

где: cosφ = {results['cosphi']}, xd'' = {results['xd']} о.е., Uном = {results['voltage']} кВ

sinφ = √(1 - cos²φ) = √(1 - {results['cosphi']}²) = {math.sqrt(1 - results['cosphi']**2):.3f}

E'' = √({results['cosphi']}² + ({math.sqrt(1 - results['cosphi']**2):.3f} + {results['xd']})²) × {results['voltage']} = {results['generator_emf']:.2f} кВ

2.2. Расчёт сопротивлений элементов схемы

Сопротивление генератора:
xг = xd'' × (Uном² / Sном) × (Sб / Uб²) = {results['generator_resistance']:.3f} Ом

Сопротивление трансформатора:
xт = (uk% / 100) × (Uном² / Sном) = {results['transformer_resistance']:.3f} Ом

Сопротивление линии:
Rл = r0 × L = {results['line_resistance']:.3f} Ом

Общее сопротивление:
Z = {results['total_resistance']:.3f} Ом

Таблица 2 - Параметры схемы замещения
┌─────────────────────────────────────┬──────────────┐
│ Параметр                            │ Значение     │
├─────────────────────────────────────┼──────────────┤
│ Сверхпереходная ЭДС генератора      │ {results['generator_emf']:.2f} кВ       │
│ Сопротивление генератора            │ {results['generator_resistance']:.3f} Ом │
│ Сопротивление трансформатора        │ {results['transformer_resistance']:.3f} Ом │
│ Сопротивление линии                 │ {results['line_resistance']:.3f} Ом      │
│ Общее сопротивление                 │ {results['total_resistance']:.3f} Ом     │
└─────────────────────────────────────┴──────────────┘

3. РАСЧЁТ ТОКОВ КОРОТКОГО ЗАМЫКАНИЯ

3.1. Ток трёхфазного короткого замыкания

Iкз(3) = E'' / (√3 × Z) = {results['generator_emf']:.2f} / (√3 × {results['total_resistance']:.3f}) = {results['three_phase_current']:.2f} кА

3.2. Ток двухфазного короткого замыкания

Iкз(2) = (√3/2) × Iкз(3) = (√3/2) × {results['three_phase_current']:.2f} = {results['two_phase_current']:.2f} кА

3.3. Ток однофазного короткого замыкания

Iкз(1) = 3 × E'' / (2 × Z + Z0) = 3 × {results['generator_emf']:.2f} / (3 × {results['total_resistance']:.3f}) = {results['single_phase_current']:.2f} кА

3.4. Ток двухфазного короткого замыкания на землю

Iкз(1,1) = √3 × E'' / (Z + Z0) = √3 × {results['generator_emf']:.2f} / (2 × {results['total_resistance']:.3f}) = {results['two_phase_ground_current']:.2f} кА

Таблица 3 - Результаты расчёта токов короткого замыкания
┌─────────────────────────────┬──────────────┐
│ Вид короткого замыкания     │ Ток (кА)     │
├─────────────────────────────┼──────────────┤
│ Трёхфазное КЗ               │ {results['three_phase_current']:.2f}          │
│ Двухфазное КЗ               │ {results['two_phase_current']:.2f}          │
│ Однофазное КЗ               │ {results['single_phase_current']:.2f}          │
│ Двухфазное КЗ на землю      │ {results['two_phase_ground_current']:.2f}          │
└─────────────────────────────┴──────────────┘

4. СИММЕТРИЧНЫЕ СОСТАВЛЯЮЩИЕ

4.1. Токи симметричных составляющих

Ток прямой последовательности: I₁ = {results['positive_sequence_current']:.2f} кА
Ток обратной последовательности: I₂ = {results['negative_sequence_current']:.2f} кА
Ток нулевой последовательности: I₀ = {results['zero_sequence_current']:.2f} кА

4.2. Напряжения симметричных составляющих

Напряжение прямой последовательности: U₁ = {results['positive_sequence_voltage']:.2f} кВ
Напряжение обратной последовательности: U₂ = {results['negative_sequence_voltage']:.2f} кВ
Напряжение нулевой последовательности: U₀ = {results['zero_sequence_voltage']:.2f} кВ

4.3. Коэффициенты токораспределения

Коэффициент генератора: Cг = {results['generator_coefficient']:.3f}
Коэффициент трансформатора: Cт = {results['transformer_coefficient']:.3f}
Коэффициент линии: Cл = {results['line_coefficient']:.3f}

Таблица 4 - Симметричные составляющие
┌──────────────────┬─────────────┬─────────────────┬──────────────┐
│ Последовательность│ Ток (кА)   │ Напряжение (кВ) │ Коэффициент  │
├──────────────────┼─────────────┼─────────────────┼──────────────┤
│ Прямая           │ {results['positive_sequence_current']:.2f}    │ {results['positive_sequence_voltage']:.2f}      │ {results['generator_coefficient']:.3f}     │
│ Обратная         │ {results['negative_sequence_current']:.2f}    │ {results['negative_sequence_voltage']:.2f}      │ {results['transformer_coefficient']:.3f}     │
│ Нулевая          │ {results['zero_sequence_current']:.2f}    │ {results['zero_sequence_voltage']:.2f}      │ {results['line_coefficient']:.3f}     │
└──────────────────┴─────────────┴─────────────────┴──────────────┘

5. ЗАКЛЮЧЕНИЕ

По результатам расчётов токов короткого замыкания в электроэнергетической системе получены следующие основные результаты:

1. Максимальный ток короткого замыкания составляет {max(results['three_phase_current'], results['two_phase_current'], results['single_phase_current'], results['two_phase_ground_current']):.2f} кА при {['трёхфазном', 'двухфазном', 'однофазном', 'двухфазном на землю'][[results['three_phase_current'], results['two_phase_current'], results['single_phase_current'], results['two_phase_ground_current']].index(max(results['three_phase_current'], results['two_phase_current'], results['single_phase_current'], results['two_phase_ground_current']))]} КЗ.

2. Сопротивление генератора составляет {results['generator_resistance']:.3f} Ом, что соответствует {results['generator_coefficient']*100:.1f}% от общего сопротивления системы.

3. Наибольший вклад в общее сопротивление вносят: {'генератор' if results['generator_coefficient'] > results['transformer_coefficient'] and results['generator_coefficient'] > results['line_coefficient'] else 'трансформатор' if results['transformer_coefficient'] > results['line_coefficient'] else 'линия'} ({max(results['generator_coefficient'], results['transformer_coefficient'], results['line_coefficient'])*100:.1f}%).

4. Полученные значения токов КЗ позволяют правильно выбрать и настроить защитное оборудование для обеспечения надёжной работы энергосистемы.

5. Рекомендации по защите:
   - Проверьте уставки релейной защиты
   - Убедитесь в селективности защит
   - Проверьте состояние заземляющих устройств
   - Рассмотрите установку ограничителей перенапряжений

{'='*80}

Список литературы

1. Справочник по проектированию электроэнергетических систем / Под ред. С.С. Рокотяна и И.М. Шапиро. – М.: Энергоатомиздат, 1985.

2. Электрические системы и сети: Методическое пособие по курсу «Электрические системы и сети» для курсового проектирования и подготовки выпускных квалификационных работ / Сост. А.А. Гирфанов, В.Г. Гольдштейн, В.П. Салтыков, Л.М. Сулейманова. Самар. гос. техн. ун-т; Самара, 2006.

3. Расчёт коротких замыканий и выбор электрооборудования: Учебное пособие для студентов энергетических ВУЗ / И.П. Крючков, Б.Н. Неклепаев, В.А. Старшинов и др.; Под ред. И.П. Крючкова и В.А. Старшинова. - М.: Академия, 2005.

4. Правила устройства электроустановок: 7-е издание (ПУЭ) / Главгосэнергонадзор России. М.: Изд-во ЗАО «Энергосервис», 2007.
'''
        
        self.results_text.insert(1.0, output)
        
    def save_to_txt(self):
        if not self.data:
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
        if not self.data:
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
    <title>Расчёт токов короткого замыкания</title>
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
        if not self.data:
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
    app = SimpleShortCircuitCalculator(root)
    root.mainloop()

