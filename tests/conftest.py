import pytest

from model_eval_harness.sources.base import EvalExample


@pytest.fixture
def sample_examples() -> list[EvalExample]:
    return [
        EvalExample(input="What is 2+2?", expected="4", metadata={"id": "1"}),
        EvalExample(input="What is the capital of France?", expected="Paris", metadata={"id": "2"}),
        EvalExample(input="Write a haiku about spring", expected="Cherry blossoms bloom"),
    ]
