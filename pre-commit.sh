set -e
set -o pipefail

echo "=== Running isort ==="
isort --profile black phonebook_project

echo "=== Running black ==="
black --line-length 79 phonebook_project

echo "=== Running flake8 ==="
flake8 phonebook_project