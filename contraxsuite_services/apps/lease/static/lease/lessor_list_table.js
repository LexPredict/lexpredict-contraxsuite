'use_strict';

function drawLessorListGrid(url, contentsElementSelector, badgeClass) {

  var dataFields = [
    {name: 'lessor', type: 'string'},
    {name: 'leases_number', type: 'integer'},
    {name: 'url', type: 'string'}
  ];
  var columns = [
    {
      text: 'Name', datafield: 'lessor', minwidth: 200,
      align: 'center', cellsalign: 'left',
      cellsrenderer: defaultLinkFormatter
    },
    {
      text: 'Count', datafield: 'leases_number', width: 90,
      align: 'center', cellsalign: 'right'
    }
  ];

  var customSourceData = {
    url: url,
    badgeClass: badgeClass
  };

  draw_grid(contentsElementSelector,
    dataFields,
    columns,
    false,
    customSourceData,
    {'autorowheight': true});
}