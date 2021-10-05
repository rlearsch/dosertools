def foldername_parse(foldername: str, fname_format: str, sampleinfo_format: str, fname_split="_", sample_split='-') -> dict:
    """Parses folder names into a dictonary of parameters using supplied format

    Parameters
    ----------
    foldername : str
        the name of the folder
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format : str
        the format of the foldername with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        the format of the sampleinfo section of the foldername
        separated by the deliminator specified by sample_split
    fname_split : str, optional
        the deliminator for splitting the folder name (default is "_")
    sample_split : str, optional
        the deliminator for splitting the sampleinfo section
        of the foldername (default is "-")
    """

    folder_split = foldername.split(fname_split) # split foldername using fname_split deliminator
    tag_split = fname_format.split(fname_split) # split fname_format into tags using fname_split deliminator

    param_dict = {} # initialize dictionary for outputting parameters from the foldername

    i = 0 # index in the folder name
    for tag in tag_split:
        value = folder_split[i] # entry in the folder name corresponding to the tag from the fname_format

        if "fps" in tag.lower():
            if "k" in value: # check if fps is formated with k to represent 1000
                fps = int(''.join(i for i in value if i.isdigit()))* 1000 # take numeric part of fps and multiply by 1000 if k was used, i.e. 25k becomes 25000
            else:
                fps = int(''.join(i for i in value if i.isdigit())) # take numeric part of fps only
            param_dict["fps"] = fps  # set entry in parameter dictionary
        elif "run" in tag.lower(): # look for run number spec
            param_dict["run"] = int(''.join(i for i in value if i.isdigit())) # take numeric part of run only and set in parameter
        elif "sampleinfo" in tag.lower():
            sampleinfo_split = value.split(sample_split) # split sampleinfo using the sample_split deliminator
            sample_tag_split = sampleinfo_format.split(sample_split) # split sampleinfo_format into sample tags using sample_split deliminator
            j = 0 # index in the sampleinfo
            for sample_tag in sample_tag_split:
                sample_value = sampleinfo_split[j] # entry within sampleinfo coresponding to the sample_tag from the sampleinfo_format
                param_dict[sample_tag] = sample_value # set entry in parameter dictionary
                j = j + 1
        else:
            param_dict[tag] = value  # set entry in parameter dictionary
        i = i + 1

    return param_dict #output parameters

def make_destination_folders():

    pass
