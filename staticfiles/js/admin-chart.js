/* Dashboard message-volume chart.
   Data rides in on the element's data-* attributes so the view stays a plain
   render — see admin_panel.views.dashboard. Colours are read from the same CSS
   custom properties the rest of the design system uses, and re-read whenever
   the theme flips (admin.js dispatches `bh:themechange`). */
(function () {
  'use strict';

  var host = document.querySelector('[data-bh-chart]');
  if (!host || typeof ApexCharts === 'undefined') return;

  var labels = (host.dataset.labels || '').split(',').filter(Boolean);
  var series = (host.dataset.series || '').split(',').map(Number).filter(function (n) { return !isNaN(n); });
  if (!labels.length || !series.length) return;

  function tokens() {
    var styles = getComputedStyle(document.documentElement);
    var read = function (name, fallback) {
      var value = styles.getPropertyValue(name).trim();
      return value || fallback;
    };
    return {
      brand: 'rgb(' + read('--bh-green', '8 127 91') + ')',
      line: 'rgb(' + read('--bh-line', '226 235 230') + ')',
      faint: 'rgb(' + read('--bh-faint', '138 154 147') + ')',
      text: 'rgb(' + read('--bh-text', '16 35 29') + ')',
      surface: 'rgb(' + read('--bh-surface', '255 255 255') + ')'
    };
  }

  var chart = null;

  function draw() {
    var c = tokens();
    var options = {
      chart: {
        type: 'area',
        height: 260,
        toolbar: { show: false },
        zoom: { enabled: false },
        fontFamily: 'Manrope, ui-sans-serif, system-ui, sans-serif',
        background: 'transparent'
      },
      series: [{ name: 'Messages', data: series }],
      colors: [c.brand],
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth', width: 3, lineCap: 'round' },
      fill: {
        type: 'gradient',
        gradient: { shadeIntensity: 0.2, opacityFrom: 0.35, opacityTo: 0.02, stops: [0, 95] }
      },
      grid: {
        borderColor: c.line,
        strokeDashArray: 4,
        xaxis: { lines: { show: false } },
        padding: { left: 4, right: 8 }
      },
      xaxis: {
        categories: labels,
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: { style: { colors: c.faint, fontSize: '12px', fontWeight: 600 } }
      },
      yaxis: {
        min: 0,
        forceIntegerScale: true,
        labels: { style: { colors: c.faint, fontSize: '12px', fontWeight: 600 } }
      },
      tooltip: {
        theme: document.documentElement.classList.contains('dark') ? 'dark' : 'light',
        x: { show: true }
      },
      legend: { show: false }
    };

    if (chart) {
      chart.updateOptions(options);
      return;
    }
    chart = new ApexCharts(host, options);
    chart.render();
  }

  draw();
  window.addEventListener('bh:themechange', draw);
})();
