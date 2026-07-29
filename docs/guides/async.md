# Async Evaluation

For evaluating large datasets, use the async runner to process examples concurrently.

## CLI

```bash
meh run eval.yaml --async-run
```

The `concurrency` field in your YAML config controls parallelism:

```yaml
concurrency: 10  # run 10 examples at once
```

## Python API

```python
import asyncio
from model_eval_harness import Harness

async def main():
    result = await harness.run_async(concurrency=10)
    result.print_report()

asyncio.run(main())
```

## Performance

- Async evaluation is 5-10x faster for typical API-bound workloads
- Set `concurrency` to match your API rate limits
- Default concurrency is 10 if not specified
