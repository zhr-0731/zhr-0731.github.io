/**
 * 天气背景壁纸自动切换（修复版）
 * 依赖：https://uapis.cn/api/v1/image/bing-daily
 */
(function() {
    'use strict';

    const WEATHER_BING_DATES = {
        '晴': '2026-07-10',
        '多云': '2026-06-21',
        '阴': '2026-06-22',
        '小雨': '2026-06-22',
        '中雨': '2026-06-22',
        '大雨': '2026-06-22',
        '雷阵雨': '2026-05-04',
        '小雪': '2025-12-20',
        '中雪': '2025-12-20',
        '大雪': '2025-12-20',
        '雨夹雪': '2026-06-23',
        '雾': '2023-12-07',
        '霾': '2026-06-23',
        '沙尘': '2026-05-14',
        'default': '2026-06-13'
    };

    const FALLBACK = 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920&q=80';

    let enabled = true;
    const body = document.body;

    function fetchBingWallpaper(date) {
        const url = `https://uapis.cn/api/v1/image/bing-daily?date=${date}&format=json&resolution=4k`;
        return fetch(url)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                // 优先取 4K 链接
                return data.image_url_4k || data.image_url || null;
            });
    }

    function setBackground(imageUrl) {
        if (!enabled) {
            body.style.backgroundImage = 'none';
            body.style.backgroundColor = '';
            return;
        }
        const url = imageUrl || FALLBACK;
        body.style.backgroundImage = `url(${url})`;
        body.style.backgroundSize = 'cover';
        body.style.backgroundPosition = 'center';
        body.style.backgroundAttachment = 'fixed';
        body.style.backgroundColor = 'rgba(0,0,0,0.3)';
        body.style.backgroundBlendMode = 'overlay';
    }

    function fetchWeatherAndApply() {
        if (!enabled) return;
        const weatherApi = 'https://uapis.cn/api/v1/misc/weather?extended=false&lang=zh';
        fetch(weatherApi)
            .then(res => res.json())
            .then(weatherData => {
                const weather = weatherData.weather || 'default';
                const date = WEATHER_BING_DATES[weather] || WEATHER_BING_DATES['default'];
                return fetchBingWallpaper(date);
            })
            .then(imgUrl => {
                setBackground(imgUrl);
                updateToggleIcon();
            })
            .catch(err => {
                console.warn('[天气背景] 错误，使用备用壁纸', err);
                setBackground(null);
            });
    }

    function updateToggleIcon() {
        const btn = document.getElementById('weatherToggle');
        if (!btn) return;
        btn.textContent = enabled ? '☀️' : '🚫';
        btn.title = enabled ? '点击关闭天气背景' : '点击开启天气背景';
    }

    function toggleBackground() {
        enabled = !enabled;
        if (enabled) {
            fetchWeatherAndApply();
        } else {
            body.style.backgroundImage = 'none';
            body.style.backgroundColor = '';
            body.style.backgroundBlendMode = 'normal';
        }
        updateToggleIcon();
    }

    function ensureToggleButton() {
        let btn = document.getElementById('weatherToggle');
        if (btn) return btn;
        const nav = document.querySelector('nav ul') || document.querySelector('.header-inner');
        if (!nav) {
            console.warn('[天气背景] 未找到导航栏');
            return null;
        }
        const li = document.createElement('li');
        li.style.listStyle = 'none';
        li.style.marginLeft = '10px';
        li.innerHTML = `<button id="weatherToggle" style="background:none;border:none;color:inherit;cursor:pointer;font-size:1.2rem;">☀️</button>`;
        if (nav.tagName === 'UL') {
            nav.appendChild(li);
        } else {
            const ul = nav.querySelector('ul');
            if (ul) ul.appendChild(li);
            else nav.appendChild(li);
        }
        return document.getElementById('weatherToggle');
    }

    function init() {
        const btn = ensureToggleButton();
        if (btn) {
            btn.addEventListener('click', toggleBackground);
        }
        fetchWeatherAndApply();
        setInterval(fetchWeatherAndApply, 3600000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();