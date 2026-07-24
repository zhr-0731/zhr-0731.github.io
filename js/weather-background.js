/**
 * 天气背景壁纸自动切换
 * 根据用户所在位置的天气，自动更换为对应的必应每日壁纸
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

    // ========== 强制设置背景（通过注入 style 标签） ==========
    function setBackground(imageUrl) {
        const url = imageUrl || FALLBACK;
        // 移除旧的背景 style
        const oldStyle = document.getElementById('dynamic-bg-style');
        if (oldStyle) oldStyle.remove();

        // 创建新的 style 标签，使用 !important 强制覆盖
        const style = document.createElement('style');
        style.id = 'dynamic-bg-style';
        style.textContent = `
            body {
                background-image: url(${url}) !important;
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
                background-color: #0a0a0f !important;
            }
        `;
        document.head.appendChild(style);
        console.log('[天气背景] 已注入背景图片:', url);
    }

    // ========== 从必应 API 获取壁纸图片 URL ==========
    function fetchBingWallpaper(date) {
        const url = `https://uapis.cn/api/v1/image/bing-daily?date=${date}&format=json&resolution=4k`;
        console.log('[天气背景] 请求壁纸 API:', url);
        return fetch(url)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log('[天气背景] 壁纸 API 返回:', data);
                return data.image_url_4k || data.image_url || null;
            })
            .catch(err => {
                console.warn('[天气背景] 壁纸请求失败，使用备用', err);
                return null;
            });
    }

    // ========== 获取天气并应用壁纸 ==========
    function fetchWeatherAndApply() {
        if (!enabled) return;

        const weatherApi = 'https://uapis.cn/api/v1/misc/weather?extended=false&lang=zh';
        console.log('[天气背景] 请求天气 API:', weatherApi);
        fetch(weatherApi)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(weatherData => {
                console.log('[天气背景] 天气 API 返回:', weatherData);
                const weather = weatherData.weather || 'default';
                console.log('[天气背景] 识别天气:', weather);
                const date = WEATHER_BING_DATES[weather] || WEATHER_BING_DATES['default'];
                console.log('[天气背景] 对应壁纸日期:', date);
                return fetchBingWallpaper(date);
            })
            .then(imgUrl => {
                if (enabled) setBackground(imgUrl);
            })
            .catch(err => {
                console.warn('[天气背景] 整体失败，使用备用壁纸', err);
                if (enabled) setBackground(null);
            });
    }

    // ========== 开关控制 ==========
    function toggleWeatherBackground() {
        enabled = !enabled;
        if (enabled) {
            fetchWeatherAndApply();
        } else {
            const style = document.getElementById('dynamic-bg-style');
            if (style) style.remove();
            console.log('[天气背景] 已关闭');
        }
    }

    // ========== 对外暴露 ==========
    window.__weatherBg = {
        enabled: enabled,
        fetch: fetchWeatherAndApply,
        toggle: toggleWeatherBackground,
        setEnabled: function(val) {
            enabled = !!val;
            if (enabled) {
                fetchWeatherAndApply();
            } else {
                const style = document.getElementById('dynamic-bg-style');
                if (style) style.remove();
                console.log('[天气背景] 已关闭');
            }
        }
    };

    // ========== 初始化 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fetchWeatherAndApply);
    } else {
        fetchWeatherAndApply();
    }

    // 每小时刷新一次
    setInterval(fetchWeatherAndApply, 3600000);

    console.log('[天气背景] 脚本已加载，可通过 window.__weatherBg 控制');
})();