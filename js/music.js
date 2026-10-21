window.BlogMusic = (function () {
    function init() {
        const backgroundMusic = document.getElementById('backgroundMusic');
        const playPauseBtnCompact = document.getElementById('playPauseBtnCompact');
        const musicTitle = document.getElementById('musicTitleCompact');
        if (!backgroundMusic || !playPauseBtnCompact || !musicTitle) return;

        function setupAutoplay() {
            const playPromise = backgroundMusic.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    playPauseBtnCompact.classList.add('playing');
                    musicTitle.textContent = '金鹰955';
                }).catch(() => {
                    playPauseBtnCompact.classList.remove('playing');
                    musicTitle.textContent = '金鹰955';
                });
            }
        }
        setTimeout(setupAutoplay, 500);

        playPauseBtnCompact.addEventListener('click', function () {
            if (backgroundMusic.paused) {
                backgroundMusic.play().then(() => {
                    this.classList.add('playing');
                    musicTitle.textContent = '金鹰955';
                }).catch(() => {
                    musicTitle.textContent = '播放失败，点击重试';
                });
            } else {
                backgroundMusic.pause();
                this.classList.remove('playing');
                musicTitle.textContent = '金鹰955';
            }
        });

        backgroundMusic.addEventListener('play', function () {
            playPauseBtnCompact.classList.add('playing');
            musicTitle.textContent = '金鹰955';
        });
        backgroundMusic.addEventListener('pause', function () {
            playPauseBtnCompact.classList.remove('playing');
            musicTitle.textContent = '金鹰955';
        });
        backgroundMusic.addEventListener('ended', function () {
            playPauseBtnCompact.classList.remove('playing');
            musicTitle.textContent = '播放结束，点击重播';
        });
        backgroundMusic.addEventListener('error', function () {
            playPauseBtnCompact.disabled = true;
            musicTitle.textContent = '音频加载失败';
            backgroundMusic.innerHTML = '<source src="https://bgithub.xyz/zhr-0731/Music-file/raw/refs/heads/main/Reach%20Me%20-%20Track%20in%20Time%20(%E7%BA%AF%E9%92%A2%E7%90%B4).mp3" type="audio/mpeg">';
            backgroundMusic.load();
            musicTitle.textContent = '切换到备用音频';
        });
    }

    return { init };
})();