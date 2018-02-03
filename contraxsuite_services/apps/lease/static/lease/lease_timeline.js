'use strict';

function buildLeaseTimeLineByLessor(container, dataUrlProvider, docDetailsUrlProvider) {

  $.ajaxSetup({cache: false});
  var url = dataUrlProvider();
  $.getJSON(url, null, function (data) {
    var leaseDocuments = data['data'];
    var addressesToDocArrays = {};
    var minDate = null;
    var maxDate = null;

    for (var i in leaseDocuments) {
      if (!leaseDocuments.hasOwnProperty(i)) continue;
      var doc = leaseDocuments[i];
      var startDate = doc['commencement_date'];
      var endDate = doc['expiration_date'];
      var address = doc['address'];

      if (!address || !startDate || !endDate) continue;

      if (!minDate || minDate > startDate) minDate = startDate;

      if (!maxDate || maxDate < endDate) maxDate = endDate;

      var addressTimeline = addressesToDocArrays[address];
      if (!addressTimeline) {
        addressTimeline = [doc];
        addressesToDocArrays[address] = addressTimeline;
      } else {
        addressTimeline.push(doc);
      }
    }

    var addresses = Object.keys(addressesToDocArrays).sort();

    var groups = new vis.DataSet();
    var items = new vis.DataSet();

    for (var j in addresses) {
      if (!addresses.hasOwnProperty(j)) continue;
      var addressJ = addresses[j];
      groups.add({
        id: addressJ, content: addressJ
      });

      var docs = addressesToDocArrays[addressJ];
      for (var k in docs) {
        if (!docs.hasOwnProperty(k)) continue;
        var docK = docs[k];
        items.add({
          id: docK['pk'],
          group: addressJ,
          start: docK['commencement_date'],
          end: docK['expiration_date'],
          content: '<a style="box-shadow: none" href="' +
          docDetailsUrlProvider(docK['pk']) + '">' + docK['name'] + '</a>'
        });
      }
    }

    if (items.length === 0) {
      container.innerHTML = "Unfortunately there are no lease contracts of this lessor " +
        "with detected premises address, commencement and expiration dates.";
      return;
    }

    var options = {
      stack: true,
      horizontalScroll: true,
      zoomKey: 'ctrlKey',
      maxHeight: 400,
      start: minDate,
      end: maxDate,
      editable: false,
      margin: {
        item: 10, // minimal margin between items
        axis: 5   // minimal margin between items and the axis
      },
      orientation: 'top'
    };


    var timeline = new vis.Timeline(container, items, groups, options);


  });

}