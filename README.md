# Whiptail

Whiptail is a Python library based on https://github.com/marwano/whiptail. It is basically a whiptail wrapper that allows calling whiptail from a python context.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install whiptail

Pay close attention to version number
```bash
pip install whiptail-<version>.tar.gz
```
e.g., if version number is 0.4 you should use
```bash
pip install whiptail-0.4.tar.gz
```

## Usage

Currently, the following whiptail methods are supported:

* input_box
* password_box
* msg_box
* text_box
* menu
* radio_list
* check_list

```python
import whiptail

whip = whiptail.Whiptail("WHIPTAIL_TITLE", height=10, width=78)  # Creates the main instance
whip.msg_box("Welcome to the whiptail library. Please hit OK to continue.")  # Displays a message box
```

## License
[BSD3](https://opensource.org/licenses/BSD-3-Clause)