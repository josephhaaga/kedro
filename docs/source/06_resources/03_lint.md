# Linting your Kedro project

> *Note:* This documentation is based on `Kedro 0.15.0`, if you spot anything that is incorrect then please create an [issue](https://github.com/quantumblacklabs/kedro/issues) or pull request.

> *Note:* The following suggestions would require installing the  `pylint` package, subject to GPL licence.


You can ensure code quality by using [pylint](https://www.pylint.org/), a popular linting tool. Sample commands you can use to help with this are included in the script below:

```bash
isort
pylint -j 0 src/<your_project> kedro_cli.py
pylint -j 0 --disable=missing-docstring,redefined-outer-name src/tests
```

Alternatively, you can opt to use it as a plugin to your Kedro project. To do this, add the following code snippet to `kedro_cli.py` in your project root directory:

```python
@cli.command()
def lint():
    """Check the Python code quality."""
    python_call("isort", ["-rc", "src/<your_project>", "src/tests", "kedro_cli.py"])
    python_call(
        "pylint", ["-j", "0", "src/<your_project>", "kedro_cli.py"]
    )
    python_call(
        "pylint",
        ["-j", "0", "--disable=missing-docstring,redefined-outer-name", "src/tests"],
    )
```

To trigger the behaviour, simply run the following command in your terminal window:
```bash
kedro lint
```

Make sure you also include the dependency in your `requirements.txt`, i.e:
```text
pylint>=2.3.1,<3.0
```
