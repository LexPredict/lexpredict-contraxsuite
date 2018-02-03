'use_strict';

function drawLeaseDocumentsGrid(url, contentsElementSelector, badgeClass, showLessorName) {

  function lessorLinkFormatter(index, columnfield, value, defaulthtml, columnproperties, row) {
    return linkFormatter(defaulthtml, row.lessor_url, value);
  }

  var dataFields = [
    {name: 'pk', type: 'int'},
    {name: 'url', type: 'string'},
    {name: 'name', type: 'string'},
    {name: 'property_type', type: 'string'},
    {name: 'area_size_sq_ft', type: 'float'},
    {name: 'address', type: 'string'},
    {name: 'lessor', type: 'string'},
    {name: 'lessor_url', type: 'string'},
    {name: 'lessee', type: 'string'},
    {name: 'commencement_date', type: 'date'},
    {name: 'expiration_date', type: 'date'},
    {name: 'lease_type', type: 'string'},
    {name: 'total_rent_amount', type: 'float'},
    {name: 'rent_due_frequency', type: 'string'},
    {name: 'mean_rent_per_month', type: 'float'},
    {name: 'security_deposit', type: 'float'}
  ];
  var columns = [
    {
      text: 'ID', datafield: 'pk', width: 50,
      align: 'center', cellsalign: 'center'
    },
    {
      text: 'Name', datafield: 'name', minwidth: 100,
      align: 'center', cellsalign: 'left',
      cellsrenderer: defaultLinkFormatter
    },
    {
      text: 'Property Type', datafield: 'property_type', width: 90,
      align: 'center', cellsalign: 'center'
    },
    {
      text: 'Area Size (sq. ft.)', datafield: 'area_size_sq_ft', width: 80,
      align: 'right', cellsalign: 'right', cellsformat: 'f2'
    },
    {
      text: 'Address', datafield: 'address', minwidth: 150,
      align: 'center', cellsalign: 'center'
    }];

  if (showLessorName) {
    columns.push({
      text: 'Lessor', datafield: 'lessor', minwidth: 150,
      align: 'center', cellsalign: 'center',
      cellsrenderer: lessorLinkFormatter
    });
  }

  columns = columns.concat([
    {
      text: 'Lessee', datafield: 'lessee', minwidth: 150,
      align: 'center', cellsalign: 'center'
    },
    {
      text: 'Commencement', datafield: 'commencement_date', width: 70,
      align: 'center', cellsalign: 'center', cellsformat: 'd'
    },
    {
      text: 'Expiration', datafield: 'expiration_date', width: 70,
      align: 'center', cellsalign: 'center', cellsformat: 'd'
    },
    {
      text: 'Lease Type', datafield: 'lease_type', width: 70,
      align: 'center', cellsalign: 'center'
    },
    {
      text: 'Total Rent Amount', datafield: 'total_rent_amount', width: 100,
      align: 'right', cellsalign: 'right', cellsformat: 'c2'
    },
    {
      text: 'Rent Due Frequency', datafield: 'rent_due_frequency', width: 70,
      align: 'center', cellsalign: 'center'
    },
    {
      text: 'Mean Rent Per Month', datafield: 'mean_rent_per_month', width: 100,
      align: 'right', cellsalign: 'right', cellsformat: 'c2'
    },
    {
      text: 'Security Deposit', datafield: 'security_deposit', width: 100,
      align: 'right', cellsalign: 'right', cellsformat: 'c2'
    }
  ]);

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