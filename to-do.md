# Current Status, Suggestions for improvement, Outstanding questions

## General Features
* Improved filename parsing
  * breaking down sample name?
  * robust to if user did not follow exact format? (ex. _exp vs _bg)
  * can we have user teach the function what kind of filename they use? (i.e. what tags to look for?)
  * What parameters do we want to parse in the filename?
    * Sample name
    * Concentration
    * fps
    * shutter speed?
    * date?
    * run #
    * Other tags: pass, sample number, ion ratio
* Different folders:
  * Initial videos
  * Destination for binaries
  * Destination for csvs of traces
  * Saving output of fits
* Handling if folders/files already exists
* Processing all videos in folder regardless of date
  * eliminate _bg and binaries from folder_list

## Existing Code
* Look for usages of global variables, change to variable in the function call if possible
  * destination_folder_name
  * crop_width_coefficient
  * crop_height_coefficient
  * crop_nozzle_coef
  * nozzle_row
  * crop_top
  * crop_bottom
  * crop_width_start
  * crop_width_end
  * read_top_border
  * nozzle_diameter
  * fps
    * might want to consider bundling the current global variables into dictionary variable of some sort (parameters, etc.)?


## Function Status
* define_image_parameters
  * Does this function still work with the zoomed in version? (is that taken care of via crop_height_coefficient?)
  * global variables: crop_width_coefficient, crop_height_coefficient, crop_nozzle_coef
  * are crop_width_start/end left and right?
* nonzero_runs
* zero_runs
* find_bottom_border_black
  * what are the differing roles of find_bottom_border_black and find_bottom_border_white?
* find_top_border
  * global variables: nozzle_row, crop_top, crop_bottom, crop_width_start, crop_width_end
* find_bottom_border_white
* process_to_csv
  * global variables: destination_folder_name, read_top_border
* find_closest_value
* determine_min_diameter
* produce_time_diameter_data
  * global variables: destination_folder_name, nozzle_diameter, fps
  * is nozzle_row used?
* plot_all
* generate_df
  * currently filenames have to be very specific to be able to parse (hard coded splitting)
  * global variables:
* convert_Li_bg_subtract
  * hard-coded filename parsing
  * global variables:
* find_lambda_E

* unnamed function(s) that capture the portions currently outside of functions

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
* Descriptions for each function

## Recently Completed
