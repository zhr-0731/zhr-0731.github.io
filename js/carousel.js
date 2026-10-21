window.BlogCarousel = (function () {
    class Carousel {
        constructor(containerId) {
            this.container = document.getElementById(containerId);
            this.slides = this.container.querySelectorAll('.carousel-slide');
            this.indicators = this.container.querySelectorAll('.indicator');
            this.prevBtn = this.container.querySelector('.prev-btn');
            this.nextBtn = this.container.querySelector('.next-btn');
            this.currentIndex = 0;
            this.totalSlides = this.slides.length;
            this.autoSlideInterval = null;
            this.autoSlideDuration = 5000;
            if (this.totalSlides === 0) return;
            this.init();
        }
        init() {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
            this.nextBtn.addEventListener('click', () => this.nextSlide());
            this.indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', () => this.goToSlide(index));
            });
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') this.prevSlide();
                if (e.key === 'ArrowRight') this.nextSlide();
            });
            this.container.addEventListener('mouseenter', () => this.stopAutoSlide());
            this.container.addEventListener('mouseleave', () => this.startAutoSlide());
            this.startAutoSlide();
        }
        updateSlide() {
            this.slides.forEach((slide, index) => {
                slide.classList.toggle('active', index === this.currentIndex);
            });
            this.indicators.forEach((indicator, index) => {
                indicator.classList.toggle('active', index === this.currentIndex);
            });
        }
        nextSlide() {
            this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
            this.updateSlide();
            this.resetAutoSlide();
        }
        prevSlide() {
            this.currentIndex = (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
            this.updateSlide();
            this.resetAutoSlide();
        }
        goToSlide(index) {
            if (index >= 0 && index < this.totalSlides) {
                this.currentIndex = index;
                this.updateSlide();
                this.resetAutoSlide();
            }
        }
        startAutoSlide() {
            this.stopAutoSlide();
            this.autoSlideInterval = setInterval(() => this.nextSlide(), this.autoSlideDuration);
        }
        stopAutoSlide() {
            if (this.autoSlideInterval) {
                clearInterval(this.autoSlideInterval);
                this.autoSlideInterval = null;
            }
        }
        resetAutoSlide() {
            this.stopAutoSlide();
            this.startAutoSlide();
        }
    }

    return { Carousel };
})();