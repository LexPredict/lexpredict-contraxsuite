/* Project specific Javascript */

/*
 Formatting hack to get around crispy-forms unfortunate hardcoding
 in helpers.FormHelper:

 if template_pack == 'bootstrap4':
 grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
 using_grid_layout = (grid_colum_matcher.match(self.label_class) or
 grid_colum_matcher.match(self.field_class))
 if using_grid_layout:
 items['using_grid_layout'] = True

 Issues with the above approach:

 1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
 2. Unforgiving: Doesn't allow for any variation in template design
 3. Really Unforgiving: No way to override this behavior
 4. Undocumented: No mention in the documentation, or it's too hard for me to find
 */
$('.form-group').removeClass('row');


// **********************************
// Search: Autocomplete/suggest
// **********************************

function getBloodhound(url){
    return new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        sufficient: 10,
        remote: {
            url: url + '?q=%QUERY',
            wildcard: '%QUERY'
        }
    });
}

function addTypeahead(url, element, name){
    $(element).typeahead(null, {
        name: name,
        display: 'value',
        source: getBloodhound(url),
        limit: 10
    });
}

addTypeahead('/document/complete/text-unit-tag/tag/',
  '#tag_search',
  'tag_search');

addTypeahead('/document/complete/document-property/key/',
  '#key_search',
  'key_search');

addTypeahead('/document/complete/document/description/',
  '#description_search',
  'description_search');

addTypeahead('/document/complete/document/name/',
  '#name_search',
  'name_search');

addTypeahead('/extract/complete/geo-entity/name/',
  '#entity_search',
  'entity_search');

addTypeahead('/analyze/complete/text-unit-classification/name/',
  '#modal_text_unit_classify_class_name',
  'modal_text_unit_classify_class_name');

addTypeahead('/analyze/complete/text-unit-classification/value/',
  '#modal_text_unit_classify_class_value',
  'modal_text_unit_classify_class_value');

var termBloodhood = getBloodhound('/extract/complete/legal-term/term/');
$('#term_search').tagsinput({
    typeaheadjs: {
        name: 'term_search',
        display: 'value',
        valueKey: 'value',
        source: termBloodhood.ttAdapter(),
        limit: 10
    }
});


// **********************************
// Document Detail: Action Buttons
// **********************************

$(".document_detail_action_classify").click(function (e) {
    var text_unit_id = $(this).data("text-unit-id");
    $("#modal_text_unit_classify_text_unit_id").val(text_unit_id);
    $("#modal_text_unit_classify").modal();
});

$(".document_detail_action_tag").click(function (e) {
    var text_unit_id = $(this).data("text-unit-id");
    $("#modal_text_unit_tag_text_unit_id").val(text_unit_id);
    $("#modal_text_unit_tag").modal();
});

// **********************************
// Submit button click
// **********************************

$("#modal_text_unit_classify_button").click(function () {
    $.ajax({
        "type": "POST",
        "dataType": "json",
        "url": "/analyze/submit/text-unit-classification/",
        "data": $(this).parents('.modal-dialog').find('form').serialize(),
        "success": function (result) {
            console.log(result);
            $("#modal_text_unit_classify").modal('hide');
        }
    });
});

$("#modal_text_unit_tag_button").click(function () {
    $.ajax({
        "type": "POST",
        "dataType": "json",
        "url": "/document/submit/text-unit-tag/",
        "data": $(this).parents('.modal-dialog').find('form').serialize(),
        "success": function (result) {
            console.log(result);
            $("#modal_text_unit_tag").modal('hide');
        }
    });
});

// **********************************


// **********************************
// Highlight terms
// **********************************

