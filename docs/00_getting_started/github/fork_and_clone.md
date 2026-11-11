# Fork і Clone

Коротка версія всього налаштування — [Швидкий старт](../quick_start.md).

## Що таке fork

Репозиторій курсу належить викладачу: читати його може кожен, а змінювати — лише він. **Fork** — це твоя особиста копія цього репозиторію **на GitHub**, яка пам'ятає, звідки її скопійовано. У своїй копії ти власник: створюєш гілки, робиш commit-и, надсилаєш домашні роботи.

- **Fork** — копія на GitHub: репозиторій викладача → твій акаунт. Один раз, кнопкою на сайті.
- **Clone** — копія на комп'ютер: твій fork → папка на диску. Один раз, командою або через PyCharm.
- **upstream** і **origin** — назви, під якими Git на твоєму комп'ютері знає репозиторій викладача і твій fork.

Fork не оновлюється сам — нові уроки ти забираєш командами з розділу [«Перед кожним заняттям»](#before-class) унизу сторінки.

Довідка GitHub: [Fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).

## 1️⃣ Створи Fork репозиторію

Потрібен акаунт GitHub — якщо його ще немає: [Реєстрація на GitHub](../quick_start.md#github-signup).

Перейди у репозиторій курсу:

```
https://github.com/NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026
```

Натисни кнопку **Fork** угорі праворуч — або відкрий сторінку створення одразу: [https://github.com/NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026/fork](https://github.com/NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026/fork).

### У вікні «Create a new fork»

**Owner** — натисни **Choose an owner** і вибери свій GitHub акаунт

**Repository name**

```
PY-Course-Victor-Nikoriak-11-11-2026
```

### Обов'язково перевір

✅ **Copy the main branch only** — увімкнено

Після цього натисни **Create fork**.

### Що відбудеться

GitHub створить копію репозиторію у твоєму акаунті:

```
https://github.com/<your-username>/PY-Course-Victor-Nikoriak-11-11-2026
```

Приклад:

```
https://github.com/student123/PY-Course-Victor-Nikoriak-11-11-2026
```

### Важливо

Ти працюєш **тільки у своєму fork**:

```
NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026  → repo викладача
your-username/PY-Course-Victor-Nikoriak-11-11-2026   → твій fork
```

## 2️⃣ Clone у PyCharm

PyCharm → `File → New Project from Version Control`

Встав **URL свого fork**:

```
github.com/<your-username>/PY-Course-Victor-Nikoriak-11-11-2026
```

## 3️⃣ Додай upstream (один раз)

У Terminal:

```bash
git remote add upstream https://github.com/NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026.git
```

Перевірка:

```bash
git remote -v
```

Повинно бути:

```
origin   → твій repo
upstream → repo викладача
```

## 🔄 Перед кожним заняттям { #before-class }

Оновлення матеріалів:

```bash
git checkout main
git pull upstream main
git push origin main
```

Якщо `git pull` зупинився з помилкою — [Часті проблеми і нюанси](../troubleshooting.md#local-changes).
