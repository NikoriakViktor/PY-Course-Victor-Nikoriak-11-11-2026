"""
Напиши функції:

count_by_student(grades) → {студент: кількість оцінок};
average_by_student(grades) → {студент: середній бал};
subjects_by_student(grades) → {студент: відсортований список предметів без повторів};
best_student(averages) → ім'я студента з найвищим середнім балом;
print_journal(grades) — друкує звіт, викликаючи функції вище.
Виклик print_journal(grades) має надрукувати:


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
    # ("Марта", "фізика", 5)
]

def count_by_student(grades):
    counts = {}
    for grade in grades:
        counts[grade[0]] = counts.get(grade[0], 0) + 1

    return counts

def subjects_by_student(grades):
    subjects_by_person = {}
    for grade in grades:
        subjects_by_person.setdefault(grade[0], set()).add(grade[1])

    return subjects_by_person

def score_by_person(grades):
    scores_by_person = {}
    for grade in grades:
        scores_by_person.setdefault(grade[0], []).append(grade[2])

    return scores_by_person

def average_by_student(grades):
    return {person: sum(scores) / len(scores) for person, scores in score_by_person(grades).items()}

def best_student(averages):
    if averages:
        return  max(averages, key=averages.get)

def print_journal(grades):
    print(f"Кількість оцінок: {count_by_student(grades)}")
    print(f"Середній бал: {average_by_student(grades)}")
    print(f"Предмети: {subjects_by_student(grades)}")
    print(f"Найкращий середній бал: {best_student(average_by_student(grades))}")

print(best_student({}))
print_journal(grades)