function highlightTerms(container, mark_if_count){

    // Get global mark variable
    var mark_context = $(container);
    var mark_instance = new Mark(mark_context.get());
    var mark_options = {separateWordSearch: false, className: 'term-mark'};

    $("#highlight_term").on("input", function () {
        if ($(this).val().length >= mark_if_count) {
            mark_instance.unmark(mark_options);
            mark_instance.mark($(this).val(), mark_options);
        }
    });

    // Initial highlighting
    $(document).ready(function () {
        mark_instance.mark($("#highlight_term").val(), mark_options);
    });
}

// **********************************
// Highlight parties
// **********************************

function highlightParties(container, keywords){

    // Get global mark variable
    var mark_context = $(container);
    var mark_instance = new Mark(mark_context.get());
    var mark_options = {separateWordSearch: false, className: 'party-mark'};
    $(document).ready(function () {
        mark_instance.mark(keywords, mark_options);
    });
}

// **********************************


// Handle CSRF
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function custom_notifications( element, remove_prev ){

    if( typeof toastr === 'undefined' ) {
        console.log('notifications: Toastr not Defined.');
        return true;
    }

    if( typeof remove_prev !== 'undefined' ) {
        toastr.remove();
    }

    var notifyElement = $(element),
      notifyPosition = notifyElement.attr('data-notify-position'),
      notifyType = notifyElement.attr('data-notify-type'),
      notifyMsg = notifyElement.attr('data-notify-msg'),
      notifyTimeout = notifyElement.attr('data-notify-timeout'),
      notifyCloseButton = notifyElement.attr('data-notify-close');

    if( !notifyPosition ) { notifyPosition = 'toast-top-right'; } else { notifyPosition = 'toast-' + notifyElement.attr('data-notify-position'); }
    if( !notifyMsg ) { notifyMsg = 'Please set a message!'; }
    if( !notifyTimeout ) { notifyTimeout = 5000; }
    if( notifyCloseButton == 'true' ) { notifyCloseButton = true; } else { notifyCloseButton = false; }

    toastr.options.positionClass = notifyPosition;
    toastr.options.timeOut = Number( notifyTimeout );
    toastr.options.closeButton = notifyCloseButton;
    toastr.options.closeHtml = '<button><i class="icon-remove"></i></button>';

    if( notifyType == 'warning' ) {
        toastr.warning(notifyMsg);
    } else if( notifyType == 'error' ) {
        toastr.error(notifyMsg);
    } else if( notifyType == 'success' ) {
        toastr.success(notifyMsg);
    } else {
        toastr.info(notifyMsg);
    }

    return false;
}

$(document).ready(function () {

    // Enable all tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // add search inputs into export form
    $('input[id$="_search"]').each(function(n, el){
        if ($(el).val() != '') {
            var new_el = $(el).clone().attr("type", "hidden");
            $('#exportForm').append(new_el)
        }
    });

    // export list
    $('.list-export').click(function() {
        $('#exportForm').submit()
    });

    // highlight term typeahead on focus
    $('.bootstrap-tagsinput .tt-input')
      .focus(function(){
          $(this).parent().parent().addClass('input-focus')
      })
      .blur(function(){
          $(this).parent().parent().removeClass('input-focus')
      });

    // init cancel button
    $('.cancel').on('click', function (evt) {
        evt.preventDefault();
        window.history.back();
    });

    // toggle Global search bar
    $('.global-search-switch').click(function(){
        // $('.global-search-bar').slideToggle(200);//.animate({width:'toggle'}, 200);
        $('.global-search-bar, .global-search').slideToggle(200);
        window.scrollTo(0, 0);
    });
    var show_global_search = false;
    $('.global-search [id$="_search"]').each(function(n, el){
        if ($(el).val() != '') {
            show_global_search = true;
        }
    });
    if (show_global_search){
        $('.global-search-bar, .global-search').slideToggle(200);
    }


    // show messages
    if( typeof SEMICOLON !== 'undefined' ) {
        SEMICOLON.widget.notifications = custom_notifications
    }
    $('.notification').each(function(){
        SEMICOLON.widget.notifications($(this))
    })

});
