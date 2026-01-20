init python:
    import random
    
    class ShakeTransform(object):
        def __init__(self, period=0.05, strength=10):
            self.period = period
            self.strength = strength
            self.time = 0
            
        def __call__(self, trans, st, at):
            self.time += st
            if self.time >= self.period:
                self.time = 0
                trans.xoffset = random.randint(-self.strength, self.strength)
                trans.yoffset = random.randint(-self.strength, self.strength)
            else:
                trans.xoffset = 0
                trans.yoffset = 0
            return 0

    def show_dramatic_text(text_content, duration=2.0, text_size=50, shake_power=10):
        renpy.music.stop(fadeout=0.5)
        renpy.scene()
        renpy.show("black")
        renpy.with_statement(Dissolve(0.5))
        renpy.pause(0.5)

        screen_text = Text(
            text_content,
            color="#ff0000",
            size=text_size,
            xalign=0.5,
            yalign=0.5,
            outlines=[(2, "#000000", 0, 0)]
        )
        
        renpy.show_screen("shake_screen", text_obj=screen_text, shake_power=shake_power)
        renpy.pause(duration)
        renpy.hide_screen("shake_screen")
        renpy.with_statement(Dissolve(0.5))

screen shake_screen(text_obj, shake_power):
    add text_obj at transform:
        function ShakeTransform(strength=shake_power)
        xalign 0.5
        yalign 0.5

define v = Character("Голос")
define y = Character("Вы")

default unlocked_levels = 1
default completed_levels = 0
default levels_data = {}
default hints_used = 0
default max_hints = renpy.random.randint(1, 3)
default last_rest_level = 0
default current_level = 1

init python:
    def load_levels_from_file():
        levels = {}
        try:
            with renpy.file("levels.txt") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    parts = line.split("|")
                    if len(parts) >= 4:
                        level_num = int(parts[0])
                        difficulty = parts[1]
                        level_label = parts[2]
                        level_name = parts[3]
                        
                        required_level = int(parts[4]) if len(parts) > 4 else 1
                        has_hint = bool(int(parts[5])) if len(parts) > 5 else True
                        
                        levels[level_num] = {
                            "number": level_num,
                            "difficulty": difficulty,
                            "label": level_label,
                            "name": level_name,
                            "required": required_level,
                            "has_hint": has_hint,
                            "completed": False
                        }
        except:
            for i in range(1, 26):
                if i <= 9:
                    diff = "e"
                    name = f"Уровень {i} (Легкий)"
                elif i <= 19:
                    diff = "m"
                    name = f"Уровень {i} (Средний)"
                else:
                    diff = "h"
                    name = f"Уровень {i} (Сложный)"
                
                levels[i] = {
                    "number": i,
                    "difficulty": diff,
                    "label": f"level_{i}",
                    "name": name,
                    "required": 1,
                    "has_hint": True,
                    "completed": False
                }
        
        return levels
    
    def get_difficulty_color(difficulty):
        if difficulty == "e":
            return "#00FF00"
        elif difficulty == "m":
            return "#FFFF00"
        else:
            return "#FF0000"

init python:
    def update_level_progress(level_num):
        if level_num in levels_data:
            levels_data[level_num]["completed"] = True
        
        new_completed = 0
        for i in range(1, 26):
            if i in levels_data and levels_data[i]["completed"]:
                new_completed = i
        
        store.completed_levels = new_completed
        
        if store.unlocked_levels < store.completed_levels + 1 and store.unlocked_levels < 25:
            store.unlocked_levels = min(store.completed_levels + 1, 25)

label start:
    play music "menu.mp3"
    scene bg castle with dissolve
    v "Приветствую, путник."

label important_choice:
    menu:
        v "Вы готовы?"
        
        "Да.":
            stop music fadeout 1.0
            "Прекрасно.."
            scene black with dissolve
            play sound "fall.wav"
            pause 1.0
            jump new_page
            
        "Нет.":
            "Что ж.."
            window hide
            $ show_dramatic_text("На этом ваше путешествие окончено...", 3.0, 60, 50)
            scene black with dissolve
            "Game over."
            return

label new_page:
    "Кажется, приземление прошло не очень удачно.."
    y "Где это я..?"
    play sound "rolling_paper.wav"
    play audio "tutorial.wav"
    scene bg map with dissolve
    
    v "Добро пожаловать на карту."
    v "Ваше приключение начнётся прямо..."
    
    "Что дальше?"
    
    menu:
        "пропустить обучение":
            scene black with dissolve
            "Что ж, удачи =)"
            v "...сейчас!"
            scene bg dungeon with dissolve
            "Чёрная пелена постепенно отступает, и к вам медленно возвращается зрение.."
            jump explore
        "играю впервые":
            jump check_map

label explore:
    scene bg dungeon with dissolve
    
    python:
        if not levels_data:
            levels_data = load_levels_from_file()
    
    "Перед вами появляется магический свиток с картой подземелья..."
    
    menu:
        "Что делать?"
        
        "Посмотреть карту подземелья":
            call screen level_selection
            
        "Осмотреться вокруг":
            "Вы находитесь в стартовой комнате подземелья..."
            "Перед вами несколько дверей, ведущих в разные части лабиринта."
            jump explore
        
        "Отдохнуть" if completed_levels - last_rest_level >= 5 or (completed_levels == 0 and last_rest_level == 0):
            $ last_rest_level = completed_levels
            $ hints_used = 0
            $ max_hints = renpy.random.randint(1, 3)
            "Вы отдыхаете и восстанавливаете силы..."
            "Лимит подсказок обновлен: теперь доступно [max_hints] подсказок."
            jump explore
    
    return

