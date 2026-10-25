from app.models import Episode, EpisodeLemma, Lemma, Title

CREDS = {"email": "user@gmail.com", "password": "password123"}


def auth_headers(client):
    client.post("/auth/register", json=CREDS)
    response = client.post(
        "/auth/login",
        data={"username": CREDS["email"], "password": CREDS["password"]},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def seed_episode(client):
    with client.testing_session() as db:
        title = Title(name="Test Show")
        db.add(title)
        db.flush()
        episode = Episode(
            title_id=title.id, season=1, number=1, subtitle_lines=10, total_words=100
        )
        db.add(episode)
        db.flush()
        lemma_ids = []
        for text, count in [("alpha", 10), ("beta", 6), ("gamma", 4)]:
            lemma = Lemma(text=text, pos="NOUN", zipf=3.0, level="C1")
            db.add(lemma)
            db.flush()
            db.add(
                EpisodeLemma(
                    episode_id=episode.id, lemma_id=lemma.id, count=count, example=""
                )
            )
            lemma_ids.append(lemma.id)
        db.commit()
        return episode.id, lemma_ids


def test_report_without_marks(client):
    headers = auth_headers(client)
    episode_id, _ = seed_episode(client)
    data = client.get(f"/episodes/{episode_id}/report", headers=headers).json()
    assert data["total_words"] == 100
    assert data["unknown_occurrences"] == 20
    assert data["coverage"] == 0.8
    assert data["words_to_target"] == 2
    assert data["to_learn"][0]["lemma"] == "alpha"


def test_mark_known_changes_report(client):
    headers = auth_headers(client)
    episode_id, lemma_ids = seed_episode(client)
    response = client.put(
        "/words/mark",
        json={"lemma_ids": [lemma_ids[0]], "status": "known"},
        headers=headers,
    )
    assert response.json() == {"updated": 1}

    data = client.get(f"/episodes/{episode_id}/report", headers=headers).json()
    assert data["unknown_occurrences"] == 10
    assert data["coverage"] == 0.9
    assert data["words_to_target"] == 1
    assert data["to_learn"][0]["lemma"] == "beta"


def test_mark_unknown_removes_word(client):
    headers = auth_headers(client)
    _, lemma_ids = seed_episode(client)
    for status in ("known", "unknown"):
        client.put(
            "/words/mark",
            json={"lemma_ids": [lemma_ids[0]], "status": status},
            headers=headers,
        )
    assert client.get("/words/mine", headers=headers).json() == []


def test_report_requires_auth(client):
    episode_id, _ = seed_episode(client)
    assert client.get(f"/episodes/{episode_id}/report").status_code == 401