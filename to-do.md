# Current Status

## General Features
* Improved filename parsing
  * breaking down sample name?
  * robust to if user did not follow exact format? (ex. _exp vs _bg)
  * can we have user teach the function what kind of filename they use? (i.e. what tags to look for?)
* Different folders:
  * Initial videos
  * Destination for binaries
  * Destination for csvs of traces
  * Saving output of fits
* Handling if folders/files already exists
* Processing all videos in folder regardless of date
  * eliminate _bg and binaries from folder_list

## Functions
* Look for usages of global variables
  * destination_folder

## Packaging
* Divide functions into modules
  * Image-processing?
  * File handling?
  * Plotting?
* Prepare package for installation
* Dependencies

## Documentation
* Installation instructions
* Usage instructions
* License

## Recently Completed
