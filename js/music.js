window.BlogMusic = (function () {
    function init() {
        const backgroundMusic = document.getElementById('backgroundMusic');
        const playPauseBtnCompact = document.getElementById('playPauseBtnCompact');
        const musicTitle = document.getElementById('musicTitleCompact');
        
        if (!backgroundMusic || !playPauseBtnCompact || !musicTitle) return;

        // 初始化状态
        playPauseBtnCompact.classList.remove('playing');
        musicTitle.textContent = '点击播放';

        // 主源 (HTTPS m3u8)
        const primarySrc = "https://rscdn.ajmide.com/r_1700/nglive_1700.m3u8";
        // 备用源 (HTTPS mp3)
        const fallbackSrc = "https://zhr-0731.github.io/Music-file/Reach%20Me%20-%20Track%20in%20Time%20(%E7%BA%AF%E9%92%A2%E7%90%B4).mp3";

        function setupAutoplay() {
            const playPromise = backgroundMusic.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    playPauseBtnCompact.classList.add('playing');
                    musicTitle.textContent = '金鹰955';
                }).catch(() => {
                    playPauseBtnCompact.classList.remove('playing');
                    musicTitle.textContent = '点击播放';
                });
            }
        }
        
        // 延迟尝试自动播放
        setTimeout(setupAutoplay, 500);

        // 按钮点击事件
        playPauseBtnCompact.addEventListener('click', function () {
            if (backgroundMusic.paused) {
                backgroundMusic.play().then(() => {
                    this.classList.add('playing');
                    musicTitle.textContent = '金鹰955';
                }).catch((err) => {
                    console.error('播放失败:', err);
                    musicTitle.textContent = '播放受阻，重试或换源';
                });
            } else {
                backgroundMusic.pause();
                this.classList.remove('playing');
                musicTitle.textContent = '已暂停';
            }
        });

        backgroundMusic.addEventListener('play', function () {
            playPauseBtnCompact.classList.add('playing');
            musicTitle.textContent = '金鹰955';
        });
        
        backgroundMusic.addEventListener('pause', function () {
            playPauseBtnCompact.classList.remove('playing');
            musicTitle.textContent = '已暂停';
        });

        // 核心降级逻辑：如果主源加载失败，自动切到备用 MP3 源
        backgroundMusic.addEventListener('error', function () {
            console.warn('主音频(主源)加载失败，尝试切换备用源...');
            playPauseBtnCompact.classList.remove('playing');
            musicTitle.textContent = '切换备用源...';

            // 如果当前不是备用源，则替换为备用源
            if (!backgroundMusic.src.includes('Music-file')) {
                backgroundMusic.innerHTML = `<source src="${fallbackSrc}" type="audio/mpeg">`;
                backgroundMusic.load();
                
                // 替换后尝试播放
                backgroundMusic.play().then(() => {
                    playPauseBtnCompact.classList.add('playing');
                    musicTitle.textContent = '备用源播放中';
                }).catch(() => {
                    musicTitle.textContent = '点击播放';
                });
            } else {
                musicTitle.textContent = '音频加载失败';
                playPauseBtnCompact.disabled = true;
                playPauseBtnCompact.style.opacity = '0.5';
            }
        });
    }

    return { init };
})();