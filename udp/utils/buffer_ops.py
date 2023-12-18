from PIL import ImageFile


def write_text(save_path: str, packets: list):
    f_write = open(save_path, "wb")

    for p in packets:
        f_write.write(p)

    print(f'Written at {save_path}.')

    f_write.close() 


def write_img(save_path: str, packets: list):
    img = ImageFile.Parser()
    
    print('Parsing image...')
    
    for p in packets:
        img.feed(p)
        
    im = img.close()
    im.save(save_path)

    print(f'Written at {save_path}.')