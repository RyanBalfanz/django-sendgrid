django.jQuery(document).ready(function() {
   django.jQuery('#emailmessage_form #body-group td.field-data').first().parent().parent().parent().after('<iframe id="html-preview" style="width:100%; height: 100%"></iframe>');
   var content = django.jQuery('<div>').html(django.jQuery('<div>').html(django.jQuery('#emailmessage_form #body-group td.field-data p').html().toString().replace(/<br>/g, '')).text());
   var ifr = django.jQuery('#html-preview');
   ifr.contents().find('body').html(content);
   ifr.height(ifr.contents().height());
});
