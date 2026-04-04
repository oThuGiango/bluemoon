/**
 * File: statistic_charts.js
 * Xử lý vẽ đồ thị cho trang Statistics
 */

document.addEventListener('DOMContentLoaded', function() {
    // Màu sắc chủ đạo theo thương hiệu BlueMoon
    const colors = {
        primary: '#1976d2',
        secondary: '#42a5f5',
        success: '#66bb6a',
        background: 'rgba(25, 118, 210, 0.1)'
    };

    // 1. BIỂU ĐỒ TRÒN (PHÂN LOẠI PHÍ)
    const ctxPie = document.getElementById('feeTypeChart').getContext('2d');
    new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: DB_DATA.pieLabels,
            datasets: [{
                data: DB_DATA.pieData,
                backgroundColor: [colors.primary, colors.secondary, '#90caf9', '#bbdefb', '#e3f2fd'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 12 } }
            }
        }
    });

    // 2. BIỂU ĐỒ ĐƯỜNG (XU HƯỚNG THÁNG)
    const ctxLine = document.getElementById('monthlyTrendChart').getContext('2d');
    new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: DB_DATA.lineLabels,
            datasets: [{
                label: 'Doanh thu thực tế (VND)',
                data: DB_DATA.lineData,
                borderColor: colors.primary,
                backgroundColor: colors.background,
                fill: true,
                tension: 0.4, // Tạo độ cong cho đường
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000000) return (value / 1000000) + ' Tr';
                            return value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ' Thu: ' + context.raw.toLocaleString() + ' VND';
                        }
                    }
                }
            }
        }
    });
});