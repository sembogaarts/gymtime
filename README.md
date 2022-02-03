# Basic-Fit CLI (unofficial)

Tired of checking the Basic-Fit app for your favourite time to become available over and over again? This script allows you to reserve your sessions through the CLI, if it's not available it will automatically retry until it is!



**Disclaimer:** _Use this script on your own risk, I recommend you to keep the interval above 15 seconds._

## Requirements

| Package | Version |
|---------|---------|
| Python  | 3       |
| Pip     | 3       |


## Installation
If you don't want to install the packages on your system, it's also possible to create a venv.
```
pip install -r requirements.txt
```

## Usage
After installation you'll be able the use the script, below is the most easy way to start the script.
```
python main.py
```

If you don't want to interact with the wizard, you can pass in some arguments to make the process even faster.
```
usage: main.py [-h] [-u EMAIL] [-p PASSWORD] [-d DATE] [-t TIME] [-i INTERVAL]

optional arguments:
  -h, --help   show this help message and exit
  -u EMAIL     E-mail used for your Basic-Fit account
  -p PASSWORD  Password used for your Basic-Fit account
  -d DATE      Date for the reservations (dd-mm-yyyy)
  -t TIME      Time for the reservations (hh:mm)
  -i INTERVAL  Interval in seconds before retrying again

```
