# Часті проблеми і нюанси

Тут зібрано помилки, які найчастіше трапляються під час налаштування й роботи з курсом. Знайди текст своєї помилки пошуком по сторінці (**Ctrl+F**, на macOS **⌘F**) або пошуком книги.

Налаштовуєш усе вперше — іди за сторінкою [Швидкий старт](quick_start.md) і повертайся сюди, коли щось не збіглося з очікуваним.

## Спершу — три команди діагностики

Більшість проблем із Git пояснюють три команди. Виконай їх **у папці проєкту** й уважно прочитай відповідь:

```bash
git status
git branch --show-current
git remote -v
```

| Команда | Що показує |
|---|---|
| `git status` | у якій ти гілці, які файли змінено, що Git радить зробити далі |
| `git branch --show-current` | назву поточної гілки |
| `git remote -v` | куди дивляться `origin` (твій fork) і `upstream` (викладач) |

Git майже завжди сам пише, що робити: підказки починаються зі слова `hint:` або стоять у дужках після `use "git …"`.

## Встановлення: Git і Python

### `git` не знайдено

```text
git : The term 'git' is not recognized as the name of a cmdlet…
zsh: command not found: git
```

- Git не встановлено → [Встановлення Git](git_setup.md).
- Git щойно встановлено, але термінал відкрито раніше → **закрий термінал і відкрий новий**. PyCharm і VS Code теж треба перезапустити: вони запам'ятовують `PATH` під час старту.

### Python не знайдено { #python-not-found }

```text
python : The term 'python' is not recognized…
Python was not found; run without arguments to install from the Microsoft Store…
zsh: command not found: python
```

