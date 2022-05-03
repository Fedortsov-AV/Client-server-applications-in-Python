from setuptools import setup, find_packages

setup(name="MyStudyChat_client",
      version="1.0.0",
      description="Клиент для сервера - MyStudyChat-server",
      author="Aleksandr Fedortsov",
      author_email="aleksandrfedorcov431@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
