import os
import random
from typing import Dict, List, Optional, Tuple


def load_words_from_file(file_name: str) -> List[str]:
    """
    Load words from a file located next to this module.
    Returns list of uppercase words (stripped).
    """
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]


def scramble_order(length: int) -> List[int]:
    order = list(range(length))
    random.shuffle(order)
    return order


def scramble_word(chosen_word: str, order: List[int]) -> str:
    return "".join(chosen_word[i] for i in order)


def make_scrambled(chosen_word: str) -> Tuple[str, List[int]]:
    if len(chosen_word) <= 1:
        return chosen_word, list(range(len(chosen_word)))
    for _ in range(20):
        order = scramble_order(len(chosen_word))
        scrambled = scramble_word(chosen_word, order)
        if scrambled != chosen_word:
            return scrambled, order
    order = scramble_order(len(chosen_word))
    return scramble_word(chosen_word, order), order


class WordGameLogic:
    """
    Core game logic separated from UI.
    Responsibilities:
    - load and filter words
    - maintain unused word pools per difficulty
    - ensure words aren't reused within a run (used_words set)
    - provide next_word() which returns (chosen_word, scrambled, order)
    - track scoreboard (total rounds, rounds won, best attempts, best_time)
    """

    DIFFICULTIES = ("Easy", "Medium", "Hard")

    def __init__(self, word_file: str = "word_list.txt"):
        self.word_file = word_file
        self.words_all: List[str] = load_words_from_file(word_file)

        # Pools and tracking for a run (initialize in start_run())
        self.unused_by_difficulty: Optional[Dict[str, List[str]]] = None
        self.used_words: set = set()

        # Scoreboard
        self.total_rounds = 0
        self.rounds_won = 0
        self.best_time: Optional[int] = None  # seconds
        self.best_attempts: Optional[int] = None

    # -------------------------
    # Difficulty and filtering
    # -------------------------
    def filter_words_by_difficulty(self, difficulty: str) -> List[str]:
        if difficulty == "Easy":
            return [w for w in self.words_all if 2 <= len(w) <= 5]
        elif difficulty == "Medium":
            return [w for w in self.words_all if 5 < len(w) <= 8]
        else:  # Hard
            return [w for w in self.words_all if len(w) > 8]

    # -------------------------
    # Run management
    # -------------------------
    def start_run(self, reset_scoreboard: bool = False) -> None:
        """
        Prepare pools for a run. Call before beginning a run.
        If reset_scoreboard True, scoreboard stats are cleared.
        """
        self.unused_by_difficulty = {
            "Easy": [],
            "Medium": [],
            "Hard": []
}

        for w in self.words_all:
            L = len(w)
            if 2 <= L <= 5:
                self.unused_by_difficulty["Easy"].append(w)
            elif 6 <= L <= 8:
                self.unused_by_difficulty["Medium"].append(w)
            else:
                self.unused_by_difficulty["Hard"].append(w)

        # shuffle each pool
        for lst in self.unused_by_difficulty.values():
            random.shuffle(lst)

        self.used_words = set()

        if reset_scoreboard:
            self.total_rounds = 0
            self.rounds_won = 0
            self.best_time = None
            self.best_attempts = None

    def remaining_counts(self) -> Dict[str, int]:
        """
        Returns how many words remain in each difficulty pool (approx).
        If pools not initialized, returns counts based on filtering.
        """
        if self.unused_by_difficulty is None:
            return {
                d: len(self.filter_words_by_difficulty(d)) for d in self.DIFFICULTIES
            }
        else:
            return {d: len(self.unused_by_difficulty.get(d, [])) for d in self.DIFFICULTIES}

    # -------------------------
    # Word selection (no repeats in run)
    # -------------------------
    def next_word(self, difficulty: str = "Medium") -> Tuple[str, str, List[int]]:
        """
        Returns (chosen_word, scrambled_word, scramble_order).
        Ensures chosen_word was not already used in this run (unless we've exhausted all).
        Call start_run() before first next_word().
        """
        if difficulty not in self.DIFFICULTIES:
            raise ValueError("Unknown difficulty")

        if self.unused_by_difficulty is None:
            self.start_run(reset_scoreboard=False)

        pool = self.unused_by_difficulty.get(difficulty, [])

        chosen = None
        while pool:
            candidate = pool.pop()
            if candidate not in self.used_words:
                chosen = candidate
                break

        if chosen is None:
            # Refill only from the SAME difficulty and EXCLUDE used words
            new_pool = [
                w for w in self.filter_words_by_difficulty(difficulty)
                if w not in self.used_words
            ]

            if not new_pool:
                raise RuntimeError(
                    f"No more unused words available in difficulty: {difficulty}"
                )

            random.shuffle(new_pool)
            self.unused_by_difficulty[difficulty] = new_pool

            chosen = self.unused_by_difficulty[difficulty].pop()

        # Mark used immediately
        self.used_words.add(chosen)
        self.total_rounds += 1

        scrambled, order = make_scrambled(chosen)
        return chosen, scrambled, order

    # -------------------------
    # Scoreboard recording
    # -------------------------
    def record_win(self, attempts: int, time_used_seconds: int) -> None:
        self.rounds_won += 1
        if self.best_attempts is None or attempts < self.best_attempts:
            self.best_attempts = attempts
        if self.best_time is None or time_used_seconds < self.best_time:
            self.best_time = time_used_seconds

    # Useful debug repr
    def __repr__(self):
        rem = self.remaining_counts()
        return f"<WordGameLogic total_words={len(self.words_all)} remaining={rem} used={len(self.used_words)}>"
