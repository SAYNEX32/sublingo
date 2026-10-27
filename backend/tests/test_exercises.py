from app.models import Episode, EpisodeLemma, Lemma, Title
from test_report import auth_headers

TARGETS = [
    ("calculation", 3.76, 5, "Show me how you did your calculations."),
    ("neutron", 3.44, 4, "Bombarded it with neutrons."),
    ("isotope", 3.15, 3, "There was an export of isotopes to Norway last year."),
]
POOL = [("gadget", 3.6), ("bridge", 3.7), ("engine", 3.8), ("garden", 3.5)]


def seed(client):
    with client.testing_session() as db:
        title = Title(name="Test Show")
        db.add(title)
        db.flush()
        episode = Episode(
            title_id=title.id, season=1, number=1, subtitle_lines=10, total_words=100
        )
        db.add(episode)
        db.flush()
        for text, zipf, count, example in TARGETS:
            lemma = Lemma(text=text, pos="NOUN", zipf=zipf, level="C1")
            db.add(lemma)
            db.flush()
            db.add(
                EpisodeLemma(
                    episode_id=episode.id,
                    lemma_id=lemma.id,
                    count=count,
                    example=example,
                )
            )
        for text, zipf in POOL:
            db.add(Lemma(text=text, pos="NOUN", zipf=zipf, level="B1"))
        db.commit()
        return episode.id


def option_id(exercise, text):
    return next(o["lemma_id"] for o in exercise["options"] if o["text"] == text)


def test_exercise_flow(client):
    headers = auth_headers(client)
    episode_id = seed(client)
    url = f"/exercises/next?episode_id={episode_id}"

    first = client.get(url, headers=headers).json()
    assert "_____" in first["sentence"]
    assert len(first["options"]) == 4
    assert first["is_new"] is True

    result = client.post(
        f"/exercises/{first['id']}/answer",
        json={"lemma_id": option_id(first, "calculation")},
        headers=headers,
    ).json()
    assert result["correct"] is True
    assert result["answer_form"] == "calculations"
    assert result["interval_days"] == 1
    assert result["status"] == "learning"

    second = client.get(url, headers=headers).json()
    assert second["id"] != first["id"]
    assert any(option["text"] == "neutron" for option in second["options"])

    wrong_id = next(o["lemma_id"] for o in second["options"] if o["text"] != "neutron")
    result = client.post(
        f"/exercises/{second['id']}/answer",
        json={"lemma_id": wrong_id},
        headers=headers,
    ).json()
    assert result["correct"] is False
    assert result["correct_lemma"] == "neutron"
    assert result["interval_days"] == 0

    again = client.post(
        f"/exercises/{second['id']}/answer",
        json={"lemma_id": wrong_id},
        headers=headers,
    )
    assert again.status_code == 409


def test_exercises_require_auth(client):
    assert client.get("/exercises/next?episode_id=1").status_code == 401

def test_unanswered_exercise_is_reused(client):
    headers = auth_headers(client)
    episode_id = seed(client)
    url = f"/exercises/next?episode_id={episode_id}"
    first = client.get(url, headers=headers).json()
    again = client.get(url, headers=headers).json()
    assert again["id"] == first["id"]
    assert again["is_new"] is True