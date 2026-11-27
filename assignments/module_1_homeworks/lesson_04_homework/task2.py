# AI log: звертався до AI щоб зрозуміти, що від мене хочуть в задачі, бо або я тупий або завдання сформульоване не надто зрозуміло

# За вказаних нижче значень результат буде неправильний оскільки в неробочий день байдуже чи йде дощ - я вдома в безпеці
have_umbrella = False
rain_level = 7.0 # будь-яке значення більше 5
have_hood = False
is_workday = False

prepared = have_umbrella or rain_level < 5 and have_hood or not rain_level > 0 and is_workday
print(prepared)

# правильним буде наступний вираз, який враховує, що я намокну лише за умови, що йде дощ і я йду на роботу без парасолі й без капюшона
# пріоритет булевих операторів: not, and, or. відповідно спочатку not rain_level > 0 повертає False і разом з is_workday = False дає False, а має бути True
prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
print(prepared)