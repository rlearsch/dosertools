def foldername_parse(foldername, fname_format, sampleinfo_format, fname_split="_", sample_split='-'):

    # file_dict = {
    #     "date" : "20210929",
    #     "mw" : "6M",
    #     "backbone" : "PEO",
    #     "fps" : 25000,
    #     "run" : 1
    # }
    folder_split = foldername.split(fname_split)
    tag_split = fname_format.split(fname_split)

    file_dict = {}

    i = 0 # index in the folder name
    for tag in tag_split:
        value = folder_split[i] # entry in the folder name corresponding to the tag from the fname_format

        if "fps" in tag.lower():
            if "k" in value:
                fps = int(''.join(i for i in value if i.isdigit()))* 1000 # take numeric part of fps and multiply by 1000 if k was used, i.e. 25k becomes 25000
            else:
                fps = int(''.join(i for i in value if i.isdigit())) # take numeric part of fps only
            file_dict["fps"] = fps
        elif "run" in tag.lower():
            file_dict["run"] = int(''.join(i for i in value if i.isdigit())) # take numeric part of run only
        elif "sampleinfo" in tag.lower():
            sampleinfo_split = value.split(sample_split)
            sample_tag_split = sampleinfo_format.split(sample_split)
            j = 0
            for sample_tag in sample_tag_split:
                sample_value = sampleinfo_split[j] # entry within sampleinfo coresponding to the sample_tag from the sampleinfo_format
                file_dict[sample_tag] = sample_value
                j = j + 1
        else:
            file_dict[tag] = value
        i = i + 1

    return file_dict
