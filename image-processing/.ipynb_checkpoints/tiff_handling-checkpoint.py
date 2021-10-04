def define_initial_parameters():
    params_dict = dict(
        nozzle_row = 1, 
        crop_width_coefficient = 0.02, 
        crop_height_coefficient = 2,
        crop_nozzle_coef = 0.15,
    )    
    return params_dict

def tiff_folder_to_image_collection(folder):
    """
    Takes a folder and produces a skiamge image collection containing all of the images as a single variable 
    """
    if folder[-2:] != '//':
        if folder[-1] == '/':
            folder = folder+"/"
        else:
            folder=folder+"//"
    return skimage.io.imread_collection(folder+"*", plugin='tifffile')

def define_image_parameters(background_video, params_dict):
    """
    From the background video, determines the first-guess for the cropping operation. Based on the nozzle width and safety factors crop_width_coefficient, crop_height_coefficient, etc.
    """
    first_frame = image_sequence[0]    
    thresh_otsu = threshold_otsu(first_frame)
    binary_otsu = first_frame < thresh_otsu
    binary_otsu = np.array(binary_otsu)*255
    binary_otsu = np.uint8(binary_otsu)

    # Crop down to nozzle: 
    ## width = nozzle + 2%
    ## height = nozzle * 2.5
    non_zero_indicies = np.nonzero(binary_otsu[nozzle_row,:])
    first_non_zero = non_zero_indicies[0][0]
    last_non_zero = non_zero_indicies[0][-1]
    diameter = last_non_zero - first_non_zero #pix
    nozzle_diameter = diameter #white to white distance
    
    (crop_width_coefficient,crop_nozzle_coef,crop_nozzle_coef) = (params_dict["crop_width_coefficient"],params_dict["crop_nozzle_coef"],params_dict["crop_nozzle_coef"]
    crop_width_start = int(first_non_zero-int(nozzle_diameter*crop_width_coefficient))
    crop_width_end = int(last_non_zero+int(nozzle_diameter*crop_width_coefficient))
    crop_bottom = int(nozzle_diameter*crop_height_coefficient)
    crop_top = int(nozzle_diameter*crop_nozzle_coef)
    (params_dict["crop_width_start"], params_dict["crop_width_end"], params_dict["crop_bottom"], parms_dict["crop_top"]) = (crop_width_start, crop_width_end, crop_bottom, crop_top)

    return params_dict
                                                                  

def produce_background_image(background_video):
    """
    Description
    """
    bg_median = np.median(background_video, axis=0)
    bg_median = bg_median[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
                                                                  
                                                                  def convert_tiff_to_binary(experimental_sequence, bg_median, params_dict, intermediate_files_optional):
    """
    Takes as arguments the skiamge image sequence holding the experimental video and the background image to subtract. 
    Performs, sequentially, cropping, background subtraction, and binarization by the Li method, and saves the binary images. 
    To do: optional arguments to save the output of the different steps
    """    
    (nozzle_row, 
     crop_width_start, crop_width_end, crop_bottom, crop_top) = (params_dict["nozzle_row"], 
                                                                 params_dict["crop_width_start"], params_dict["crop_width_end"], params_dict["crop_bottom"], parms_dict["crop_top"])

    for i in range(0,len(experimental_sequence)):
        image = image_sequence[i]
        cropped_image = image[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
        # if intermediate_files_options = save cropped:
            # save cropped 
            #skimage.io.imsave(filename, bg_subtract_image)

        bg_subtract_image = cropped_image - bg_median
        bg_subtract_image = np.abs((bg_subtract_image < 0)*bg_subtract_image) #eliminates half the noise
            #if interemeddiate_files_optional = save cropped and bg subtract:
                #save bg subtracted 
                #bg_subtract_image = np.uint16(bg_subtract_image)
                #skimage.io.imsave(filename, bg_subtract_image)

        filename = f"{destination_folder_name}{i:03}.png"
        thresh_li = threshold_li(bg_subtract_image)
        binary_li = bg_subtract_image > thresh_li
        binary_li = np.array(binary_li)*255
        binary_li = np.uint8(binary_li)
        skimage.io.imsave(filename, binary_li, check_contrast=False)
                                                                  
                                                                  
def tiffs_to_binary(experimental_video_folder, background_video_folder, save_location, intermediate_files_optional):
    """
    Overall video processing pipeline: takes experimental video and background video, produces binarized video in target directory
    """
    params_dict = define_initial_parameters()
    experimental_video = tiff_folder_to_image_collection(experimental_video_folder)
    background_video = tiff_folder_to_image_collection(background_video_folder)
    #make_destination_folders()
    params_dict = define_image_parameters(background_video)
    bg_image = produce_background_image(background_video, params_dict)
    convert_tiff_to_binary(experimental_video, bg_image, params_dict, intermediate_files_optional)
