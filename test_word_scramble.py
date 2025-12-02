import pytest
from word_scramble_logic import WordGameLogic, make_scrambled

# We override the words file with a small controlled list.
TEST_WORDS = ["MILK", "KIWI", "BANANA", "ORANGE", "STRAWBERRY"]


@pytest.fixture
def logic(monkeypatch, tmp_path):
    """
    Provide a fully initialized WordGameLogic instance
    with a controlled word list stored in a temp file.
    """
    word_file = tmp_path / "word_list.txt"
    word_file.write_text("\n".join(TEST_WORDS))

    wl = WordGameLogic(word_file=str(word_file))
    wl.start_run(reset_scoreboard=True)
    return wl


def test_filter_words_by_difficulty(logic):
    # Easy: 2–5 letters
    assert set(logic.filter_words_by_difficulty("Easy")) == {"MILK", "KIWI"}

    # Medium: 6–8 letters
    assert set(logic.filter_words_by_difficulty("Medium")) == {"BANANA", "ORANGE"}

    # Hard: > 8 letters
    assert set(logic.filter_words_by_difficulty("Hard")) == {"STRAWBERRY"}


def test_start_run_initializes_pools(logic):
    rem = logic.remaining_counts()
    assert rem["Easy"] == 2
    assert rem["Medium"] == 2
    assert rem["Hard"] == 1

    assert logic.used_words == set()


def test_next_word_no_repeats(logic):
    logic.start_run()

    chosen1, _, _ = logic.next_word("Easy")
    chosen2, _, _ = logic.next_word("Easy")

    assert chosen1 != chosen2  # Easy has exactly 2 unique words

    # Now Easy is empty: next_word should fail cleanly in your implementation
    with pytest.raises(RuntimeError):
        logic.next_word("Easy")


def test_scrambled_word_is_scrambled(logic):
    original = "BANANA"
    scrambled, order = make_scrambled(original)

    # Same letters
    assert sorted(scrambled) == sorted(original)

    # Different order
    assert scrambled != original


def test_record_win(logic):
    logic.record_win(attempts=5, time_used_seconds=30)

    assert logic.rounds_won == 1
    assert logic.best_attempts == 5
    assert logic.best_time == 30

    # New win is better → should update
    logic.record_win(attempts=3, time_used_seconds=20)

    assert logic.best_attempts == 3
    assert logic.best_time == 20

    # Worse win should NOT replace best
    logic.record_win(attempts=10, time_used_seconds=120)

    assert logic.best_attempts == 3
    assert logic.best_time == 20


def test_repr_does_not_crash(logic):
    s = repr(logic)
    assert isinstance(s, str)
    assert "remaining" in s
