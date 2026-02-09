document.addEventListener('DOMContentLoaded', function () {
    // === Globals ===
    const menuToggle = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');
    const sectionTitle = document.getElementById('section-title');
    const navLinks = document.querySelectorAll('.list-group-item');
    const sections = document.querySelectorAll('.content-section');

    let weatherChart, riskTrendChart, importanceChart;

    // === Sidebar & Navigation ===
    menuToggle.onclick = function () {
        wrapper.classList.toggle('toggled');
    };

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            // Skip logout button - let it navigate normally
            if (this.id === 'logout-btn') {
                return; // Don't prevent default, allow normal navigation
            }

            e.preventDefault();
            const targetSection = this.getAttribute('data-section');
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            sectionTitle.textContent = this.textContent.trim();
            sections.forEach(sec => {
                if (sec.id === `${targetSection}-section`) {
                    sec.classList.remove('d-none');
                } else {
                    sec.classList.add('d-none');
                }
            });
            if (targetSection === 'dashboard' || targetSection === 'visualization') {
                refreshDashboard();
            }
        });
    });

    // === Initialize Charts ===
    function initCharts() {
        const ctxWeather = document.getElementById('weatherChart').getContext('2d');
        weatherChart = new Chart(ctxWeather, {
            type: 'line',
            data: {
                labels: [], datasets: [
                    { label: 'Temp (°C)', data: [], borderColor: '#ff4d4d', backgroundColor: 'rgba(255, 77, 77, 0.1)', fill: true, tension: 0.4 },
                    { label: 'Hum (%)', data: [], borderColor: '#17a2b8', backgroundColor: 'rgba(23, 162, 184, 0.1)', fill: true, tension: 0.4 }
                ]
            },
            options: { responsive: true, plugins: { legend: { labels: { color: '#a0a0a5' } } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a5' } }, x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a5' } } } }
        });

        const ctxTrend = document.getElementById('riskTrendChart').getContext('2d');
        riskTrendChart = new Chart(ctxTrend, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Temperature', data: [], backgroundColor: '#ff4d4d' }] },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a5' } }, x: { grid: { display: false }, ticks: { color: '#a0a0a5' } } } }
        });

        const ctxImportance = document.getElementById('importanceChart').getContext('2d');
        importanceChart = new Chart(ctxImportance, {
            type: 'doughnut',
            data: { labels: ['Temp', 'Humidity', 'Wind', 'Rain', 'NDVI', 'History'], datasets: [{ data: [40, 30, 10, 5, 10, 5], backgroundColor: ['#e74c3c', '#3498db', '#f1c40f', '#2ecc71', '#9b59b6', '#34495e'] }] },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#a0a0a5' } } } }
        });
    }

    // === Refresh Dashboard Data ===
    async function refreshDashboard() {
        try {
            // Fetch Stats
            const statsResp = await fetch('/api/dashboard_stats');
            const stats = await statsResp.json();
            document.getElementById('stat-active-fires').textContent = stats.active_hotspots;
            document.getElementById('stat-risk-level').textContent = stats.global_risk;

            // Update border colors based on risk
            const riskCard = document.getElementById('stat-risk-level').closest('.bg-card');
            riskCard.classList.remove('border-left-danger', 'border-left-warning', 'border-left-success');
            if (stats.global_risk === 'High Risk') riskCard.classList.add('border-left-danger');
            else if (stats.global_risk === 'Medium Risk') riskCard.classList.add('border-left-warning');
            else riskCard.classList.add('border-left-success');

            // Fetch Trends (Charts)
            const trendsResp = await fetch('/api/weather_trends');
            const history = await trendsResp.json();

            const labels = history.map(h => h.time);
            const temps = history.map(h => h.temp);
            const hums = history.map(h => h.hum);

            weatherChart.data.labels = labels;
            weatherChart.data.datasets[0].data = temps;
            weatherChart.data.datasets[1].data = hums;
            weatherChart.update();

            riskTrendChart.data.labels = labels;
            riskTrendChart.data.datasets[0].data = temps; // Showing temp trend as risk proxy
            riskTrendChart.update();

        } catch (err) {
            console.error("Dashboard refresh failed:", err);
        }
    }

    // === API Interactions ===

    // Data Upload

    // Fetch Satellite Data
    document.getElementById('fetch-form').onsubmit = async (e) => {
        e.preventDefault();
        const region = document.getElementById('region').value;
        const from_date = document.getElementById('from_date').value;
        const to_date = document.getElementById('to_date').value;
        const statusDiv = document.getElementById('fetch-status');
        statusDiv.innerHTML = '<div class="text-info">Fetching satellite data...</div>';
        try {
            const resp = await fetch('/fetch_satellite_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ region, from_date, to_date })
            });
            const data = await resp.json();
            statusDiv.innerHTML = `<div class="text-success">Found ${data.firms_count} hotspots. State updated.</div>`;

            // Auto-populate prediction values
            document.getElementById('pred-temp').value = data.weather_data.temperature;
            document.getElementById('pred-humidity').value = data.weather_data.humidity;
            document.getElementById('pred-wind').value = data.weather_data.wind_speed;
            document.getElementById('pred-rain').value = data.weather_data.rainfall;
            document.getElementById('pred-ndvi').value = data.weather_data.ndvi;

            refreshDashboard();
        } catch (err) {
            statusDiv.innerHTML = `<div class="text-danger">Fetch failed: ${err}</div>`;
        }
    };

    // Run Prediction
    document.getElementById('run-prediction').onclick = async () => {
        const payload = {
            temperature: parseFloat(document.getElementById('pred-temp').value),
            humidity: parseFloat(document.getElementById('pred-humidity').value),
            wind_speed: parseFloat(document.getElementById('pred-wind').value),
            rainfall: parseFloat(document.getElementById('pred-rain').value),
            ndvi: parseFloat(document.getElementById('pred-ndvi').value),
            historical_fire: parseInt(document.getElementById('pred-hist').value),
            phone_number: document.getElementById('pred-phone').value,
            region: document.getElementById('region').value
        };

        const resultDiv = document.getElementById('prediction-result');
        const riskAlert = document.getElementById('risk-alert');
        const riskText = document.getElementById('risk-text');
        const confidenceText = document.getElementById('confidence-text');
        const smsStatusText = document.getElementById('sms-status-text');
        const tgStatusText = document.getElementById('tg-status-text');

        try {
            const resp = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();

            resultDiv.classList.remove('d-none');
            riskText.textContent = data.risk_level.toUpperCase();
            confidenceText.textContent = data.confidence;
            smsStatusText.textContent = data.sms_status ? "SMS Alert: " + data.sms_status : "";
            tgStatusText.textContent = data.telegram_status ? "Telegram: " + data.telegram_status : "";

            riskAlert.classList.remove('risk-low', 'risk-medium', 'risk-high');
            if (data.prediction === 0) riskAlert.classList.add('risk-low');
            else if (data.prediction === 1) riskAlert.classList.add('risk-medium');
            else riskAlert.classList.add('risk-high');

            refreshDashboard();
        } catch (err) {
            alert('Prediction failed: ' + err);
        }
    };

    // Initialize
    initCharts();
    refreshDashboard();
    // Auto-refresh every 30 seconds
    setInterval(refreshDashboard, 30000);
});
