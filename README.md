# Automate-Glyph-Extraction

## How we parse the OCR jsons
We took the 50 random images from each volume of the Tengyur Pecing with Work id `W1KG13126`.
There are 224 volumes so total 11200 images, then OCR all those 11200 images. after the OCR, I created a yml file with all the images sorted in a way that we are taking the one image from the 1 volume's 50 images and then one image from the last or 224 Volume's 50 images and so until both of them exhaust and then move on to the 2 volume and 223 volume. so on.


## how we crop
To crop the symbols from the source images, WE go thourhg the sorted images list and then take the OCR ouput of that corresponding image. Parse google OCR's symbols from the fullTextAnnotation
and then take the each symbol and then its bounding poly and then expand that bounding poly but a certain percentage
and then use that new expanded vertices value to crop that symbol from the image. Then save that image with name `symbolText_symbolNumber` and when it gets its 50 cropped images for that symbol. we stop cropping that symbol.