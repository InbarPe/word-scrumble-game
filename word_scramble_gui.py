import tkinter as tk
from tkinter import ttk, messagebox
import time

from word_scramble_logic import WordGameLogic


class WordScrambleGUI:
    def __init__(self, root: tk.Tk, word_file: str = "word_list.txt"):
        self.root = root
        root.title("Word Scramble - Food Edition")
        root.geometry("700x460")
        root.resizable(False, False)

        # Colors / style
        self.bg_color = "#323327"
        self.card_color = "#323327"
        self.primary = "#c183d3"
        self.good = "#51c486"
        self.bad = "#e06666"
        self.neutral = "#8E8989"

        root.configure(bg=self.bg_color)

        # Logic
        try:
            self.logic = WordGameLogic(word_file)
        except Exception as e:
            messagebox.showerror("Error loading words", f"Couldn't load words:\n{e}")
            root.destroy()
            return

        # GUI game state
        self.chosen_word = None
        self.scrambled_word = None
        self.attempts = 0
        self.timer_seconds = 0
        self.timer_id = None
        self.round_active = False
        self.round_start_time = None

        # Build UI
        self.build_start_screen()
        self.build_game_screen()
        self.show_start_screen()

    # -------------------------
    # Start screen
    # -------------------------
    def build_start_screen(self):
        self.start_frame = tk.Frame(self.root, bg=self.bg_color)
        self.start_frame.place(relwidth=1, relheight=1)

        title = tk.Label(
            self.start_frame,
            text="Word Scramble\nFood Edition",
            font=("Segoe UI", 28, "bold"),
            bg=self.bg_color,
            fg=self.primary,
            justify="center",
        )
        title.pack(pady=(30, 6))

        subtitle = tk.Label(
            self.start_frame,
            text="Guess the scrambled food word!",
            font=("Segoe UI", 12),
            bg=self.bg_color,
            fg=self.neutral,
        )
        subtitle.pack(pady=(0, 12))

        # Difficulty selector
        difficulty_frame = tk.Frame(self.start_frame, bg=self.bg_color)
        difficulty_frame.pack(pady=6)
        tk.Label(
            difficulty_frame,
            text="Difficulty:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.neutral,
        ).grid(row=0, column=0, padx=(0, 8))
        self.difficulty_var = tk.StringVar(value="Easy")
        difficulty_menu = ttk.Combobox(
            difficulty_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=10,
        )
        difficulty_menu.grid(row=0, column=1)

        # Timer hint
        self.timer_hint = tk.Label(
            self.start_frame, text="", font=("Segoe UI", 10), bg=self.bg_color, fg=self.neutral
        )
        self.timer_hint.pack(pady=(6, 8))
        self.update_timer_hint()
        difficulty_menu.bind("<<ComboboxSelected>>", lambda e: self.update_timer_hint())

        start_btn = tk.Button(
            self.start_frame,
            text="Start Game",
            font=("Segoe UI", 14, "bold"),
            bg=self.primary,
            fg="black",
            command=self.start_game,
        )
        start_btn.pack(pady=(8, 8), ipadx=12, ipady=6)

        instr = (
            "Type your guess and press Guess (or Enter).\nUse Solve to reveal the word.\n"
            "Next Word loads a new word.\nTimer will expire each round."
        )
        tk.Label(
            self.start_frame,
            text=instr,
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.neutral,
            justify="center",
        ).pack(pady=(10, 0))

    def update_timer_hint(self):
        diff = self.difficulty_var.get()
        secs = self.difficulty_to_seconds(diff)
        self.timer_hint.config(text=f"Selected difficulty: {diff}\nRound time: {secs} seconds")

    def show_start_screen(self):
        self.start_frame.lift()

    def start_game(self):
        # initialize logic for run (keeps scoreboard by default)
        self.logic.start_run(reset_scoreboard=False)
        self.show_game_screen()
        self.new_round()

    # -------------------------
    # Game screen
    # -------------------------
    def build_game_screen(self):
        self.game_frame = tk.Frame(self.root, bg=self.bg_color)
        self.game_frame.place(relwidth=1, relheight=1)

        top_bar = tk.Frame(self.game_frame, bg=self.bg_color)
        top_bar.pack(fill="x", pady=(12, 0), padx=12)

        self.diff_display = tk.Label(top_bar, text="", font=("Segoe UI", 10), bg=self.bg_color, fg=self.neutral)
        self.diff_display.pack(side="left")

        self.timer_label = tk.Label(top_bar, text="", font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg=self.primary)
        self.timer_label.pack(side="right")

        card = tk.Frame(self.game_frame, bg=self.card_color, bd=0, relief="ridge")
        card.pack(padx=12, pady=12, fill="both", expand=False)

        self.scrambled_label = tk.Label(card, text="", font=("Segoe UI", 36, "bold"), bg=self.card_color, fg=self.primary, pady=20)
        self.scrambled_label.pack()

        info_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        info_frame.pack(pady=(6, 0), fill="x", padx=14)

        left_info = tk.Frame(info_frame, bg=self.bg_color)
        left_info.pack(side="left", anchor="w")

        self.attempts_label = tk.Label(left_info, text="Attempts: 0", font=("Segoe UI", 11), bg=self.bg_color, fg=self.neutral)
        self.attempts_label.pack(anchor="w")

        self.remaining_label = tk.Label(left_info, text="", font=("Segoe UI", 11), bg=self.bg_color, fg=self.neutral)
        self.remaining_label.pack(anchor="w", pady=(4, 0))

        self.result_label = tk.Label(self.game_frame, text="", font=("Segoe UI", 12), bg=self.bg_color, fg=self.neutral)
        self.result_label.pack(pady=(6, 8))

        entry_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        entry_frame.pack(pady=(6, 8))
        self.entry = tk.Entry(entry_frame, font=("Segoe UI", 16), justify="center", width=30)
        self.entry.grid(row=0, column=0, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.check_guess())

        btn_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        btn_frame.pack(pady=(6, 8))

        self.btn_guess = tk.Button(btn_frame, text="Guess", width=12, command=self.check_guess, bg=self.primary)
        self.btn_guess.grid(row=0, column=0, padx=6)

        self.btn_solve = tk.Button(btn_frame, text="Solve (Reveal)", width=12, command=self.solve_word, bg="#fed07a")
        self.btn_solve.grid(row=0, column=1, padx=6)

        self.btn_next = tk.Button(btn_frame, text="Next Word", width=12, command=self.new_round, bg="#5b835d")
        self.btn_next.grid(row=0, column=2, padx=6)

        back_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        back_frame.pack(fill="x", pady=(12, 0), padx=12)
        back_btn = tk.Button(back_frame, text="Back to Start", command=self.back_to_start, bg="#a87f7f")
        back_btn.pack(side="left")
        score_btn = tk.Button(back_frame, text="Scoreboard", command=self.show_scoreboard, bg="#497679")
        score_btn.pack(side="right")

    def show_game_screen(self):
        self.diff_display.config(text=f"Difficulty: {self.difficulty_var.get()}")
        self.game_frame.lift()

    # -------------------------
    # Game logic integration
    # -------------------------
    def difficulty_to_seconds(self, difficulty: str) -> int:
        return {"Easy": 75, "Medium": 50, "Hard": 30}.get(difficulty, 50)

    def update_remaining_label(self):
        rem = self.logic.remaining_counts()
        self.remaining_label.config(text=f"Words remaining — Easy: {rem['Easy']}  Medium: {rem['Medium']}  Hard: {rem['Hard']}")

    def new_round(self):
        # cancel any existing timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.attempts = 0
        self.update_attempts_label()
        self.result_label.config(text="", fg=self.neutral)
        self.entry.config(state="normal")
        self.btn_guess.config(state="normal")
        self.round_active = True

        difficulty = self.difficulty_var.get()
        try:
            chosen, scrambled, order = self.logic.next_word(difficulty)
        except RuntimeError as e:
            # No more words in this difficulty
            messagebox.showinfo(
                "Out of words",
                f"No more unused words left in difficulty: {difficulty}.\n"
                "Please choose another difficulty."
            )
            self.back_to_start()
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not pick next word: {e}")
            return

        self.chosen_word = chosen
        self.scrambled_word = scrambled

        self.scrambled_label.config(text=self.scrambled_word)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

        # update remaining counts
        self.update_remaining_label()

        # setup timer
        self.timer_seconds = self.difficulty_to_seconds(difficulty)
        self.update_timer_label()
        self.round_start_time = time.time()
        self.countdown()

    def update_attempts_label(self):
        self.attempts_label.config(text=f"Attempts: {self.attempts}")

    def check_guess(self):
        if not self.round_active:
            return

        guess = self.entry.get().upper().strip()
        if not guess:
            messagebox.showwarning("No Input", "Please enter a guess!")
            return

        self.attempts += 1
        self.update_attempts_label()

        if guess == self.chosen_word:
            time_used = int(time.time() - (self.round_start_time or time.time()))
            self.result_label.config(text=f"Correct! You solved it in {self.attempts} attempts.", fg=self.good)
            # update logic scoreboard
            self.logic.record_win(self.attempts, time_used)
            self.round_won()
        else:
            self.result_label.config(text="Wrong…", fg=self.bad)

        # clear entry after guess
        self.entry.delete(0, tk.END)

    def solve_word(self):
        if not self.round_active:
            return
        self.result_label.config(text=f"The word was: {self.chosen_word}", fg=self.neutral)
        self.reveal_and_end("solved")

    def reveal_and_end(self, reason="time"):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.round_active = False
        self.entry.delete(0, tk.END)
        self.entry.config(state="disabled")
        self.btn_guess.config(state="disabled")

        if reason == "time":
            messagebox.showinfo("Time's up", f"Time's up! The word was: {self.chosen_word}")

        # update remaining label (in case pools were refilled)
        self.update_remaining_label()

    def round_won(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.round_active = False
        self.entry.config(state="disabled")
        self.btn_guess.config(state="disabled")
        self.update_remaining_label()

    # -------------------------
    # Scoreboard window
    # -------------------------
    def show_scoreboard(self):
        sb = tk.Toplevel(self.root)
        sb.title("Scoreboard / Highscores")
        sb.geometry("320x260")
        sb.resizable(False, False)
        sb.configure(bg=self.bg_color)

        tk.Label(sb, text="Scoreboard", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.primary).pack(pady=10)

        tk.Label(sb, text=f"Total rounds:  {self.logic.total_rounds}", font=("Segoe UI", 12), bg=self.bg_color, fg=self.neutral).pack(pady=2)
        tk.Label(sb, text=f"Rounds won:   {self.logic.rounds_won}", font=("Segoe UI", 12), bg=self.bg_color, fg=self.neutral).pack(pady=2)

        ba = "—" if self.logic.best_attempts is None else f"{self.logic.best_attempts} attempts"
        tk.Label(sb, text=f"Best attempts: {ba}", font=("Segoe UI", 12), bg=self.bg_color, fg=self.neutral).pack(pady=2)

        bt = "—" if self.logic.best_time is None else f"{self.logic.best_time} seconds"
        tk.Label(sb, text=f"Best time:     {bt}", font=("Segoe UI", 12), bg=self.bg_color, fg=self.neutral).pack(pady=2)

        tk.Button(sb, text="Close", command=sb.destroy, bg="#736969").pack(pady=12)

    # -------------------------
    # Timer
    # -------------------------
    def update_timer_label(self):
        mins, secs = divmod(self.timer_seconds, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

    def countdown(self):
        self.update_timer_label()
        if self.timer_seconds <= 0:
            self.result_label.config(text=f"Time's up! The word was: {self.chosen_word}", fg=self.bad)
            self.reveal_and_end("time")
            return
        self.timer_seconds -= 1
        self.timer_id = self.root.after(1000, self.countdown)

    # -------------------------
    # Navigation
    # -------------------------
    def back_to_start(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.show_start_screen()


def main():
    root = tk.Tk()
    app = WordScrambleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
