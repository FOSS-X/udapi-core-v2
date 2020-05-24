# udapi-core-v2

## Installation Instructions

1. Clone the repository

```sh
git clone https://github.com/FOSS-X/udapi-core-v2.git
cd udapi-core-v2
```

2. Create a virtual environment

```sh
pipenv install
pipenv shell
```

3.Run the UDAPI backend server. 
```sh
export FLASK_APP=api.py
flask run -h localhost -p 2020
```

