# Завдання 2.
# Знайдіть баг. Ви в безпеці від сьогоднішньої погоди, якщо:
# у тебе є парасолька...
# або якщо дощ не надто сильний (rain_level < 5) і у вас є капюшон...
# інакше все гаразд, хіба що йде дощ (rain_level > 0) і це робочий день
# Цей код намагається перетворити ці правила в один логічний вираз, але в ньому є помилка:
# have_umbrella = True
# rain_level = 0.0
# have_hood = True
# is_workday = True
# prepared = have_umbrella or rain_level < 5 and have_hood or not rain_level > 0 and is_workday
# print(prepared)
# Змініть значення чотирьох змінних, щоб знайти випадок, коли prepared дає неправильну відповідь.
# Перед кожним запуском запишіть очікуваний результат як коментар.
# Виправте вираз за допомогою дужок.
# Над виправленням додайте коментар, # Bug:що пояснює своїми словами, як Python згрупував вихідний вираз.

have_umbrella = True # Якщо have_umbrella = False при всіх інших True:
                       # False or (True and True) or (False and True)
                       # тоді маємо - False or True or True = True.
rain_level = 0      # Можемо вийти за діапазон подальшої умови (rain_level < 5) і прописати число > 5, доприкладу 8
                    # тоді отримуємо False; 8 > 0 дає True, а not True дає False.
                    # При have_umbrella=False, have_hood=True, is_workday=True:
                    # False or (False and True) or (False and True) = False.
have_hood = True    # Якщо поміняти have_hood на False, а is_workday на False
                    # False or (False and False) or (False and False) = False.
is_workday = True
# Bug: Програма згрупувала вираз як ((not (rain_level > 0)) and is_workday)
prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
print(prepared)