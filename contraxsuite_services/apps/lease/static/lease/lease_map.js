'use_strict';


function buildLeaseDocumentsMap(mapDataUrlProvider, leaseDocumentDetailUrlProvider, countrySelector,
                                provinceSelector, mapComponent, bindActivateListenerFunction,
                                predefinedLessor, localStoragePrefix) {
  var geocoder = new google.maps.Geocoder();

  var countryToProvinceToLeaseNum = null;
  var countryToLeaseNum = null;
  var countryToCode = null;

  var selCountryFromStorage = null;
  var selProvinceFromStorage = null;

  function str(s) {
    return s ? s : "";
  }

  function prepareMarker(map, leaseDocument) {
    if (!(leaseDocument && leaseDocument.address_latitude &&
        leaseDocument.address_longitude)) return;

    var latlng = new google.maps.LatLng(leaseDocument.address_latitude,
      leaseDocument.address_longitude);
    var title = "Lessor: " + str(leaseDocument.lessor) + "\nLessee: " +
      str(leaseDocument.lessee) + "\nAddress: " + str(leaseDocument.address);
    var marker = new google.maps.Marker({
      map: map, title: title, position: latlng
    });
    google.maps.event.addListener(marker, 'click', function (evt) {
      window.location.href = leaseDocumentDetailUrlProvider(leaseDocument["pk"]);
    });
  }


  function buildCountrySelector() {
    var sel = countrySelector;
    sel.off('change', buildProvinceSelector);

    var oldSelected = sel.val();

    if (!oldSelected) oldSelected = selCountryFromStorage;

    sel.find('option').remove();
    sel.append($("<option>").attr('value', 'all').text('Leases by Country'));
    sel.val('all');

    for (var country in countryToProvinceToLeaseNum) {
      if (!countryToProvinceToLeaseNum.hasOwnProperty(country)) continue;
      sel.append($("<option>").attr('value', country).text(country));
      if (country === oldSelected) sel.val(country);
    }

    sel.on('change', buildProvinceSelector);
    buildProvinceSelector();
  }

  function buildProvinceSelector() {
    var sel = provinceSelector;
    sel.off('change', drawMap);

    var oldSelected = sel.val();
    if (!oldSelected) oldSelected = selProvinceFromStorage;
    sel.find('option').remove();


    var country = countrySelector.val();
    if (country === 'all') {
      sel.hide();
      drawMapOrPlanDrawing();
      return;
    } else {
      sel.show();
    }


    var provinces = countryToProvinceToLeaseNum[country];

    sel.append($("<option>").attr('value', 'all').text('Leases by State / Province'));
    sel.val('all');

    for (var province in provinces) {
      if (!provinces.hasOwnProperty(province)) continue;
      sel.append($("<option>").attr('value', province).text(province));
      if (province === oldSelected) sel.val(province);
    }

    sel.on('change', drawMap);

    drawMapOrPlanDrawing();
  }

  var bound = false;

  function drawMapOrPlanDrawing() {
    if (mapComponent.is(":visible")) drawMap(); else if (!bound) {
      bindActivateListenerFunction(function () {
        if (mapComponent.is(":visible")) drawMap();
      });
      bound = true;
    }
  }

  function storeSelectedConfig() {
    window.localStorage[localStoragePrefix + '_country'] = countrySelector.val();
    window.localStorage[localStoragePrefix + '_province'] = provinceSelector.val();
  }

  function drawMap() {
    var selCountry = countrySelector.val();
    var selProvince = provinceSelector.val();

    storeSelectedConfig();

    if ((selCountry !== 'all' && selProvince !== 'all')
      || (selCountry !== 'United States' && selCountry !== 'Canada' && selProvince === 'all')) {
      var url = mapDataUrlProvider(selCountry, selProvince, predefinedLessor);

      var mapOptions = {
        center: new google.maps.LatLng(20, 20), zoom: 2, minZoom: 1
      };
      var map = new google.maps.Map(mapComponent[0], mapOptions);

      geocoder.geocode(
        {'address': (selProvince !== 'all' ? (selProvince + ", ") : "") + selCountry},
        function (results, status) {
          if (status === google.maps.GeocoderStatus.OK) {
            map.setCenter(results[0].geometry.location);
            map.fitBounds(results[0].geometry.viewport);
          } else {
            console.error('Can not get results from Google Geocoder', status);
            map.setCenter(new google.maps.LatLng(0, 0));
            map.setZoom(1);
            map.setMinZoom(1);
          }
        });
      $.getJSON(url, null, function (data) {
        for (var j = 0; j < data.length; j++) prepareMarker(map, data[j]);
      });
    } else {
      var data = new google.visualization.DataTable();
      var options = {};
      if (selCountry !== 'all' && selProvince === 'all') {
        data.addColumn('string', 'State/Province');
        data.addColumn('number', 'Lease Documents Number');
        var provinceToLeaseNum = countryToProvinceToLeaseNum[selCountry];
        for (var province in provinceToLeaseNum) {
          if (!provinceToLeaseNum.hasOwnProperty(province)) continue;
          data.addRow([province, provinceToLeaseNum[province]]);
        }
        options = {
          "displayMode": "region",
          "region": countryToCode[selCountry],
          "resolution": "provinces"
        };
      } else {
        data.addColumn('string', 'Country');
        data.addColumn('number', 'Lease Documents Number');
        for (var country in countryToLeaseNum) {
          if (!countryToLeaseNum.hasOwnProperty(country)) continue;
          data.addRow([country, countryToLeaseNum[country]]);
        }
        options = {
          "displayMode": "region", "region": "world", "resolution": "countries"
        };
      }

      var chart = new google.visualization.GeoChart(mapComponent[0]);

      function geoChartClickHandler() {
        var selection = chart.getSelection();
        for (var i = 0; i < selection.length; i++) {
          var item = selection[i];
          if (item.row !== null) {
            var value = data.getValue(item.row, 0);
            if (selCountry !== 'all') {
              //country is already selected => province has been clicked
              provinceSelector.val(value);
              drawMap();
            } else {
              countrySelector.val(value);
              buildProvinceSelector();
            }
          }
        }
      }

      google.visualization.events.addListener(chart, 'select', geoChartClickHandler);
      chart.draw(data, options);
    }
  }

  function loadMapSelectors() {
    $.ajaxSetup({cache: false});
    var url = mapDataUrlProvider('all', null, predefinedLessor);

    $.getJSON(url, null, function (data) {
      countryToProvinceToLeaseNum = {};
      countryToLeaseNum = {};
      countryToCode = {};
      for (var i = 0; i < data.length; i++) {
        var country = data[i].address_country;
        if (!country) continue;
        countryToCode[country] = data[i].address_country_code;
        var province = data[i].address_state_province;
        var provinceToLeaseNum = countryToProvinceToLeaseNum[country];
        if (!provinceToLeaseNum) {
          provinceToLeaseNum = {};
          countryToProvinceToLeaseNum[country] = provinceToLeaseNum;
        }
        provinceToLeaseNum[province] = data[i].leases_number;

        if (!countryToLeaseNum[country]) {
          countryToLeaseNum[country] = data[i].leases_number;
        } else {
          countryToLeaseNum[country] += data[i].leases_number;
        }
      }
      buildCountrySelector();
    });
  }


  function windowLoaded() {
    selCountryFromStorage = window.localStorage[localStoragePrefix + '_country'];
    selProvinceFromStorage = window.localStorage[localStoragePrefix + '_province'];


    google.charts.load('upcoming', {'packages': ['geochart']});
    google.charts.setOnLoadCallback(function () {
      setTimeout(loadMapSelectors, 100);
    });
  }


  google.maps.event.addDomListener(window, "load", windowLoaded);


}