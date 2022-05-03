from cx_Freeze import setup, Executable

executables = [Executable('serverGUI.py', targetName='Server.exe', base='Win32GUI',
                          icon='static/Servericon.png')]



include = ['sqlalchemy', 'PyQt5', 'pyodbc']

include_files = ['server_config.ini',
                 'static',
                 'DateBase',
                 'static/exit.png',
                 'static/play.png',
                 'static/stop.png',
                 'static/Servericon.png',
                 ]

# zip_include_packages = ['PyQt5.uic.widget-plugins', 'lib', 'PyQt5']

options = {
    'build_exe': {
        'include_msvcr': True,
        'packages': include,
        'namespace_packages': ['sqla_utils', 'sqla_declaratives'],
        # 'zip_include_packages': zip_include_packages,
        'build_exe': 'ChatServer',
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
