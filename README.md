# Trunchbull: a facial-recognition attendance tracker
![alt text](https://i.pinimg.com/originals/3d/1f/b7/3d1fb76d7af237e7773fa8a789fceb71.gif)

## Run
1. [Download the repository](https://github.com/qe/trunchbull/archive/refs/heads/master.zip)
2. In the folder called ***images*** within the downloaded folder, replace the images in the with the ones you want
3. Format the file names with a hyphen separating first and last name (e.g. ***john-doe.png*** or ***jane-doe.jpg***) 
4. Open **Terminal**
5. ```cd``` into the directory of the downloaded repository
6. ```source agatha/bin/activate``` activates the virtual environment (called *agatha*)
7. ```python3 trunchbull.py``` to run
8. Click on the video output
9. Press ```r``` to begin the roll call
10. Press ```f``` to finish the roll call (CSV file should automatically open)
11. Press ```ESC``` to close the application

<br>

![](example.gif)

<br>

The CSV file from the example above looks like this 👇

status | name | time
------------ | ------------- | -------------
P | agent-bill | 12:48:42
P | alex-ismodes | 17:18:38
P | agatha-trunchbull | 17:18:41
P | agent-bob | 17:18:45
A | jennifer-honey | NA

<br>

## To-Do 
- [ ] Give the option of setting a timer to gather who is late 
- [ ] Add docstrings to functions and methods
- [ ] Add requirements.txt file
    - Automatically do this using ```pip install pipreqs```

<br>
