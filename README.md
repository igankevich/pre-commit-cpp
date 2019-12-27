Git [pre-commit](https://github.com/pre-commit/pre-commit) hooks for C/C++.

### Using with pre-commit

Add the following code to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/igankevich/pre-commit-cpp
    rev: 0.2.1
    hooks:
    -   id: normalise
        args: ['--tab-width=4']
    -   id: header-guard
```


### Available hooks

- `normalise` — normalise white space in C/C++ files:
  - change encoding to UTF-8 using [chardet](https://pypi.org/project/chardet/) library
  - replace tabs at the beginning of the line with spaces
  - replace white space at the end of the line with a newline character
  - remove empty lines from the beginning and the end of the file
- `header-guard` — add/update header guard in C/C++ headers.


### License

Public domain.

