# dosertools

dosertools is a Python package for analyzing dripping-onto-substrate extensional rheology (DoSER) videos.\
The software converts an input video into a series of binary images, produces a dataset of D/D0 and time values for 
each frame in the video, and generates values for the elongational relaxation time lambda_E, the diameter at critical 
time (the onset of elasto-capillary behavior) D(t_c)/D0, and a guess for the quantity of 
(elongational viscosity / surface tension) eta_E/sigma.  

## Authors
Rob Learsch and Red Lhota\
Contact:\
rlearsch (at) caltech (dot) edu 

## Installation

dosertools is hosted as a package on [pypi](https://pypi.org/). You can use the package manager 
[pip](https://pip.pypa.io/en/stable/) to install dosertools by typing
```bash
pip install dosertools
```
in your terminal. 

See the file named "example-and-settings.md" and "example_script.py" for more information 
on how to use this package.
## Usage
### Folder Structure  
dosertools operates on an entire folder at once. Within that folder, there should be folders for each experimental video
and background video you intend to process. *Those* folders should contain your video decomposed into a series of images
(we prefer .tif but it should work with any image file format).\
If we are operating on a folder named "PCOD_Samples_subset_multi" (the folder used in example_script.py),
with 3 experiment videos and 1 background video, 
the structure should look like this: 
```commandline
├── PCOD_Samples_subset_multi
|   ├── experiment_1
|   |   ├── frame001.tif
|   |   ├── frame002.tif
|   |   ├── ...
|   |   ├── frame300.tif
|   ├── experiment_2
|   |   ├── frame001.tif
|   |   ├── frame002.tif
|   |   ├── ...
|   |   ├── frame420.tif
|   ├── experiment_3
|   |   ├── frame001.tif
|   |   ├── frame002.tif
|   |   ├── ...
|   |   ├── frame334.tif
|   ├── background
|   |   ├── frame001.tif
|   |   ├── frame002.tif
|   |   ├── ...
|   |   ├── frame100.tif
```
### Types of videos
The "experiment" video contains the actual experiment, where the fluid transitions from needle to substrate, and the "background" video that contains only the
needle and the literal background of the camera's view. In our testing, we found a background video 
of 100 frames gives plenty of data to overcome any noise that would be found in a single frame.

Here are examples of a background image with and without a drop: 

<img src="https://user-images.githubusercontent.com/66884317/160924210-dcc02af0-61e7-4759-abdf-532405069a2e.png" width="200" height="400"> and <img src="https://user-images.githubusercontent.com/66884317/160924320-0e1f3157-0de3-40d1-a600-8dbfdccd271f.png" width="200" height="400">. 
 
 Here is a single image from the corresponding experimental video: 
 
 <img src="https://user-images.githubusercontent.com/66884317/160925518-2d72b26b-6d8b-4f0b-9f28-95eca0f20c43.png" width="200" height="400">

Either type of background video is acceptable (it may be easier to harvest a background that 
contains a drop from old videos). You can try to remove it algorithmically by setting the 
`bg_drop_removal` to True in optional_settings. Another key setting is `one_background`.\
Our method is to use a single background video for each sample because changing the needle/syringe can
reposition the needle in the frame. This is reflected in `one_background` defaulting to `True`
If you have highly variable lighting or experimental conditions between samples, you
may want to supply a background video paired to each experimental video and set `one_background` to `False`

Please reference the information in 
[Examples-and-settings.md](https://github.com/rlearsch/dosertools/blob/main/Example-and-settings.md) 
for more information. 

dosertools is written for DoSER videos of viscoelastic fluids. It can perform background 
subtraction and image processing on videos of any type. However, the data processing 
(calculating elongational relaxation time, elongational viscosity, etc) is done using assumptions that
are only true for fluids that exhibit elastocapillary behavior. 

dosertools calculates values with machine precision. It is up to the user to decide where to truncate the 
data produced, based on the specifics of their own experimental setup.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## Testing
dosertools comes bundled with a pipfile which creates the python environment it needs to run. 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pipenv. 
You will need to install
pipenv if your installation of python doesn't have it. You can do this by typing 
```bash
pip install pipenv
````
in your terminal, followed by 
```bash
pipenv install
```
 in the terminal from your dosertools directory. 

dosertools comes with a collection of [tests](https://docs.pytest.org/en/7.0.x/) to help us write better code and 
prevent unintended consequences when modifying code. 

If you are getting unexpected results, or you are modifying the code on your machine, you may want to 
run tests to troubleshoot or verify you haven't unintentionally changed anything. 

To do this, navigate to the src folder:
```terminal
..\dosertools> cd .\src\
```
and run pytest within the pipenv
```terminal
..\dosertools\src> pipenv run python -m pytest
```
## Changelog
### 2022-06-13
1. Fixed [issue #11](https://github.com/rlearsch/dosertools/issues/11), where a background image exactly 
matching an experimental would cause an error and halt processing.
2. Updated use and expectations in the readme file. 
## License
MIT License

Copyright (c) 2022 Red C. Lhota and Robert W. Learsch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
