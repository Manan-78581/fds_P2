from games.webhooks import sign_payload


def test_sign_payload_is_stable():
    payload_a = {"b": 2, "a": 1}
    payload_b = {"a": 1, "b": 2}

    assert sign_payload("secret", payload_a) == sign_payload("secret", payload_b)
