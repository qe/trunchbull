<p align="center">
  <img src="trunchbull.png" alt="Agatha Trunchbull" width="42%" height="42%">
</p>

<h3 align="center">Trunchbull</h3>
<p align="center">
  The facial-recognition attendance tracker.
  <br>
  <br>
  <a href="https://github.com/qe/trunchbull/archive/refs/heads/master.zip">Download</a>
  ยท
  <a href="https://github.com/qe/trunchbull/issues/new?template=bug_report.md">Report bug</a>
  <br>
  <br>
  Trunchbull is a facial-recognition program that tracks attendance using<br>
  computer vision by noting, in a CSV file, the time when the student<br>
  appeared in the camera. Named after Miss Trunchbull, the main<br>
  antagonist in Roald Dahl's <a href="https://en.wikipedia.org/wiki/Matilda_(novel)"><i>Matilda</i></a>, I believe this program captures<br>
  some of her uncompromising persona.
</p>


## Run
1. Download the repository
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


<p align="center">
  <img src="example.gif" alt="Example of Trunchbull" width="88%" height="88%">
</p>


<br>

The CSV file from the example above looks like this ๐

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



