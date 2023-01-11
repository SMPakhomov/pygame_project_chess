import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QLCDNumber, QCheckBox, QInputDialog, QFileDialog
# from start_screen import start_screen


class Registration(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('DATA/registration.ui', self)
        self.sms_label.hide()
        self.double_psw_lineedit.hide()
        self.label_8.hide()
        self.vhod_btn.hide()
        self.registration_btn.hide()
        self.voiti_btn.setText(" ")
        self.setWindowTitle('Авторизация')

        type_of_registration, ok_pressed = QInputDialog.getItem(
            self, "Выберите тип входа", "",
            ("Вход", "Регистрация"), 1, False)
        if ok_pressed:
            if type_of_registration == "Вход":
                self.voiti_btn.setText("Войти")
                self.double_psw_lineedit.hide()
                self.label_8.hide()
                self.voiti_btn.clicked.connect(self.get_id)
            else:
                self.double_psw_lineedit.show()
                self.label_8.show()
                self.voiti_btn.setText("Зарегистрироваться")
                self.voiti_btn.clicked.connect(self.add_id)

    def get_id(self):  # функция для входа в уже существующий аккаунт. для получения id пользователя из дб
        self.name = self.name_lineedit.text()
        self.password = self.password_lineedit.text()
        self.surname = self.surname_lineedit.text()
        con = sqlite3.connect("DATA/new.db")
        cur = con.cursor()
        result = str(cur.execute('''select psw from first
                            where name like ?
                            and surname like ?''', (self.name, self.surname)).fetchall())[3:-4]
        if result == self.password:
            check = 'Вход произведен успешно, '
        else:
            check = 'Введены неверные данные'
        if check == "Вход произведен успешно, ":
            self.sms_label.hide()
            con = sqlite3.connect("DATA/new.db")
            cur = con.cursor()
            self.id = str(cur.execute('''select id from first
                            where name like ? and
                            surname like ?
                            and psw like ?''', (self.name, self.surname, self.password)).fetchall())[2:-3]
            self.sms_label.setText("Вход произведен успешно, " + self.name)
            self.sms_label.show()
            self.voiti_btn.hide()
            con.close()

        else:
            self.sms_label.setText(check)

    def add_id(self):  # функция для регистрации нового пользователя
        if self.password_lineedit.text() != self.double_psw_lineedit.text():
            self.double_psw_lineedit.setText("Пароли не совпадают")
        else:
            self.password = self.password_lineedit.text()

            self.name = self.name_lineedit.text()
            self.surname = self.surname_lineedit.text()
            con = sqlite3.connect("DATA/new.db")
            cur = con.cursor()
            cur.execute('''insert into first(name, surname, psw)
                               values (?, ?, ?)''', (self.name, self.surname, self.password))

            self.id = str(cur.execute('''select id from first
                                        where surname like ? and name like ? and psw like ?''',
                                      (self.surname, self.name, self.password)).fetchall())[2:-3]

            cur.execute('''insert into play(person, loose, win)
                               values (?,
                               '0', '0')''', (self.id,))

            self.sms_label.setText('Регистрация прошла успешно, ' + self.name)
            self.sms_label.show()
            con.commit()
            con.close()
            self.voiti_btn.hide()
        # start_screen(self.id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Registration()
    ex.show()
    sys.exit(app.exec())