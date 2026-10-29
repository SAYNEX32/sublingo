import pytest
from sqlalchemy import select

from app.models import UserWord
from test_report import auth_headers, seed_episode


def coverage(client, headers, episode_id):
    url = f"/episodes/{episode_id}/report"
    return client.get(url, headers=headers).json()["coverage"]


def test_learning_word_never_lowers_coverage(client):
    headers = auth_headers(client)
    episode_id, lemma_ids = seed_episode(client)
    before = coverage(client, headers, episode_id)

    client.put(
        "/words/mark",
        json={"lemma_ids": [lemma_ids[0]], "status": "learning"},
        headers=headers,
    )
    assert coverage(client, headers, episode_id) >= before

    with client.testing_session() as db:
        word = db.scalar(select(UserWord))
        word.interval_days = 15
        db.commit()
    assert coverage(client, headers, episode_id) == pytest.approx(0.8714, abs=0.001)