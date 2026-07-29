import os

from model_eval_harness.models.openai import OpenAIModel


def test_openai_model_init_defaults() -> None:
    model = OpenAIModel(api_key="sk-test")
    assert model.model_id == "gpt-4o"
    assert model._temperature == 0.0
    assert model._max_tokens == 1024


def test_openai_model_custom_params() -> None:
    model = OpenAIModel(
        model_id="gpt-4o-mini",
        api_key="sk-test",
        base_url="https://custom.api/v1",
        temperature=0.5,
        max_tokens=512,
    )
    assert model.model_id == "gpt-4o-mini"
    assert model._temperature == 0.5
    assert model._max_tokens == 512


def test_openai_build_messages_string() -> None:
    model = OpenAIModel(api_key="sk-test")
    messages = model._build_messages("hello")
    assert messages == [{"role": "user", "content": "hello"}]


def test_openai_build_messages_list() -> None:
    model = OpenAIModel(api_key="sk-test")
    messages = model._build_messages(
        [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
    )
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_openai_model_env_var() -> None:
    os.environ["OPENAI_API_KEY"] = "sk-from-env"
    model = OpenAIModel()
    assert model.model_id == "gpt-4o"
    del os.environ["OPENAI_API_KEY"]