label check_map:
    scene bg map with dissolve
    "Logica - игра, в которой вам придётся проявить немалую смекалку чтобы выбраться из подземелья."
    "Каждая комната - загадка.."
    "Для прохождения нужно разгадать их все."
    "Если решение не идёт совсем, то можете воспользоваться подсказкой."
    "Но будьте осторожны, использование подсказок вытягивает из вас силы.."
    "Никто не знает, какой раз станет последним.."
    scene black with dissolve
    menu:
        "Вы готовы продолжить?"

        "Нет (прочитать обучение вновь)":
            jump check_map

        "Да":
            scene black with dissolve
            "Что ж, удачи =)"
            v "...сейчас!"
            scene bg dungeon with dissolve
            "Чёрная пелена постепенно отступает, и к вам медленно возвращается зрение.."
            stop music
            jump explore
    return

screen level_selection():
    tag menu
    add "bg map"
    
    frame:
        xalign 0.5
        yalign 0.1
        xpadding 50
        ypadding 30
        
        vbox:
            spacing 10
            text "ВЫБОР УРОВНЯ" size 40 xalign 0.5
            
            hbox:
                spacing 50
                textbutton "Открыто: [unlocked_levels]/25" action None
                textbutton "Пройдено: [completed_levels]/25" action None
                textbutton "Подсказки: [hints_used]/[max_hints]" action None
            
            if completed_levels - last_rest_level >= 5:
                text "Можно отдохнуть!" color "#00FF00" xalign 0.5
            else:
                text "До отдыха: [5 - (completed_levels - last_rest_level)] ур." color "#FFFF00" xalign 0.5
            
            null height 20
            
            textbutton "Вернуться в лагерь" action Jump("explore") xalign 0.5
    
    grid 5 5:
        xalign 0.5
        yalign 0.8
        xspacing 20
        yspacing 20
        
        for i in range(1, 26):
            $ level_info = levels_data.get(i)
            if level_info:
                $ is_locked = (i > unlocked_levels)
                $ is_completed = level_info["completed"]
                
                if is_locked:
                    button:
                        xsize 100
                        ysize 100
                        background Solid("#666666", xsize=100, ysize=100)
                        hover_background Solid("#888888", xsize=100, ysize=100)
                        action NullAction()
                        
                        text "[i]" size 36 color "#333333" xalign 0.5 yalign 0.5
                        
                else:
                    button:
                        xsize 100
                        ysize 100
                        
                        if level_info['difficulty'] == "e":
                            background Solid("#00CC00", xsize=100, ysize=100)
                            hover_background Solid("#00FF00", xsize=100, ysize=100)
                        elif level_info['difficulty'] == "m":
                            background Solid("#FFAA00", xsize=100, ysize=100)
                            hover_background Solid("#FFCC00", xsize=100, ysize=100)
                        else:
                            background Solid("#CC0000", xsize=100, ysize=100)
                            hover_background Solid("#FF0000", xsize=100, ysize=100)
                        
                        action [SetVariable("current_level", i), Jump("level_generic")]
                        
                        text "[i]" size 36 color "#FFFFFF" outlines [(3, "#000000", 0, 0)] xalign 0.5 yalign 0.5
                        
                        if is_completed:
                            text "✓" size 48 color "#00FF00" outlines [(3, "#000000", 0, 0)] xalign 0.5 yalign 0.5
                        
            else:
                button:
                    xsize 100
                    ysize 100
                    background Solid("#444444", xsize=100, ysize=100)
                    text "?" size 36 color "#FFFFFF" xalign 0.5 yalign 0.5
                    action NullAction()

label game_over_hints:
    scene black with dissolve
    "Вы полагались на подсказки слишком часто..."
    "Ваши силы окончательно иссякли, и тьма поглотила вас."
    window hide
    $ show_dramatic_text("СМЕРТЬ ОТ ИСТОЩЕНИЯ", 3.0, 60, 20)
    "Game Over"
    return

label level_generic:
    $ level_num = current_level
    
    if level_num <= 9:
        $ diff_text = "Легкий"
        $ scene_img = "bg puzzle_room_easy"
    elif level_num <= 19:
        $ diff_text = "Средний"
        $ scene_img = "bg puzzle_room"
    else:
        $ diff_text = "Сложный"
        $ scene_img = "bg puzzle_room_hard"
    
    if not renpy.has_image(scene_img):
        $ scene_img = "bg puzzle_room"
    
    scene expression scene_img with dissolve
    
    "=== УРОВЕНЬ [level_num] ==="
    "Сложность: [diff_text]"
    "Использовано подсказок: [hints_used]"
    "Кто знает, сколько ещё вы протянете..."
    "Новая загадка"
    
    menu:
        "Ваши действия:"
        
        "Попытаться решить":
            "Вы сосредоточенно думаете над решением..."
            "И... у вас получается!"
            
            python:
                update_level_progress(level_num)
            
            "Головоломка решена!"
            
        "Использовать подсказку":
            if hints_used >= max_hints:
                "Вы использовали слишком много подсказок!"
                "Ваши силы иссякли..."
                jump game_over_hints
            else:
                $ hints_used += 1
                "Вы используете магическую подсказку..."
                "Часть ваших сил уходит, но решение становится яснее."
                jump level_generic
        
        "Вернуться к карте":
            "Вы возвращаетесь к карте подземелья."
    
    call screen level_selection
    return