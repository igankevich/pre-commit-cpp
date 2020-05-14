Git [pre-commit](https://github.com/pre-commit/pre-commit) hooks for C/C++.

### Using with pre-commit

Add the following code to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/igankevich/pre-commit-cpp
    rev: 0.6.3
    hooks:
    -   id: normalise
        args: ['--tab-width=4']
    -   id: header-guard
    -   id: normalise-opencl
    -   id: normalise-cpp
        args: ['--src=src', '--top=sys/types.h']
    -   id: legal
        args: ['--copyright-string=©', '--programme-name=Foobar',
               '--license-notice=gpl3+', # or any text
               '--alias=gituser:Git User',
               '--preamble=', '--postamble=']
```


### Available hooks

- `normalise` — normalise white space in C/C++ files:
  - change encoding to UTF-8 using [chardet](https://pypi.org/project/chardet/) library
  - replace tabs at the beginning of the line with spaces
  - replace white space at the end of the line with a newline character
  - remove empty lines from the beginning and the end of the file
- `header-guard` — add/update header guard in C/C++ headers.
- `normalise-cpp` — fix include paths in C/C++ files:
  - replace relative include paths with the paths relative to source directory
  - sort headers excluding the ones that should always be on the top (e.g. `sys/types.h`)
- `normalise-opencl` — remove leading underscores from OpenCL keywords (e.g.
  `kernel` instead of `__kernel`. Currently this is pure regular expression
  substitution.
- `legal` — add copyright and license notices at the beginning of the file. License notice
  argument can be any text and in this text `{0}` expands to programme name. Author names
  are read from git log and can be aliased.


### License

Public domain.
