import customtkinter as ui
import winsound
import re
import random
import Ai
import json
import os
import atexit

DATASET_FILE = "speler_scores.json"

# Definieer knopafmetingen
windowX = 1200
windowY = 800
button_width = 270
button_height = 65
button_font = ("Arial", 42)
memdark = 0
memcolor = 0
volume = 100
naam = "no name"
catagorypad = "catogory.txt"
quizepad = ""
speler_scores = {}
time = 20

# Functie om de scores te laden
def load_scores():
    global speler_scores
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "r") as file:
            speler_scores = json.load(file)
    else:
        speler_scores = {}

# Functie om de scores op te slaan
def save_scores():
    with open(DATASET_FILE, "w") as file:
        json.dump(speler_scores, file)

load_scores()

# Functie om de categorieen te laden
def load_categories():
    with open(catagorypad, "r") as file:
        return [line.strip() for line in file if line.strip()]

# Functie om de categorieen op te slaan
def save_categories(categories):
    with open(catagorypad, "w") as file:
        for category in categories:
            file.write(f"{category}\n")

def open_ai_window(home):
    home.destroy()
    ai_window = ui.CTkToplevel()
    ai_window.geometry(f"{windowX}x{windowY}")
    ai_window.title("AI")

    # Voeg een label toe
    theme_label = ui.CTkLabel(ai_window, text="Geef een thema", font=button_font)
    theme_label.pack(pady=10)

    # Voeg een invoerveld toe
    theme_entry = ui.CTkEntry(ai_window, width=button_width, font=button_font)
    theme_entry.pack(pady=20)

    # Voeg een error label toe
    error_label = ui.CTkLabel(ai_window, text="", font=("Arial", 20), text_color="red")
    error_label.pack(pady=5)

    # Voeg een frame toe voor de knoppen
    button_frame = ui.CTkFrame(ai_window)
    button_frame.pack(pady=20)

    # Voeg de "Terug" knop toe
    back_button = ui.CTkButton(button_frame, text="Terug", command=lambda: close_window(ai_window), width=button_width//2, height=button_height, font=button_font)
    back_button.pack(side="left", padx=10)

    # Voeg de "Start Quiz" knop toe
    start_quiz_button = ui.CTkButton(button_frame, text="generate Quiz", command=lambda: gen_quiz(), width=button_width//2, height=button_height, font=button_font)
    start_quiz_button.pack(side="right", padx=10)

    def gen_quiz():
        theme = theme_entry.get().strip()
        if not theme:
            error_label.configure(text="Thema mag niet leeg zijn")
            return
        if len(theme) > 12:
            error_label.configure(text="Thema mag niet langer zijn dan 12 karakters")
            return
        if not re.match("^[a-zA-Z0-9]*$", theme):
            error_label.configure(text="Thema mag alleen letters en cijfers bevatten")
            return

        result = Ai.generate_quiz(theme)
        if result == -1:
            error_label.configure(text="Quiz kon niet worden gegenereerd")
        else:
            global quizepad
            quizepad = result
            ai_window.destroy()
            start_quiz()


def start_quiz():
    global naam, quizepad, timer_enabled

    quiz_window = ui.CTkToplevel()
    quiz_window.geometry(f"{windowX}x{windowY}")
    quiz_window.title("Quiz")

    # Lees de quizvragen uit het bestand
    with open(quizepad, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    print(lines)    
    questions = []
    options = []
    answers = []
    # Lees de vragen, opties en antwoorden uit het bestand
    for i in range(0, len(lines),6):#elke vraag is 6 regels lang
        questions.append(lines[i].strip())
        options.append([lines[i+1].strip(), lines[i + 2].strip(), lines[i + 3].strip(), lines[i + 4].strip()])
        answers.append(lines[i + 5].strip())

    # Schud de vragen en antwoorden door elkaar
    combined = list(zip(questions, options, answers))
    random.shuffle(combined)
    questions, options, answers = zip(*combined)
    # Initialiseer de quizstatus
    current_question = 0
    score = 0
    Levens = 3

    def update_question():
        nonlocal current_question, score, Levens

        if current_question >= len(questions):
            # Quiz is afgelopen want je hebt alle vragen beantwoord
            quiz_window.destroy()
            show_results(score)
            return

        question_label.configure(text=questions[current_question])
        A_button.configure(text=options[current_question][0])
        B_button.configure(text=options[current_question][1])
        C_button.configure(text=options[current_question][2])
        D_button.configure(text=options[current_question][3])
        score_label.configure(text=f"Score: {score}")
        lives_label.configure(text=f"Levens: {Levens}")
                                                                                                                                                                                   
    def get_answer_text(option):
        option_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        return options[current_question][option_index[option]]
    def check_answer(selected_option):
        nonlocal current_question, score, Levens

        # Verberg de timer
        timer_label.pack_forget()

        if selected_option == answers[current_question]:
            score += 1
            answer_label.configure(text=f"correct", text_color="Green")
        else:
            Levens -= 1
            answer_label.configure(text=f"FOUT antwoordt was {get_answer_text(answers[current_question])}", text_color="red")

        current_question += 1
        if Levens <= 0:
            quiz_window.destroy()
            show_results(score)
        else:
            def next_question():
                answer_label.configure(text="")
                # Maak de timer weer zichtbaar en reset deze
                global time 
                time = 20
                timer_label.configure(text=str(time))
                timer_label.pack(pady=10)
                update_question()

            quiz_window.after(3600, next_question)  # sleep werkte niet en after neemt maar een argument, vandaar de extra functie next_question

    # Maak een frame voor de quizinformatie
    info_frame = ui.CTkFrame(quiz_window)
    info_frame.pack(pady=20)

    # Naam label
    name_label = ui.CTkLabel(info_frame, text=f"Naam: {naam}", font=("Arial", 20))
    name_label.grid(row=0, column=0, padx=20)

    # Score label
    score_label = ui.CTkLabel(info_frame, text=f"Score: {score}", font=("Arial", 20))
    score_label.grid(row=0, column=1, padx=20)

    # Levens label
    lives_label = ui.CTkLabel(info_frame, text=f"Levens: {Levens}", font=("Arial", 20))
    lives_label.grid(row=0, column=2, padx=20)

    # Vraag label
    question_label = ui.CTkLabel(quiz_window, text="", font=("Arial", 36))
    question_label.pack(pady=40)

    # Opties frame
    options_frame = ui.CTkFrame(quiz_window)
    options_frame.pack(pady=20)

    # Optie knoppen
    A_button = ui.CTkButton(options_frame, text="", width=button_width, height=button_height, font=button_font, command=lambda: check_answer('A'))
    A_button.grid(row=0, column=0, padx=30, pady=18)

    B_button = ui.CTkButton(options_frame, text="", width=button_width, height=button_height, font=button_font, command=lambda: check_answer('B'))
    B_button.grid(row=0, column=1, padx=30, pady=18)

    C_button = ui.CTkButton(options_frame, text="", width=button_width, height=button_height, font=button_font, command=lambda: check_answer('C'))
    C_button.grid(row=1, column=0, padx=30, pady=18)

    D_button = ui.CTkButton(options_frame, text="", width=button_width, height=button_height, font=button_font, command=lambda: check_answer('D'))
    D_button.grid(row=1, column=1, padx=30, pady=18)

    # antwoordt label
    answer_label = ui.CTkLabel(quiz_window, text="", font=("Arial", 32, "bold"))
    answer_label.pack(pady=40)

    # Start de eerste vraag
    update_question()

    if timer_enabled:
        # Timer label
        timer_label = ui.CTkLabel(quiz_window, text="20", font=("Arial", 48), text_color="red")
        timer_label.pack(pady=10)

        # Start de countdown
        countdown(time, timer_label, quiz_window, on_timeout=lambda: check_answer(9))

def countdown(time_left, label, window, on_timeout):
    global time
    if time_left > 0:
        time_left = time
        label.configure(text=str(time_left))
        time = time - 1
        window.after(1000, countdown, time_left, label, window, on_timeout)
    else:
        # Tijd is om, markeer de vraag als fout
        label.configure(text="Tijd is om!")
        on_timeout()

def show_results(score):
    global naam, quizepad
    # Haal de categorie naam uit het pad
    categorie = quizepad.split("/")[-1].replace(".txt", "")

    # Zet de naam om naar kleine letters
    naam_lower = naam.lower()

    # Update de dataset
    if naam_lower not in speler_scores:
        speler_scores[naam_lower] = {}
    if categorie not in speler_scores[naam_lower] or speler_scores[naam_lower][categorie] < score:
        speler_scores[naam_lower][categorie] = score
    
    # Sla de bijgewerkte dataset direct op
    save_scores()

    # Maak een nieuw venster voor de resultaten
    result_window = ui.CTkToplevel()
    result_window.geometry(f"{windowX}x{windowY}")
    result_window.title("Resultaten")

    result_label = ui.CTkLabel(result_window, text=f"Je score is: {score}", font=("Arial", 30))
    result_label.pack(pady=40)

    replay_button = ui.CTkButton(result_window, text="Opnieuw spelen", width=button_width, height=button_height, font=button_font, command=lambda: [result_window.destroy(), start_quiz()])
    replay_button.pack(pady=20)
    close_button = ui.CTkButton(result_window, text="Sluiten", width=button_width, height=button_height, font=button_font, command=lambda: [result_window.destroy(), home_start()])
    close_button.pack(pady=20)

timer_enabled = False

def toggle_timer(timer_toggle_button):
    global timer_enabled
    timer_enabled = not timer_enabled
    if timer_enabled:
        timer_toggle_button.configure(text="Timer is Aan")
    else:
        timer_toggle_button.configure(text="Timer is Uit")

def Open_Quiz_setup(home):
    global quizepad

    # Verberg het hoofdvenster
    home.withdraw()
    Quiz_setup = ui.CTkToplevel()
    Quiz_setup.geometry(f"{windowX}x{windowY}")
    Quiz_setup.title("Quiz Setup")

    # Maak een frame om de setup-widgets te houden en centreer ze verticaal
    setup_frame = ui.CTkFrame(Quiz_setup)
    setup_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Spelersnaam invoer
    name_label = ui.CTkLabel(setup_frame, text="Player Naam", font=button_font)
    name_label.pack(pady=10)
    name_entry = ui.CTkEntry(setup_frame, width=button_width, font=button_font)
    name_entry.pack(pady=20)
    error_label = ui.CTkLabel(setup_frame, text="", font=("Arial", 20), text_color="red")
    error_label.pack(pady=5)
    # Categorie selectie
    # Lees categorieën uit het bestand
    with open(catagorypad, 'r') as file:
        categories = [line.strip() for line in file if line.strip()]

    # Maak een woordenboek om categorieën aan hun paden te koppelen
    category_dict = {category.replace('.txt', ''): category for category in categories}

    # Maak een selectiebox voor categorieën
    category_choices = list(category_dict.keys())

    # Controleer of category_choices niet leeg is
    if category_choices:
        selected_category = ui.StringVar(value=category_choices[0])
    else:
        selected_category = ui.StringVar(value="Geen categorieën beschikbaar")

    def select_category(choice):
        global quizepad
        quizepad = category_dict.get(choice, "")

    category_selection_box = ui.CTkOptionMenu(setup_frame, variable=selected_category, values=category_choices, width=button_width, height=button_height, font=button_font, command=select_category)
    category_selection_box.pack(pady=20)

    def validate_name(name):
        if not name:
            error_label.configure(text="Naam mag niet leeg zijn")
            return 1
        if len(name) > 10:
            error_label.configure(text="Naam mag niet langer zijn dan 10 karakters")
            return 1
        if not re.match("^[a-zA-Z0-9]*$", name):    
            error_label.configure(text="Naam mag alleen letters en cijfers bevatten")
            return 1
        error_label.configure(text="")
        return

    def next():
        global naam
        naam = name_entry.get()
        if validate_name(naam)==1:
            return  # Stop als de naam ongeldig is
        elif not quizepad:
            error_label.configure(text="Selecteer een categorie")
            return
        else:
            Quiz_setup.withdraw()
            start_quiz()
    # Timer toggle button
    timer_toggle_button = ui.CTkButton(setup_frame, text="Timer isUit", width=button_width, height=button_height, font=button_font, command=lambda:toggle_timer(timer_toggle_button))
    timer_toggle_button.pack(pady=20)         
    # Next 
    next_button = ui.CTkButton(setup_frame, text="Next", width=button_width, height=button_height, font=button_font, command=next)
    next_button.pack(pady=20)

    # Terug-knop om het venster te sluiten en het hoofdvenster weer te tonen
    back_button = ui.CTkButton(setup_frame, text="Back", width=button_width, height=button_height, font=button_font, command=lambda: close_window(Quiz_setup))
    back_button.pack(pady=20)

# Open instellingen
def open_settings(home):
    # Verberg het hoofdvenster
    home.destroy()
    
    # Maak een nieuw venster voor instellingen
    settings_window = ui.CTkToplevel()
    settings_window.geometry(f"{windowX}x{windowY}")
    settings_window.title("Instellingen")

    # Maak een frame om de instellingen-widgets te houden en centreer ze verticaal
    settings_frame = ui.CTkFrame(settings_window)
    settings_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Volume
    volume_label = ui.CTkLabel(settings_frame, text="Volume", font=button_font)
    volume_label.pack(pady=10)
    volume_slider = ui.CTkSlider(settings_frame, from_=0, to=100, width=button_width, height=30, number_of_steps=100)
    volume_slider.set(volume)
    volume_slider.pack(pady=20)
    def change_volume(value):
        global volume
        volume = int(value)
    volume_slider.configure(command=change_volume)

    # Thema selectie
    choices = ["Licht", "Donker"]
    selected_choice = ui.StringVar(value=choices[memdark])
    def change_theme(choice):
        global memdark
        if choice == "Licht":
            ui.set_appearance_mode("light")
            memdark = 0
        else:
            ui.set_appearance_mode("dark")
            memdark = 1
    selection_box = ui.CTkOptionMenu(settings_frame, variable=selected_choice, values=choices, width=button_width, height=button_height, font=button_font, command=change_theme)
    selection_box.pack(pady=20)

    # Kleurthema selectie
    color_choices = ["Blauw", "Groen"]
    selected_color = ui.StringVar(value=color_choices[memcolor])
    def change_color_theme(color):
        global memcolor
        if color == "Blauw":
            ui.set_default_color_theme("blue")
            memcolor = 0
        elif color == "Groen":
            ui.set_default_color_theme("green")
            memcolor = 1
        settings_window.destroy()
        open_settings(home)
    color_selection_box = ui.CTkOptionMenu(settings_frame, variable=selected_color, values=color_choices, width=button_width, height=button_height, font=button_font, command=change_color_theme)
    color_selection_box.pack(pady=20)

    # Categorie verwijderen
    categories = load_categories() # Haal alle categorieen uit catogory.txt
    if categories:
        selected_remove_category = ui.StringVar(value=categories[0]) # Start met de eerste categorie als geselecteerd
        # Functie om categorieen te verwijderen
        def remove_category():
            category = selected_remove_category.get()
            if category in categories:
                categories.remove(category) # Verwijder de geselecteerde categorie
                save_categories(categories)  # Update het bestand catogory.txt
                # Verwijder het bestand van de categorie
                category_file = f"{category}"
                if os.path.exists(category_file): # Controleer of het bestand bestaat
                    os.remove(category_file) # Verwijder het bestand
                selected_remove_category.set(categories[0] if categories else "") # Update de waarde van selected_remove_category
                category_menu.configure(values=categories) # Update het dropdown-menu
                category_remove_label.configure(text=f"Categorie '{category}' verwijderd")  # Update de tekst van category_remove_label
        # Label met tekst
        category_label = ui.CTkLabel(settings_frame, text="Verwijder Categorie:", font=("Arial", 24))
        category_label.pack(pady=5)
        # Dropdown-menu met categorieen om de geselecteerde categorie te wijzigen
        category_menu = ui.CTkOptionMenu(settings_frame, variable=selected_remove_category, values=categories, width=button_width, height=button_height, font=button_font)
        category_menu.pack(pady=20)
        # Label met tekst om weer te geven welke categorie is verwijderd
        category_remove_label = ui.CTkLabel(settings_frame, text="", font=("Arial", 16), text_color="red")
        category_remove_label.pack(pady=5)
        # Verwijder-knop om de geselecteerde categorie te verwijderen
        category_button = ui.CTkButton(settings_frame, text="Verwijder", width=button_width, height=button_height, font=button_font, command=remove_category)
        category_button.pack(pady=20)

    # Terug-knop om terug te keren naar het hoofdscherm
    back_button = ui.CTkButton(settings_frame, text="Back", width=button_width, height=button_height, font=button_font, command=lambda: close_window(settings_window))
    back_button.pack(pady=20)

def open_score_board(home):
    # Verberg het hoofdvenster
    home.destroy()
    
    # Maak een nieuw venster voor het Score Bord
    score_board_window = ui.CTkToplevel()
    score_board_window.geometry(f"{windowX}x{windowY}")
    score_board_window.title("Score Bord")

    # Maak een frame om de widgets te houden
    score_board_frame = ui.CTkFrame(score_board_window)
    score_board_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Controleer of er spelers in de dataset zijn
    if not speler_scores:
        # Toon bericht als er geen spelers zijn
        no_players_label = ui.CTkLabel(score_board_frame, text="Er zijn nog geen spelers aangemaakt", font=("Arial", 24))
        no_players_label.pack(pady=20)

        # Back-knop om terug te keren naar het hoofdscherm
        back_button = ui.CTkButton(score_board_frame, text="Back", width=button_width, height=button_height, font=button_font, command=lambda: close_window(score_board_window))
        back_button.pack(pady=20)
    else:
        # Toon Dropdown-menu om speler te selecteren
        players = list(speler_scores.keys())  # Haal alle speler namen uit de dataset
        selected_player = ui.StringVar(value=players[0])  # Start met de eerste speler als geselecteerd

        # Label om de geselecteerde speler en scores te tonen
        player_scores_label = ui.CTkLabel(score_board_frame, text="", font=("Arial", 20))
        player_scores_label.pack(pady=20)

        # Functie om scores van de geselecteerde speler te tonen
        def show_selected_player_scores(speler):
            if speler in speler_scores:
                scores_text = f"Scores voor speler {speler}:\n"
                scores_text += "\n".join([f"Categorie: {cat} - Hi-score: {score}" for cat, score in speler_scores[speler].items()])

            # Update het label met scores van de geselecteerde speler
            player_scores_label.configure(text=scores_text)

        # Dropdown-menu met spelers om de geselecteerde speler te wijzigen
        player_selection_box = ui.CTkOptionMenu(score_board_frame, variable=selected_player, values=players, width=button_width, height=button_height, font=button_font, command=show_selected_player_scores)
        player_selection_box.pack(pady=20)

        # Toon scores van de standaard eerst geselecteerde speler
        show_selected_player_scores(selected_player.get())

        # Terug-knop om terug te keren naar het hoofdscherm
        back_button = ui.CTkButton(score_board_frame, text="Back", width=button_width, height=button_height, font=button_font, command=lambda: close_window(score_board_window))
        back_button.pack(pady=20)

# Zorg ervoor dat save_scores wordt aangeroepen bij afsluiten
atexit.register(save_scores)

def close_window(window):
    window.destroy()
    home_start()

def exit_app():
    welcome.quit()

def home_start():
    # Verberg het welkomstvenster als het bestaat
    welcome.withdraw()
    # Initialiseer het hoofdvenster
    home = ui.CTkToplevel()
    home.geometry(f"{windowX}x{windowY}")
    home.title("main")

    # Maak een titel label
    title_label = ui.CTkLabel(home, text="Quiz", font=("Arial", 60))
    title_label.pack(pady=80)

    # Maak een frame om de knoppen te houden
    button_frame = ui.CTkFrame(home)
    button_frame.pack(pady=0)

    # Start Quiz knop
    start_quiz_button = ui.CTkButton(button_frame, text="Start Quiz", width=button_width, height=button_height, font=button_font)
    start_quiz_button.grid(row=0, column=0, padx=30, pady=18)
    start_quiz_button.configure(command=lambda: Open_Quiz_setup(home))

    # Instellingen knop
    settings_button = ui.CTkButton(button_frame, text="Instellingen", width=button_width, height=button_height, font=button_font)
    settings_button.grid(row=1, column=0, padx=30, pady=18)
    settings_button.configure(command=lambda: open_settings(home))

    # AI knop
    ai_button = ui.CTkButton(button_frame, text="AI", width=button_width, height=button_height, font=button_font)
    ai_button.grid(row=2, column=0, padx=30, pady=18)
    ai_button.configure(command=lambda: open_ai_window(home))

    # Score Bord knop
    score_board_button = ui.CTkButton(button_frame, text="Score Bord", width=button_width, height=button_height, font=button_font)
    score_board_button.grid(row=3, column=0, padx=30, pady=18)
    score_board_button.configure(command=lambda: open_score_board(home))

    # Exit knop
    exit_button = ui.CTkButton(button_frame, text="Exit", width=button_width, height=button_height, font=button_font)
    exit_button.grid(row=4, column=0, padx=30, pady=18)
    exit_button.configure(command=exit_app)

# Initialiseer het welkomstvenster
welcome = ui.CTk()
welcome.geometry(f"{windowX}x{windowY}")
welcome.title("WELCOME")
# Maak een welkomstlabel
welcome_label = ui.CTkLabel(welcome, text="Welkom bij de Quiz", font=("Arial", 60))
welcome_label.pack(pady=80)

# Maak een knop om naar het hoofdscherm te gaan
home_button = ui.CTkButton(welcome, text="Ga naar Home", width=button_width, height=button_height, font=button_font, command=home_start)
home_button.pack(pady=20)

# Start de applicatie
welcome.mainloop()
