function scroll_callback() {
	bLazy.revalidate();
};


function HtmlDecode(s) {
    return $('<div>').html(s).text();
}


function get_more_text(cur_post) {
    var more_text = $(cur_post).find('.moretext').html();
    if (null == more_text) return '';
    more_text = more_text.replace('<pre>', '').replace('</pre>', '');
    more_text = HtmlDecode(more_text);
    more_text = " " + more_text.trimLeft();
    more_text = more_text.replace(/\r?\n/g, '<br>');
    return more_text;
}

function first_text_without_ending_tags(start_div) {
    var start_div_html = start_div.html();
    var split_pos = start_div_html.indexOf('\u200B');
    if (split_pos > 0) {
        start_div_html = start_div_html.substring(0,split_pos);
    }
    return start_div_html;
}

function load_post_content(cur_post) {
    var more_text = get_more_text(cur_post);

    var text_div = $(cur_post).find('.post-body-start');
    var text_div_html = first_text_without_ending_tags(text_div);
    text_div.html((text_div_html + more_text));

    $(cur_post).find('.sources-div').removeClass('hidden');
    $(cur_post).find('.readmore-wrapper').hide();
    $(cur_post).find('.second-image-wrapper').removeClass('hidden');
    bLazy.revalidate();
}

function open_first() {
    var cur_post = $.find('.post')[0];
    send_action(cur_post, 'open_link');
    load_post_content(cur_post);
}

function show_more_click() {
	$(".jscroll-inner").on('click', '.readmore', function() {
        // show or hide the dots and the extra text
        var post_id = get_post_id($(this));
        if ($(this).closest('.post').hasClass('locked'))  {
            send_action($(this), 'locked');
            $('#subscribeModal').modal('show');
        }
        else if (views_left <= 0) {
            send_action($(this), 'reach_limit');
            $('#nosnipsModal').modal('show');
        }
        else {
            send_action($(this), 'readmore');
            fbq('track', 'ViewContent', {content_ids: [get_post_id($(this))]});
            load_post_content($(this).closest('.post'));
        }
        return false;
	});
}

function set_and_show_views_left(val) {
    if (!is_auth) {
        views_left = val;
        var text;
        if (val <= 0) {
            text = 'no snips';
        }
        else if (val == 1) {
            text = '1 free snip';
        }
        else {
            text = val + ' free snips'
        }
        $('#signupFooterNum').text(text)
        $('#signupFooter').show();
        setTimeout(function(){
            $('#signupFooter').hide();
        }, 8*1000);
    };
}

function send_action(button, action, param1, param2) {
    var csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var params = {'action': action, 'param1': param1, 'param2': param2, 'csrfmiddlewaretoken': csrf};
    var action_url = $(button).closest('section').attr('data-log-url');
    mixpanel.track(action,{'post': get_post_id(button), 'param1': param1, 'param2': param2});
    $.post(action_url, params)
    .done(function(data) {
        console.log("action success");
        if (data.message == 'readmore') {
            set_and_show_views_left(data.num_left);
        }
    })
    .fail(function(data) {
        if (data.message == 'signin') {
            $('#nosnipsModal').modal('show');
        }
        console.log("action fail");
    });
}

function get_post_id(button) {
    return $(button).closest('section').attr('id');
}

function share_link(url, winWidth, winHeight) {
    var winTop = (screen.height / 2) - (winHeight / 2);
    var winLeft = (screen.width / 2) - (winWidth / 2);
    window.open(url, 'sharer', 'top=' + winTop + ',left=' + winLeft + ',toolbar=0,status=0,width='+winWidth+',height='+winHeight);
}

function vote_handler(button, vote, offClass, onClass, other_class, other_offClass, other_onClass) {
    var icon = $(button).find('i')[0];
    var mark_remove;
    var mark = 'mark_vote'
    var remove = 'remove_vote'
    if ($(button).hasClass(mark)) {
        $(button).removeClass(mark);
        $(icon).addClass(offClass).removeClass(onClass);
        mark_remove = remove
    }
    else {
        $(button).addClass(mark);
        $(icon).addClass(onClass).removeClass(offClass);
        mark_remove = mark
    }
    var other_button = $(button).parent().find('.' + other_class)[0];
    if ($(other_button).hasClass(mark)) {
        $(other_button).removeClass(mark);
        $(other_button).find('i').addClass(other_offClass).removeClass(other_onClass);
    }
    if (is_auth) {
        send_action(button, vote, mark_remove);
    }
}

