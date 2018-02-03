(function () {
  var __bind = function (fn, me) {
      return function () {
        return fn.apply(me, arguments);
      };
    },
    __hasProp = {}.hasOwnProperty,
    __extends = function (child, parent) {
      for (var key in parent) {
        if (__hasProp.call(parent, key)) child[key] = parent[key];
      }

      function ctor() {
        this.constructor = child;
      }

      ctor.prototype = parent.prototype;
      child.prototype = new ctor();
      child.__super__ = parent.prototype;
      return child;
    };

  Annotator.Plugin.Contraxsuite = (function (_super) {
    __extends(Contraxsuite, _super);


    Contraxsuite.prototype.options = {
      getFieldCode: function () {
        return "";
      },
      getFieldTitle: function () {
        return "";
      },
      saveFunc: function (fieldCode, quote) {
      }
    };

    function Contraxsuite(element) {
      this.AnnotationEditorShown = __bind(this.AnnotationEditorShown, this);
      this.AnnotationViewerShown = __bind(this.AnnotationViewerShown, this);
      this.AnnotationEditorSubmit = __bind(this.AnnotationEditorSubmit, this);
      this.AnnotationsLoaded = __bind(this.AnnotationsLoaded, this);
      Contraxsuite.__super__.constructor.apply(this, arguments);
    }


    Contraxsuite.prototype.pluginInit = function () {
      if (!Annotator.supported()) {
        return;
      }

      this.annotator.subscribe("annotationEditorShown", this.AnnotationEditorShown);
      this.annotator.subscribe("annotationEditorSubmit", this.AnnotationEditorSubmit);
      this.annotator.subscribe("annotationViewerShown", this.AnnotationViewerShown);
      this.annotator.subscribe("annotationsLoaded", this.AnnotationsLoaded);

    };

    Contraxsuite.prototype.AnnotationEditorShown = function (editor, annotation) {
      var editor = $('form.annotator-widget > ul.annotator-listing');
      var _select;

      if ($('li.annotator-set-field-value').length == 0) {
        editor.append("<li class='annotator-item'>" +
          "<label class=\"left-side\" for=\"annotator-item-field\">Field: </label>\n" +
          "<select name=\"annotator-item-field\" id=\"annotator-item-field\"\n" +
          "                  style=\"margin-right: 10px; height: 31px\"></select>" +
          "</li>");
        _select = $('#annotator-item-field');
        var fields = this.options.getFieldsByCodeDict();

        var fieldCodesSorted = [];
        var fieldCode;
        var field;

        for (fieldCode in fields) {
          if (fields.hasOwnProperty(fieldCode))
            fieldCodesSorted.push(fieldCode);
        }

        fieldCodesSorted.sort();

        _select.append($("<option>").attr("value", '').text("Neither of Fields"));

        var i = 0;
        for (i in fieldCodesSorted) {
          if (!fieldCodesSorted.hasOwnProperty(i))
            continue;
          fieldCode = fieldCodesSorted[i];
          field = fields[fieldCode];
          _select.append($("<option>").attr("value", field.code).text(field.name));
        }


        editor.append("<li class='annotator-item annotator-set-field-value'></li>");

        var _container = $('li.annotator-set-field-value');
        var checked = "checked = 'checked'";
        var checkbox = "<input  id='annotator-contraxsuite-set-field-value-checkbox' " +
          "                     type='checkbox' " +
          "                     checked='true' />";
        checkbox += "<label for=\"annotator-contraxsuite-set-field-value-checkbox\"" +
          "                 style=\"vertical-align: middle;text-transform:capitalize;\">" +
          "Store field value from this annotation</label>";
        _container.append(checkbox);
      }

      _select = $('#annotator-item-field');
      _select.val(annotation.document_field || '');
    };

    Contraxsuite.prototype.AnnotationViewerShown = function (viewer, annotations) {
      var annotation;
      var txt;
      var field;

      var fieldByCode = this.options.getFieldsByCodeDict();

      var i;
      if (annotations.length > 0) {
        for (i = 0, len = annotations.length; i < len; i++) {
          annotation = annotations[i];

          field = annotation.document_field ? fieldByCode[annotation.document_field] : null;

          if (!annotation.user_id) {
            txt = field ? "Suggested by system for: " + field.name
              : "Suggested by system as not matching any field";
          } else {
            txt = field ? "Annotated by user for: " + field.name :
              "Annotated by user as not matching any field";
          }

          var lis = $('ul.annotator-widget > li.annotator-item');
          $(lis[i]).append("<div class='annotator-viewer-description'>" + txt + "</div>");
        }
      }
    };

    Contraxsuite.prototype.AnnotationsLoaded = function (annotations) {
      var annotation;
      var i;
      var fieldCode;
      var field;
      var fieldName;
      var fieldByCode = this.options.getFieldsByCodeDict();

      for (i = 0; i < annotations.length; i++) {
        annotation = annotations[i];
        fieldCode = annotation.document_field;
        if (fieldCode === null)
          continue;
        $(annotation.highlights).attr("data-field-code", fieldCode);
        if (!annotation.user_id)
          $(annotation.highlights).addClass("annotator-hl-suggested-by-system");
      }


    };


    Contraxsuite.prototype.AnnotationEditorSubmit = function (editor, annotation) {
      annotation.document_field = $('#annotator-item-field').val();
      this.options.saveFunc(annotation.document_field, annotation.quote);
    };

    return Contraxsuite;

  })(Annotator.Plugin);

}).call(this);