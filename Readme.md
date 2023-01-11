# prerequirements
if using PyCharm, you need to install the following python packages to your venv:
* py2exe

# build executable
```shell
python.exe .\setup.py py2exe
```

# install the executable
```shell
Move-Item .\dist 'C:\Program Files\ChocoDepts'
```


# run the program
```shell
cd 'c:\Program Files\ChocoDepts'
.\ChocoDept.exe
```
For simplification you may want to right-click the executable and select
`Send to` ➜ `Shortcut on Desktop`
