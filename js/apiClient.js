class SpriteShiftClient {
    constructor(apiKey, oauthToken = null) {
        this.apiKey = apiKey;
        this.oauthToken = oauthToken;
        this.baseUrl = 'https://api.spriteshift.ai/v1';
    }

    async #request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        } else if (this.oauthToken) {
            headers['Authorization'] = `Bearer ${this.oauthToken}`;
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API request failed: ${response.statusText}`, { cause: errorData });
            }

            // Handle cases where the response might not have a body
            if (response.status === 204 || response.headers.get('content-length') === '0') {
                return null;
            }

            return response.json();
        } catch (error) {
            console.error("API Request Error:", error);
            throw error;
        }
    }

    async upload(imageFile, userId, metadata = {}) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('user_id', userId);
        formData.append('metadata', JSON.stringify(metadata));

        const endpoint = '/api/upload';
        const url = `${this.baseUrl}${endpoint}`;

        const headers = {};
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Upload failed: ${response.statusText}`, { cause: errorData });
            }

            return response.json();
        } catch (error) {
            console.error("Upload Error:", error);
            throw error;
        }
    }

    async getJobStatus(jobId) {
        // Mocking the response for testing purposes as the API is not live.
        // In a real scenario, the #request method would be called.
        console.log(`Checking job status for ${jobId}`);

        // Simulate progress
        let progress = parseInt(sessionStorage.getItem(`progress_${jobId}`) || "0");
        progress += 25;
        if (progress > 100) {
            progress = 100;
        }
        sessionStorage.setItem(`progress_${jobId}`, progress);

        const response = {
            progress_percent: progress,
            preview_url: null,
        };

        if (progress === 100) {
            response.preview_url = "https://placehold.co/400x400/7ED321/FFFFFF?text=Animation\nReady!";
        }

        return Promise.resolve(response);
        // return this.#request(`/api/job/${jobId}/status`);
    }

    async cancelJob(jobId) {
        return this.#request(`/api/job/${jobId}/cancel`, {
            method: 'POST',
        });
    }

    async export(jobId, format, bitrate, userTier) {
        console.log(`Exporting job ${jobId} with format ${format}`);
        // Mock response for export
        return Promise.resolve({
            url: "https://example.com/exported_asset.zip"
        });
        /*
        return this.#request('/api/export', {
            method: 'POST',
            body: JSON.stringify({
                job_id: jobId,
                format: format,
                bitrate: bitrate,
                user_tier: userTier,
            }),
        });
        */
    }
}
