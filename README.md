# dostools

dostools is a Python package for analyzing dripping-onto-substrate rheology videos.\
The software converts an input video into a series of binary images, produces a dataset of D/D0 and time values for 
each frame in the video, and generates values for the elongational relaxation time lambda_E, the diameter at critical 
time (the onset of elasto-capillary behavior) D(t_c)/D0, and a guess for the quantity of 
(elongational viscosity / surface tension) eta_E/sigma.  

## Authors
Rob Learsch and Red Lhota\
Contact:\
rlearsch (at) caltech (dot) edu 

## Installation

dostools comes bundled with a pipfile which creates the python environment it needs to run. 
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
 in the terminal from your dostools directory. 

See the file named "example-and-settings.md" and "example_script.py" for more information 
on how to use this package.
## Usage
dostools is expecting experiments that contain a pair of videos - one "experimental" video that contains 
the fluid transitioning from needle to substrate, and one "background" video that contains only the
needle and the literal background of the camera's view. In our testing, we found a background video 
of 100 frames gives plenty of data to overcome any noise that would be found in a single frame. 

dostools is written for DOS videos of viscoelastic fluids. It can perform background 
subtraction and image processing on videos of any type. However, the data processing 
(calculating elongational relaxation time, elongational viscosity, etc) is done using assumptions that
are only true for fluids that exhibit elastocapillary behavior. 

dostools calculates values with machine precision. It is up to the user to decide where to truncate the 
data produced, based on the specifics of their own experimental setup. 
<!--
```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

-->
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
