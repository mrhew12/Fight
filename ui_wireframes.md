# UI Wireframes for SpriteShift AI

This document describes the wireframes for the key pages of the SpriteShift AI web application.

## 1. Landing Page

The landing page is designed to be a clean, modern, and compelling funnel to encourage user sign-ups and uploads.

### 1.1. Hero Section

*   **Layout:** Full-width section at the top of the page.
*   **Content:**
    *   **Headline (H1):** "Animate Your Characters in Minutes, Not Months." (A/B Test against: "AI-Powered Sprites, Instantly.")
    *   **Sub-headline (p):** "Upload your static 2D character art and get game-ready animations powered by our advanced AI pipeline."
    *   **Primary CTA (Button):** "Try for Free" - links to the uploader section.

### 1.2. Uploader & Demo Section

*   **Layout:** Two-column layout.
*   **Left Column:**
    *   **Uploader:** A simple drag-and-drop file uploader with a button to "Choose a file".
    *   **Text:** "Supports .png and .jpg files. Max size 10MB."
*   **Right Column:**
    *   **Demo:** An interactive demo. A pre-loaded sample sticker is shown. When the user clicks a "Animate" button, it shows a loading spinner and then displays a short, looping "idle" animation of the character. This gives a direct preview of the product's capability.

### 1.3. Preview & Sample Moves Section

*   **Layout:** A gallery or carousel.
*   **Content:**
    *   Shows a larger preview of the animated sample character from the uploader.
    *   A list of "moves" (e.g., "walk", "jump", "punch", "kick"). Clicking on a move updates the preview to show that animation.
    *   This section demonstrates the variety of animations generated.

### 1.4. Pricing Tiers

*   **Layout:** A comparison table with 2-3 columns.
*   **Columns:**
    *   **Free / Hobbyist:** Lists features like 5 renders/month, 720p resolution, watermark.
    *   **Pro / Indie:** Lists features like unlimited renders, 1080p, no watermark, priority queue.
*   **CTA:** Each column has a "Sign Up" button.

### 1.5. Primary Call to Action (CTA)

*   **Layout:** A full-width, visually distinct section.
*   **Content:**
    *   **Headline (H2):** "Ready to bring your characters to life?"
    *   **Button:** "Sign Up and Upload Your First Character"

### 1.6. FAQ & Footer

*   **Layout:** A simple, clean section at the bottom of the page.
*   **Content:**
    *   **FAQ:** Accordion-style questions and answers (e.g., "What file formats are supported?", "How long does it take?").
    *   **Footer:** Links to "Terms of Service", "Privacy Policy", and "Safety Policy".

## 2. Studio / Preview Page

This page is where users see the results for their own uploaded characters.

### 2.1. Main View

*   **Layout:** A large central area for the animated preview.
*   **Content:**
    *   Displays the user's character, animated.
    *   Defaults to the "idle" animation.

### 2.2. Animation Controls

*   **Layout:** A sidebar or a panel next to the main view.
*   **Content:**
    *   A list of all generated animations (e.g., "idle", "walk", "jump").
    *   Clicking an animation name plays it in the main view.
    *   Playback controls: Play/Pause, speed control (0.5x, 1x, 2x).

### 2.3. Export & Upsell Options

*   **Layout:** A section below the animation controls.
*   **Content:**
    *   **Export Options:**
        *   Dropdown for format (e.g., "Sprite Sheet (.png)", "GIF").
        *   Dropdown for resolution (e.g., "720p").
    *   **Upsell Hook:** If the user is on the free tier, a "1080p HD" option is visible but disabled, with a "Upgrade to Pro" link next to it. This is the premium HD export upsell.
    *   **Export Button:** "Download Assets"

## 3. UX Tokens

### 3.1. Color Palette

*   **Primary:** `#4A90E2` (A friendly, accessible blue)
*   **Secondary:** `#50E3C2` (A vibrant teal for accents and highlights)
*   **Background:** `#FFFFFF` (White)
*   **Text:** `#333333` (Dark Gray)
*   **Borders/Dividers:** `#EAEAEA` (Light Gray)
*   **Success:** `#7ED321` (Green)
*   **Error:** `#D0021B` (Red)

### 3.2. Typography

*   **Font Family:** "Inter", sans-serif
*   **Type Scale:**
    *   H1: 48px
    *   H2: 36px
    *   H3: 24px
    *   Body: 16px
    *   Caption: 12px

### 3.3. Spacing

*   **Base Unit:** 8px
*   **Scale:**
    *   `xs`: 4px
    *   `sm`: 8px
    *   `md`: 16px
    *   `lg`: 24px
    *   `xl`: 32px
    *   `xxl`: 64px
