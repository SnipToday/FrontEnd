$(document).ready(function(){
    $("#search_icon").click(function () {
        $(".search_main").slideToggle("fast");
        $('#search-input').focus();
    });

    $(".nav_menu").click(function () {
        $(".nav_open").css("transform","translate(0)");
        $(".overlay").css("display","block");
        $("body").addClass('no_scroll');
    });

    $(".overlay").click(function () {
        $(".nav_open").css("transform","translate(100%)");
        $(".overlay").css("display","none");
        $("body").removeClass('no_scroll');
    });

    $(".nav_close").click(function () {
        $(".nav_open").css("transform","translate(100%)");
        $(".overlay").css("display","none");
        $("body").removeClass('no_scroll');

    });
    $('html').on('click', '.log-b', function() {
        var action = $(this).attr('data-action');
        var param1 = $(this).attr('data-param1');
        send_log(action, param1);
    });

    $('html').on('submit', '.search-form', function() {
        var text = $('input[name=search]').val();
        send_log('search', text);
    });


});


function send_log(event, param1, param2) {
    var csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var params = {'action': event, 'param1': param1, 'param2': param2, 'csrfmiddlewaretoken': csrf};
    mixpanel.track(event,{'param1': param1, 'param2': param2});
    $.post(log_url, params)
    .done(function(data) {
        console.log("success");
    })
    .fail(function(data) {
        console.log("fail");
    });
}


