import React from 'react';
import axios from 'axios';
import { Slider, Switch } from 'antd';

import './styles.scss';
import ReactCompareImage from 'react-compare-image';

const units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

const marks = {
  0: {
    value: {
      vector: 4,
      codebook: 8,
    },
    label: <p style={{ marginLeft: '12px' }}>Thấp</p>,
  },
  25: {
    value: {
      vector: 4,
      codebook: 16,
    },
    label: <p style={{ marginLeft: '12px' }}></p>,
  },
  50: {
    value: {
      vector: 2,
      codebook: 16,
    },
    label: <p style={{ marginLeft: '12px', color: 'black' }}>Vừa</p>,
  },
  75: {
    value: {
      vector: 2,
      codebook: 32,
    },
    label: <p style={{ marginLeft: '12px' }}></p>,
  },
  100: {
    value: {
      vector: 2,
      codebook: 64,
    },
    label: <p style={{ marginLeft: '12px', color: 'black' }}>Cao</p>,
  },
};

function niceBytes(x) {
  let l = 0,
    n = parseInt(x, 10) || 0;
  while (n >= 1024 && ++l) {
    n = n / 1024;
  }
  return n.toFixed(n < 10 && l > 0 ? 1 : 0) + ' ' + units[l];
}

const Compress = ({ uploadFile }) => {
  const [results, setResults] = React.useState();
  const [imageName, setImageName] = React.useState('');
  const [leftImage, setLeftImage] = React.useState('');
  const [rightImage, setRightImage] = React.useState('');
  const [vectorSize, setVectorSize] = React.useState(2);
  const [codebookSize, setCodebookSize] = React.useState(16);
  const [loading, setLoading] = React.useState(false);
  const [isAdvanToggle, setIsAdvanToggle] = React.useState(false);
  const [rangeValue, setRangValue] = React.useState(50);
  console.log(vectorSize, codebookSize);
  const handleCompressImage = async () => {
    setLoading(true);

    //Add file to packet
    const formData = new FormData();
    formData.append('file', uploadFile);

    //Create file name
    let fileName = uploadFile.name;
    fileName = fileName.slice(0, -4) + Math.random() + fileName.slice(-4);

    setImageName(fileName);
    setLeftImage(`http://localhost:5000/image/origin/${fileName}`);
    setRightImage(`http://localhost:5000/image/decompress/${fileName}`);

    try {
      const resultCompress = await axios.post(
        `http://localhost:5000/api/compress?name=${fileName}&codebookSize=${codebookSize}&vectorSize=${vectorSize}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setResults(resultCompress?.data);
    } catch (error) {
      console.error(error);
      alert(error.response?.data.error);
    }

    setLoading(false);
  };

  const handleSlide = (e) => {
    setVectorSize(marks[e].value.vector);
    setCodebookSize(marks[e].value.codebook);
    setRangValue(e);
    // handleCompressImage();
  };

  const handleSwitch = () => {
    setIsAdvanToggle(!isAdvanToggle);
    if (isAdvanToggle) {
      setCodebookSize(16);
      setVectorSize(2);
      setRangValue(50);
    }
  };

  const handleDownloadCompressFile = async () => {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/download?name=${imageName}&operation=compress`,
        {
          responseType: 'blob',
        }
      );

      // Tạo đường dẫn URL từ phản hồi
      const url = window.URL.createObjectURL(new Blob([response.data]));

      // Tạo một thẻ a để tải file về
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${imageName.slice(0, -4)}.npz`);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error(error);
    }
  };

  React.useEffect(() => {
    handleCompressImage();
  }, [uploadFile]);

  return (
    <div className="compress">
      <div className="compress__comparison">
        {loading ? (
          <div className="d-flex">
            <div
              className="spinner-border text-primary"
              style={{ width: '3rem', height: '3rem', margin: 'auto' }}
              role="status"
            >
              <span className="sr-only">Loading...</span>
            </div>
          </div>
        ) : (
          <ReactCompareImage
            className="comparision"
            leftImage={leftImage}
            rightImage={rightImage}
          />
        )}
      </div>
      <div className="compress__custom">
        <Switch
          className="switch"
          checkedChildren="Nâng cao"
          unCheckedChildren="Cơ bản"
          onChange={handleSwitch}
        />

        {isAdvanToggle ? (
          <>
            <div className="mb-3">
              <label htmlFor="exampleFormControlInput1" className="form-label">
                Kích thước vector
              </label>
              <input
                type="number"
                className="form-control"
                value={vectorSize}
                min={2}
                max={8}
                required
                onChange={(e) => setVectorSize(e.target.value)}
                placeholder="Nhập kích thước vector"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="exampleFormControlTextarea1" className="form-label">
                Kích thước codebook
              </label>
              <input
                type="number"
                className="form-control"
                value={codebookSize}
                onChange={(e) => setCodebookSize(e.target.value)}
                min={4}
                max={64}
                required
                placeholder="Nhập kích thước codebook"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="exampleFormControlTextarea1" className="form-label">
                Tỷ số nén
              </label>
              <input
                type="number"
                className="form-control"
                value={results?.compressRatio || 0}
                disabled
              />
            </div>
            <div className="mb-3">
              <label htmlFor="exampleFormControlTextarea1" className="form-label">
                PSNR
              </label>
              <input type="number" className="form-control" value={results?.psnr || 0} disabled />
            </div>
          </>
        ) : (
          <>
            <p style={{ fontWeight: '700' }}>Độ phân giải ảnh sau khi nén:</p>
            <Slider
              vertical
              marks={marks}
              step={null}
              defaultValue={50}
              style={{
                height: '50%',
                margin: '20px 60px 40px',
              }}
              onChange={(e) => handleSlide(e)}
              value={rangeValue}
            />
          </>
        )}

        <div className="compress">
          <div className="mb-3">
            <label htmlFor="exampleFormControlTextarea1" className="form-label">
              Kích thước file ảnh
            </label>
            <input
              type="text"
              className="form-control"
              value={niceBytes(results?.originSize || 0)}
              disabled
            />
          </div>
          <div className="mb-3">
            <label htmlFor="exampleFormControlTextarea1" className="form-label">
              Kích thước file nén
            </label>
            <input
              type="text"
              className="form-control"
              value={niceBytes(results?.compressedSize || 0)}
              disabled
            />
          </div>
        </div>

        <div className="action">
          <button className="btn btn-primary" onClick={() => handleCompressImage()}>
            Xem trước
          </button>
          <button className="btn btn-primary" onClick={handleDownloadCompressFile}>
            Tải file nén
          </button>
        </div>
      </div>
    </div>
  );
};

export default Compress;
