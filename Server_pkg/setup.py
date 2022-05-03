from setuptools import setup, find_packages

setup(name="MyStudyChat_server",
      version="1.0.0",
      description="Сервер для чата",
      author="Aleksandr Fedortsov",
      author_email="aleksandrfedorcov431@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
