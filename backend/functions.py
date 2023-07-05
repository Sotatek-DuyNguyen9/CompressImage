#Import package
import sys
import numpy as np

import os
import matplotlib.pyplot as plt, mpld3
from sklearn.cluster import KMeans
from flask import abort

# import pyrebase

# config = {
#   "apiKey": "AIzaSyDUMgCIRYPWkbIyRiKDMqtd7pZStnBGWlo",
#   "authDomain": "iot-project-f52c7.firebaseapp.com",
#   "projectId": "iot-project-f52c7",
#   "storageBucket": "iot-project-f52c7.appspot.com",
#   "messagingSenderId": "377815157173",
#   "appId": "1:377815157173:web:905b4eb36000bd9f4cb1fc",
#   "serviceAccount": "key.json",
#   "databaseURL": "https://iot-project-f52c7-default-rtdb.asia-southeast1.firebasedatabase.app/"
# }

# firebase = pyrebase.initialize_app(config)
# storage = firebase.storage()

def handle_compress(image_name, codebook_size, vector_size):
    image_path = f"./image/origin/{image_name}"
    compress_path = f'./compress/download/{image_name[:-4]}.npz'

    # Đọc ảnh
    input_image = plt.imread(image_path)

    # Từ chối nếu đây không phải ảnh đa mức xám
    if input_image.ndim != 2:
        print(input_image.shape)
        return { "error": "This is not gray image" }

    # Xử lý nếu ảnh đã được chuẩn hóa
    if np.issubdtype(input_image.dtype, np.floating):
        input_image = (input_image * 255).astype(np.uint8)

    # Chuyển đổi kích thước ma trận ảnh
    input_height, input_width = input_image.shape
    output_height = input_height // vector_size
    output_width = input_width // vector_size

    ########### XÂY DỰNG CODEBOOK ###########
    # Chuyển đổi ma trận ảnh thành các vector ô vuông vector_size x vector_size pixel
    training_img = input_image[:output_height * vector_size, :output_width * vector_size].reshape(
        (output_height, vector_size, output_width, vector_size)
    ).transpose(0, 2, 1, 3).reshape(-1, vector_size * vector_size)

    # Tạo model VQ sử dụng thuật toán KMeans
    vq_model = KMeans(n_clusters=codebook_size, n_init=4)

    # Huấn luyện model trên dữ liệu ảnh
    vq_model.fit(training_img)

    # Lấy ra các centroids/codebook từ model đã huấn luyện
    codebook = vq_model.cluster_centers_
    codebook = np.round(codebook).astype(int)

    ########### NÉN ẢNH ###########
    compressed_img = input_image[:output_height * vector_size, :output_width * vector_size].reshape(
        (output_height, vector_size, output_width, vector_size)
    ).transpose(0, 2, 1, 3).reshape(-1, vector_size * vector_size)

    # Lấy ra index của các vector
    labels = vq_model.predict(compressed_img)

    ########### GIẢI NÉN ẢNH ###########
    # Thực hiện giải nén ảnh bằng cách thay thế mã hóa nén bằng các giá trị của centroids/codebook
    decompressed_img = np.zeros_like(compressed_img)
    for i in range(len(codebook)):
        decompressed_img[labels==i] = codebook[i]

    # Đưa ảnh đã nén về kích thước ban đầu
    decompressed_img = decompressed_img.reshape(
        (output_height, output_width, vector_size, vector_size)
    ).transpose(0, 2, 1, 3).reshape(input_image.shape)

    # image_filename = 'E:\\Tài liệu học tập\\20222\\Mã hóa dữ liệu đa phương tiện\\image-vq\\frontend\\src\\assets\\image\\results\\decompress.png'
    plt.imsave(f'./image/decompress/{image_name}', decompressed_img, cmap='gray')

    ########### XUẤT FILE NÉN ###########
    np.savez_compressed(compress_path,
                    image_type=image_name[-3:],
                    vector_size=vector_size,
                    codebook_size=codebook_size,
                    input_shape=input_image.shape,
                    compressed_shape=compressed_img.shape,
                    codebook=codebook,
                    labels=labels)

    ########### TÍNH TỶ SỐ NÉN ###########
    # # Định nghĩa số lượng vectơ đại diện trong codebook
    # num_codevectors = len(codebook)

    # # Định nghĩa số lượng bit cần thiết đã mã hóa toàn bộ index
    # bit_per_index = int(np.ceil(np.log2(num_codevectors)))

    # # Đếm số lượng label cần để mã hóa toàn bộ ảnh
    # num_labels = len(labels)

    # # Kích thước ảnh trước khi nén
    # height, width = input_image.shape
    # bit_per_pixel = 8  # Số bit cần thiết để mã hóa 256 giá trị của mỗi pixel
    # size_before_compression = height * width * bit_per_pixel

    # # Tính kích thước dữ liệu sau khi nén
    # compressed_size = num_labels * bit_per_index + codebook_size * (vector_size ** 2) * bit_per_pixel
    size_before_compression = os.path.getsize(image_path)
    compressed_size = os.path.getsize(compress_path)

    compression_ratio = (size_before_compression / compressed_size)
    compression_ratio = round(compression_ratio, 2)

    ########### TÍNH PSNR ###########
    # Chuyển đổi ma trận ảnh về kiểu dữ liệu số nguyên 8-bit
    input_image = input_image.astype(np.uint8)
    decompressed_img = decompressed_img.astype(np.uint8)

    # Tính độ lỗi bình phương trung bình (Mean Squared Error)
    mse = np.mean((input_image - decompressed_img) ** 2)

    # Tính PSNR
    max_pixel_value = 255  # Giá trị pixel tối đa
    psnr = 10 * np.log10((max_pixel_value ** 2) / mse)
    psnr = round(psnr, 2)

    return {
        "name": image_name,
        "originSize": size_before_compression,
        "compressedSize": compressed_size,
        "compressRatio": compression_ratio,
        "psnr": psnr,
    }

def handle_decompress(file_name):
    data = np.load(f'./compress/upload/{file_name}')
    image_type = data['image_type'].item()
    vector_size = data['vector_size'].item()
    codebook_size = data['codebook_size'].item()
    input_shape = tuple(data['input_shape'])
    compressed_shape = tuple(data['compressed_shape'])
    codebook = data['codebook']
    labels = data['labels']

    # Chuyển đổi kích thước ma trận ảnh
    input_height, input_width = input_shape
    output_height = input_height // vector_size
    output_width = input_width // vector_size

    # Thực hiện giải nén ảnh bằng cách thay thế mã hóa nén bằng các giá trị của centroids/codebook
    decompressed_img = np.zeros(compressed_shape, dtype=np.uint8)
    for i in range(len(codebook)):
        decompressed_img[labels==i] = codebook[i]

    # Đưa ảnh đã nén về kích thước ban đầu
    decompressed_img = decompressed_img.reshape(
        (output_height, output_width, vector_size, vector_size)
    ).transpose(0, 2, 1, 3).reshape(input_shape)

    plt.imsave(f'./image/request/{file_name[:-4]}.{image_type}', decompressed_img, cmap='gray')

    return {
        "name": f'{file_name[:-4]}.{image_type}',
        "vectorSize": vector_size,
        "codebookSize": codebook_size,
        "height": str(input_height),
        "width": str(input_width),
        "labelSize": len(labels)
    }