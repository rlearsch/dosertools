# Current Status, Suggestions for improvement, Outstanding questions

## Next Steps
* Video selector: identify videos that are already processed
* Pairing a background with its experiment
* Read nozzle diameter off background and compare it to experimental
* Rob's/JAK's "frame shifting" idea to dial in t_c
* Saving all outputs: csv of R vs t, lambda_E, plot of R vs t, plot of eta_E vs strain, eta_E plateau value
* Save/produce dataset of fluid properties with sample variables 
* Find eta_E plateau value
* Plotting functions (mostly as a vetting step)
* Finish tests for binary related functions
* New sample data set
* Clean up fixtures folder
* Integration tests
* Variable, function, module naming cleanup pass
* Docstrings, type hinting
* Comment cleanup
* Improved filename parsing
  * can we make functions that look at the images be agnostic to what the folder is called? (so that people can easily rename their data folders to add additional information for the code without having to rename every image inside) - **double check this**
* Different folders:
  * Saving output of fits
* Handling if folders/files already exists
* Processing all videos in folder regardless of date
  * eliminate _bg and binaries from folder_list
* check for file sorting issues when images exceed 999
  * Write a test that checks this

## Packaging
* Prepare package for installation
* Dependencies

## Documentation
* Installation instructions
* Usage instructions
  * Function-level instructions can be generated with Sphinx?
* License
* Descriptions for each function
* Type hinting
* Brainstorming use cases and writing instructions for each of those

## Ideas to keep in mind
* DRY : Don't Repeat Yourself
* Single purpose functions
* Write tests
* Modify main only with validated code
