from datetime import date, datetime
from dataclasses import dataclass
from io import BytesIO
from base64 import b64encode
from PyPDF2 import PdfReader
from number_to_string import get_string_by_number
from docxtpl import DocxTemplate
import os.path

@dataclass
class Passport:
    """ Класс для хранения данных паспорта """
    seria: str = ''
    number: str = ''
    date_of: date = None
    kemvidan: str = ''


@dataclass
class Person:
    """ Класс для хранения двнных продавца / покупателя"""
    fio: str = ''
    addres: str = ''
    passport: Passport = None


@dataclass
class Epts:
    brand: str = ''
    model: str = ''
    vin: str = ''
    year: str = ''
    engine: str = ''
    cabin: str = ''
    color: str = ''
    number: str = ''
    data: date = None
    rama: str = 'Отсутствует'
    organisation: str = 'ООО "ИСПЫТАТЕЛЬНЫЙ ЦЕНТР СПЕКТР-Ч"'


def check_person(person: Person) -> str:
    error = ''
    if person.fio == '':
        error = 'Не заполнено ФИО!!!'
    elif person.addres == '':
        error = 'Не заполнена прописка!!!'
    elif person.passport.seria == '':
        error = 'Не заполнена серия паспорта!!!'
    elif person.passport.number == '':
        error = 'Не заполнен номер паспорта!!!'
    elif person.passport.date_of is None:
        error = 'Не заполнена дата выдачи!!!'
    elif person.passport.kemvidan == '':
        error = 'Не заполнено поле кем выдан паспорт!!!'
    return error


def check_epts(epts: Epts) -> str:
    error = ''
    if epts.brand == '':
        error = 'Не заполнено поле Марка, модель ТС:'
    if epts.model == '':
        error = 'Не заполнено поле Марка, модель ТС:'
    if epts.vin == '':
        error = 'Не заполнено поле VIN'
    if epts.year == '':
        error = 'Не заполнено поле год выпуска'
    if epts.engine == '':
        error = 'Не заполнено поле № двигателя'
    if epts.cabin == '':
        error = 'Не заполнено поле № кузова'
    if epts.color == '':
        error = 'Не заполнено поле цвет автомобиля'
    if epts.number == '':
        error = 'Не заполнено поле № ЕПТС'
    if epts.data is None:
        error = 'Не заполнено поле Дата выдачи'
    if epts.rama == '':
        error = 'Не заполнено поле рамма/шасси'
    if epts.organisation is None:
        error = 'Не заполнено поле организация выдавшая ЭПТС'
    return error


def check_original_pts(up_file) -> dict:
    dt = {'OK': False, 'text': ''}
    file = BytesIO(up_file.getvalue())
    reader = PdfReader(file)
    try:
        page = reader.pages[0]
        text = page.extract_text()
    except:
        return dt
    list_of_rows = text.split('\n')
    if list_of_rows[0].strip() == 'Выписка' and list_of_rows[1].strip() == 'из электронного паспорта' \
                                                                           ' транспортного средства':
        dt['OK'] = True
        dt['text'] = text
        return dt
    else:
        return dt


def parse_pts(first_page: str, epts: Epts) -> Epts:
    rows = first_page.split('\n')[2:-4]
    epts.number = rows[0].strip()
    epts.vin = rows[3].split()[2].strip()
    epts.brand = rows[4].split()[1].strip()
    epts.model = rows[5].split()[0].strip()
    epts.engine = rows[10].split()[3].strip()
    epts.cabin = rows[12].split()[4].strip()
    epts.color = rows[13].split()[4].strip()
    epts.year = rows[14].split()[2].strip()
    epts.data = datetime.strptime(rows[-1].split()[-2].strip(), '%d.%m.%Y')
    return epts


def sum_to_str(summ):
    sm_propis = get_string_by_number(summ)
    sum_ls = sm_propis.split()
    sm_propis = ' '.join(sum_ls[:-2])
    return sm_propis


def make_dkp_docx(data: date, place: str, seller: Person, buyer: Person, epts: Epts, car_price: int):
    summa = f'{car_price} ({sum_to_str(car_price)})'
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    context = {'day': str(data.day),  # составление доумента
               'month': months[data.month-1],  # составление доумента
               'year': str(data.year),  # составление доумента
               'city': place,  # место составления
               'seller_name': seller.fio,
               'seller_address': seller.addres,
               'pass_s': seller.passport.seria,
               'pass_no': seller.passport.number,
               'p_d': str(seller.passport.date_of.day),
               'p_m': months[data.month-1],
               'p_y': str(seller.passport.date_of.year),
               'pass_vidano': seller.passport.kemvidan,
               'buyer_name': buyer.fio,
               'buyer_address': buyer.addres,
               'pass_s2': buyer.passport.seria,
               'pass_no2': buyer.passport.number,
               'p_d2': str(buyer.passport.date_of.day),
               'p_m2': months[data.month-1],
               'p_y2': str(buyer.passport.date_of.year),
               'pass_vidano2': buyer.passport.kemvidan,
               'model': f'{epts.brand} {epts.model}',
               'vin': epts.vin,
               'year_avto': epts.year,
               'engine': epts.engine,
               'shassi': epts.rama,
               'kuzov': epts.cabin,
               'color': epts.color,
               'epts_no': epts.number,
               'epts_kem': epts.organisation,
               'epts_d': str(epts.data.day),
               'epts_m': months[data.month-1],
               'epts_y': str(epts.data.year),
               'summa': summa
               }
    doc = DocxTemplate('template.docx')
    doc.render(context)
    doc.save(f'{epts.vin}.docx')
    if os.path.exists(f'{epts.vin}.docx'):
        return True
    else:
        return False
    # sleep(5)
    # convert(f'{epts.vin}.docx')



def main():
    doc = DocxTemplate('template.docx')
    context = {
        'day': '12',
        'month':'april',
        'year': '2023'
    }
    doc.render(context)
    doc.save('v1.docx')
    with open('v1.docx', 'rb') as f:
        file = f.read()
        file_2 = b64encode(file).decode('utf-8')
        print(file_2)

if __name__ == "__main__":
    main()
