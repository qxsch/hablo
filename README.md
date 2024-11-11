# Hablo

**H**ierarchical **a**nnotation for **b**idirectional **l**anguage **o**utput


How to use?
```python
import hablo
hablo.mucho() # default uses Gunicorn Channel

# you can also set your own channel: hablo.mucho(con=Channel)
```


```bash
python3 -m pip install --upgrade build
python3 -m build
pip3 install --no-index dist/hablo-0.0.1
```
