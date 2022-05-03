from cx_Freeze import setup, Executable

executables = [Executable('ClientGUI.py', targetName='Client.exe', base='Win32GUI',
                          icon='static/clienticon.png')]

# excludes = ['unicodedata', 'html', 'http', 'xml', 'bz2']

include = ['sqlalchemy', 'PyQt5', 'pyodbc']

include_files = ['client_config.ini',
                 'static',
                 'DateBase',
                 'key',
                 'static/eye_hidden.svg',
                 'static/eye_visible.svg',
                 'static/play.png',
                 'static/clienticon.png',
                 ]

# zip_include_packages = ['PyQt5.uic.widget-plugins', 'lib', 'PyQt5']

options = {
    'build_exe': {
        'include_msvcr': True,
        'packages': include,
        # 'excludes': excludes,
        'namespace_packages': ['sqla_utils', 'sqla_declaratives'],
        # 'zip_include_packages': zip_include_packages,
        'build_exe': 'ChatClient',
        'include_files': include_files,
    }
}

setup(name='MyStudyChat_client',
      version='1.0.0',
      description='Клиент для сервера - MyStudyChat-server',
      author="Aleksandr Fedortsov",
      author_email="aleksandrfedorcov431@gmail.com",
      executables=executables,
      options=options, )
