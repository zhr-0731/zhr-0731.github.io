/**
 * 天气背景壁纸自动切换（带控制台日志调试）
 * 依赖：https://uapis.cn/api/v1/misc/weather（天气）
 *       https://uapis.cn/api/v1/image/bing-daily（壁纸）
 */
(function() {
    'use strict';

    // ========== 天气 → 必应壁纸日期映射 ==========
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

    // ========== 从必应 API 获取壁纸图片 URL ==========
    function fetchBingWallpaper(date) {
        const url = `https://uapis.cn/api/v1/image/bing-daily?date=${date}&format=json&resolution=4k`;
        console.log(`[天气背景] 请求必应壁纸 API: ${url}`);
        return fetch(url)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log('[天气背景] 必应壁纸 API 返回:', data);
                return data.image_url_4k || data.image_url || null;
            })
            .catch(err => {
                console.warn('[天气背景] 必应壁纸 API 请求失败:', err);
                return null;
            });
    }

    // ========== 设置背景壁纸 ==========
    function setBackground(imageUrl) {
        if (!enabled) {
            body.style.backgroundImage = 'none';
            body.style.backgroundColor = '';
            return;
        }
        const url = imageUrl || FALLBACK;
        console.log(`[天气背景] 应用壁纸: ${url}`);
        body.style.backgroundImage = `url(${url})`;
        body.style.backgroundSize = 'cover';
        body.style.backgroundPosition = 'center';
        body.style.backgroundAttachment = 'fixed';
        body.style.backgroundColor = 'rgba(0,0,0,0.3)';
        body.style.backgroundBlendMode = 'overlay';
    }

    // ========== 获取天气并应用壁纸 ==========
    function fetchWeatherAndApply() {
        if (!enabled) return;

        const weatherApi = 'https://uapis.cn/api/v1/misc/weather?extended=false&lang=zh';
        console.log(`[天气背景] 请求天气 API: ${weatherApi}`);

        fetch(weatherApi)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(weatherData => {
                console.log('[天气背景] 天气 API 返回:', weatherData);
                const weather = weatherData.weather || 'default';
                console.log(`[天气背景] 识别天气: ${weather}`);
                const date = WEATHER_BING_DATES[weather] || WEATHER_BING_DATES['default'];
                console.log(`[天气背景] 对应壁纸日期: ${date}`);
                return fetchBingWallpaper(date);
            })
            .then(imgUrl => {
                setBackground(imgUrl);
                updateToggleIcon();
            })
            .catch(err => {
                console.warn('[天气背景] 获取天气或壁纸失败，使用备用壁纸', err);
                setBackground(null);
            });
    }

    // ========== 更新开关按钮图标 ==========
    function updateToggleIcon() {
        const btn = document.getElementById('weatherToggle');
        if (!btn) return;
        btn.textContent = enabled ? '☀️' : '🚫';
        btn.title = enabled ? '点击关闭天气背景' : '点击开启天气背景';
    }

    // ========== 切换开关 ==========
    function toggleBackground() {
        enabled = !enabled;
        if (enabled) {
            console.log('[天气背景] 功能已开启');
            fetchWeatherAndApply();
        } else {
            console.log('[天气背景] 功能已关闭');
            body.style.backgroundImage = 'none';
            body.style.backgroundColor = '';
            body.style.backgroundBlendMode = 'normal';
        }
        updateToggleIcon();
    }

    // ========== 创建/绑定开关按钮 ==========
    function ensureToggleButton() {
        let btn = document.getElementById('weatherToggle');
        if (btn) return btn;
        const nav = document.querySelector('nav ul') || document.querySelector('.header-inner');
        if (!nav) {
            console.warn('[天气背景] 未找到导航栏，无法添加开关按钮');
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

    // ========== 初始化 ==========
    function init() {
        const btn = ensureToggleButton();
        if (btn) {
            btn.addEventListener('click', toggleBackground);
        }
        // 首次加载
        fetchWeatherAndApply();
        // 每小时刷新一次
        setInterval(fetchWeatherAndApply, 3600000);
        console.log('[天气背景] 脚本已初始化，查看控制台可看到API请求日志');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();