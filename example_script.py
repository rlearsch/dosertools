#### Instructions for use ####
## First time - install repository

# install pipenv
# grab git repository
# pipenv install
##

# edit this file
# to run this file
# pipenv run python example-script.py
####

# This conditional is required for multiprocessing to work on windows
# See https://stackoverflow.com/a/18205006 and similiar discussions
if __name__ == '__main__':
    import data_processing.integration as integration
    import os

    ## User edittable settings ##
    # videos_folder =
    # Absolute path to raw videos to process #
    videos_folder = "C:\\Users\\rlearsch\\Documents\\Photron\\PFV4\\PCOD_Samples_subset_multi"
    # See documentation (data_processing\integration.py, docstring for set_defaults)
    # for information about the optional settings
    optional_settings = {"crop_height_coefficient" : 3, "verbose" : True}
    # See documentation for how to use fname_format and sampleinfo_format
    # one example is below
    # folder name: 2021-03-16_RWL_0.3M-PEO-2.17wtpct-H2O_22G_shutter-60k_fps-40k_DOS-Al_5_1830_42
    # follows this pattern, delinated by '_'
    # (date)_(experimenter's name)_(sample info)_(needle guage)_(shutter speed)_(fps)_(substrate)_(run)_
    # (hours, minutes)_(seconds)
    # sample info: 0.3M-PEO-2.17wtpct-H2O
    # follows this pattern, delineated by '-':
    # (molecular weight)-(polymer backbone)-(concentration)-(solvent)
    # following these patterns when defining the variables fname_format and sampleinfo_format
    fname_format = "date_experimenter_sampleinfo_needle_shutter_fps_substrate_run_vtype_remove_remove"
    sampleinfo_format = "MW-backbone-concentration-solvent"

    images_folder = os.path.join(videos_folder,"images") # Path to where to save the binary images
    csv_folder = os.path.join(videos_folder, "csvs") # Path to where to save the csvs
    summary_folder = os.path.join(videos_folder, "summary") # Path to where to save the summary csvs
    ## End user edittable settings ##
    ## under normal use circumstances ##
    ## do not modify code below this comment block ##


    # If the images, csv, and summary folders don't exist, we make them.
    if not os.path.isdir(images_folder):
        os.mkdir(images_folder)
    if not os.path.isdir(csv_folder):
        os.mkdir(csv_folder)
    if not os.path.isdir(summary_folder):
        os.mkdir(summary_folder)

    integration.videos_to_summaries(videos_folder, images_folder, csv_folder, summary_folder, fname_format, sampleinfo_format,optional_settings)
