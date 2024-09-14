import openai
import os
from PIL import Image

# Open an image file
image = Image.open("path/to/image.jpg")

# train_data, _, test_data = ImageDataset.from_folders('https://autogluon.s3.amazonaws.com/datasets/shopee-iet.zip', train='train', test='test')
# print('train #', len(train_data), 'test #', len(test_data))
# train_data.head()

# data/
# ├── test/
# └── train/
# train # 800 test # 80

