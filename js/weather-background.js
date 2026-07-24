/**
 * 天气背景壁纸自动切换（使用必应每日壁纸 API）
 * 依赖：https://uapis.cn/api/v1/image/bing-daily
 * 说明：根据天气类型，从必应壁纸 API 获取对应日期的壁纸
 */

(function() {
    'use strict';

    // ========== 配置区（天气对应的必应壁纸日期） ==========
    // 这些日期是我之前找到的与天气主题匹配的必应壁纸日期
    const WEATHER_BING_DATES = {
        '晴': '2026-07-10',   // 浮木海滩，南卡罗来纳州（阳光沙滩）
        '多云': '2026-06-21', // 恒河上空多彩天空与云层
        '阴': '2026-06-22',   // 奎诺尔特雨林（阴雨氛围）
        '小雨': '2026-06-22', // 同阴
        '中雨': '2026-06-22',
        '大雨': '2026-06-22',
        '雷阵雨': '2026-05-04', // 保加利亚平原雷暴
        '小雪': '2025-12-20',   // 博尔米奥雪景
        '中雪': '2025-12-20',
        '大雪': '2025-12-20',
        '雨夹雪': '2026-06-23', // 富士山（雪景）
        '雾': '2023-12-07',     // 韦尔东峡谷雾晨
        '霾': '2026-06-23',     // 富士山（朦胧）
        '沙尘': '2026-05-14',   // 阿拉巴马山拱门与银河（沙漠）
        'default': '2026-06-13' // 恶地国家公园日落（默认）
    };

    // 备选壁纸（如果 API 获取失败，使用这些 Unsplash 链接）
    const FALLBACK_WALLPAPERS = {
        '晴': 'https://images.unsplash.com/photo-1601297183306-3df142d5b2c3?w=1920&q=80',
        '多云': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1920&q=80',
        '阴': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=80',
        '小雨': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1920&q=80',
        '中雨': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1920&q=80',
        '大雨': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1920&q=80',
        '雷阵雨': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=80',
        '小雪': 'https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?w=1920&q=80',
        '中雪': 'https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?w=1920&q=80',
        '大雪': 'https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?w=1920&q=80',
        '雨夹雪': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=1920&q=80',
        '雾': 'https://images.unsplash.com/photo-1487621167305-5d248087c724?w=1920&q=80',
        '霾': 'https://images.unsplash.com/photo-1523655733528-5f4ccf22b478?w=1920&q=80',
        '沙尘': 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1920&q=80',
        'default': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920&q=80'
    };

    const DEBUG = true;
    let enabled = true;
    const body = document.body;

    // ========== 从必应 API 获取壁纸图片 URL ==========
    function fetchBingWallpaper(date) {
        const apiUrl = `https://uapis.cn/api/v1/image/bing-daily?date=${date}&format=json&resolution=4k`;

        return fetch(apiUrl)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                // 返回 4K 图片 URL
                return data.image_url_4k || data.image_url || null;
            })
            .catch(err => {
                console.warn('[天气背景] 必应 API 请求失败', err);
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

        if (imageUrl) {
            body.style.backgroundImage = `url(${imageUrl})`;
            body.style.backgroundSize = 'cover';
            body.style.backgroundPosition = 'center';
            body.style.backgroundAttachment = 'fixed';
            body.style.backgroundColor = 'rgba(0,0,0,0.3)';
            body.style.backgroundBlendMode = 'overlay';
        } else {
            // 使用备选
            const fallback = FALLBACK_WALLPAPERS['default'];
            body.style.backgroundImage = `url(${fallback})`;
        }
        if (DEBUG) console.log('[天气背景] 壁纸已应用');
    }

    // ========== 获取天气并应用壁纸 ==========
    function fetchWeatherAndApply() {
        if (!enabled) {
            setBackground(null);
            return;
        }

        // 1. 获取天气
        const weatherApi = 'https://uapis.cn/api/v1/misc/weather?extended=false&lang=zh';
        fetch(weatherApi)
            .then(res => res.json())
            .then(weatherData => {
                const weather = weatherData.weather || 'default';
                const date = WEATHER_BING_DATES[weather] || WEATHER_BING_DATES['default'];

                // 2. 根据日期获取必应壁纸
                return fetchBingWallpaper(date)
                    .then(imageUrl => {
                        if (imageUrl) {
                            setBackground(imageUrl);
                        } else {
                            // 使用备选
                            const fallback = FALLBACK_WALLPAPERS[weather] || FALLBACK_WALLPAPERS['default'];
                            setBackground(fallback);
                        }
                        // 更新开关按钮图标（可选）
                        updateToggleIcon(weather);
                    });
            })
            .catch(err => {
                console.warn('[天气背景] 获取天气失败，使用默认壁纸', err);
                const fallback = FALLBACK_WALLPAPERS['default'];
                setBackground(fallback);
            });
    }

    // ========== 更新开关按钮图标 ==========
    function updateToggleIcon(weather) {
        const btn = document.getElementById('weatherToggle');
        if (!btn) return;
        const iconMap = {
            '晴': '☀️', '多云': '⛅', '阴': '☁️', '小雨': '🌦️',
            '中雨': '🌧️', '大雨': '🌧️', '雷阵雨': '⛈️',
            '小雪': '❄️', '中雪': '❄️', '大雪': '❄️',
            '雨夹雪': '🌨️', '雾': '🌫️', '霾': '🌫️',
            '沙尘': '🏜️', 'default': '🌍'
        };
        const icon = iconMap[weather] || '🌍';
        btn.textContent = enabled ? icon : '🚫';
        btn.title = enabled ? `当前天气：${weather}，点击关闭背景` : '背景已关闭，点击开启';
    }

    // ========== 切换开关 ==========
    function toggleBackground() {
        enabled = !enabled;
        const btn = document.getElementById('weatherToggle');
        if (btn) {
            btn.textContent = enabled ? '☀️' : '🚫';
            btn.title = enabled ? '点击关闭天气背景' : '点击开启天气背景';
        }
        if (enabled) {
            fetchWeatherAndApply();
        } else {
            body.style.backgroundImage = 'none';
            body.style.backgroundColor = '';
            body.style.backgroundBlendMode = 'normal';
        }
    }

    // ========== 创建开关按钮 ==========
    function ensureToggleButton() {
        let toggleBtn = document.getElementById('weatherToggle');
        if (!toggleBtn) {
            const nav = document.querySelector('nav ul') || document.querySelector('.header-inner');
            if (nav) {
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
                toggleBtn = document.getElementById('weatherToggle');
            } else {
                console.warn('[天气背景] 未找到导航栏，无法添加开关按钮');
                return null;
            }
        }
        return toggleBtn;
    }

    // ========== 初始化 ==========
    function init() {
        const toggleBtn = ensureToggleButton();
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleBackground);
            toggleBtn.textContent = '☀️';
            toggleBtn.title = '点击关闭天气背景';
        }
        fetchWeatherAndApply();
        // 每小时刷新一次
        setInterval(fetchWeatherAndApply, 3600000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();