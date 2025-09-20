---
hide:
 - navigation
 - toc
---

<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
  
  /* Example carousel styles */
  .examples-container {
    position: relative;
    margin: 2rem 0;
  }
  
  .examples-carousel {
    position: relative;
    overflow: hidden;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background: white;
  }
  
  .examples-slides {
    display: flex;
    transition: transform 0.3s ease;
  }
  
  .example-slide {
    min-width: 100%;
  }
  
  .example-slide iframe {
    width: 100%;
    min-height: 80vh;
    border: none;
    display: block;
  }
  
  .example-info {
    background: white;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 0;
  }
  
  .example-title {
    font-size: 1.1rem;
    font-weight: 500;
    margin: 0;
    color: #333;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  .example-description {
    font-size: 0.9rem;
    color: #757575;
    margin: 0.3rem 0 0 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  /* Navigation controls */
  .carousel-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1rem;
    padding: 0 0.5rem;
  }
  
  .nav-button {
    background: white;
    color: #1976d2;
    border: 1px solid #e0e0e0;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  .nav-button:hover {
    background: #f5f5f5;
    border-color: #1976d2;
  }
  
  .nav-button:disabled {
    background: #fafafa;
    color: #bdbdbd;
    border-color: #e0e0e0;
    cursor: not-allowed;
  }
  
  .nav-button:disabled:hover {
    background: #fafafa;
    border-color: #e0e0e0;
  }
  
  /* Dots indicator */
  .carousel-dots {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e0e0e0;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .dot.active {
    background: #1976d2;
    transform: scale(1.3);
  }
  
  .dot:hover {
    background: #1976d2;
  }
  
  /* Counter */
  .carousel-counter {
    color: #757575;
    font-size: 0.875rem;
    font-weight: 400;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  /* Responsive design */
  @media (max-width: 768px) {
    .carousel-nav {
      flex-direction: column;
      gap: 1rem;
    }
    
    .nav-button {
      padding: 0.6rem 1.2rem;
      font-size: 0.8rem;
    }
    
    .example-slide iframe {
      min-height: 60vh;
    }
  }
</style>

## [Vid2Txt](https://github.com/ahmedsalim3/vid2txt)

A Python package for transcribing videos/audios to text using various speech-to-text services. Currently supports AssemblyAI for high-quality transcription.

## Features

- Download and transcribe from YouTube or any URL (via `yt-dlp`)
- Extract audio from video files using `FFmpeg`
- Direct support for audio formats (MP3, WAV, M4A, AAC, FLAC, OGG, WMA)
- Transcribe audio using AssemblyAI API
- Export transcripts in multiple formats:
    - Plain text (.txt)
    - SubRip subtitles (.srt)
    - Interactive HTML (.html) with embedded video/audio player
- Language forcing support

## Examples

<div class="examples-container">
  <div class="carousel-nav">
    <button class="nav-button" id="prevBtn" onclick="changeSlide(-1)">
      ← Previous
    </button>
    
    <div style="display: flex; align-items: center; gap: 1rem;">
      <div class="carousel-dots" id="dotsContainer"></div>
      <span class="carousel-counter">
        <span id="currentSlide">1</span> of <span id="totalSlides">3</span>
      </span>
    </div>
    
    <button class="nav-button" id="nextBtn" onclick="changeSlide(1)">
      Next →
    </button>
  </div>
  <div class="examples-carousel">
    <div class="examples-slides" id="examplesSlides">
      
      <div class="example-slide">
        <div class="example-info">
          <h3 class="example-title">Arabic Video</h3>
          <p class="example-description">Transcription of an Arabic news with RTL text support</p>
        </div>
        <iframe src="./examples/arabic/arabic_example.html"></iframe>
      </div>
      
      <div class="example-slide">
        <div class="example-info">
          <h3 class="example-title">Rick Astley - Never Gonna Give You Up</h3>
          <p class="example-description">Classic YouTube video transcription with subtitles</p>
        </div>
        <iframe src="./examples/english/rick_astley_example.html"></iframe>
      </div>
      
      <div class="example-slide">
        <div class="example-info">
          <h3 class="example-title">Assembly AI</h3>
          <p class="example-description">Overview video on Assembly AI</p>
        </div>
        <iframe src="./examples/assemblyai/assemblyai.html"></iframe>
      </div>
      
    </div>
  </div>
</div>

<script>
let currentSlideIndex = 0;
const totalSlides = 3;

// Initialize dots
function initializeDots() {
  const dotsContainer = document.getElementById('dotsContainer');
  for (let i = 0; i < totalSlides; i++) {
    const dot = document.createElement('div');
    dot.className = 'dot';
    if (i === 0) dot.classList.add('active');
    dot.addEventListener('click', () => goToSlide(i));
    dotsContainer.appendChild(dot);
  }
}

// Update slide position
function updateSlides() {
  const slides = document.getElementById('examplesSlides');
  const translateX = -currentSlideIndex * 100;
  slides.style.transform = `translateX(${translateX}%)`;
  
  // Update counter
  document.getElementById('currentSlide').textContent = currentSlideIndex + 1;
  
  // Update dots
  document.querySelectorAll('.dot').forEach((dot, index) => {
    dot.classList.toggle('active', index === currentSlideIndex);
  });
  
  // Update button states
  document.getElementById('prevBtn').disabled = currentSlideIndex === 0;
  document.getElementById('nextBtn').disabled = currentSlideIndex === totalSlides - 1;
}

// Change slide function
function changeSlide(direction) {
  const newIndex = currentSlideIndex + direction;
  if (newIndex >= 0 && newIndex < totalSlides) {
    currentSlideIndex = newIndex;
    updateSlides();
  }
}

// Go to specific slide
function goToSlide(index) {
  if (index >= 0 && index < totalSlides) {
    currentSlideIndex = index;
    updateSlides();
  }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') {
    changeSlide(-1);
  } else if (e.key === 'ArrowRight') {
    changeSlide(1);
  }
});

// Touch/swipe support
let touchStartX = 0;
let touchEndX = 0;

document.getElementById('examplesSlides').addEventListener('touchstart', (e) => {
  touchStartX = e.changedTouches[0].screenX;
});

document.getElementById('examplesSlides').addEventListener('touchend', (e) => {
  touchEndX = e.changedTouches[0].screenX;
  handleSwipe();
});

function handleSwipe() {
  const swipeThreshold = 50;
  const diff = touchStartX - touchEndX;
  
  if (Math.abs(diff) > swipeThreshold) {
    if (diff > 0) {
      changeSlide(1); // Swipe left - next slide
    } else {
      changeSlide(-1); // Swipe right - previous slide
    }
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  initializeDots();
  updateSlides();
});
</script>
