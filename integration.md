# SpriteShift AI Integration Guide

## 1. Introduction

This guide provides instructions on how to integrate the SpriteShift AI API into your JavaScript application using our lightweight client SDK.

## 2. Installation

To use the SDK, simply copy the `SpriteShiftClient` class into your project. It has no external dependencies.

## 3. JavaScript SDK (`SpriteShiftClient`)

Below is the source code for the client.

```javascript
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

        const response = await fetch(url, config);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`API request failed: ${response.statusText}`, { cause: errorData });
        }

        return response.json();
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
    }

    async getJobStatus(jobId) {
        return this.#request(`/api/job/${jobId}/status`);
    }

    async cancelJob(jobId) {
        return this.#request(`/api/job/${jobId}/cancel`, {
            method: 'POST',
        });
    }

    async export(jobId, format, bitrate, userTier) {
        return this.#request('/api/export', {
            method: 'POST',
            body: JSON.stringify({
                job_id: jobId,
                format: format,
                bitrate: bitrate,
                user_tier: userTier,
            }),
        });
    }
}
```

## 4. Usage Example

Here's how you can use the `SpriteShiftClient` to upload an image and check its status.

```javascript
// 1. Initialize the client with your API key
// For headless integrations, use an API key.
const client = new SpriteShiftClient('YOUR_API_KEY');

// For user-facing applications, you would use an OAuth token.
// const userClient = new SpriteShiftClient(null, 'USER_OAUTH_TOKEN');

// 2. Get your file from an input element
const imageInput = document.querySelector('#image-upload');
const imageFile = imageInput.files[0];

// 3. Upload the image
async function processUpload() {
    if (!imageFile) {
        console.error('Please select an image file.');
        return;
    }

    try {
        console.log('Uploading image...');
        const uploadResponse = await client.upload(imageFile, 'user-123');
        const { job_id, status_url } = uploadResponse;
        console.log(`Upload accepted! Job ID: ${job_id}`);

        // 4. Poll for status
        const pollInterval = setInterval(async () => {
            try {
                console.log('Checking job status...');
                const statusResponse = await client.getJobStatus(job_id);
                console.log(`Progress: ${statusResponse.progress_percent}%`);

                if (statusResponse.progress_percent === 100) {
                    console.log('Job complete!');
                    console.log('Preview URL:', statusResponse.preview_url);
                    clearInterval(pollInterval);

                    // 5. Export the final asset
                    const exportResult = await client.export(job_id, 'spritesheet', 1080, 'pro');
                    console.log('Export URL:', exportResult.url);
                }
            } catch (error) {
                console.error('Error checking status:', error);
                clearInterval(pollInterval);
            }
        }, 5000); // Poll every 5 seconds

    } catch (error) {
        console.error('Upload failed:', error);
    }
}

// Example of triggering the upload
// In a real app, this would be tied to a button click.
// processUpload();
```
