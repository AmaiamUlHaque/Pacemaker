# DCM

This is the DCM subfolder it is comprised of the following directories:

```bash
DCM/
│
├── main.py                 # Entry point – launches the GUI
│
├── gui/                    # All user interface code
│   ├──
│
├── core/                   # Core logic and data models
│   ├── \_\_init\_\_.py
│   ├── user_management.py  # Register and Login stores up to __10__ users
│
├── storage/                # Local persistence
│   ├── users.json          # Store the local user data
│
├── tests/                  # Unit tests for each core module
│   ├──\_\_init\_\_.py
│   ├── test_user_management.py  #Unit test all the functions in user management file
│
└── docs/                   # Documentation, screenshots, design notes
    ├── README.md           # This document
```
