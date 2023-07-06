import React from 'react';
import './styles.scss';
import Compress from './components/compress';
import Decompress from './components/decompress';
import staticImage from '../../assets/image/static';

const Homepage = () => {
  const [uploadFile, setUploadFile] = React.useState(null);
  const [isCompress, setIsCompress] = React.useState(true);

  const handleChangeFile = (e, setCompress) => {
    setUploadFile(e.target.files[0]);
    setIsCompress(setCompress);
  };

  return (
    <div className="homepage">
      <h1 className="homepage__title">Nén hình ảnh trực tuyến</h1>
      <p className="homepage__description">
        Công cụ nén ảnh này sử dụng một hệ thống thông minh từ sự tối ưu hóa tốt nhất và thuật toán
        lượng tử hóa vector để nén hình ảnh JPEG, GIF và PNG thành dung lượng nhỏ nhất có thể với
        cấp độ chất lượng yêu cầu.
      </p>
      <div className="homepage__box">
        <div className="homepage__upload">
          <label className="custom-file-upload button mr">
            <input type="file" accept=".png, .jpg" onChange={(e) => handleChangeFile(e, true)} />
            <i className="fa fa-image"></i>
            <span className="button__text">Tải ảnh lên</span>
          </label>
          <label className="custom-file-upload button button_secondary">
            <input type="file" accept=".npz" onChange={(e) => handleChangeFile(e, false)} />
            <i className="fa fa-upload"></i>
            <span className="button__text">Tải tệp nén lên</span>
          </label>
        </div>
        <hr style={{ margin: '12px -12px' }} />
        {uploadFile && isCompress && <Compress uploadFile={uploadFile} />}
        {uploadFile && !isCompress && <Decompress uploadFile={uploadFile} />}
        {!uploadFile && (
          <div className="homepage__default">
            <img src={staticImage.addImage} alt="Add Image" />
            <p>Upload your image to here...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Homepage;
