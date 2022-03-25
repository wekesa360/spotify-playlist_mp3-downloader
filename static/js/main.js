$(document).ready(function() {
$("#btnFetch").click(function() {
// add spinner to button
$(this).html(
'<i class="fa fa-circle-o-notch fa-spin"></i> converting...'
);
});
});