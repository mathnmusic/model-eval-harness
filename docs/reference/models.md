# Models

Models generate responses to prompts.

## OpenAIModel

```python
from model_eval_harness.models import OpenAIModel

model = OpenAIModel(
    model_id="gpt-4o",
    api_key="sk-...",          # or set OPENAI_API_KEY
    base_url=None,              # for proxies/alternate endpoints
    temperature=0.0,
    max_tokens=1024,
)

# Sync
output = model.generate("What is 2+2?")

# Async
output = await model.generate_async("What is 2+2?")
```

### Chat Messages

Pass a list of message dicts for multi-turn conversations:

```python
output = model.generate([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
])
```

## Custom Models

Implement the `Model` abstract class:

```python
from model_eval_harness.models.base import Model

class MyModel(Model):
    model_id = "my-model"

    def generate(self, prompt, **kwargs):
        # your sync implementation
        return response

    async def generate_async(self, prompt, **kwargs):
        # your async implementation
        return response
```