function sharing_handlers() {
    $("body").on('click', '.share', function(e) {
        var children = $(this).find(".fab");
        children.removeClass("no");
        if(e.target != this) return;
        children.toggleClass("active");
        $(this).toggleClass("active");
    });

    $("body").on('click', '.email-share', function(e) {
        send_action($(this), 'share', 'email');
        window.location = 'mailto:?subject=You should read that snip&body=' + $(this).parent().attr('data-url');
    });

    $("body").on('click', '.twtr-share', function(e) {
        send_action($(this), 'share', 'twtr');
        share_link('https://twitter.com/intent/tweet?url='+ $(this).parent().attr('data-url') +'&text=Great snip!', 500, 300);
    });

    $("body").on('click', '.reddit-share', function(e) {
        send_action($(this), 'share', 'reddit');
        var url = $(this).parent().attr('data-url');
        var title = $(this).parent().attr('data-title');
        window.open('https://www.reddit.com/submit?url='+ url +'&title=' + title, '_blank');
    });

    $("body").on('click', '.fb-share', function(e) {
        send_action($(this), 'share', 'fb');
        FB.ui({
            method: 'share',
            href: $(this).parent().attr('data-url'),
        }, function(response){});
    });
}

function update_trans_field(data_name, field_id) {
    var data_value = $(this).data(data_name);
    $(field_id).text(data_value);
}

var cur_post_id = "";


$(document).ready(function() {

    // bind show more function
    show_more_click();

    sharing_handlers();

    if (!is_auth) {
        $('head').append("<style>.m-replyform { display: none }</style>");
    };

    $("body").on('click', '.vote', function(e) {
        var like = 'like';
        var dislike = 'dislike';
        var vote;
        if ($(this).hasClass(like)) {
            vote = like;
        }
        else if ($(this).hasClass(dislike)) {
            vote = dislike;
        }
        else {
            return;
        }

        if (!is_auth) {
            $('#voteFooter').show();
            setTimeout(function(){
                $('#voteFooter').hide();
            }, 10*1000);
            send_action($(this), vote + '_noauth');
        }
        if ($(this).hasClass(like)) {
            vote_handler($(this), like, 'fa-thumbs-o-up', 'fa-thumbs-up', dislike, 'fa-thumbs-o-down', 'fa-thumbs-down');
        }
        else if ($(this).hasClass(dislike)) {
            vote_handler($(this), dislike, 'fa-thumbs-o-down', 'fa-thumbs-down', like, 'fa-thumbs-o-up', 'fa-thumbs-up');
        }

    });

    var maxScrollPos = 0;
    var scrollDown = false;

    // url scroller
    $(document).bind('scroll',function(e){
        var st = $(this).scrollTop();
        if (st > maxScrollPos)
            {
            scrollDown = true;
            maxScrollPos = st;
            }
        else
            {scrollDown = false;}

        $('section').each(function(){
            if (
               $(this).offset().top < window.pageYOffset + 10
                //begins before top
                && $(this).offset().top + $(this).height() > window.pageYOffset + 10
                //but ends in visible area
                && (cur_post_id != $(this).attr('id'))
                && scrollDown
                )
                {
                    cur_post_id = $(this).attr('id');
                    send_action($(this), 'viewed');
                    ga('set', 'page', $(this).attr('data-title'));
                    ga('send', 'pageview');
                }
        });
    });

    $('.scroll').jscroll({
        loadingHtml: '<img src="' + loading_gif + '" style="height: 30px;" alt="Loading" />',
        padding: 150,
        nextSelector: 'a.jscroll-next:last',
        callback: scroll_callback
    });

    $('.modal').on('show.bs.modal', function (e) {
        $('body').addClass('no-padding-right');
    })

    $(document).on("click", ".tip-btn", function () {
        var author_name = $(this).data('author');
        $('#tip_author').text(author_name);
        $('#tip_nonce').val('');
        $('#tip_amount').val('');
        $('#tip_err').val('');
        $('#tip_success').val('');
        $('#author_address_qr').html('');


        var address = $(this).data('address');
        var address_field = '#author_address';
        var no_address_field = '#author_no_address';

        if (address) {
            $(address_field).text(address);
            $(no_address_field).hide();
            $(address_field).closest('label').show();
            new QRCode(document.getElementById("author_address_qr"),
                            {text: "ethereum:" + address,  width: 128, height: 128 }
                        );
        }
        else {
//            $(no_address_field).show();
            $(address_field).closest('label').hide();
        }
    });

    $(document).on("click", "#toggle_private_key", function () {
        var p_key_id = '#private_key';
        var cur_type = $(p_key_id).attr('type');
        if (cur_type == 'password') {
            $(p_key_id).attr('type', 'text');
            $(this).children().addClass('fa-eye').removeClass('fa-eye-slash');
        }
        else {
            $(p_key_id).attr('type', 'password');
            $(this).children().addClass('fa-eye-slash').removeClass('fa-eye');
        }
    });


});
