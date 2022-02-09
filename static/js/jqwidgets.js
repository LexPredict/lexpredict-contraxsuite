  // Base jqxgrid options and utils

  var base_jqxgrid_options = {
    altrows: true,
    columnsheight: 40,
    rowsheight: 40,
    filterrowheight: 40,
    width: '100%',
    editable: false,
    columnsresize: true,
    groupable: false,
    sortable: true,
    filterable: true,
    showstatusbar: false,
    statusbarheight: 50,
    showaggregates: true,
    pageable: true,
    pagermode: 'default',
    autoheight: true,
    autorowheight: false, // auto?
    enabletooltips: true, // another solution: http://www.jqwidgets.com/community/topic/grid-tooltip/
    pagesize: 10,
    pagesizeoptions: ['10', '15', '20', '30', '40', '50', '100'],
    virtualmode: false
  };

  var draw_grid = function(selector, datafields, columns, server_pagination,
                           custom_source_data, custom_grid_options) {
    var source = {
      url: window.location.href,
      datafields: datafields,
      datatype: "json",
      id: 'pk',
      root: 'data',
      data: { enable_pagination: false },
      beforeprocessing: function (data) {
        // for server-side pagination
        source.totalrecords = data.total_records;
        disable_data_export = data.disable_data_export || false;
        render_error(data);
      },
      loadError: function (xhr, status, error){
        if(xhr.responseText=='logout'){
          window.location.href = login_url
        }
      }
    };

    if (custom_source_data) {
      if (custom_source_data.badgeClass){
        custom_source_data.loadComplete = function(data){
          $('.'+custom_source_data.badgeClass).text(data.total_records || 0)
        }
      }
      source = $.extend({}, source, custom_source_data);
    }

    var dataAdapter = new $.jqx.dataAdapter(source);

    var current_jqxgrid_options = {
      source: dataAdapter,
      columns: columns,
      // for server-side pagination
      rendergridrows: function () {
        return dataAdapter.records;
      },
      updatefilterconditions: function (type, defaultconditions) {
        var stringcomparisonoperators = ['EMPTY', 'NOT_EMPTY', 'CONTAINS', 'CONTAINS_CASE_SENSITIVE', 'FULL_TEXT_SEARCH',
          'DOES_NOT_CONTAIN', 'DOES_NOT_CONTAIN_CASE_SENSITIVE', 'STARTS_WITH', 'STARTS_WITH_CASE_SENSITIVE',
          'ENDS_WITH', 'ENDS_WITH_CASE_SENSITIVE', 'EQUAL', 'EQUAL_CASE_SENSITIVE', 'NULL', 'NOT_NULL'];
        var numericcomparisonoperators = ['EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'NULL', 'NOT_NULL'];
        var datecomparisonoperators = ['EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'NULL', 'NOT_NULL'];
        var booleancomparisonoperators = ['EQUAL', 'NOT_EQUAL'];
        switch (type) {
          case 'stringfilter':
            return stringcomparisonoperators;
          case 'numericfilter':
            return numericcomparisonoperators;
          case 'datefilter':
            return datecomparisonoperators;
          case 'booleanfilter':
            return booleancomparisonoperators;
        }
      }
    };

    if (custom_grid_options) {
      current_jqxgrid_options = $.extend({}, current_jqxgrid_options, custom_grid_options);
    }

    if (typeof server_pagination !== 'undefined' && server_pagination) {
      current_jqxgrid_options.virtualmode = true;
      current_jqxgrid_options.autoheight = true;
      current_jqxgrid_options.source._source.data.enable_pagination = server_pagination;
      current_jqxgrid_options.source._source.sort = function () {
        // update the grid and send a request to the server.
        $(selector).jqxGrid('updatebounddata');
      };
      current_jqxgrid_options.source._source.filter = function () {
        // update the grid and send a request to the server.
        $(selector).jqxGrid('updatebounddata', 'filter');
      };
    }

    var opts = $.extend({}, base_jqxgrid_options, current_jqxgrid_options);

    // needed to add custom filters (full text search)
    $(selector).bind('bindingcomplete', function (a, b) {
      var localizationObject = {};
      filterstringcomparisonoperators = ['empty', 'not empty', 'contains', 'contains(match case)', 'full text search(or contains)',
        'does not contain', 'does not contain(match case)', 'starts with', 'starts with(match case)',
        'ends with', 'ends with(match case)', 'equal', 'equal(match case)', 'null', 'not null'];
      filternumericcomparisonoperators = ['equal', 'not equal', 'less than', 'less than or equal', 'greater than', 'greater than or equal', 'null', 'not null'];
      filterdatecomparisonoperators = ['equal', 'not equal', 'less than', 'less than or equal', 'greater than', 'greater than or equal', 'null', 'not null'];
      filterbooleancomparisonoperators = ['equal', 'not equal'];
      localizationObject.filterstringcomparisonoperators = filterstringcomparisonoperators;
      localizationObject.filternumericcomparisonoperators = filternumericcomparisonoperators;
      localizationObject.filterdatecomparisonoperators = filterdatecomparisonoperators;
      localizationObject.filterbooleancomparisonoperators = filterbooleancomparisonoperators;

      // change default message for empty data set if user_projects_selected is empty
      if (!window.user_projects_selected.length && typeof(skip_project_selection) === 'undefined'){
        localizationObject.emptydatastring = "Select Project(s) Above for Viewing Data";
        $(".project_selection label")
            .fadeOut(300)
            .fadeIn(300)
            .fadeOut(300)
            .fadeIn(300)
      }
      else if (window.table_warning) {
        localizationObject.emptydatastring = window.table_warning;
      }
      else {
        localizationObject.emptydatastring = "No data to display";
      }
      $(selector).jqxGrid('localizestrings', localizationObject);
    });

    $(selector).jqxGrid(opts)
  };

  // custom cell renderer for jqxgrid
  function renderCell(defaulthtml, new_value) {
    var el = $(defaulthtml);
    el.html(new_value);
    return el.clone().wrap('<div>').parent().html();
  }

  function linkFormatter(defaulthtml, url, val, new_window, button_options) {
    if (new_window || window.name == 'new'){
      var window_width = $(window).width()*0.8;
      var window_height = $(window).height()*0.8;
      var new_value = '<a href="' + url +
          '" onclick="window.open(this.href, \'new\', \'width=' +
          window_width + ', height=' + window_height + ',scrollbars\'); return false;">' +
          val + '</a>';
    }
    else {
      new_value = '<a href="' + url + '">' + val + '</a>';
    }
    if (button_options) {
      new_value = $(new_value)
          .addClass('btn')
          .addClass(button_options.klass)
          .css({margin: 0, height: '100%', width: '100%'});
      if (button_options.css){
        new_value.css(button_options.css)
      }
      defaulthtml = $(defaulthtml);
      defaulthtml.css({margin: 0, padding: '2px', height: '100%'})
    }
    return renderCell(defaulthtml, new_value);
  }

  function defaultLinkFormatter(index, columnfield, value, defaulthtml, columnproperties, row) {
    return linkFormatter(defaulthtml, row.url, value);
  }

  function baseLinkFormatter(url, value, defaulthtml, columnproperties) {
    if (columnproperties.cellsformat != '') {
      if ($.jqx.dataFormat) {
        if ($.jqx.dataFormat.isDate(value)) {
          value = $.jqx.dataFormat.formatdate(value, columnproperties.cellsformat);
        }
        else if ($.jqx.dataFormat.isNumber(value)) {
          value = $.jqx.dataFormat.formatnumber(value, columnproperties.cellsformat);
        }
      }
    }
    return linkFormatter(defaulthtml, url, value);
  }

  function updateLinkFormatter(index, columnfield, value, defaulthtml, columnproperties, row) {
    var main = window.location.pathname.split('/')[1];
    var url = ['', main, row.slug || row.pk, ''].join('/');
    return baseLinkFormatter(url, value, defaulthtml, columnproperties);
  }

  function detailLinkFormatter(index, columnfield, value, defaulthtml, columnproperties, row) {
    var main = window.location.pathname.split('/')[1];
    var url = ['', main, row.slug || row.pk, 'detail', ''].join('/');
    return baseLinkFormatter(url, value, defaulthtml, columnproperties);
  }

  function bool_renderer(index, columnfield, value, defaulthtml, columnproperties, row) {
    var fa_cls = value ? 'fa-check-square-o' : 'fa-square-o';
    value = '<i class="fa ' + fa_cls + '"></i>';
    return renderCell(defaulthtml, value)
  }

  function render_in_table_knob(val, row, columnfield) {
    var $knob = $('<div><input type="text" class="in-table-knob"></div>');
    $knob
        .find('input')
        .attr('value', (val || 0) + '%')
        .knob({
          readOnly: true,
          width: 50,
          height: 50,
          skin: "tron",
          fgColor: "#85AED2",
          inputColor: "#666",
          draw: function () {
            $(this.i).css({'font-size': '10px', 'margin-top': '18px'});
          }
        });
    var $canvas = $knob.find('canvas');
    var dataURL = $canvas[0].toDataURL();
    $canvas.remove();
    $knob.prepend($('<img src="' + dataURL + '" width="50px" height="50px">'));
    // TODO: update
    if (columnfield=='progress') {
      $knob.attr('title', 'Total Documents: ' + row.total_documents_count + '\nCompleted Documents: ' + row.completed_documents_count)
    }
    return $knob;
  }

  function knob_cellsrenderer(index, columnfield, value, defaulthtml, columnproperties, row) {
    var knobbed = render_in_table_knob(value, row, columnfield);
    var $defaulthtml = $(defaulthtml).css('margin-top', '4px');
    return renderCell($defaulthtml, knobbed);
  }

  function inactive_cellsclassrenderer(row, columnfield, value, data) {
    if (!data.is_active){
      return 'inactive'
    }
  }

  function note_renderer(index, columnfield, value, defaulthtml, columnproperties, row) {
    // this throws error on simple text like ",.'p"
    // var $defaulthtml = $(defaulthtml).attr('title', $(value).text());
    var $defaulthtml = $(defaulthtml);
    return renderCell($defaulthtml, value)
  }

  // helpers for jquery-confirm popups
  function reviewers_renderer(index, columnfield, value, defaulthtml, columnproperties, row){
    var $defaulthtml = $(defaulthtml).prop('title', row.reviewers_usernames);
    return renderCell($defaulthtml, value);
  }

  var cancel_button_action = {
    text: 'Cancel',
    btnClass: 'btn-u btn-sm btn-l',
    action: function(){}
  };
  var ajax_error_handler = function(xhr){
    console.log(xhr);
    SEMICOLON.widget.notifications($('<span class="notification" data-notify-type="danger" data-notify-msg="Error"></span>'));
  };
  var ajax_success_handler = function(response){
    var status = response.level || response.status;
    SEMICOLON.widget.notifications($('<span class="notification" data-notify-type="' + status + '" data-notify-msg="' + response.message.replace(/(['"])/g, "") + '"></span>'))
  };

  // remove item on "Yes" button click - send ajax request, refresh table
  function show_remove_popup(url, grid){
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'orange',
      icon: 'fa fa-warning text-warning',
      title: 'Delete this object?',
      backgroundDismiss: true,
      content: 'url:' + url,
      buttons: {
        remove: {
          text: 'Remove',
          btnClass: 'btn-u btn-sm btn-w',
          action: function(){
            $.ajax({
              method: 'POST',
              url: url,
              data: { csrfmiddlewaretoken: token },
              success: function(response){
                grid.jqxGrid('updatebounddata');
                ajax_success_handler(response)
              },
              error: ajax_error_handler
            })
          }
        },
        cancel: cancel_button_action
      }
    });
  }

  // tag text unit popup
  function tag_popup(target, pk, grid, tag_pk, tag) {
    if (typeof tag_pk === "undefined"){
      tag_pk = null;
      tag = ''
    }
    if (target == 'document') {
      var url = doc_tag_url;
      var title = 'Tag Document'
    }
    else if (target == 'text_unit') {
      url = tu_tag_url;
      title = 'Tag Text Unit'
    }
    else if (target == 'cluster_documents') {
      url = cl_doc_tag_url;
      title = "Tag cluster's documents"
    }
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'blue',
      icon: 'fa fa-tags',
      title: title,
      backgroundDismiss: true,
      content: '<input type="text" class="form-control" name="tag" id="tag" placeholder="Tag" value="' + tag + '">',
      buttons: {
        tag: {
          text: 'Save',
          btnClass: 'btn-u btn-sm',
          action: function(){
            var tag = this.$content.find('input').val();
            if (tag) {
              $.ajax({
                method: 'POST',
                url: url,
                data: {
                  csrfmiddlewaretoken: token,
                  owner_id: pk,
                  tag_pk: tag_pk,
                  tag: tag },
                success: function(response){
                  if (grid){
                    $(grid).jqxGrid('updatebounddata');
                  }
                  ajax_success_handler(response)
                },
                error: ajax_error_handler
              })
            }
          }
        },
        cancel: cancel_button_action
      }
    })
  }

  // classify text unit popup
  function classify_text_unit_popup(pk, grid) {
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'blue',
      icon: 'fa fa-gavel',
      title: 'Classify Text Unit',
      backgroundDismiss: true,
      buttons: {
        classify: {
          text: 'Save',
          btnClass: 'btn-u btn-sm',
          action: function(){
            var class_name = this.$content.find('#text_unit_classify_class_name').val();
            var class_value = this.$content.find('#text_unit_classify_class_value').val();
            if (class_name && class_value) {
              $.ajax({
                method: 'POST',
                url: tuc_submit_url,
                data: {
                  csrfmiddlewaretoken: token,
                  owner_id: pk,
                  class_name: class_name,
                  class_value: class_value },
                success: function(response){
                  if (grid){
                    $(grid).jqxGrid('updatebounddata');
                  }
                  ajax_success_handler(response)
                },
                error: ajax_error_handler
              })
            }
          }
        },
        cancel: cancel_button_action
      },
      content: '<input type="text" class="form-control" id="text_unit_classify_class_name" name="class_name" placeholder="Class Name">' +
      '<input type="text" class="form-control" id="text_unit_classify_class_value" name="class_value" placeholder="Class Value">',
      onContentReady: function () {
        this.$content.css('overflow-y', 'scroll');
        addTypeahead(tuc_type_name_url,
            '#text_unit_classify_class_name',
            'text_unit_classify_class_name');
        addTypeahead(tuc_type_value_url,
            '#text_unit_classify_class_value',
            'text_unit_classify_class_value');
      }
    })
  }

  // mark Document completed OR reopen
  function mark_document_completed(text, url, grid) {
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'orange',
      icon: 'fa fa-gavel text-warning',
      title: text,
      content: '',
      backgroundDismiss: true,
      buttons: {
        action: {
          text: 'Go',
          btnClass: 'btn-u btn-sm btn-w',
          action: function(){
            $.ajax({
              method: 'POST',
              url: url,
              data: {
                csrfmiddlewaretoken: token
              },
              success: function(response){
                var is_nested = grid.hasClass('sub-grid');
                var task_queue_grid = is_nested ? grid.parents('.jqxgrid') : grid;
                task_queue_grid.jqxGrid('updatebounddata');
                if (is_nested) {
                // for Task Queue list view
                  task_queue_grid.on('bindingcomplete', function(){
                    task_queue_grid.jqxGrid('showrowdetails', grid.attr('id').replace('grid', ''))
                  });
                }
                ajax_success_handler(response)
              },
              error: ajax_error_handler
            })
          }
        },
        cancel: cancel_button_action
      }
    });
  }

  // remove Document from Task Queue
  function remove_document_from_task_queue(text, url, grid) {
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'orange',
      icon: 'fa fa-remove text-warning',
      title: text,
      content: '',
      useBootstrap: false,
      boxWidth: "500px",
      backgroundDismiss: true,
      buttons: {
        action: {
          text: 'Confirm',
          btnClass: 'btn-u btn-sm btn-w',
          action: function(){
            $.ajax({
              method: 'POST',
              url: url,
              data: {
                csrfmiddlewaretoken: token
              },
              success: function(response){
                var is_nested = grid.hasClass('sub-grid');
                var task_queue_grid = is_nested ? grid.parents('.jqxgrid') : grid;
                task_queue_grid.jqxGrid('updatebounddata');
                if (is_nested) {
                  // for Task Queue list view
                  task_queue_grid.on('bindingcomplete', function(){
                    task_queue_grid.jqxGrid('showrowdetails', grid.attr('id').replace('grid', ''))
                  });
                }
                else {
                  // TODO!!! append removed task queue name/url in dropdown "Add to Task Queue
                }
                ajax_success_handler(response)
              },
              error: ajax_error_handler
            })
          }
        },
        cancel: cancel_button_action
      }
    });
  }

  // purge task
  function purge_task_popup(pk, url, grid) {
     show_task_popup(pk, url, grid,
        'Purge this task?',
        'fa fa-eraser text-warning');
  }

  function recall_task_popup(pk, url, grid, title, sessionId) {
     var token = jQuery("[name=csrfmiddlewaretoken]").val();
     $.ajax({
       method: 'GET',
       url: url,
       data: {
         task_pk: pk,
         csrfmiddlewaretoken: token,
         session_id: sessionId
       },
       success: function(response) {
         var popText = 'Restart ' + response['tasks']
             + (response['tasks'] === 1 ? ' task ' : ' tasks ')
             + 'with "' + response['status'] + '" status?';
         show_task_popup(pk, url, grid,
            title,
            'fa fa-refresh text-warning',
            sessionId,
            popText);
       },
       error: ajax_error_handler
     });
  }

  function show_task_popup(pk, url, grid, title, icon,
                           sessionId, content) {
    var token = jQuery("[name=csrfmiddlewaretoken]").val();
    $.confirm({
      type: 'orange',
      icon: icon,
      title: title,
      content: content || '',
      backgroundDismiss: true,
      buttons: {
        action: {
          text: 'Confirm',
          btnClass: 'btn-u btn-sm btn-w',
          action: function(){
            $.ajax({
              method: 'POST',
              url: url,
              data: {
                task_pk: pk,
                csrfmiddlewaretoken: token,
                session_id: sessionId
              },
              success: function(response){
                grid.jqxGrid('updatebounddata');
                ajax_success_handler(response)
              },
              error: ajax_error_handler
            })
          }
        },
        cancel: cancel_button_action
      }
    });
  }

  // open popup window on menu button click in jqxgrid
  var show_menu = function (menu_data, grid, pk, width) {
    var default_link_data = {
      url: '#', cls: '', icon: '', onclick: '', text: '', target: '_parent'
    };
    var ul = $('<ul class="popup-menu"></ul>');
    $.each(menu_data, function(index, item){
      item = $.extend({}, default_link_data, item);
      var itemData = '';
      if (item['data']) {
          for (var dataKey in item['data'])
              itemData += ' data-' + dataKey + '="' + item['data'][dataKey] + '" ';
      }
      var li = $('<li><a href="' + item.url +
                     '" class="' + item.cls +
                     '" target"' + item.target +
                   '" onclick="' + item.onclick +
                   '" ' + itemData +
                   'data-pk="' + pk + '"><i class="' + item.icon + '"></i>' + item.text + '</a></li>');
      ul.append(li)
    });
    width = typeof width === "undefined" ? 200 : width;
    var jc = $.dialog({
      title: null,
      content: ul,
      type: 'blue',
      animation: 'right',
      closeAnimation: 'right',
      backgroundDismiss: true,
      useBootstrap: false,
      boxWidth: width + "px",
      closeIconClass: 'fa fa-remove',
      onContentReady: function () {
        $('.popup-menu a').click(function() {
          jc.close();
        });
        $('.popup-menu a.remove').click(function(event) {
          event.preventDefault();
          show_remove_popup($(this).attr('href'), grid)
        });
        $('.popup-menu a.retrain-classifier').click(function(event) {
          event.preventDefault();
          alert('Not implemented')
        });
        $('.popup-menu a.tag-text-unit').click(function(event) {
          event.preventDefault();
          tag_popup('text_unit', pk)
        });
        $('.popup-menu a.classify-text-unit').click(function(event) {
          event.preventDefault();
          classify_text_unit_popup(pk)
        });
        $('.popup-menu a.purge-task').click(function(event) {
          event.preventDefault();
          purge_task_popup(pk, $(this).attr('href'), grid);
        });
        $('.popup-menu a.recall-task').click(function(event) {
          event.preventDefault();
          var popupTitle = $(this).data('title');
          recall_task_popup(pk, $(this).attr('href'), grid, popupTitle);
        });
        $('.popup-menu a.recall-session').click(function(event) {
          event.preventDefault();
          var popupTitle = $(this).data('title');
          var sessionId = $(this).data('session');
          recall_task_popup(pk, $(this).attr('href'), grid, popupTitle, sessionId);
        });
        $('.popup-menu a.mark-document-completed').click(function(event) {
          event.preventDefault();
          mark_document_completed($(this).text(), $(this).attr('href'), grid)
        });
        $('.popup-menu a.remove-from-task-queue').click(function(event) {
          event.preventDefault();
          remove_document_from_task_queue($(this).text(), $(this).attr('href'), grid)
        });
      }
    });
    return true
  };

  function expand_row(event, grid, row_number){
    event.preventDefault();
    $(grid).jqxGrid('showrowdetails', row_number)
  }

  function apply_filter(grid, column_name, sentence, tabs_id, tab_no){
    // grid and tabs_id - html elements, i.e. ".jqxgrid" and "#tab1"
    var filtergroup = new $.jqx.filter();
    var filter = filtergroup.createfilter('stringfilter', sentence, 'contains');
    filtergroup.addfilter(1, filter);
    $(grid).jqxGrid('addfilter', column_name, filtergroup);
    $(grid).jqxGrid('applyfilters');
    $(tabs_id).tabs('option', 'active', tab_no)
  }

  // resize table if window or container resized
  $( window ).resize(function() {
    if ($('.jqxgrid')) {
      $('.jqxgrid').jqxGrid('refresh');
    }
  });
  $('.dev-page-sidebar-collapse, .dev-page-sidebar-minimize').click(function() {
    setTimeout(function(){
      $('.jqxgrid').jqxGrid('refresh')
    }, 200)
  });

  // init Update button
  $(".update-jqxgrid-data").click(function () {
    $(this).parent().siblings().find('.jqxgrid').jqxGrid('updatebounddata');
  });

  // init "Selection mode" button
  $('.jqxgrid-select-mode').click(function(){
    $(this).toggleClass('active');
    var mode = $(this).hasClass('active') ? 'singlecell' : 'singlerow';
    $(this).parent().siblings().find('.jqxgrid').jqxGrid('selectionmode', mode);
  });

  // init "Switch filterrow"
  $('.jqxgrid-filterrow').click(function(){
    $(this).toggleClass('active');
    var value = $(this).hasClass('active') ? true : false;
    $(this).parent().siblings().find('.jqxgrid').jqxGrid('showfilterrow', value);
  });

  function now(){
    var currentdate = new Date();
    return currentdate.getFullYear().toString()
        + (currentdate.getMonth()+1).toString()
        + currentdate.getDate().toString()
        + '_'
        + currentdate.getHours().toString()
        + currentdate.getMinutes().toString();
  }

  // init "csvExport" button
  $(".gridExport li").click(function() {
    var to = $(this).data('export-to');
    var $grid = $(this).parents('.gridExport').parent().siblings().find('.jqxgrid');
    var source = $grid.jqxGrid('source');
    var query_data_initial = source._source.data;
    var query_data = $.extend({}, query_data_initial);
    var filterinfo = $grid.jqxGrid('getfilterinformation');
    query_data['filterscount'] = filterinfo.length;
    for (var i = 0; i < filterinfo.length; i++) {
        var filter = filterinfo[i];
        var filterdata = filter.filter.getfilters()[0];
        query_data['filterdatafield'+i] = filter.filtercolumn;
        query_data['filteroperator'+i] = filterdata.operator;
        query_data['filtercondition'+i] = filterdata.condition;
        query_data['filtervalue'+i] = filterdata.value;
    }
    var sortinfo = $grid.jqxGrid('getsortinformation');
    if (typeof sortinfo.sortcolumn !== 'undefined') {
      query_data['sortdatafield'] = sortinfo.sortcolumn;
      query_data['sortorder'] = sortinfo.sortdirection.ascending ? 'asc' : 'desc';
    }
    query_data['export_to'] = to;
    query_data['return_raw_data'] = '1';
    var conjunct = source._source.url.indexOf('?') >= 0 ? '&' : '?';
    var downloadUrl = source._source.url.replace('#', '') + conjunct + $.param(query_data);
    if (disable_data_export) {
      window.open(downloadUrl, "_self");
    } else {
      window.open(downloadUrl);
    }
    source._source.data = query_data_initial;
  });

  function render_error(data) {
    window.table_warning = data.table_warning;
    if (!data) return;
    var messages = [];
    var severity = 'Warning';
    if (data.error) {
        messages.push(safe_tags_replace(data.error));
        severity = 'Error';
    }
    if (data.warning)
        messages.push(safe_tags_replace(data.warning));
    if (!messages.length) return;
    var msg = messages.join('<br/><br/>');
    var dlgData = {title: severity,
                   backgroundDismiss: true,
                   content: msg};
    if (!data.prompt_reload)
        $.alert(dlgData);
    else {
        dlgData.buttons = {
          confirm: {
            text: 'Reload',
            btnClass: 'btn-u btn-sm',
            action: function() {
                window.location.reload();
            }
          },
          cancel: {
            btnClass: 'btn-u btn-sm btn-l',
            text: 'Okay'
          }
        };
        $.confirm(dlgData);
    }
  }

var tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function replaceTag(tag) {
    return tagsToReplace[tag] || tag;
}

function safe_tags_replace(str) {
    return str.replace(/[&<>]/g, replaceTag);
}