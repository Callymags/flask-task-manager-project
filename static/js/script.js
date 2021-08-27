// Jquery to initialize Materialize elements
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"}); // edge = Materialize class to push toggler to right
    $('.collapsible').collapsible(); // Initialize Collapsible Component
    $('.tooltipped').tooltip(); // Initialize Tooltip
    $('.datepicker').datepicker({
      format: 'dd mmmm, yyyy',
      yearRange: 3,
      showClearBtn: true,
      i18n: {
        done: 'Select'
      }
    }); // Initialize datepicker
  });