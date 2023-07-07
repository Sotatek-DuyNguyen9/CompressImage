import numpy as np

import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from flask import abort

# import pyrebaseE:\anaconda3\Scripts\activate base

def handle_compress(image_name, codebook_size, vector_size):
    image_path = f"./image/origin/{image_name}"
    compress_path = f'./compress/download/{image_name[:-4]}.npz'

    # Đọc ảnh
    input_image = plt.imread(image_path)

    if input_image.ndim not in [2, 3]:
        return { "error": "Invalid image" }

    channel_size = 1
    if len(input_image.shape) >= 3:
        channel_size = input_image.shape[2]
    else:
        print("Đây là ảnh đa mức xám")

    # Xử lý ảnh đã chuẩn hóa
    if np.issubdtype(input_image.dtype, np.floating):
        input_image = (input_image * 255).astype(np.uint8)

    codebook_list = []
    label_list = []

    # Tạo một ma trận zeros có kích thước giống với ảnh gốc
    decompressed_img = np.zeros_like(input_image)

    # Tách từng kênh màu
    for channel in range(channel_size):  # 3 kênh màu: R, G, B
        # Lấy kênh màu hiện tại
        if channel_size > 1:
            channel_data = input_image[:, :, channel]
        else:
            channel_data = input_image

        # Chuyển đổi kích thước ma trận ảnh
        input_height, input_width = channel_data.shape
        output_height = (input_height // vector_size) * vector_size
        output_width = (input_width // vector_size) * vector_size

        # Đối xứng gương kích thước ảnh đến kích thước chia hết cho vector_size
        channel_data = channel_data[:output_height, :output_width]

        # Chuyển đổi ma trận ảnh thành các vector ô vuông vector_size x vector_size pixel
        training_img = channel_data.reshape(
            (output_height // vector_size, vector_size, output_width // vector_size, vector_size)
        ).transpose(0, 2, 1, 3).reshape(-1, vector_size * vector_size)

        # Tạo model VQ sử dụng thuật toán KMeans
        vq_model = KMeans(n_clusters=codebook_size, n_init=4)

        # Huấn luyện model trên dữ liệu ảnh
        vq_model.fit(training_img)

        # Lấy ra các centroids/codebook từ model đã huấn luyện
        codebook = vq_model.cluster_centers_
        codebook = np.round(codebook).astype(int)

        ########### NÉN KÊNH MÀU ###########
        # Chuyển đổi ma trận ảnh thành các vector ô vuông vector_size x vector_size pixel
        compressed_channel = channel_data.reshape(
            (output_height // vector_size, vector_size, output_width // vector_size, vector_size)
        ).transpose(0, 2, 1, 3).reshape(-1, vector_size * vector_size)

        # Lấy ra index của các vector
        labels = vq_model.predict(compressed_channel)

        ########### GIẢI NÉN KÊNH MÀU ###########
        # Thực hiện giải nén kênh màu bằng cách thay thế mã hóa nén bằng cácgiá trị của centroids/codebook
        decompressed_channel = np.zeros_like(compressed_channel)
        for i in range(len(codebook)):
            decompressed_channel[labels == i] = codebook[i]

        # Đưa kênh màu đã giải nén về kích thước ban đầu
        decompressed_channel = decompressed_channel.reshape(
            (output_height // vector_size, output_width // vector_size, vector_size, vector_size)
        ).transpose(0, 2, 1, 3).reshape(output_height, output_width)

        # Ghép lại kênh màu đã giải nén vào ảnh nén hoàn chỉnh
        if channel_size > 1:
            decompressed_img[:output_height, :output_width, channel] = decompressed_channel
        else:
            decompressed_img = decompressed_channel

        codebook_list.append(codebook)
        label_list.append(labels)
    
    # Lưu ảnh đã giải nén
    plt.imsave(f'./image/decompress/{image_name}', decompressed_img, cmap='gray')

    # Xuất file nén
    np.savez_compressed(compress_path,
                    image_type=image_name[-3:],
                    channel_size=channel_size,
                    vector_size=vector_size,
                    codebook_size=codebook_size,
                    input_shape=input_image.shape,
                    codebook_list=codebook_list,
                    label_list=label_list)
    
    ########### TÍNH tỷ số nén ###########
    size_before_compression = os.path.getsize(image_path)
    compressed_size = os.path.getsize(compress_path)

    compression_ratio = (size_before_compression / compressed_size)
    compression_ratio = round(compression_ratio, 2)

    ########### TÍNH PSNR ###########
    # Chuyển đổi ma trận ảnh về kiểu dữ liệu số nguyên 8-bit
    input_image = input_image.astype(np.uint8)
    decompressed_img = decompressed_img.astype(np.uint8)

    # Tính độ lỗi bình phương trung bình (Mean Squared Error)
    mse = np.mean((input_image[:output_height, :output_width] - decompressed_img[:output_height, :output_width]) ** 2)

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
    channel_size = data['channel_size'].item()
    vector_size = data['vector_size'].item()
    codebook_size = data['codebook_size'].item()
    input_shape = tuple(data['input_shape'])
    codebook_list = data['codebook_list']
    label_list = data['label_list']

    decompressed_img = np.zeros(input_shape, dtype=np.uint8)
    for channel in range(channel_size):  # 3 kênh màu: R, G, B
        # Lấy kênh màu hiện tại
        channel_data = np.zeros(input_shape[:2], dtype=np.uint8)

        # Chuyển đổi kích thước ma trận ảnh
        input_height, input_width = channel_data.shape
        output_height = (input_height // vector_size) * vector_size
        output_width = (input_width // vector_size) * vector_size
        
        # Đối xứng gương kích thước ảnh đến kích thước chia hết cho vector_size
        channel_data = channel_data[:output_height, :output_width]

        ########### NÉN KÊNH MÀU ###########
        # Chuyển đổi ma trận ảnh thành các vector ô vuông vector_size x vector_size pixel
        compressed_channel = channel_data.reshape(
            (output_height // vector_size, vector_size, output_width // vector_size, vector_size)
        ).transpose(0, 2, 1, 3).reshape(-1, vector_size * vector_size)

        ########### GIẢI NÉN KÊNH MÀU ###########
        # Thực hiện giải nén kênh màu bằng cách thay thế mã hóa nén bằng cácgiá trị của centroids/codebook

        decompressed_channel = np.zeros_like(compressed_channel)
        for i in range(len(codebook_list[channel])):
            decompressed_channel[label_list[channel]==i] = codebook_list[channel][i]

        # Đưa kênh màu đã giải nén về kích thước ban đầu
        decompressed_channel = decompressed_channel.reshape(
            (output_height // vector_size, output_width // vector_size, vector_size, vector_size)
        ).transpose(0, 2, 1, 3).reshape(output_height, output_width)

        # Ghép lại kênh màu đã giải nén vào ảnh nén hoàn chỉnh
        if channel_size > 1:
            decompressed_img[:output_height, :output_width, channel] = decompressed_channel
        else:
            decompressed_img = decompressed_channel

    decompressed_path = f'./image/request/{file_name[:-4]}.{image_type}'

    plt.imsave(decompressed_path, decompressed_img, cmap='gray')

    decompressed_size = os.path.getsize(decompressed_path)

    return {
        "name": f'{file_name[:-4]}.{image_type}',
        "vectorSize": vector_size,
        "codebookSize": codebook_size,
        "height": str(input_height),
        "width": str(input_width),
        "channelSize": channel_size,
        "decompressedSize": decompressed_size
    }