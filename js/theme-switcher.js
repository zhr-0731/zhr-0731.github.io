/**
 * 自动主题切换脚本（仅修改轮播图第一张 + 中央标题，不修改跳转链接）
 * 使用方式：在 index.html 的 </body> 前引入此脚本：
 *   <script src="theme-switcher.js"></script>
 * 要求：页面中必须包含以下元素（建议添加对应 id）：
 *   - 轮播第一张图片：<img id="slide1Img" ...>
 *   - 轮播第一张标题：<h3 id="slide1Title" ...>
 *   - 轮播第一张摘要：<p id="slide1Excerpt" ...>
 *   - 中央主标题：<div id="bannerMainTitle" ...>
 *   - 中央副标题：<div id="bannerSubTitle" ...>
 */

(function() {
    'use strict';

    // ========== 配置区 ==========
    const CONFIG = {
        // 春节主题（正月初一前后，除夕~初七）
        spring: {
            mainTitle: '🧨 新春快乐',
            subTitle: '万事如意 · 阖家团圆',
            slide: {
                image: 'https://s41.ax1x.com/2026/07/24/pmgT1ne.jpg',   // 春节轮播图
                title: '🐉 新年新气象',
                excerpt: '辞旧迎新，愿新的一年平安顺遂，幸福安康。'
            }
        },
        // 国家公祭日（12月13日）
        memorial: {
            mainTitle: '🕯️ 国家公祭日',
            subTitle: '铭记历史 · 珍爱和平',
            slide: {
                image: 'https://s41.ax1x.com/2026/07/24/pmgT5B4.png',   // 公祭日轮播图
                title: '勿忘国耻 振兴中华',
                excerpt: '1937年12月13日，南京大屠杀。铭记历史，珍爱和平。'
            }
        },
        // 默认（平时）
        default: {
            mainTitle: 'zhr的博客',
            subTitle: '随便写写'
        }
    };

    // ========== 工具函数：获取春节日期（2024-2030） ==========
    function getChineseNewYear(year) {
        const dates = {
            2024: new Date(2024, 1, 10), // 2月10日
            2025: new Date(2025, 0, 29), // 1月29日
            2026: new Date(2026, 1, 17), // 2月17日
            2027: new Date(2027, 1, 6),  // 2月6日
            2028: new Date(2028, 0, 26), // 1月26日
            2029: new Date(2029, 1, 13), // 2月13日
            2030: new Date(2030, 1, 3)   // 2月3日
        };
        return dates[year] || null;
    }

    // ========== 判断当前主题 ==========
    function getCurrentTheme() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1; // 1-12
        const day = now.getDate();

        // 公祭日：12月13日
        if (month === 12 && day === 13) {
            return 'memorial';
        }

        // 春节：除夕～初七
        const cny = getChineseNewYear(year);
        if (cny) {
            const start = new Date(cny);
            start.setDate(start.getDate() - 1); // 除夕
            const end = new Date(cny);
            end.setDate(end.getDate() + 6);     // 初七
            if (now >= start && now <= end) {
                return 'spring';
            }
        }

        return 'default';
    }

    // ========== 应用主题 ==========
    function applyTheme(theme) {
        const config = CONFIG[theme];
        if (!config) return;

        // 1. 修改中央标题
        const mainTitle = document.getElementById('bannerMainTitle');
        const subTitle = document.getElementById('bannerSubTitle');
        if (mainTitle) mainTitle.textContent = config.mainTitle;
        if (subTitle) subTitle.textContent = config.subTitle;

        // 2. 修改轮播图第一张（仅当 theme 不是 default 时）
        if (theme !== 'default' && config.slide) {
            const img = document.getElementById('slide1Img');
            const title = document.getElementById('slide1Title');
            const excerpt = document.getElementById('slide1Excerpt');

            if (img) img.src = config.slide.image;
            if (title) title.textContent = config.slide.title;
            if (excerpt) excerpt.textContent = config.slide.excerpt;
            // 注意：不修改跳转链接，保持原有 href
        }

        console.log(`[主题切换] 当前主题: ${theme}，已应用配置`);
    }

    // ========== 执行 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            const theme = getCurrentTheme();
            applyTheme(theme);
        });
    } else {
        const theme = getCurrentTheme();
        applyTheme(theme);
    }
})();
