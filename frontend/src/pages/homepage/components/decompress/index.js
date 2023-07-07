import React from "react";
import axios from "axios";
import "./styles.scss";

const units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

function niceBytes(x) {
  let l = 0,
    n = parseInt(x, 10) || 0;
  while (n >= 1024 && ++l) {
    n = n / 1024;
  }
  return n.toFixed(n < 10 && l > 0 ? 1 : 0) + ' ' + units[l];
}

const Decompress = ({ uploadFile }) => {
  const [results, setResults] = React.useState();
  const [loading, setLoading] = React.useState(false);

  const handleDecompressImage = async () => {
    setLoading(true);

    //Add file to packet
    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const resultCompress = await axios.post(
        `http://localhost:5000/api/decompress?name=${uploadFile.name}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(resultCompress.data);
      setResults(resultCompress.data);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  const handleDownloadDecompressFile = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/download?name=${results?.name}&operation=decompress`, {
        responseType: 'blob',
      });
  
      // Tạo đường dẫn URL từ phản hồi
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Tạo một thẻ a để tải file về
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', results?.name);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error(error);
    }
  }

  React.useEffect(() => {
    handleDecompressImage()
  }, [uploadFile])

  return (
    <div className="compress">
          <div className="compress__comparison">
            {loading ? (
              <div className="d-flex">
                <div
                  className="spinner-border text-primary"
                  style={{ width: "3rem", height: "3rem", margin: "auto" }}
                  role="status"
                >
                  <span className="sr-only">Loading...</span>
                </div>
              </div>
            ) : (
              <img src={`http://localhost:5000/image/request/${results?.name}`}/>
            )}
          </div>
          <div className="compress__custom">
            <div className="mb-3">
              <label htmlFor="exampleFormControlInput1" className="form-label">
                Kích thước vector
              </label>
              <input
                type="number"
                className="form-control"
                value={results?.vectorSize || 0}
                disabled
                placeholder="Nhập kích thước vector"
              />
            </div>
            <div className="mb-3">
              <label
                htmlFor="exampleFormControlTextarea1"
                className="form-label"
              >
                Kích thước codebook
              </label>
              <input
                type="number"
                className="form-control"
                value={results?.codebookSize || 0}
                disabled
                placeholder="Nhập kích thước codebook"
              />
            </div>
            <div className="mb-3">
              <label
                htmlFor="exampleFormControlTextarea1"
                className="form-label"
              >
                Chiều cao ảnh
              </label>
              <input
                type="number"
                className="form-control"
                value={results?.height || 0}
                disabled
              />
            </div>
            <div className="mb-3">
              <label
                htmlFor="exampleFormControlTextarea1"
                className="form-label"
              >
                Chiều rộng ảnh
              </label>
              <input
                type="number"
                className="form-control"
                value={results?.width || 0}
                disabled
              />
            </div>
            <div className="mb-3">
              <label
                htmlFor="exampleFormControlTextarea1"
                className="form-label"
              >
                Kích thước ảnh mới
              </label>
              <input
                type="text"
                className="form-control"
                value={niceBytes(results?.decompressedSize) || 0}
                disabled
              />
            </div>
            <button
                className="btn btn-primary"
                onClick={handleDownloadDecompressFile}
              >
                Tải file ảnh
            </button>
          </div>
        </div>
  );
};

export default Decompress;