| Система | Що робити |
|---|---|
| macOS / Linux | команда називається `python3`: `python3 --version`. Після активації `.venv` запрацює і `python` |
| Windows | спробуй `py --version`. Якщо працює — Python встановлено, але його немає в `PATH`: створюй середовище командою `py -m venv .venv` |
| Windows, відкривається Microsoft Store | **Параметри → Програми → Додаткові параметри програм → Псевдоніми виконання програм** (App execution aliases) → вимкни `python.exe` і `python3.exe`, потім відкрий новий термінал |
| Windows, нічого не допомогло | перевстанови Python з [python.org/downloads](https://www.python.org/downloads/) і постав галочку **Add python.exe to PATH** на першому екрані інсталятора |

### Встановлено кілька версій Python

Подивись, який саме Python запускається:

=== "Windows (PowerShell)"

    ```powershell
    py --list
    where.exe python
    ```

=== "macOS / Linux"

    ```bash
    which -a python3
    ```

Для курсу достатньо будь-якої версії 3.10+. Усередині активованого `.venv` завжди працює той Python, яким це середовище створено, — тому важливо працювати саме у `.venv`.

## Віртуальне середовище і бібліотеки

### PowerShell: «виконання сценаріїв вимкнено»

```text
.venv\Scripts\activate : File …\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

Виконай один раз і повтори активацію:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Команда активації «не знайдена»

Команда залежить від термінала, а не лише від системи:

| Термінал | Команда |
|---|---|
| Windows PowerShell | `.venv\Scripts\activate` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| Git Bash на Windows | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

Якщо папки `.venv` немає — ти не в папці проєкту (`cd` у неї) або середовище ще не створено ([Швидкий старт → крок 6](quick_start.md#venv)).

### Linux: `ensurepip is not available`

```text
The virtual environment was not created successfully because ensurepip is not available.
```

На Ubuntu/Debian модуль `venv` ставиться окремо:

```bash
sudo apt install python3-venv
```

Потім видали недостворену папку `.venv` і створи середовище ще раз.

### `error: externally-managed-environment`

Ти запускаєш `pip install` у системному Python, а не у `.venv`. Активуй середовище (на початку рядка має бути `(.venv)`) і повтори. Не використовуй `--break-system-packages`.

### `pip` не знайдено

Викликай pip через Python — це працює завжди:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Не встановлюються бібліотеки з `requirements.txt` { #pip-install-fails }

Якщо хоч один пакет зі списку не вдалося встановити, `pip install -r requirements.txt` не встановлює нічого.

1. Прочитай **останні рядки** виводу: там назва пакета, на якому сталася помилка.
2. Для модуля 1 повний список не потрібен. Постав мінімум і працюй далі:

    ```bash
    pip install jupyterlab notebook ipykernel
    ```

3. Типові причини:

    | Текст помилки | Причина | Рішення |
    |---|---|---|
    | `pg_config executable not found` (пакет `psycopg2`) | пакет збирається з вихідного коду й потребує встановленого PostgreSQL | `pip install psycopg2-binary`; сам пакет потрібен лише в модулі баз даних |
    | `Microsoft Visual C++ 14.0 or greater is required` | для пакета немає готової збірки під твою версію Python | встанови попередню стабільну версію Python і створи `.venv` заново |
    | `Could not find a version that satisfies the requirement` | надто нова або надто стара версія Python | те саме |
    | `ReadTimeoutError`, `Connection reset` | нестабільний інтернет | повтори команду; `pip install --default-timeout=100 -r requirements.txt` |
    | `No space left on device` | закінчилося місце на диску | звільни місце й повтори |

4. Якщо не вдається — надішли викладачу останні 20 рядків виводу.

### `ModuleNotFoundError`, хоча бібліотеку встановлено { #wrong-kernel }

Бібліотеку встановлено в один Python, а код виконується іншим. Перевір, який Python працює:

```python
import sys
print(sys.executable)
```

У шляху має бути `.venv` проєкту. Якщо ні:

- **PyCharm** — вибери інтерпретатор `.venv` у правому нижньому куті ([PyCharm → Інтерпретатор](pycharm.md)).
- **VS Code** — **Ctrl+Shift+P → Python: Select Interpreter**; для ноутбука — **Select Kernel** угорі праворуч ([VS Code](vscode.md)).
- **Jupyter у браузері** — запускай `jupyter lab` з активованим `.venv` ([Jupyter локально → Кернели](jupyter.md)).

Встановити бібліотеку саме в той Python, на якому працює ноутбук, можна прямо з клітинки:

```python
%pip install назва_пакета
```

### Зламалося середовище — як створити заново

Папку `.venv` можна безпечно видалити: у ній немає твого коду.

=== "Windows (PowerShell)"

    ```powershell
    deactivate
    Remove-Item -Recurse -Force .venv
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install jupyterlab notebook ipykernel
    ```

=== "macOS / Linux"

    ```bash
    deactivate
    rm -rf .venv
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install jupyterlab notebook ipykernel
    ```

Якщо `deactivate` каже, що такої команди немає, — середовище не було активне, іди далі.

## GitHub: акаунт, SSH, доступ

### Хочу змінити логін на GitHub

Можна: **Settings → Account → Change username** ([github.com/settings/admin](https://github.com/settings/admin)). Але зваж наслідки:

- посилання зі старим логіном, які ти вже залишив на сторонніх ресурсах (резюме, LinkedIn, чати, інші сайти), можуть перестати працювати й показувати помилку 404;
- адреса профілю і сайти на GitHub Pages (`<логін>.github.io`) перестають відкриватися за старою адресою одразу; приклад: `nikoriakviktot.github.io/notes_chat_app/` після зміни логіна на `NikoriakViktor` показує `404 — There isn't a GitHub Pages site here`;
- на комп'ютері треба оновити адресу `origin`:

    ```bash
    git remote set-url origin git@github.com:<новий-логін>/PY-Course-Victor-Nikoriak-11-11-2026.git
    ```

Після зміни повідом викладачу новий логін. Як обрати логін одразу добре — [Швидкий старт → Реєстрація на GitHub](quick_start.md#github-signup).

### `Permission denied (publickey)`

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

GitHub не впізнав твій комп'ютер: SSH-ключ не створено або не додано в акаунт. Пройди [SSH-ключі](github/ssh_keys.md) і перевір командою `ssh -T git@github.com`.

Тимчасовий обхід — перейти на HTTPS:

```bash
git remote set-url origin https://github.com/<твій-логін>/PY-Course-Victor-Nikoriak-11-11-2026.git
```

### `Permission to NikoriakViktor/… denied` або помилка 403 під час `git push`

```text
remote: Permission to NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026.git denied to <твій-логін>.
```

Ти надсилаєш код у репозиторій викладача, а не у свій fork. Перевір `git remote -v` і див. наступний розділ. Чому так — [Що таке fork і навіщо він](quick_start.md#fork).

### Клонував репозиторій викладача замість fork { #cloned-upstream }

`git remote -v` показує `NikoriakViktor` у рядках `origin`. Переклоновувати не треба — достатньо перейменувати:

```bash
git remote rename origin upstream
git remote add origin git@github.com:<твій-логін>/PY-Course-Victor-Nikoriak-11-11-2026.git
git remote -v
```

Якщо fork ще не створено — спершу створи його: [Швидкий старт → крок 4](quick_start.md#fork).

### На сторінці Fork немає мого акаунта в полі **Owner**

- Ти не увійшов у GitHub — увійди й онови сторінку.
- У тебе вже є fork цього репозиторію — GitHub не дає створити другий у тому самому акаунті. Відкрий наявний: `https://github.com/<твій-логін>/PY-Course-Victor-Nikoriak-11-11-2026`.

### `remote upstream already exists` / `remote origin already exists`

Такий remote уже додано. Подивись, куди він веде (`git remote -v`), і за потреби виправ адресу:

```bash
git remote set-url upstream https://github.com/NikoriakViktor/PY-Course-Victor-Nikoriak-11-11-2026.git
```

### `Repository not found`

- Помилка в адресі: перевір логін і назву репозиторію.
- В адресі лишилися кутові дужки: має бути `git@github.com:olena-kovalenko/…`, а не `git@github.com:<olena-kovalenko>/…`.
- Fork ще не створено.

### GitHub просить пароль і не приймає його

```text
remote: Support for password authentication was removed…
```

GitHub не приймає пароль від акаунта в командному рядку. Варіанти:

- налаштуй [SSH-ключ](github/ssh_keys.md) і перемкни адресу на SSH: `git remote set-url origin git@github.com:<твій-логін>/PY-Course-Victor-Nikoriak-11-11-2026.git`;
- на Windows Git відкриває вікно входу через браузер — увійди там;
- або створи [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) і введи його замість пароля.

### `push declined due to email privacy restrictions`

У налаштуваннях GitHub увімкнено приховування email, а в commit-ах стоїть справжня адреса. Або вимкни **Block command line pushes that expose my email** на сторінці [github.com/settings/emails](https://github.com/settings/emails), або вкажи в Git адресу виду `…@users.noreply.github.com` з тієї ж сторінки.

### У терміналі SSH працює, а в PyCharm — ні

Див. [SSH-ключі → розділ 8](github/ssh_keys.md).

## Git: щоденна робота

### Не бачу нових уроків

```bash
git checkout main
git pull upstream main
git push origin main
```

- `fatal: 'upstream' does not appear to be a git repository` → не додано `upstream`: [Швидкий старт → крок 5](quick_start.md#clone).
- Команда пройшла, а уроку немає → переконайся, що ти в гілці `main` (`git branch --show-current`): у гілці домашки нових уроків не буде, доки не оновиш її.

### `Your local changes to the following files would be overwritten by merge` { #local-changes }

**Найчастіша проблема курсу.** Ти відкрив ноутбук уроку в гілці `main` і запустив клітинки — файл змінився. Тепер викладач оновив той самий файл, і Git не знає, чию версію лишити.

Спершу подивись, які файли змінено:

```bash
git status
```

Далі — один із трьох варіантів:

=== "Зміни не потрібні"

    Відкинь їх і забери оновлення. **Зміни у вказаних файлах зникнуть назавжди.**

    ```bash
    git restore .
    git pull upstream main
    ```

=== "Зміни потрібні"

    Сховай їх, онови `main`, поверни:

    ```bash
    git stash
    git pull upstream main
    git stash pop
    ```

    Якщо після `git stash pop` з'явився конфлікт — див. [«Конфлікт»](#conflict).

=== "Це була домашка"

    Перенеси зміни в гілку — див. [«Зробив домашку в main»](#homework-in-main).

!!! tip "Як цього уникнути"
    Не змінюй файли уроків у `main`. Для експериментів зроби копію ноутбука з іншою назвою (наприклад, `my_lesson_03.ipynb`) або працюй в окремій гілці. Файли з власними назвами оновленню не заважають.

### Зробив домашку в `main` { #homework-in-main }

**Варіант 1 — commit ще не зроблено** (`git status` показує змінені файли):

```bash
git checkout -b homework-XX
git add .
git commit -m "Homework XX"
git push -u origin homework-XX
git checkout main
```

Незбережені зміни «переїжджають» у нову гілку разом із тобою.

**Варіант 2 — commit уже зроблено в `main`:**

```bash
git branch homework-XX
git fetch upstream
git reset --hard upstream/main
git checkout homework-XX
git push -u origin homework-XX
```

Перший рядок зберігає твої commit-и в новій гілці, третій повертає `main` до стану викладача. **Виконуй рядки саме в цьому порядку**: `git reset --hard` без попереднього `git branch` знищить твою роботу.

### `Updates were rejected` під час `git push`

```text
! [rejected]        main -> main (non-fast-forward)
```

На GitHub є commit-и, яких немає в тебе.

- У гілці домашки (ти працював з двох комп'ютерів або редагував файл на сайті): `git pull`, потім `git push`.
- У `main`: твій `main` розійшовся з викладацьким — див. [«Зробив домашку в main»](#homework-in-main), варіант 2.

Не використовуй `git push --force`, якщо викладач прямо не сказав цього зробити.

### `Need to specify how to reconcile divergent branches`

Git просить один раз обрати спосіб об'єднання:

```bash
git config --global pull.rebase false
```

Після цього повтори `git pull`.

### Відкрився дивний редактор і я не можу вийти

Git відкрив Vim, щоб ти ввів повідомлення commit-а або підтвердив злиття.

- Зберегти й вийти: натисни **Esc**, введи `:wq`, натисни **Enter**.
- Вийти без збереження: **Esc**, `:q!`, **Enter**.

Щоб Git надалі відкривав зрозуміліший редактор:

```bash
git config --global core.editor "code --wait"   # VS Code
git config --global core.editor "nano"          # nano (macOS / Linux)
```

### Конфлікт (`CONFLICT … Automatic merge failed`) { #conflict }

Ти й викладач змінили ті самі рядки одного файлу. Git позначив спірні місця:

```text
<<<<<<< HEAD
твоя версія
=======
версія викладача
>>>>>>> upstream/main
```

1. `git status` покаже файли з конфліктом (`both modified`).
2. Якщо конфлікт у **файлі уроку**, який тобі не потрібно зберігати, візьми версію викладача:

    ```bash
    git checkout --theirs шлях/до/файлу
    git add шлях/до/файлу
    git commit -m "Merge upstream main"
    ```

3. Якщо у **твоєму файлі** — відкрий його, залиш потрібний варіант, видали рядки з `<<<<<<<`, `=======`, `>>>>>>>`, потім `git add` і `git commit`. PyCharm і VS Code показують конфлікт у зручному вікні з кнопками вибору.
4. Хочеш скасувати злиття й повернутися до стану перед ним — `git merge --abort`.

Конфлікт у ноутбуці `.ipynb` вручну розв'язувати важко: це великий JSON-файл. Збережи свою версію під іншою назвою, а оригінал візьми у викладача (пункт 2).

### `fatal: not a git repository`

Ти не в папці проєкту. Перейди в неї:

```bash
cd шлях/до/PY-Course-Victor-Nikoriak-11-11-2026
```

Підказка: команда `pwd` показує, де ти зараз, а `ls` — що лежить у цій папці.

### `Author identity unknown` / `Please tell me who you are`

Не виконано перше налаштування Git:

```bash
git config --global user.name "Імʼя Прізвище"
git config --global user.email "твій_email_на_GitHub"
```

### `detected dubious ownership in repository`

Папку створено іншим користувачем системи (часто — якщо проєкт лежить на зовнішньому диску або ти запускав термінал від імені адміністратора). Git сам підказує команду — виконай її:

```bash
git config --global --add safe.directory шлях/до/проєкту
```

### Windows: `Filename too long`

```bash
git config --global core.longpaths true
```

І клонуй проєкт у коротку папку, наприклад `C:\Projects`.

### `warning: LF will be replaced by CRLF`

Це попередження, а не помилка: Git узгоджує символи кінця рядка між Windows та іншими системами. Нічого робити не треба.

### `git add .` додав зайві файли

Подивись, що потрапило в commit, **до** того як його зробити:

```bash
git status
```

Прибрати файл зі списку (сам файл лишиться на диску):

```bash
git restore --staged шлях/до/файлу
```

У commit домашки мають потрапляти лише файли завдання. Папки `.venv` та `.idea` репозиторій ігнорує автоматично.

### Хочу скасувати останній commit

Commit ще **не** надіслано (`git push` не було):

```bash
git reset --soft HEAD~1
```

Зміни лишаться у файлах, зникне тільки сам commit. Якщо commit уже на GitHub — просто зроби новий commit із виправленням.

### `pathspec 'homework-01' did not match` / гілка не знайдена

- Гілки з такою назвою немає: `git branch` покаже наявні.
- Створити нову — `git checkout -b homework-01`; перейти в наявну — `git checkout homework-01` (без `-b`).

## Pull Request

### На GitHub немає кнопки **Compare & pull request**

Відкрий вкладку **Pull requests → New pull request** і вибери гілки вручну. Якщо гілки домашки немає у списку — її не надіслано: `git push -u origin homework-XX`.

### `There isn't anything to compare`

У гілці домашки немає commit-ів, яких немає в `main`: ти забув `git add` і `git commit` або зробив commit в іншій гілці. Перевір `git log --oneline -5` у гілці домашки.

### У Pull Request потрапили зайві файли або чужі зміни

Гілку створено не від свіжого `main`, або в commit потрапило зайве через `git add .`. Надалі перед кожною домашкою:

```bash
git checkout main
git pull upstream main
git checkout -b homework-XX
```

### Виправив зауваження — чи створювати новий Pull Request?

Ні. Зроби commit у ту саму гілку й `git push` — Pull Request оновиться сам. Докладно: [Pull Request](github/pull_request.md).

### Випадково натиснув **Merge** у своєму Pull Request

Напиши викладачу. Самостійно зливати Pull Request у курсі не можна — це правило з розділу [Здача домашніх робіт](homework_workflow.md).

## PyCharm

| Симптом | Що робити |
|---|---|
| `No Python interpreter configured for the project` | вибери інтерпретатор `.venv` у правому нижньому куті — [PyCharm → Інтерпретатор](pycharm.md) |
| `Invalid Python SDK` / `Invalid Python interpreter selected` | папку `.venv` видалено або перенесено разом із проєктом → створи середовище заново й вибери його знову |
| у терміналі немає `(.venv)` | **Settings → Tools → Terminal** → увімкни **Activate virtualenv** → відкрий нову вкладку термінала |
| PowerShell-команди не працюють у терміналі PyCharm | перевір **Settings → Tools → Terminal → Shell path** — [SSH-ключі → розділ 8](github/ssh_keys.md) |
| імпорт підкреслено червоним, хоча код працює | пакет встановлено в інший інтерпретатор; постав його через **Python Packages** |
| PyCharm довго «думає» після відкриття проєкту | триває індексація (смужка внизу) — дочекайся завершення |
| ноутбук не запускається, просить встановити Jupyter | погодься на встановлення або виконай `pip install jupyterlab notebook ipykernel` у терміналі з `(.venv)` |

Докладно: [PyCharm](pycharm.md).

## VS Code

| Симптом | Що робити |
|---|---|
| `Git not found. Install it or configure it using the 'git.path' setting` | встанови Git і **повністю перезапусти** VS Code |
| немає кнопки ▶ для запуску Python-файлу | не встановлено розширення **Python** (Microsoft) |
| `Select Kernel` не показує `.venv` | **Ctrl+Shift+P → Python: Select Interpreter** → вибери `.venv`; потім **Developer: Reload Window** |
| ноутбук просить встановити `ipykernel` | погодься або `pip install ipykernel` у терміналі з `(.venv)` |
| у терміналі немає `(.venv)` | відкрий **новий** термінал після вибору інтерпретатора |
| термінал: «виконання сценаріїв вимкнено» | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` — див. вище |
| VS Code питає «Do you trust the authors…» | для папки курсу натисни **Yes, I trust the authors** — інакше розширення працюють в обмеженому режимі |
| команда `code` не працює в терміналі (macOS) | **⇧⌘P → Shell Command: Install 'code' command in PATH** |

Докладно: [VS Code](vscode.md).

## Jupyter і ноутбуки

Повна таблиця — на сторінці [Jupyter локально → Типові проблеми](jupyter.md). Найчастіше:

| Симптом | Що робити |
|---|---|
| `jupyter: command not found` | активуй `.venv` або запусти `python -m jupyter lab` |
| `NameError`: змінна «не визначена», хоча клітинка з нею є | клітинку не виконано в цьому сеансі → **Run All** згори донизу |
| клітинка «зависла», `[*]` не зникає | **Kernel → Interrupt Kernel** |
| після `%pip install` нічого не змінилося | **Kernel → Restart Kernel** |
| ноутбук не знаходить файл із даними | подивись, від якої папки рахуються шляхи: `import os; print(os.getcwd())` |

!!! note "Який ноутбук відкривати"
    На заняттях працюй у файлах із закінченням `_student.ipynb` — це вправи без розв'язків. Клітинки з позначкою `🔒 DO NOT EDIT` не змінюй і не видаляй.

## Google Colab

### «Could not find … .ipynb» / «There was an error loading this notebook»

Кнопка Colab веде на шлях, де файлу вже немає (ноутбук перенесли або кнопка веде на інший репозиторій). Відкрий ноутбук через книгу курсу або заміни в адресі GitHub `https://github.com/` на `https://colab.research.google.com/github/`. Докладно: [Ноутбуки в Google Colab](colab.md).

### Зміни в Colab не збереглися

Ноутбук, відкритий із репозиторію курсу, не зберігає змін. Одразу після відкриття: **File → Save a copy in Drive**.

Решта: [Colab → Типові проблеми](colab.md).

## Нюанси, про які варто знати заздалегідь

- **Логін на GitHub.** Обери нормальний логін одразу — він буде в кожному посиланні на твої проєкти. Зміна логіна пізніше ламає посилання, які ти вже десь залишив. Докладно: [Швидкий старт → Реєстрація на GitHub](quick_start.md#github-signup).
- **Windows і OneDrive.** Не тримай проєкт у папці, яку синхронізує OneDrive (часто це Робочий стіл і «Документи»): синхронізація заважає Git і `.venv`. Використовуй `C:\Projects`.
- **Кирилиця й пробіли в шляху.** Шлях на кшталт `C:\Users\Олена\Мої проєкти\…` ламає частину інструментів. Латиниця без пробілів — надійніше.
- **Антивірус.** Перше встановлення бібліотек може тривати довго, бо антивірус перевіряє кожен файл у `.venv`.
- **Термінал усередині редактора й окремий термінал — різні вікна.** Активація `.venv` в одному не діє на інший.
- **`origin` і `upstream`.** Забираєш уроки з `upstream`, надсилаєш домашки в `origin`. Команди `git push upstream …` у курсі немає.
- **Гілка створюється від тієї, у якій ти стоїш.** Перед `git checkout -b homework-XX` завжди переходь у свіжий `main`, інакше в нову домашку потрапить попередня.
- **Fork не оновлюється сам.** Нові уроки з'являються у твоєму fork лише після `git pull upstream main` і `git push origin main`.
- **Кнопка «Sync fork» на GitHub** оновлює fork на сайті, але не папку на комп'ютері: після неї все одно потрібен `git pull origin main`. Простіше щоразу користуватися трьома командами з розділу [«Перед заняттям»](quick_start.md#before-class).
- **Регістр літер у назвах.** Windows і macOS зазвичай не розрізняють `Lesson.py` і `lesson.py`, а Linux і GitHub — розрізняють. Називай файли малими літерами.
- **Не видаляй і не перейменовуй файли курсу.** Власні файли називай так, щоб вони не збігалися з викладацькими.
- **Секрети.** Паролі, токени й приватний SSH-ключ (`id_ed25519` без `.pub`) не потрапляють у commit і не надсилаються нікому.
- **Два комп'ютери.** На кожному окремо: Git, Python, SSH-ключ, `git clone`, `.venv`. Перед роботою — `git pull`, після — `git push`.

## 🧰 Git шпаргалка

```bash
git status                  # що відбувається
git branch                  # які є гілки
git checkout назва_гілки    # перейти в гілку
git log --oneline -10       # останні 10 commit-ів
git diff                    # що змінено, але ще не додано
```

Повніша версія: [Git шпаргалка](../git-cheatsheet.md).

## 🆘 Якщо нічого не допомогло

Надішли викладачу **одним повідомленням**:

- що ти робив і яку команду виконав;
- **повний текст** помилки — текстом або скріншотом усього вікна термінала;
- вивід трьох команд:

    ```bash
    git status
    git remote -v
    git branch --show-current
    ```

- операційну систему (Windows / macOS / Linux) і редактор (PyCharm / VS Code).

Що точніший опис, то швидше знайдеться рішення 🙂
