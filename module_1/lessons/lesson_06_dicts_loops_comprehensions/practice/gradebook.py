"""
Є записи оцінок, кожен — кортеж (студент, предмет, оцінка) grades.
Напиши програму, яка виводить:
Кількість оцінок: {'Олена': 3, 'Тарас': 2, 'Марта': 1}
Середній бал: {'Олена': 10.0, 'Тарас': 8.0, 'Марта': 11.0}
Предмети: {'Олена': ['математика', 'фізика'], 'Тарас': ['математика', 'фізика'], 'Марта': ['математика']}
Найкращий середній бал: Марта
"""

grades = [
    ("Олена", "математика", 10),
    ("Тарас", "математика", 7),
    ("Олена", "фізика", 12),
    ("Марта", "математика", 11),
    ("Тарас", "фізика", 9),
    ("Олена", "математика", 8),
]

number_of_rating = {}
subjects_by_person = {}
scores_by_person = {}

for grade in grades:
    number_of_rating[grade[0]] = number_of_rating.get(grade[0], 0) + 1
    scores_by_person.setdefault(grade[0], []).append(grade[2])
    subjects_by_person.setdefault(grade[0], set()).add(grade[1])

average_score = {person: sum(scores) / len(scores) for person, scores in scores_by_person.items()}
max_average = max(average_score, key=average_score.get)

print(f"Кількість оцінок: {number_of_rating}")
print(f"Середній бал: {average_score}")
print(f"Предмети: {subjects_by_person}")
print(f"Найкращий середній бал: {max_average} = {average_score[max_average]}")