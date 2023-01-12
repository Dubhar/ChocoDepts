# Install

* download latest zip (see "Releases")
* extract zip to `C:\Program Files\ChocoDepts`
* open `C:\Program Files\ChocoDepts` in explorer
* right-click `ChocoDepts.exe` and click `Send to` ➜ `Shortcut on Desktop`

# Build it from source
```shell
# get source code
git clone https://github.com/Dubhar/ChocoDepts.git

# build the exe
cd ChocoDepts
python.exe .\setup.py py2exe

# install
Move-Item .\dist 'C:\Program Files\ChocoDepts'
```
now you can create a shortcut, see regular install above 
