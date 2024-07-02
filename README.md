# Whats the script do?

The script accepts an XLS file that comes from the Hilan system and allows uploading its content to the Synerion system by Browser Automation.

## Requirements
1. python 3.10+
2. Python Libraries: `selenium, bs4`
3. Browser Driver Automation that compatible with the current browser that installed


## Syntax
`python convert.py --username="user" --password="pass" --file=test.xls`

OR with System Enviroments

```
EXPORT SYNERION_USER="username"
EXPORT SYNERION_PASS="password"
```
`python convert.py --file=test.xls`
