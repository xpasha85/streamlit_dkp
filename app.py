import datetime
import os
from base64 import b64encode
from io import BytesIO

import streamlit as st
from datetime import date, datetime
from PyPDF2 import PdfReader
import my_classes
from my_classes import Person, Passport

st.set_page_config(page_title='Бланк ДКП', page_icon='📝')
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
# st.header('Бланк ДКП')

# --------- Шапка договора -----------------------
data = st.date_input(label='Дата составления договора')
place = st.text_input(label='Место составления договора', value='Уссурийск')

# ----------- Блок продавца -----------------------------------
expander_seller = st.expander('Данные продавца:')
seller = Person()
with expander_seller:
    seller.fio = st.text_input(label='Фио', placeholder='Фамилия Имя Отчество', label_visibility='hidden').title()
    # Форма с колонками для ввода серии номера паспорта, даты выдачи и на строке ниже - кем выдано
    # st.write('Паспорт')
    passport_seller = Passport()
    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        passport_seller.seria = st.text_input('серия', placeholder='серия паспорта', label_visibility='hidden')
    with scol2:
        passport_seller.number = st.text_input('номер', placeholder='номер паспорта', label_visibility='hidden')
    with scol3:
        # max_date = date(date.today().year-18, date.today().month, date.today().day)
        passport_seller.date_of = st.date_input(label='Дата выдачи', min_value=date(1930, 1, 1))
    passport_seller.kemvidan = st.text_input('Кем выдан', placeholder='Кем выдан', label_visibility='hidden')
    seller.addres = st.text_input(label='Адрес', placeholder='Адрес регистрации (прописка)', label_visibility='hidden')
    seller.passport = passport_seller

# ----------- Блок покупателя -----------------------------------
expander_buyer = st.expander('Данные покупателя:')
buyer = Person()
with expander_buyer:
    buyer.fio = st.text_input(label='Фио1', placeholder='Фамилия Имя Отчество', label_visibility='hidden').title()
    # Форма с колонками для ввода серии номера паспорта, даты выдачи и на строке ниже - кем выдано
    # st.write('Паспорт')
    passport_buyer = Passport()
    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        passport_buyer.seria = st.text_input('серия1', placeholder='серия паспорта', label_visibility='hidden')
    with bcol2:
        passport_buyer.number = st.text_input('номер1', placeholder='номер паспорта', label_visibility='hidden')
    with bcol3:
        # max_date = date(date.today().year-18, date.today().month, date.today().day)
        passport_buyer.date_of = st.date_input(label='Дaта выдачи', min_value=date(1930, 1, 1))
    passport_buyer.kemvidan = st.text_input('Кем выдан1', placeholder='Кем выдан', label_visibility='hidden')
    buyer.addres = st.text_input(label='Адрес1', placeholder='Адрес регистрации (прописка)', label_visibility='hidden')
    buyer.passport = passport_buyer

# --------------------- Блок проверки ПТС -----------------------------------
have_pts = st.checkbox('У меня есть оригинал ЭПТС')
epts = my_classes.Epts()
is_ok_pts = False
if have_pts:
    up_file = st.file_uploader('Загрузить ЭПТС', 'pdf')
    if up_file:
        is_ok_pts = my_classes.check_original_pts(up_file)['OK']
        text_first_page = my_classes.check_original_pts(up_file)['text']
        if not is_ok_pts:
            st.error('Некорректный ЭПТС!!!')
        else:
            st.success('ЭПТС распознан.')
            epts = my_classes.parse_pts(text_first_page, epts)

# --------------- Блок ПТС -----------------------------
expander_pts = st.expander('Данные транспортного средства', is_ok_pts)
with expander_pts:
    ecol1, ecol2, ecol7 = st.columns(3)
    with ecol1:
        if is_ok_pts:
            br_mod = st.text_input('Марка, модель ТС:', value=f'{epts.brand} {epts.model}')
        else:
            br_mod = st.text_input('Марка, модель ТС:')
        if len(br_mod.split()) > 1:
            epts.brand = br_mod.split()[0].upper()
            epts.model = ' '.join(br_mod.split()[1:]).upper()
        else:
            st.warning('Поле должно содержать минимум 2 слова.')
        #  st.text(f'{epts.brand} {epts.model}')
    with ecol2:
        epts.vin = st.text_input('Идентификационный номер (VIN):', value=epts.vin).upper()
    with ecol7:
        epts.cabin = st.text_input('№ кузова:', value=epts.cabin).upper()
    ecol3, ecol4, ecol5, ecol6 = st.columns(4)
    with ecol3:
        epts.year = st.text_input('Год выпуска:', value=epts.year)
    with ecol4:
        epts.engine = st.text_input('№ двигателя:', value=epts.engine).upper()
    with ecol5:
        epts.rama = st.text_input('№ шасси(рамы):', value=epts.rama)
    with ecol6:
        epts.color = st.text_input('Цвет:', value=epts.color)
    ecol8, ecol9, ecol10 = st.columns(3)
    with ecol8:
        epts.number = st.text_input('№ ЕПТС:', value=epts.number)
    with ecol9:
        epts.organisation = st.text_input('Орган выдавший ЕПТС:', value=epts.organisation)
    with ecol10:
        if epts.data:
            epts.data = st.date_input('Дата выдачи:', value=epts.data)
        else:
            epts.data = st.date_input('Дата выдачи:')
    # st.write(epts)

# ---- Блок с ценой на авто -------------------
car_price = st.number_input('Стоимость транспортного средства', min_value=1)

is_docx = False
if st.button('Сформировать'):
    # ------ всякие проверки заполнености ---------
    err_seller = my_classes.check_person(seller)
    err_buyer = my_classes.check_person(buyer)
    err_eptr = my_classes.check_epts(epts)
    if err_seller != '':
        st.error(err_seller)
        st.stop()
    if err_buyer != '':
        st.error(err_buyer)
        st.stop()
    if err_eptr != '':
        st.error(err_eptr)
        st.stop()

    # ----------Формирование документа ----------
    is_docx = my_classes.make_dkp_docx(data, place, seller, buyer, epts, car_price)

if is_docx:
    st.success('👇👇👇 Документ успешно создан. Скачать можно по кнопке ниже ')
    mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    filename = f'{epts.vin}.docx'
    with open(filename, 'rb') as file:
        st.download_button(
            label='Скачать ДКП',
            data=file,
            mime=mime,
            file_name=filename
        )
    os.remove(filename)