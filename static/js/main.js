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

    $('.list-group').click(function(e) {
        e.preventDefault();
        $('.list-group a').removeClass('active');
        $(event.target).addClass('active');
        var listLabel = $(event.target).text();
        $.ajax({
            type : "POST",
            url : "/",
            data: {label: listLabel},
            success: function(query) {
                $('.form-control').val(query);
            }
        });
    });

    $('#shuffle').click(function(e) {
        e.preventDefault();
        $('.list-group a').removeClass('active');
        $.ajax({
            type : "POST",
            url : "/",
            data: {sample: "sampleQueries"},
            success: function(sampleQueries) {
                var sample = JSON.parse(sampleQueries);
                var i = 0;
                $(".list-group a").each(function(){
                    $(this).text(sample[i]);
                    i++;
                });
            }
        });
    });
});