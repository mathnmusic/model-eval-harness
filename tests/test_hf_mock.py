from unittest.mock import patch

from model_eval_harness.sources.huggingface import HuggingFaceSource


def test_hf_source_initialization() -> None:
    mock_dataset = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "Capital of France?", "answer": "Paris"},
    ]

    with patch("model_eval_harness.sources.huggingface.load_dataset", return_value=mock_dataset):
        source = HuggingFaceSource(
            dataset_name="mmlu",
            split="test",
            input_column="question",
            expected_column="answer",
        )

        assert len(source) == 2
        examples = list(source.load())
        assert examples[0].input == "What is 2+2?"
        assert examples[0].expected == "4"
        assert examples[0].metadata["source"] == "mmlu"


def test_hf_source_with_config() -> None:
    mock_dataset = [{"question": "Q1", "answer": "A1"}]

    with patch("model_eval_harness.sources.huggingface.load_dataset") as mock_load:
        mock_load.return_value = mock_dataset
        HuggingFaceSource(
            dataset_name="mmlu",
            split="dev",
            config="abstract_algebra",
        )
        mock_load.assert_called_once_with(path="mmlu", split="dev", name="abstract_algebra")


def test_hf_source_without_expected() -> None:
    mock_dataset = [{"prompt": "Explain AI"}]

    with patch("model_eval_harness.sources.huggingface.load_dataset", return_value=mock_dataset):
        source = HuggingFaceSource(
            dataset_name="custom",
            input_column="prompt",
            expected_column=None,
        )
        examples = list(source.load())
        assert examples[0].expected is None


def test_hf_source_with_missing_expected_column() -> None:
    mock_dataset = [{"prompt": "Hello"}]

    with patch("model_eval_harness.sources.huggingface.load_dataset", return_value=mock_dataset):
        source = HuggingFaceSource(
            dataset_name="custom",
            input_column="prompt",
            expected_column="nonexistent",
        )
        examples = list(source.load())
        assert examples[0].expected is None


def test_hf_source_limit() -> None:
    mock_dataset = [{"q": f"Q{i}"} for i in range(100)]

    with patch("model_eval_harness.sources.huggingface.load_dataset", return_value=mock_dataset):
        source = HuggingFaceSource(dataset_name="big", input_column="q", limit=5)
        assert len(source) == 5
