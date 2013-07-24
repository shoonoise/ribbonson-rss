function get_article(feed_id, number) {
    $.ajax({
        type:"GET",
        url:feed_id + '/' + number,
        success:function (result) {
            $('.article').html(function(){
                return art = '<h2>' + result['title'] + '</h2>' + '<small>' + result['published'] +
                '</small><br>' + '<p>' + result['summary'] + '</p>';
            });
        }
    });
}

$(document).ready(function() {

    function show_feed(feed_id, feed_len){
        var current_article = 0;
        get_article(feed_id, current_article);
        $(window).keydown(function(e){
                console.log(e.keyCode);
                if (e.keyCode == 74 || e.keyCode == 40) {
                    get_article(feed_id, current_article);
                    if (current_article < feed_len) {
                        current_article += 1;
                    }

                }
                else if (e.keyCode == 75 || e.keyCode == 38) {
                    get_article(feed_id, current_article);
                    if (current_article > 0) {
                        current_article -= 1;
                    }
                }
        });
    }

    $(".feed").click(function(){
        feed_id = $(this).data('id');
        feed_count = $(this).data('count');
        $('.active').removeClass('active');
        $(this).addClass('active');
        show_feed(feed_id, feed_count)
    });

});