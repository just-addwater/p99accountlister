# P99 Account Lister
A simple, clean, and minimalist account helper overlay for Project 1999 (EverQuest). Tired of alt-tabbing or looking at a messy notepad to remember your dozens of alt or guild bot account details? This tool provides an "always on top" window that you can place next to your login screen for easy access to all your usernames and passwords.

## Important Disclaimer

This tool **does not** interact with the EverQuest game client, its files, or its memory in any way. It is a completely standalone program that simply displays the contents of a local text file (`act.txt`) that you create. 

<img width="445" height="895" alt="2025-09-03 23_07_32-Account Lister" src="https://github.com/user-attachments/assets/b4d49840-552e-400d-b5ac-2a35dc2feeb7" />



## Features

*   **Always on Top:** Stays on top of the EverQuest client so you never have to alt-tab.
*   **Zero Dependencies:** No complex installation needed—it runs with a standard Python installation.

---

## Installation & Setup

This application is designed to be as simple as possible to run.

**Prerequisite:** You must have Python installed on your system. If you don't, you can download it from [python.org](https://www.python.org/downloads/).

**Steps:**

1.  Download the `thelonglist.py` file from this repository.
2.  Place the file in a new, empty folder anywhere on your computer.
3.  Run the script. You can usually do this by simply double-clicking the `thelonglist.py` file.
    *   Alternatively, you can open a command prompt/terminal in that folder and run `python thelonglist.py`.
4.  The first time you run it, the program will automatically create a file named `act.txt`. This is where you will store your account information.

You can use the EQ titanium batch file to start both EQ and this. Just replace "C:\" below with the directory the python program is in. 

```
@echo off

REM --- Part 1: Launch the game in its own window ---
echo Starting the game...
start eqgame patchme

REM --- Part 2: Launch the Python script from its specific directory ---
echo Launching the Python script...

REM Temporarily change the directory to where the Python script is located
pushd "C:\"

REM Run the Python script using the Python launcher 'py'
REM Using 'start' will run the python script in its own, new command window.
start "Python Script" py thelonglist.py

REM Return to the original directory (good practice)
popd

echo Both processes have been launched.
```
---

## How to Use

### 1. Adding Your Accounts

The program loads all account information from the `act.txt` file. You need to edit this file with a text editor (like Notepad) to add your characters or use the "Add Character" button at the bottom of the app. 

The file uses a simple JSON format. Here is an example of how to format it with two characters:

```json
{
    "accounts": [
        {
            "name": "Fippy",
            "level": 10,
            "server": "Blue",
            "class": "Warrior",
            "username": "fippy_darkpaw",
            "password": "",
            "note": "My first warrior"
        },
        {
            "name": "Lucan",
            "level": 50,
            "server": "Green",
            "class": "Paladin",
            "username": "lucan_dlere",
            "password": "",
            "note": ""
        }
    ],
    "recent": [],
    "last_server": "All",
    "window_geometry": {
        "x": 1000,
        "y": 100,
        "width": 420,
        "height": 700
    },
    "expanded_classes": {}
}
```

Add each new character as a new block inside the "accounts": [ ... ].
Make sure each character block is enclosed in curly braces {} and separated by a comma.
The "note" field is optional and can be left as an empty string "".

2. Using the Interface
Move: Click and drag any part of the background to move the window.
Resize: Drag the edges or corners of the window to resize it. The app will remember its size and position for the next launch.
Filter: Click the Blue, Green, or Red radio buttons to show only characters from that server.
Expand/Collapse: Click on a class name (e.g., "▶ Warrior (5)") to hide or show the characters in that class.
Select: Click anywhere on a character's entry to highlight it.

Technology Used
Python 3
Tkinter (Python's standard cross-platform GUI library)
