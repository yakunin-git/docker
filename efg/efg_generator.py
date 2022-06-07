#!/usr/bin/python3.8

import random
import time

efk_name_list = [
    "Сергеев Натан Тарасович",
    "Медведев Гарри Рубенович",
    "Никонов Панкратий Федосеевич",
    "Сысоев Лука Христофорович",
    "Кудряшов Павел Борисович",
    "Селезнёв Кирилл Сергеевич",
    "Маслов Альфред Эдуардович",
    "Трофимов Герман Валентинович",
    "Смирнов Федор Германнович",
    "Дорофеев Корнелий Германович",
    "Осипов Георгий Тимофеевич",
    "Панов Назарий Кимович",
    "Мухин Евгений Антонович",
    "Лыткин Ираклий Александрович",
    "Исаков Аркадий Парфеньевич"
]

efk_bill_list = [
    5000,
    600,
    2340,
    890,
    1000,
    3000,
    500,
    8000,
    590,
    700,
    760,
    390,
    4000,
    10000,
    400
]

efk_city_list = [
    "Уфа",
    "Волгоград",
    "Павлодар",
    "Москва",
    "Чита",
    "Сочи",
    "Казань",
    "Ужгород",
    "Тюмень",
    "Воронеж",
    "Суздаль",
    "Екатеринбург",
    "Уральск",
    "Подольск",
    "Серпухов"
]

efk_age_list = [
    27,
    34,
    51,
    44,
    25,
    31,
    37,
    42,
    35,
    29,
    26,
    38,
    41,
    54,
    53

]

efk_index_list = [
    1.5,
    2.1,
    6.7,
    0.5,
    5.2,
    3.7,
    5.4,
    2.5,
    7.4,
    6.3,
    6.7,
    4.9,
    3.6,
    6.4,
    4.4
]

while True:
    random_time = range(random.randint(3, 10))
    with open("/var/log/fluent-bit.log", "a") as fluent_file:
        log_message = ("%s %d %s %d %f\n" % (random.choice(efk_name_list), random.choice(efk_age_list),
                                              random.choice(efk_city_list), random.choice(efk_bill_list),
                                              random.choice(efk_index_list)))
        print(log_message)
        fluent_file.write(log_message)
    time.sleep(random_time.stop)

