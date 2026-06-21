def test_classify_requires_email_content(client):
    response = client.post("/api/classify", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing email_content"


def test_classify_returns_classification_and_reply(mocker, client):
    mocker.patch("services.gemini.classify_email", return_value="Produtivo")
    mocker.patch(
        "services.gemini.generate_response",
        return_value={
            "classification": "Produtivo",
            "suggested_reply": "Obrigado pelo contato.",
        },
    )

    response = client.post(
        "/api/classify",
        json={
            "email_content": "Preciso da proposta até sexta-feira.",
            "subject": "Proposta comercial",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["classification"] == "Produtivo"
    assert payload["suggested_reply"] == "Obrigado pelo contato."
