// Test
function mkLine(id, labels, datasets) {
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: datasets.length > 1,
          position: 'top',
          labels: {
            font: { size: 10 }
          }
        }
      },
      scales: {
        x: {
          ticks: { font: { size: 10 } }
        },
        y: {
          ticks: { font: { size: 10 } }
        }
      }
    }
  });
}
