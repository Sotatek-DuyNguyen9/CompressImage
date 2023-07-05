import axios from 'axios';

const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post('http://localhost:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log(response.data);
  } catch (error) {
    console.error(error);
  }
};

const downloadFile = async () => {
    try {
      const response = await axios.get('http://localhost:5000/download', {
        responseType: 'blob',
      });
  
      // Tạo đường dẫn URL từ phản hồi
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Tạo một thẻ a để tải file về
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'filetest.jpg');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error(error);
    }
};

// Sự kiện khi người dùng chọn file
const handleFileChange = (event) => {
  const file = event.target.files[0];
  uploadFile(file);
};

const imageSrc = 'http://localhost:5000/image/lena.jpg';

// Render component
const TestComponent = () => {
  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={downloadFile} className="btn btn-primary">Download file</button>
      <img src={imageSrc} alt="Image" />
    </div>
  );
};

export default TestComponent;
