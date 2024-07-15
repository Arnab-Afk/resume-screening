import { useState, useEffect } from 'react';
import axios from 'axios';
import Content from './content';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [responseData, setResponseData] = useState({});
  const [uploaded, setUploaded] = useState(false);
  const [keywords, setKeywords] = useState(''); // new state for keywords
  const [content, setContent] = useState({}); // new state for content
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file.type !== 'application/pdf') {
      alert('Only PDF files are allowed');
      return;
    }
    setFile(file);
  };

  const handleUpload = () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append('pdf_file', file);
    axios.post(`https://resume-screening-chr8.onrender.com/upload_pdf?keywords=${keywords}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then((response) => {
        console.log(response);
        setContent(response.data);
        setResponseData(response.data);
        console.log(typeof(response.data));
        console.log(content);
        setUploaded(true);
        setUploading(false);
      })
      .catch((error) => {
        console.error(error);
        setUploading(false);
      });
  };
  const requirements = responseData.requirements;

  return (
    <>
      <div className='p-4'>
        <button
          type="button"
          className="relative block w-full rounded-lg border-2 border-dashed border-gray-300 p-12 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          onClick={handleUpload}
        >
          <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true" >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v20c0 4.418 7.163 8 16 8 1.381 0 2.721-.087 4-.252M8 14c0 4.418 7.163 8 16 8s16-3.582 16-8M8 14c0-4.418 7.163-8 16-8s16 3.582 16 8m0 0v14m0-4c0 4.418-7.163 8-16 8S8 28.418 8 24m32 10v6m0 0v6m0-6h6m-6 0h-6" />
          </svg>
          <span className="mt-2 block text-sm font-semibold text-gray-900">
            {uploading ? 'Uploading...' : 'Create a new database'}
          </span>
          <input
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleFileChange}
            accept="application/pdf"
          />
        </button>
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Enter keywords"
          className="mt-4 p-2 pl-5 bg-gray-100 rounded-lg"
        />
        <button
          className="ml-2 p-2 bg-blue-500 text-white rounded-lg"
          onClick={handleUpload}
        >
          Upload
        </button>
        {uploading && (
          <p className="text-sm font-semibold text-gray-900">
            Uploading...
          </p>
        )}
        {uploaded && (
          <p className="text-sm font-semibold text-gray-900">
            Parsed.. 
            <Content data={requirements} />
          </p>
        
                    
        )}
        
      </div>
    </>
  );
}

export default App;
