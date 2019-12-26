Git [pre-commit](https://github.com/pre-commit/pre-commit) hooks for C/C++.

### Using with pre-commit

Add the following code to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/igankevich/pre-commit-cpp
    rev: 0.1.0
    hooks:
    -   id: header-guard
```


### Available hooks

- `header-guard` — add/update header guard in C/C++ headers.


### License

Public domain.

