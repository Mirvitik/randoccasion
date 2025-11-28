document.getElementById('date_from').addEventListener('change', function() {
    document.getElementById('date_to').min = this.value || '';
});

document.getElementById('date_to').addEventListener('change', function() {
    document.getElementById('date_from').max = this.value || '';
});