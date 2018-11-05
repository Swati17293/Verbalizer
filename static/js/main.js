$(document).ready( function() {
    $('#submit_btn').click(function(e) {
        e.preventDefault();
        var sparqlQuery = $('#query').val();
        $.ajax({
            type : "POST",
            url : "/",
            data: {query: sparqlQuery},
            success: function(answer) {
                $('#answer').html(answer);
            }
        });
    });
});