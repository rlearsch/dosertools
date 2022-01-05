# Current Status, Suggestions for improvement, Outstanding questions

## Next Steps
* elasped time unit
* verbose folder name cut off

* **Video selector**
    * identify videos that are already processed (needs testing on actual data)
    * Handling if folders/files already exists -- overwrite vs. not overwrite (needs testing on actual data)
    * Let user specify what file type to look for (needs testing with non tiff files)
* **Integrating into a single script**
    * Different start/end points (what additional start/end do we need?)
* **Error Handling**
    * handle errors from threshold_otsu encountering a non-grayscale image
      * Print out a warning if non-grayscale, identifying the folder and then skip?
      * Currently, attempting to convert into grayscale (Needs testing)
    * vet optional settings--validate that entries given make sense
    * handle missing fps tag for binaries_to_csvs
    * handle missing parameters for binary_to_radius_time
    * If run, sample, fps missing from folder name
* **Moonshots**
    * Run different processing method if there is no background video to subtract from
        * try to harvest one from the last frames of the video
        * or, use Li method on experiment video, seems to work better than others when no background subtraction is present
    * Read nozzle diameter off background and compare it to experimental
      * decide if needed
    * Rob's/JAK's "frame shifting" idea to dial in t_c
    * Find $\eta_E$ plateau value with functional form
    * Refine $\lambda_E$ calculation
    * Save an error log if crash occurs
* **Clean up**
    * fixtures folder (substantially cleaned)
    * Variable, function, module naming cleanup pass
    * Comment cleanup
    * tests
    * docstrings
    * Check for remaining TODO items
* Integration tests
* check for file sorting issues when images exceed 999
  * Write a test that checks this
* **Tests**
  * Image format
  * Images in non-grayscale
  * tiffs_to_binary
  * videos_to_summaries
  * Tests noted in TODO


## Packaging
* Prepare package for installation: Tutorial--https://packaging.python.org/en/latest/tutorials/packaging-projects/
* Dependencies
  * https://github.com/scikit-image/scikit-image/issues/4780
  * Write up of under what circumstances msvc-runtime may need to be installed

## Documentation
* Sphinx https://www.sphinx-doc.org/en/master/usage/quickstart.html
  * Installation instructions
  * Usage instructions
    * Brainstorming use cases and writing instructions for each of those
  * Function-level instructions can be automatically generated as part of documentation
    * Descriptions and usage for each function in docstring
    * Type hinting
    * Examples where useful (i.e. select_video_folders)
* License

## Ideas to keep in mind
* DRY : Don't Repeat Yourself
* Single purpose functions
* Write tests
* Modify main only with validated code
