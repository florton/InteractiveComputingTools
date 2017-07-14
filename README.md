# Interactive Logic

##### Ver: Alpha 1.1
##### Created by Flanders Lorton

### Interactive Logic is a python app for creating and modeling simple logic circuits
### The app should be intuitive and simple to use for new and experienced users

## Installing and running
Currently there are no builds for OSX, Win32, or Linux.

### Windows 64 Bit executable now added for version Alpha 1.1!

##### Just download and run!


### Steps for installation from source code:
1. Install Python 2.7 https://www.python.org/downloads/release/python-2713/
2. Install Pygame http://www.pygame.org/download.shtml
3. Download InteractiveLogicAlpha1_1SourceCode.zip
4. Unzip and run `python InteractiveLogic.py`

### Buttons / Layout

###### Line tool is active when cursor is a diamond. Right click on white space to cancel.  
![Instructions](http://puu.sh/wJDMh/fd546eb060.png)

### Full Adder
![FullAdder](http://puu.sh/wJDOF/a98120f6f9.png)

#### Adder Truth Table
![FullAdderTT](http://puu.sh/wJDP3/68198a8e12.png)

### J K Flip Flop
![FlipFlop](http://puu.sh/wJDPB/d098189ad5.png)

#### Flip Flop Timing Diagram
![FlipFlopTG](http://puu.sh/wJDQ3/d330d7b66d.png)

## Known bugs
- Dragging either window will disrupt clock output on timing diagrams
- Pausing timing diagram will not stop clock cycling
- Some large component loops may be evaluated incorrectly (Speculation)

Please send me a message if you find additional bugs

## Features To Be Added
- Clear button and timescale on timing diagram
- Scroll bar for large truth tables
- Export as Image
- Custom Re-Usable Components
