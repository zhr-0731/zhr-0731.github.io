/**
 * 天气背景壁纸自动切换（使用 document.documentElement 避免 body null 问题）
 * 依赖：https://uapis.cn/api/v1/misc/weather
 *       https://uapis.cn/api/v1/image/bing-daily
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

    // ========== 安全获取目标元素（优先 html，备选 body） ==========
    function getTargetElement() {
        // 优先使用 document.documentElement (<html>)
        // 因为它在 DOM 树中总是最先存在
        const el = document.documentElement;
        if (el) return el;
        // 备选：尝试获取 body
        return document.body || document.querySelector('body') || null;
    }

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

    // ========== 设置背景壁纸（直接操作 html 元素） ==========
    function setBackground(imageUrl) {
        const target = getTargetElement();
        if (!target) {
            console.warn('[天气背景] 无法获取目标元素，跳过设置');
            // 尝试用 setTimeout 再试一次
            setTimeout(() => setBackground(imageUrl), 1000);
            return;
        }

        if (!enabled) {
            target.style.backgroundImage = 'none';
            target.style.backgroundColor = '';
            target.style.backgroundBlendMode = 'normal';
            return;
        }

        const url = imageUrl || FALLBACK;
        console.log(`[天气背景] 应用壁纸到 <${target.tagName.toLowerCase()}>: ${url}`);
        target.style.backgroundImage = `url(${url})`;
        target.style.backgroundSize = 'cover';
        target.style.backgroundPosition = 'center';
        target.style.backgroundAttachment = 'fixed';
        target.style.backgroundColor = 'rgba(0,0,0,0.3)';
        target.style.backgroundBlendMode = 'overlay';
        target.style.minHeight = '100vh';
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
            const target = getTargetElement();
            if (target) {
                target.style.backgroundImage = 'none';
                target.style.backgroundColor = '';
                target.style.backgroundBlendMode = 'normal';
            }
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
        // 检测目标元素是否存在，如果不存在则等待
        if (!getTargetElement()) {
            console.log('[天气背景] 目标元素未就绪，等待 500ms 后重试...');
            setTimeout(init, 500);
            return;
        }

        const btn = ensureToggleButton();
        if (btn) {
            btn.addEventListener('click', toggleBackground);
        }

        // 首次加载
        fetchWeatherAndApply();
        // 每小时刷新一次
        setInterval(fetchWeatherAndApply, 3600000);
        console.log('[天气背景] 脚本已初始化，目标元素: <' + (getTargetElement()?.tagName?.toLowerCase() || 'unknown') + '>');
    }

    // 立即执行，无需等待 DOMContentLoaded
    // 因为 document.documentElement 在脚本执行时通常已经存在
    if (document.documentElement) {
        // 但 body 可能还没加载完成，给一个缓冲
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    } else {
        // 极端情况：连 html 都没准备好
        document.addEventListener('DOMContentLoaded', init);
    }
})();