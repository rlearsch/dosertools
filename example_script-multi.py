# install pipenv
# grab git repository
# pipenv install
# pipenv run python nameofthisfile.py
if __name__ == '__main__':
    import data_processing.integrationmulti as integration
    #import data_processing.integration as integration
    import file_handling.tags as tags
    import os 
    import pandas as pd

    # videos_folder = os.path.join() # Absolute path to videos
    #videos_folder = "C:\\Users\\rlearsch\\Documents\\Photron\\PFV4\\example_script_test_videos_wip"
    videos_folder = "C:\\Users\\rlearsch\\Documents\\Photron\\PFV4\\PCOD_Samples_subset_multi"
    #videos_folder = "C:\\Users\\rlearsch\\Documents\\Photron\\PFV4\\Hydrocarbon_solvents"

    # 20211214_RCL_670k-PCOD-DADB-0p60wtper-PAO_22G_shutter-70k_fps-25k_Al_5_bg_2112_1820
    images_folder = os.path.join(videos_folder,"images")
    # i had to make this folder 
    fname_format = "date_experimenter_sampleinfo_needle_shutter_fps_substrate_run_vtype_remove_remove"
    sampleinfo_format = "MW-backbone-association-concentration-solvent"
    #sampleinfo_format = 'solvent'
    csv_folder = os.path.join(videos_folder, "csvs") # Absolute path to where to save the csvs
    summary_folder = os.path.join(videos_folder, "summary")
    # I made this folder ahead of time
    #will we make this folder automatically?

    optional_settings = {"crop_height_coefficient" : 3, "verbose" : True}
    #integration.videos_to_csvs(videos_folder, images_folder, csv_folder, fname_format, optional_settings)

    integration.videos_to_summaries(videos_folder, images_folder, csv_folder, summary_folder, fname_format, sampleinfo_format,optional_settings)
    short_fname_format = tags.shorten_fname_format(fname_format, optional_settings)
    #integration.csvs_to_summaries(csv_folder,summary_folder,short_fname_format,sampleinfo_format,optional_settings)

    # needle_diameter = []
    # sample_name = []
    # folders = os.listdir(images_folder)
    # for folder in folders:
    #     csv_path = os.path.join(images_folder,folder,folder + "_params.csv")
    #     params = pd.read_csv(csv_path)
    #     needle_diameter.append(params[params["Keys"] == "nozzle_diameter"]["Values"])
    #     sample_name.append(os.path.basename(folder))

    #df = pd.DataFrame({"sample":sample_name,"needle_diameter":needle_diameter})
    #df.to_csv(os.path.join(images_folder,"pcod_samples.csv"),index=False)


