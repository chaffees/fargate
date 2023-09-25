# Source the venv On Linux & MacOS

source venv/bin/activate

## Execute test.py

python3 test.py $(pulumi stack output EndpointName)
