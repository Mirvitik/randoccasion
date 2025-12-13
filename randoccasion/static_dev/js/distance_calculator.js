(function() {
  ymaps.ready(function () {
    if (document.querySelectorAll('.distance-to').length === 0) return;
    const translations = document.getElementById('distance-translations');
    const kmText = translations ? translations.dataset.km : 'км';
    const mText = translations ? translations.dataset.m : 'м';

    ymaps.geolocation
      .get({
        provider: "yandex",
        mapStateAutoApply: false,
      })
      .then(
        function (result) {
          const userPoint = result.geoObjects.get(0).geometry.getCoordinates();
          calculateDistances(userPoint);
        },
        function (err) {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              function (position) {
                const userPoint = [
                  position.coords.latitude,
                  position.coords.longitude,
                ];
                calculateDistances(userPoint);
              },
              function (error) {
                showDistanceError();
              }
            );
          } else {
            showDistanceError();
          }
        }
      );

    function calculateDistances(userPoint) {
      document
        .querySelectorAll(".distance-to")
        .forEach(function (distanceElement) {
          const eventLat = parseFloat(distanceElement.dataset.eventLat);
          const eventLon = parseFloat(distanceElement.dataset.eventLon);

          if (eventLat && eventLon && !isNaN(eventLat) && !isNaN(eventLon)) {
            const eventPoint = [eventLat, eventLon];
            const distanceInMeters = ymaps.coordSystem.geo.getDistance(
              eventPoint,
              userPoint
            );

            let finalText;
            if (distanceInMeters >= 1000) {
              finalText = "\u00A0(" + (distanceInMeters / 1000).toFixed(1) + " " + kmText + ")";
            } else {
              finalText = "\u00A0(" + Math.round(distanceInMeters) + " " + mText + ")";
            }
            distanceElement.textContent = finalText;
          }
        });
    }
  });
})();