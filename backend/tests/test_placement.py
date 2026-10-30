from sqlalchemy import select

from app.models import Lemma, PlacementAnswer, User
from app.nlp.knowledge import estimate_threshold
from test_report import auth_headers, seed_episode


def seed_lemmas(client):
    with client.testing_session() as db:
        for i in range(60):
            zipf = 2.0 + (i % 10) * 0.25
            db.add(Lemma(text=f"word{i}", pos="NOUN", zipf=zipf, level="B2"))
        db.commit()


def test_placement_flow(client):
    headers = auth_headers(client)
    seed_lemmas(client)

    response = client.get("/placement/words?n=20", headers=headers)
    assert response.status_code == 200
    words = response.json()
    assert len(words) == 20

    with client.testing_session() as db:
        zipf_by_id = {lemma.id: lemma.zipf for lemma in db.scalars(select(Lemma))}
    answers = [
        {"lemma_id": word["lemma_id"], "known": zipf_by_id[word["lemma_id"]] >= 3.25}
        for word in words
    ]

    result = client.post("/placement/submit", json={"answers": answers}, headers=headers)
    assert result.status_code == 200
    data = result.json()
    assert 2.7 < data["vocab_threshold"] < 3.6
    assert data["answers_used"] == 20

    known = client.get("/words/mine?status=known", headers=headers).json()
    assert len(known) == data["known_count"]


def test_placement_requires_auth(client):
    assert client.get("/placement/words").status_code == 401


def test_report_uses_vocab_threshold(client):
    headers = auth_headers(client)
    episode_id, _ = seed_episode(client)
    with client.testing_session() as db:
        user = db.scalar(select(User))
        user.vocab_threshold = 3.0
        db.commit()

    data = client.get(f"/episodes/{episode_id}/report", headers=headers).json()
    assert data["unknown_occurrences"] == 10.0
    assert data["coverage"] == 0.9
    assert data["vocab_threshold"] == 3.0

def test_placement_offers_new_words(client):
    headers = auth_headers(client)
    seed_lemmas(client)
    first = client.get("/placement/words?n=20", headers=headers).json()
    answers = [{"lemma_id": word["lemma_id"], "known": True} for word in first]
    client.post("/placement/submit", json={"answers": answers}, headers=headers)
    second = client.get("/placement/words?n=20", headers=headers).json()
    assert not {w["lemma_id"] for w in first} & {w["lemma_id"] for w in second}

def test_placement_threshold_uses_all_answers(client):
    headers = auth_headers(client)
    seed_lemmas(client)
    with client.testing_session() as db:
        zipf_by_id = {lemma.id: lemma.zipf for lemma in db.scalars(select(Lemma))}

    result = None
    for _ in range(2):
        words = client.get("/placement/words?n=20", headers=headers).json()
        answers = [
            {"lemma_id": w["lemma_id"], "known": zipf_by_id[w["lemma_id"]] >= 3.25}
            for w in words
        ]
        result = client.post(
            "/placement/submit", json={"answers": answers}, headers=headers
        ).json()

    with client.testing_session() as db:
        rows = db.execute(select(PlacementAnswer.zipf, PlacementAnswer.known)).all()
    assert len(rows) == 40
    assert result["vocab_threshold"] == estimate_threshold([(z, k) for z, k in rows])