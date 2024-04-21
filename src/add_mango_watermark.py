import os
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def get_images(workdir):
    """获取目录中所有图片的路径列表，并按照文件名数字排序，排除最后一个文件。"""
    img_lists = []
    for root, _, files in os.walk(workdir):
        if files:
            files = sorted(files, key=lambda x: int(x.split('.')[0]))
            for file in files[:-1]:
                img_path = os.path.join(root, file)
                img_lists.append(img_path)
    return img_lists

def add_watermark_to_image(input_file_path, watermark, watermark_folder):
    """为单个图片添加水印。"""
    watermark_path = os.path.join(watermark_folder, 'Mango_Right.png')
    watermark = Image.open(watermark_path)
    try:
        base_image = Image.open(input_file_path)
        position = (base_image.width - watermark.width, base_image.height - watermark.height)
        if base_image.mode != 'RGBA':
            base_image = base_image.convert('RGBA')
        transparent = Image.new("RGBA", base_image.size)
        transparent.paste(base_image, (0, 0))
        transparent.paste(watermark, position, mask=watermark)
        if base_image.format == 'JPEG' or input_file_path.lower().endswith('.jpg'):
            transparent = transparent.convert('RGB')
        transparent.save(input_file_path, format=base_image.format if base_image.format else 'JPEG', quality=100)
    except Exception as e:
        print(f"无法将水印添加到 {input_file_path}：{e}")

def add_watermarks_concurrently(img_lists, watermark_folder, thread_count=4):
    """多线程添加水印。"""
    watermark_path = os.path.join(watermark_folder, 'Mango_Right.png')
    watermark = Image.open(watermark_path)
    with tqdm(total=len(img_lists), desc="添加水印中") as progress, ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(add_watermark_to_image, img, watermark, watermark_folder) for img in img_lists]
        for future in futures:
            future.result()  # 等待线程完成
            progress.update(1)

def main(workdir, watermark_folder, thread_count=4):
    img_lists = get_images(workdir)
    add_watermarks_concurrently(img_lists, watermark_folder, thread_count)

if __name__ == '__main__':
    workdir = 'Mango' 
    watermark_folder = 'watermark' 
    main(workdir, watermark_folder)