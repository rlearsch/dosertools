# First time setup
dostools comes bundled with a pipfile which creates the python environment it needs to run. You will need to install
pipenv if your installation of python doesn't have it. You can do this by typing 
```bash
pip install pipenv
````
in your terminal, followed by 
```bash
pipenv install
```
 in the terminal from your dostools directory.  

# example_script.py
Once this is set up, make your own copy of example_script.py and modify the values within. 

The key variables are 
1. videos_folder
2. optional_settings
3. fname_format
4. sampleinfo_format

### videos_folder:
This is the path to a folder containing all of your dos videos you wish to process. You can give an explicit 
path, eg, 
```python
videos_folder = "C:\\Users\\rlearsch\\Documents\\Photron\\PFV4\\PCOD_Samples"
```
or you can use the os package in python. The same path could be constructed as 
```python
videos_folder = os.path.join("C:\\", "Users","rlearsch","Documents","Photron","PFV4","PCOD_Samples")
```

### optional_settings:
There are many settings used in the processing algorithm we have decided the user should be able to easily modify.
We have provided default values based on our own experience, but they will not always be the best values for every 
video. If the package is not working as you expect it to, modifying these values may help.  
A brief explanation of each setting and its default value is at the bottom of this document. 

### fname_format
Here, tell the computer the pattern you have used to name your samples. It reads the filenames expecting them to match 
the pattern given.\
For example, we use the following pattern: (date) _ (experimenter's name) _ (sample info) _ (needle guage) 
_ (shutter speed) _ (fps) _ (substrate) _ (run) _ (hours, minutes) _ (seconds), resulting in filenames such as this: 
2021-03-16_RWL_0.3M-PEO-2.17wtpct-H2O_22G_shutter-60k_fps-40k_DOS-Al_5_1830_42 

We want to keep most of this information, but not the last two values (they are automatically added by our video 
camera's software). We use the following defintion for fname format: 
```python
fname_format = "date_experimenter_sampleinfo_needle_shutter_fps_substrate_run_vtype_remove_remove"
```
Note that we name the last two items as "remove", telling the computer not to save those. The categories in fname_format
are delineated by the optional setting fname_split, which defaults to '_'.

### sampleinfo_format
sampleinfo_format follows a similar idea to fname_format, but deals exclusively in unpacking the information contained 
in sampleinfo. It reads the string marked as sampleinfo and matches it to the pattern given.  
For example, our filename from the previous example is:\
2021-03-16_RWL_0.3M-PEO-2.17wtpct-H2O_22G_shutter-60k_fps-40k_DOS-Al_5_1830_42
and according to the pattern given in fname_format, the string between the second and third '_' is the sample info. 
That string is "0.3M-PEO-2.17wtpct-H2O" and is of the pattern 
(molecular weight)-(polymer backbone)-(concentration)-(solvent)
so we use 
```python
sampleinfo_format = "MW-backbone-concentration-solvent"
```

The categories in sampleinfo_format are delineated by the optional setting sample_split, which defaults to '-'.

### images_folder, csvs_folder, summary_folder
These variables are the location the binary images (images_folder), raw csvs (csvs_folder), and summary 
csvs (summary_folder) should be saved. We default to storing them inside of videos_folder as that is how we like to 
organize our data. You are of course welcome to change the values of these variables as well. 

# Running the script
After you've modified the important variables, you can run the script. Do this by executing
```bash
pipenv run python example_script.py 
```
in the terminal from the dostools directory.
# Optional settings
```python
nozzle_row: int 
```
Row to use for determining the nozzle diameter.\
Default is 1.
```python
crop_width_coefficient: float
```
Multiplied by the calculated nozzle_diameter to determine the buffer
on either side of the observed nozzle edges to include in the cropped.\
Default is 0.02
```python
crop_height_coefficient: float
```      
Multiplied by the calculated nozzle_diameter to determine the bottom
        row that will be included in the cropped image.
        Default is 2.
    
```python
crop_nozzle_coefficient: float
```
Multiplied by the calculated nozzle_diameter to determine the top
        row of the cropped image.\
        Default is 0.15.
    
```python
fname_split: string
```
The deliminator for splitting folder/file names, used in fname_format.\
        Default is "_".
    
```python
sample_split: string
```
The deliminator for splitting sampleinfo tag in folder/file names,
        used in sampleinfo_format.\
        Default is "-".
    
```python
experiment_tag: string
```
  The tag for identifying experimental videos. May be empty ("").\
        Default is "exp".
    
```python
background_tag: string
```
  The tag for identifying background videos. May not be empty.\
        Default is "bg".
    
```python
one_background: bool
```
 True to use one background for a group of experiments only differing by
        run number. False to pair backgrounds and experiments 1:1.\
        Default is False.
    
```python
save_crop: bool
```
  True to save intermediate cropped images (i.e. experimental video
        images cropped but not background-subtracted or binarized). We view this as a troubleshooting method.\
        Default is False.
    
```python
save_bg_sub: bool
```
  True to save background-subtracted images (i.e. experimental video
        images cropped and background-subtracted but not binarized). We view this as a troubleshooting method.\
        Default is False.
    
```python
fitting_bounds: 2 element list of floats
```
  [start, end].\
        The D/D0 to bound the start and end of fitting of EC region.\
        Default is [0.1, 0.045].
    
```python
tc_bounds: 2 element list of floats
```
  [start, end].\
        The D/D0 to bound the start and end for finding the critical time.\
        Default is [0.3,0.07].
    
```python
needle_diameter_mm: float
```
  The needle outer diameter in millimeters.\
        Default is 0.7176 mm (22G needle).
```python
skip_existing: bool
```
 Determines the behavior when a file already appears exists
        when a function would generate it. True to skip any existing files.
        False to overwrite (or delete and then write, where overwriting would
        generate an error).\
        Default is True.
    
```python
verbose: bool
```
  Determines whether processing functions print statements as they
        progress through major steps. True to see print statements, False to
        hide non-errors/warnings.\
        Default is False.
```python
image_extension: string
```
 The extension for images in the video folder. TIFF recommended.\
        Default is "tif". Do not include ".".\
```python
summary_filename: string
```
  The base filename (no extension) for saving the summary csvs. If not
        provided, will be generated automatically based on the current date
        and time.\
        Default is "" to trigger automatic generation.
```python
cpu_count: int
```
  How many cores to use for multithreading/multiprocessing. If nothing
        provided, default will be the maximum number of cores.\
        Default is os.cpu_count().
