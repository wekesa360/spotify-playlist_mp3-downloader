$(document).ready(function() {
    
    $("#loader").removeClass("load");

    $("#btnFetch").click(function() {
        console.log("Ready to go!")
        // add spinner to button
        $(this).html(
        '<i class="fa text-whites"> converting...</i>'
        );
        
        $("#loader").addClass("load");
    });
});