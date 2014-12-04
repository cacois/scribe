var config = null;
var users = null;
var categories = null;

//** Tag Regular Expressions **//
var userRE = /(@\w+)/ig
var tagsRE = /(#\w+)/ig
// regular expressions to match various date formats
var dateREs = [/\d{1,2}\/\d{1,2}\/(\d\d){1,2}( |$)/ig,
               /\d{1,2}-\d{1,2}-(\d\d){1,2}( |$)/ig,
               /(\d\d){1,2}-\d{1,2}-(\d){2}( |$)/ig,
               /(\d\d){1,2}\/\d{1,2}\/(\d){2}( |$)/ig]

var dateFormats = ["MM-DD-YY","MM-DD-YYYY"]

var manualTags = {'users': [],
                  'categories': [],
                  'tags': []};

//** Helper Methods **//

var tagFields = {
    users: {element: null, api: null},
    tags: {element: null, api: null},
    categories: {element: null, api: null},
    date: {element: null, api: null}
};

function registerTagFields(tagsElem, usersElem, categoriesElem, dateElem) {
    tagFields.tags.element = tagsElem;
    tagFields.users.element = usersElem;
    tagFields.categories.element = categoriesElem;
    tagFields.date.element = dateElem;

    tagFields.tags.api = tagFields.tags.element.tagsManager();
    tagFields.users.api = tagFields.users.element.tagsManager();
    tagFields.categories.api = tagFields.categories.element.tagsManager();
    tagFields.date.api = tagFields.date.element.tagsManager({maxTags: 1});
}

function initTypeahead() {

    // initialize the suggestion engines
    var users = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch: $SCRIPT_ROOT + '/api/users'
    });

    var categories = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      // `states` is an array of state names defined in "The Basics"
      local: $.map(config.categories, function(cat) { return { value: cat }; })
    });

    users.initialize();
    categories.initialize();

    $('#tm-users').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      },
      {
        name: 'users',
        displayKey: 'value',
        // `ttAdapter` wraps the suggestion engine in an adapter that
        // is compatible with the typeahead jQuery plugin
        source: users.ttAdapter()
      }
    ).on('typeahead:selected', function (e, d) {
      tagFields.users.api.tagsManager("pushTag", d.value);
    });

    $('#tm-categories').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      },
      {
        name: 'categories',
        displayKey: 'value',
        // `ttAdapter` wraps the suggestion engine in an adapter that
        // is compatible with the typeahead jQuery plugin
        source: categories.ttAdapter()
      }
    ).on('typeahead:selected', function (e, d) {
      tagFields.categories.api.tagsManager("pushTag", d.value);
    });

    // these are some css hacks to fix a bug in twitter typeahead integration with tag manager
    $('.typeahead').not('[id]').css("opacity", "0");
    $('.typeahead').css("background-color", "rgb(255,255,255)"); // note: does not work in Firefox
}

function parseUsers(str) {
    var users = str.match(userRE);

    if(users) {
      users.forEach(function(user) {
        tagFields.users.api.tagsManager('pushTag',user.split('@')[1]);
      });
    }
}

function parseHashTags(str) {
    var tags = str.match(tagsRE);

    if(tags) {
      var tag = null;
      tags.forEach(function(tag) {
        tag = tag.split('#')[1];

        // check to see if hashtag is a known category tag
        if($.inArray(tag, config.categories) >= 0) {
          tagFields.categories.api.tagsManager('pushTag',tag);
        }
        else {
          tagFields.tags.api.tagsManager('pushTag',tag);
        }
      });
    }
}

function parseDate(str) {
    var dateStr = null;
    dateREs.forEach(function(re) {
        matched = str.match(re);
        if(matched) dateStr = matched[0];
    });

    if(dateStr) {
        // validate date string
        if (moment(dateStr, dateFormats).isValid()) {
            tagFields.date.api.tagsManager('pushTag', moment(dateStr, dateFormats).format('MMMM Do YYYY'));
        }
    }
}

function recordManualTag(type) {
  var tags = tagFields.users.api.tagsManager('tags');
  manualTags[type].push(tags[tags.length-1]);
  console.log('Saved tag: ' + JSON.stringify(manualTags));
}

function resetTags() {
    tagFields.users.api.tagsManager('empty');
    manualTags.users.forEach(function(tag){
      tagFields.users.api.tagsManager('pushTag', tag);
    });

    tagFields.tags.api.tagsManager('empty');
    manualTags.tags.forEach(function(tag){
      tagFields.tags.api.tagsManager('pushTag', tag);
    });

    tagFields.categories.api.tagsManager('empty');
    manualTags.categories.forEach(function(tag){
      tagFields.categories.api.tagsManager('pushTag', tag);
    });

    tagFields.date.api.tagsManager('empty');
}

function setConfig(conf) {
    config = conf;
}

/**
 * updateConfig()
 *
 * Send an ajax post to the server with the client's current config dict, which
 * may contain new values fo rusers, tags, or categories. The server will accept
 * this data and update the global config to add (not delete) to these lists
 * based on any new values.
 */
function updateConfig() {
    $.ajax({
        url: $SCRIPT_ROOT + '/api/config',
        type: "POST",
        data: JSON.stringify(config),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(res){
          console.log('Posted. response: ' + JSON.stringify(res));
        }
    }).fail(function( jqXhr, textStatus, errorThrown ){ console.log( 'POST error: ' + errorThrown ); });
}

function saveActivity() {
  // submit form
  $('.form').submit();

  // move data from form into background display of submitted activities
  console.log('tags: ' + $('[name=hidden-tm-tags]').val());
  console.log('users: ' + $('[name=hidden-tm-users]').val());
  console.log('categories: ' + $('[name=hidden-tm-categories]').val());
  console.log('date: ' + $('[name=hidden-tm-date]').val());
}

function resetForm() {
  $('[name=hidden-tm-tags]').val("");
  $('[name=hidden-tm-users]').val("");
  $('[name=hidden-tm-categories]').val("");
  $('[name=hidden-tm-date]').val("");
  $('[name=activity]').val("");

  tagFields.tags.api.tagsManager('empty');
  tagFields.users.api.tagsManager('empty');
  tagFields.categories.api.tagsManager('empty');
  tagFields.date.api.tagsManager('empty');

  manualTags = {'users': [], 'categories': [], 'tags': []};
}
