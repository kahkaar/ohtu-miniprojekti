# ohtu-miniprojekti

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/kahkaar/ohtu-miniprojekti/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/kahkaar/ohtu-miniprojekti/actions/workflows/ci.yaml)

- [Product Backlog](https://helsinkifi-my.sharepoint.com/:x:/g/personal/aaronkah_ad_helsinki_fi/IQATnYMBAMCEQ57iHxkj_qhWAaD1NGwKU3RmEI25Eqsbi7s?e=A2Yyww)

## Installation Instructions

- Clone the repository
```bash
git clone https://github.com/kahkaar/ohtu-miniprojekti
```

- Cd to the directory
```bash
cd ohtu-miniprojekti
```

- Install dependencies
```bash
poetry install
```

- Install and configure PostgreSQL [Documentation](https://www.postgresql.org/docs/)

- Create ".env" file with the following template, replace "xxx" with the link to the PostgreSQL database and replace "satunnainen_merkkijono" with a random string
```
DATABASE_URL=postgresql://xxx
TEST_ENV=true
SECRET_KEY=satunnainen_merkkijono
```

- Initialize database
```bash
poetry run python src/db_helper.py
```

- Start the application
```bash
poetry run python src/index.py
```


### Development Instructions

- Install pre-commit hook
```bash
pre-commit install
```


## Definition of done
- The feature is implemented
- Unit tests are implemented and passing
- Robot tests are implemented and passing
- No linting errors
- Pull request created, reviewed and merged into main branch
