function updateStatusFilter(status) {
    const url = new URL(window.location.href);
    url.searchParams.set('status', status);
    window.location.href = url.toString();
}

function updateSortFilter(sortBy) {
    const url = new URL(window.location.href);
    url.searchParams.set('sort_by', sortBy);
    window.location.href = url.toString();
}

function updateTypeFilter(type) {
    const url = new URL(window.location.href);
    url.searchParams.set('type', type);
    window.location.href = url.toString();
}