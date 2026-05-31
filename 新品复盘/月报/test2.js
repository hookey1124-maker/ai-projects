// Test
function mkLine(id, labels, datasets) {
  var options = { responsive: true };
  new Chart(ctx, {type: 'line', data: { labels: labels, datasets: datasets }, options: options});
}
