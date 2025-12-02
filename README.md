# Word Scramble — Food Edition 🥑🍓🥕

A word scramble game built in Python with Tkinter.

Players pick a difficulty, race against a timer, and try to guess scrambled food-related words.

The game keeps track of high scores, prevents repeats, and includes a clean separation between core logic and GUI code.

The game utilizes file handling with the word_list.txt file, reading it into the game.

## 📜 Game Rules

1. Choose a difficulty.
2. Press Start Game.
3. A scrambled word appears.
4. Type your guess and press Guess or Enter.
5. You have a limited time based on difficulty:
    * Easy → 75 seconds
    * Medium → 50 seconds
    * Hard → 30 seconds
6. If you give up, press Solve.
7. Press Next Word to continue.
8. Try to beat your:
    * Best time
    * Fewest attempts

## 🎮 Gameplay

* Words are randomly scrambled using a shuffle algorithm.
* Three difficulty levels:
   - Easy: 2–5 letters
   - Medium: 6–8 letters
   - Hard: 9+ letters
* A timer for each round (depends on difficulty).
* Attempts counter that resets each round.
* Solve button to reveal the word if stuck.
* Press Enter to submit your guess.
* Next Word button to skip to another round.
* Back to Start button to leave the game at any time.

## 💾 No Repeated Words

* Across a single run:
* No word is ever repeated.
* Even if difficulty is changed mid-run, words do not overlap.
* Pools automatically refill only when absolutely necessary, excluding used words.

## 📊 Scoreboard / Highscores

Tracks:
* Total rounds played.
* Number of wins.
* Best time.
* Fewest attempts needed.
* Displayed in a clean, separate window.

## 🧪 Tests

A separate tests file verifies:
* Word loading
* Difficulty grouping and filtering
* start_run() initialization
* “No repeats” logic
* Scrambling algorithm
* Record win

To run the test:
``` bash
pytest -v
```

For this you may need to install *pytest*:
``` bash
pip install pytest
```

## 📁 File Structure

📦 word-scramble-game project has:
* word_scramble_gui.py     # All Tkinter UI code
* word_scramble_logic.py   # Core game logic
* test_word_scramble.py    # Tests for the logic module
* word_list.txt            # Source word list

! Ensure that all required files are present in the folder.

## ▶️ How to Run the Game

Make sure Python 3.8+ is installed.

Install Tkinter (usually pre-installed).

Run:
``` bash
python word_scramble_gui.py
```
