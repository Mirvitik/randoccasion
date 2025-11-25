(function () {
  'use strict';
  var input = document.getElementById('server-time');
  if (!input) return;

  var serverTimeStr = input.value;
  var serverDate = new Date(serverTimeStr);
  if (isNaN(serverDate.getTime())) return;

  var now = new Date();
  var diffMs = Math.abs(serverDate - now);
  var diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  var date = new Date(diffDays < 1 ? now : serverDate);
  var yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = date.getFullYear();
  }
})();
