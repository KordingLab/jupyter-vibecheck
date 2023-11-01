# jupyter-vibecheck

A Jupyter Widget to get atomic feedback as a student progresses through a didactic jupyter notebook.

## Setup

```
pip install vibecheck datatops
```

## Usage

```python
from vibecheck import DatatopsContentReviewContainer

DatatopsContentReviewContainer(
    "",  # No text prompt
    "W1D1-GD-Explanation-v1",
    {
        "url": "https://datatops-example-server.com",
        "name": "deep-learning-101",
        "user_key": "30d8xnd2",
    },
).render()
```

![image](https://user-images.githubusercontent.com/693511/234666584-f09e84af-148e-4cb0-aef4-68104b512dbf.png)

For more information, see the [documentation](./docs/).
