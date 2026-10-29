from app.services.exercises import make_blank


def test_make_blank_plural_noun():
    blanked, form = make_blank("Show me how you did your calculations.", "calculation")
    assert blanked == "Show me how you did your _____."
    assert form == "calculations"


def test_make_blank_missing_word():
    assert make_blank("Nothing to see here at all.", "calculation") is None

def test_make_blank_hides_every_occurrence():
    result = make_blank("Scalp, scalp and more scalp, said the old doctor.", "scalp")
    assert result is not None
    assert "scalp" not in result[0].lower()


def test_make_blank_rejects_sentence_without_context():
    assert make_blank("Scalp, scalp...scalp.", "scalp") is None