document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const imageUploadInput = document.getElementById('image-upload');
    const uploadStatus = document.getElementById('upload-status');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('highlight'), false);
    });

    // Handle dropped files
    uploadArea.addEventListener('drop', handleDrop, false);

    // Handle file selection via button
    imageUploadInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    }

    async function handleFileUpload(file) {
        if (!file.type.startsWith('image/')) {
            uploadStatus.textContent = 'Error: Please upload an image file (.png, .jpg).';
            uploadStatus.style.color = 'var(--error-color)';
            return;
        }

        uploadStatus.textContent = 'Uploading...';
        uploadStatus.style.color = 'var(--text-color)';

        // Initialize the API client
        // In a real app, the API key would be stored securely.
        const client = new SpriteShiftClient('YOUR_API_KEY_HERE');

        try {
            // Mocking the user ID for now
            const response = await client.upload(file, 'user-123');

            // The real API call is mocked in apiClient.js for now.
            // For testing, we'll manually create a mock job_id.
            const mockJobId = "job-" + Date.now();
            sessionStorage.removeItem(`progress_${mockJobId}`); // Clear previous progress

            uploadStatus.textContent = 'Upload successful! Redirecting...';
            uploadStatus.style.color = 'var(--success-color)';

            // Redirect to the studio page with the job ID
            window.location.href = `studio.html?job_id=${mockJobId}`;

        } catch (error) {
            console.error('Upload failed:', error);
            uploadStatus.textContent = `Upload failed: ${error.message}`;
            uploadStatus.style.color = 'var(--error-color)';
        }
    }
});
