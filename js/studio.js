document.addEventListener('DOMContentLoaded', () => {
    const loadingStatus = document.getElementById('loading-status');
    const progressPercent = document.getElementById('progress-percent');
    const previewImage = document.getElementById('preview-image');
    const exportButton = document.getElementById('export-button');

    const client = new SpriteShiftClient('YOUR_API_KEY_HERE');
    let pollingInterval;

    // Get job_id from URL
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('job_id');

    if (!jobId) {
        loadingStatus.textContent = 'Error: No job ID provided.';
        loadingStatus.style.color = 'var(--error-color)';
        return;
    }

    function startPolling() {
        pollingInterval = setInterval(async () => {
            try {
                const status = await client.getJobStatus(jobId);
                updateProgress(status);

                if (status.progress_percent === 100) {
                    clearInterval(pollingInterval);
                    showPreview(status.preview_url);
                }
            } catch (error) {
                console.error('Error polling for status:', error);
                loadingStatus.textContent = 'Error checking job status.';
                loadingStatus.style.color = 'var(--error-color)';
                clearInterval(pollingInterval);
            }
        }, 2000); // Poll every 2 seconds
    }

    function updateProgress(status) {
        progressPercent.textContent = status.progress_percent;
    }

    function showPreview(previewUrl) {
        loadingStatus.style.display = 'none';
        previewImage.src = previewUrl;
        previewImage.style.display = 'block';
        exportButton.disabled = false;
        // In a real app, we would also populate the animation list here.
    }

    exportButton.addEventListener('click', async () => {
        try {
            const formatSelect = document.getElementById('format-select');
            const resolutionSelect = document.getElementById('resolution-select');

            const format = formatSelect.value;
            const resolution = resolutionSelect.value; // In a real app, bitrate might be derived from this.

            alert('Preparing your download...');
            const result = await client.export(jobId, format, 1080, 'pro');

            // In a real app, this would trigger a download.
            alert(`Your download is ready at: ${result.url}`);
            window.open(result.url, '_blank');

        } catch (error) {
            console.error('Export failed:', error);
            alert('There was an error exporting your assets.');
        }
    });

    // Start the process
    startPolling();
});
