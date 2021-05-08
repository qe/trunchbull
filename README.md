# Trunchbull: a facial-recognition attendance tracker
![alt text](https://i.pinimg.com/originals/3d/1f/b7/3d1fb76d7af237e7773fa8a789fceb71.gif)

## Run
1. [Download the repository](https://github.com/qe/trunchbull/archive/refs/heads/master.zip)
2. Open **Terminal**
3. ```cd``` into the directory of the downloaded repository
4. ```source agatha/bin/activate``` activates the virtual environment (called *agatha*)
5. ```python3 trunchbull.py``` to run
6. ```click on the video output```
7. press ```r``` to begin the roll call
8. press ```f``` to finish the roll call (CSV file should automatically open)
9. press ```ESC``` to close the application

<br>

the CSV file should look like this 👇

status | name | time
------------ | ------------- | -------------
P | alex-ismodes | 12:48:42
P | agatha-trunchbull | 12:49:3
A | agent-bob | NA
A | agent-bill | NA
A | jennifer-honey | NA

<br>

## To-Do List
- [ ] give the option of setting a timer to gather who is late 
- [ ] add docstrings to functions and methods
- [ ] add requirements.txt file
    - automatically do this using ```pip install pipreqs```

<br>
