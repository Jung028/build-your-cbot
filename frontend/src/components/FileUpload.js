import React, { useState } from 'react';

const FileUpload = () => {
    const [uploadedFiles, setUploadedFiles] = useState([]); // Initialize with an empty array
    const [message, setMessage] = useState("");  // State to store message from the backend
    const [isProcessing, setIsProcessing] = useState(false);  // State to track the processing status

    const handleFileUpload = async (event) => {
        const files = event.target.files;
        const formData = new FormData();
        
        // Append files to form data
        Array.from(files).forEach(file => formData.append('documents', file));

        setIsProcessing(true);  // Start processing
        setMessage("");  // Clear any previous messages

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            console.log('Backend response:', result);

            // Check for the success message and files in the response
            if (result.message) {
                setMessage(result.message);  // Display the success message
            } else {
                setMessage("Documents processed, but no message returned from backend.");
            }

            // Ensure that "files" is an array and process it
            if (result.files && Array.isArray(result.files)) {
                setUploadedFiles(result.files); // Set files from the response
            } else {
                console.error('Expected "files" to be an array:', result.files);
                setUploadedFiles([]); // If not an array, set to empty array
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            setUploadedFiles([]); // In case of error, clear the state
            setMessage("Error uploading files. Please try again."); // Set error message
        } finally {
            setIsProcessing(false);  // End processing
        }
    };

    return (
        <div>
            <input type="file" multiple onChange={handleFileUpload} />
            
            {/* Show processing indicator */}
            {isProcessing && <p>Processing files, please wait...</p>}
            
            <div>
                {/* Display success/error message */}
                {message && <p>{message}</p>}
                
                <h3>Uploaded Files:</h3>
                {/* Ensure uploadedFiles is defined and is an array before mapping */}
                {uploadedFiles && Array.isArray(uploadedFiles) && uploadedFiles.length > 0 ? (
                    uploadedFiles.map((file, index) => {
                        const fileName = file.split('/').pop();  // Extracts the file name from the path
                        return <div key={index}>{fileName}</div>;
                    })
                ) : (
                    <p>No files uploaded yet.</p>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
