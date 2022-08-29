import math
import sys
from typing import Union, Optional
from operator import add, sub, mul, truediv

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFontDatabase # Для шрифта

from design import Ui_MainWindow


operations = {
    '+': add,
    '-': sub,
    'x': mul,
    '/': truediv,
}

error_zero_div = 'Division by zero'
error_undefined = 'Result is undefined'

default_font_size = 40  
default_entry_font_size = 40

class Calculator(QMainWindow):
    """Тут располагается дефолтный код для QT приложения.
     с файлом дизайна
    """
    def __init__(self):
        super(Calculator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.entry_max_len = self.ui.le_entry.maxLength() 

        QFontDatabase.addApplicationFont("fonts/Rubik-Regular.ttf")

        # цифры
        self.ui.btn_0.clicked.connect(self.add_digit)
        self.ui.btn_1.clicked.connect(self.add_digit)
        self.ui.btn_2.clicked.connect(self.add_digit)
        self.ui.btn_3.clicked.connect(self.add_digit)
        self.ui.btn_4.clicked.connect(self.add_digit)
        self.ui.btn_5.clicked.connect(self.add_digit)
        self.ui.btn_6.clicked.connect(self.add_digit)
        self.ui.btn_7.clicked.connect(self.add_digit)
        self.ui.btn_8.clicked.connect(self.add_digit)
        self.ui.btn_9.clicked.connect(self.add_digit)

        # действия
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_ce.clicked.connect(self.clear_entry)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.negate)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        # математические операции
        self.ui.btn_calc.clicked.connect(self.calculate)
        self.ui.btn_plus.clicked.connect(self.math_operation)
        self.ui.btn_sub.clicked.connect(self.math_operation)
        self.ui.btn_mul.clicked.connect(self.math_operation)
        self.ui.btn_div.clicked.connect(self.math_operation)

    def add_digit(self):
        """Это метод добавляет цифр в поле ввода.
        Сигнал- это нажатие кнопки, то есть в переменной будет хранится последняя нажатая кнока
        Чтобы понять, что нажатая кнопка- это цифра, создаем кортеж с именами кнопок цифр
        Если имя объекта, которое послало сигнал есть в этом кортеже, значит выполняем тот самый метод добавления цифры
        """

        self.remove_error()
        self.clear_temp_if_equality()
        btn = self.sender() # QT объект, который посылает сигнал

        digit_buttons = ('btn_0', 'btn_1', 'btn_2', 'btn_3', 'btn_4',
                         'btn_5', 'btn_6', 'btn_7', 'btn_8', 'btn_9')

        if btn.objectName() in digit_buttons:
            if self.ui.le_entry.text() == '0':
                self.ui.le_entry.setText(btn.text())
            else:
                self.ui.le_entry.setText(self.ui.le_entry.text() +btn.text())
        
        self.adjust_entry_font_size()

    def add_point(self) -> None:
        """Метод для добавления точки.
        Если точки нет в поле ввода, то добавляем её при нажатии.
        """
        self.clear_temp_if_equality()
        if '.' not in self.ui.le_entry.text():
            self.ui.le_entry.setText(self.ui.le_entry.text() + '.')
            self.adjust_entry_font_size()

    def negate(self):
        """Метод добавления отрицания.
        Если отрицания нет в поле, значит добавляем.
        Иначе убираем левый символ с помощью среза [1:]"""
        self.clear_temp_if_equality()
        entry = self.ui.le_entry.text()

        if '-' not in entry:
            if entry != '0':
                entry = '-' + entry
        else:
            entry = entry[1:]

        if len(entry) == self.entry_max_len + 1 and '-' in entry:
            self.ui.le_entry.setMaxLength(self.entry_max_len + 1)
        # чтобы отрицательное число не вытесняло последнюю цифру
        else:
            self.ui.le_entry.setMaxLength(self.entry_max_len)
            self.adjust_entry_font_size()
    
    def backspace(self) -> None:
        """Метод обризает 1 крайний символ.
        Метод ставит в поле ввода ноль,
        если длина поля равна 1 или одной цифре с отрицанием"""
        self.remove_error()
        self.clear_temp_if_equality()
        entry = self.ui.le_entry.text()

        if len(entry) != 1:
            if len(entry) == 2 and '-' in entry:
                self.ui.le_entry.setText('0')
            else:
               self.ui.le_entry.setText(entry[:-1]) 
        else:
            self.ui.le_entry.setText('0')
        self.adjust_entry_font_size()

    def clear_all(self) -> None:
        """Метод для очистки всех полей.
        При использовании устанавливает в поле ввода значение '0'
        """
        self.remove_error()
        self.ui.le_entry.setText('0')
        self.adjust_entry_font_size()
        self.ui.lbl_temp.clear()
        self.adjust_temp_font_size()

    def clear_entry(self) -> None:
        """Метод для очистки поля ввода.
        """
        self.remove_error()
        self.clear_temp_if_equality()
        self.ui.le_entry.setText('0')
        self.adjust_entry_font_size()

    def clear_temp_if_equality(self) -> None:
        """Нажатая кнопка удаляет равенство во временном выражении.
        Метод присутствует в нескольких функциях."""
        if self.get_math_sign() == '=':
            self.ui.lbl_temp.clear()
            self.adjust_temp_font_size()

    @staticmethod
    def remove_trailing_zeros(num: str) -> str:
        """Метод для обрезания конечных нулей.
        Передаем в функцию стринг число, получать- тоже самое.
        Метод делает так, чтобы в конце чисел оставалось максимум .0,
        а не .0000000
        Возвращаем срез строки без двух последних символов, если они равны .0
        Иначе возвращаем просто n."""
        n = str(float(num))
        return n[:-2] if n[:-2] == '.0' else n

    def add_temp(self) -> None:
        """Метод для добавления временного выражения.
        Есть два типа временных выражений:
        1- число и математический знак (память калькулятора),
        2- равенство.
        Прежде всего мы убеждаемся, что в лейбле нет ничего,
        после этого можно что-либо добавлять или
        если временного выражения нет или есть равенство"""
        btn = self.sender()
        entry = self.remove_trailing_zeros(self.ui.le_entry.text())

        if not self.ui.lbl_temp.text() or self.get_math_sign() == '=':
            self.ui.lbl_temp.setText(entry + f' {btn.text()}')
            self.adjust_temp_font_size()
            self.ui.le_entry.setText('0')
            self.adjust_entry_font_size()

    def get_entry_num(self) -> Union[int, float]:
        """Метод для получения числа из поля ввода.
        Получаем текст ввода.
        Убираем точку при помощи strip.
        Возвращаем float или int в зависимости от получаемого числа."""
        entry = self.ui.le_entry.text().strip('.')
        return float(entry) if '.' in entry else int(entry)

    def get_temp_num(self) -> Union[int, float, None]:
        """Метод ждя получения числа из временного выражения.
        Если в лейбле есть текст, то получаем его, разделяем по пробелам
        и берем первый элемент.
        Возвращаем тоже самое, что и в методе получения числа из поля ввода."""
        if self.ui.lbl_temp.text():
            temp = self.ui.lbl_temp.text().strip('.').split()[0]
            return float(temp) if '.' in temp else int(temp)

    def get_math_sign(self) -> Optional[str]: # возвращает только строку или ничего
        """Метод для получения знака из временного выражения.
        Сначала удостоверимся о том, что в лейбле есть текст,
        затем получаем текст из него, разделяем по пробелам и вытаскиваем последний элемент.
        """
        if self.ui.lbl_temp.text():
            return self.ui.lbl_temp.text().strip('.').split()[-1]

    def get_entry_text_width(self) -> int:
        """Вспомогательный метод для получения ширины текста из поля."""
        return self.ui.le_entry.fontMetrics().boundingRect(self.ui.le_entry.text()).width()

    def get_temp_text_width(self) -> int:
        """Вспомогательный метод для получения ширины текста из лейбла."""
        return self.ui.lbl_temp.fontMetrics().boundingRect(self.ui.lbl_temp.text()).width()

    def calculate(self) -> Optional[str]:
        """Функция вычисления.
        Если в лейбле есть текст, то вводим переменную результата.
        Обрезаем конечные нули и приводим к строке.
        В скобках указываем с какими числами провести операцию.
        Порядок аргументов важен для деления и вычитания:
        сначала передаем число из временного выражения, а затем из поля ввода.
        """
        entry = self.ui.le_entry.text()
        temp = self.ui.lbl_temp.text()

        if temp:
            try:
                result = self.remove_trailing_zeros(
                    str(operations[self.get_math_sign()](self.get_temp_num(), self.get_entry_num()))
                )
                self.ui.lbl_temp.setText(temp + self.remove_trailing_zeros(entry) + ' =')
                self.adjust_temp_font_size()
                self.ui.le_entry.setText(result)
                self.adjust_entry_font_size()
                return result
            except KeyError:
                pass

            except ZeroDivisionError:
                if self.get_temp_num() == 0:
                    self.show_error(error_undefined)
                else:
                    self.show_error(error_zero_div)

    def math_operation(self) -> None:
        """Функция математической операции.
        Если в лейбле нет выражения- мы его добавляем.
        Если выражение есть- берем знак.
        Если он не равен знаку аргумента метода, тоесть 2 случая:
        1- равенство (добавляем временное выражение,
        иначе меняем знак выражения на знак нажатой кнопки.
        2- если знак равен знаку аргумента метода,
        то мы считаем выражение и добавляем в конец лейбла знак."""
        temp = self.ui.lbl_temp.text()
        btn = self.sender()

        try:
            if not temp:
                self.add_temp()
            else:
                if self.get_math_sign() != btn.text():
                    if self.get_math_sign() == '=':
                        self.add_temp()
                    else:
                        self.ui.lbl_temp.setText(temp[:-2] + f'{btn.text()}')
                else:
                    self.ui.lbl_temp.setText(self.calculate() + f'{btn.text()}')
        except:
            pass

        self.adjust_temp_font_size()

    def show_error(self, text: str) -> None:
        self.ui.le_entry.setMaxLength(len(text))
        self.ui.le_entry.setText(text)
        self.adjust_entry_font_size()
        self.disable_buttons(True)

    def remove_error(self) -> None:
        """Если текст поля равен ошибке.
        То ставим максимальную длину поля обратную к дефолтному значению
        и ставим текст 0"""
        if self.ui.le_entry.text() in (error_undefined, error_zero_div):
            self.ui.le_entry.setMaxLength(self.entry_max_len)
            self.ui.le_entry.setText('0')
            self.adjust_entry_font_size()
            self.disable_buttons(False)

    def disable_buttons(self, disable: bool) -> None:
        """Метод блокирует кнопки знаков, точки и отрицания."""
        self.ui.btn_calc.setDisabled(disable)
        self.ui.btn_plus.setDisabled(disable)
        self.ui.btn_sub.setDisabled(disable)
        self.ui.btn_mul.setDisabled(disable)
        self.ui.btn_div.setDisabled(disable)
        self.ui.btn_neg.setDisabled(disable)
        self.ui.btn_point.setDisabled(disable)

        color = 'color: #888;' if disable else 'color: white;'
        self.change_buttons_color(color)

    def change_buttons_color(self, css_color: str) -> None:
        """Метод меняет цвет кнопок при блокировке."""
        self.ui.btn_calc.setStyleSheet(css_color)
        self.ui.btn_plus.setStyleSheet(css_color)
        self.ui.btn_sub.setStyleSheet(css_color)
        self.ui.btn_mul.setStyleSheet(css_color)
        self.ui.btn_div.setStyleSheet(css_color)
        self.ui.btn_neg.setStyleSheet(css_color)
        self.ui.btn_point.setStyleSheet(css_color)

    def adjust_entry_font_size(self) -> None:
        """Метод регулирования размера шрифта в поле ввода."""
        font_size = default_entry_font_size
        while self.get_entry_text_width() > self.ui.le_entry.width() -15:
            font_size -= 1
            self.ui.le_entry.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

        font_size = 1
        while self.get_entry_text_width() < self.ui.le_entry.width() -60:
            font_size += 1

            if font_size > default_font_size:
                break

            self.ui.le_entry.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

    def adjust_temp_font_size(self) -> None:
        font_size = default_font_size
        while self.get_temp_text_width() > self.ui.lbl_temp.width() - 15:
            font_size -= 1
            self.ui.lbl_temp.setStyleSheet(f'font-size: ' + str(font_size) + 'pt; color: #888;')

        font_size = 1
        while self.get_temp_text_width() < self.ui.lbl_temp.width() - 60:
            font_size += 1

            if font_size > default_font_size:
                break

            self.ui.lbl_temp.setStyleSheet(f'font-size: ' + str(font_size) + 'pt; color: #888;')

    def resizeEvent(self, event) -> None:
        """Метод меняет размер шрифта при растягивания ширины окна.
        """
        self.adjust_entry_font_size()
        self.adjust_temp_font_size()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())