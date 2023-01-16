from py2exe import freeze

freeze(
    windows=[{'script': 'ChocoDepts.py'}],
    data_files=None,
    zipfile='library.zip',
    options={'includes': ['pygments']},
    version_info={}
)
