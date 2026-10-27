from app.services.exercises import make_blank


def test_make_blank_plural_noun():
    blanked, form = make_blank("Show me how you did your calculations.", "calculation")
    assert blanked == "Show me how you did your _____."
    assert form == "calculations"


def test_make_blank_missing_word():
    assert make_blank("Nothing to see here at all.", "calculation") is None