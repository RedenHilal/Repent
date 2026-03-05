# Repent

Report automation with latex and jinja using [sleek template](https://github.com/francois-rozet/sleek-template).

## Set up

1. `git clone https://github.com/RedenHilal/Repent.git`
2. `chmod +x repent.py`
3. `sudo ln -s "$(pwd)/repent.py" /usr/local/bin/repent`
4. `python -m venv .venv`
5. `lastly, install jinja2 on the virtual env`

## Get Started

1. Set up venv and executable, by following set up before.
2. Prepare your data with the structure of `structure.json`.
3. Launch it!

example

```
repent -j data.json -o report.pdf
```


