$(document).ready( function () {
    
    function get_emblem_class( navhead ) {
        var classname = navhead.attr('class').split(/\s+/)[1];
        return classname+"-emblem";
    }
    
    $(".navbar li").hover( function () {
        var navhead = $(this).children(".nav-head");
        navhead.css('text-shadow', '0px 1px 1px rgb(100,100,100)');
        navhead.addClass(get_emblem_class(navhead));
        $(this).children(".nav-title").stop().fadeIn(200);
    },
    function () {
        var navhead = $(this).children(".nav-head");
        navhead.css('text-shadow', 'none');
        navhead.removeClass(get_emblem_class(navhead));
        $(this).children(".nav-title").stop().fadeOut(200);
    });
    
    
    $("article.post").hover( function () {
        $(this).children(".post-actions").children("ul").children("li").fadeIn(200);
    },
    function () {
        $(this).children(".post-actions").children("ul").children("li").fadeOut(200);
    });
    
    $("#email").keyup(function () {
        if ($(this).val() == "") {
            $(".comment-form-email > label").css('display', 'block');
        }
        else {
            $(".comment-form-email > label").css('display', 'none');
        }
    });
    $("#email").focusin( function () {
        $(".nopublish").fadeIn(200);
    });
    $("#email").focusout( function () {
        $(".nopublish").fadeOut(200);
    });
    $("#author").keyup(function () {
        if ($(this).val() == "") {
            $(".comment-form-author > label").css('display', 'block');
        }
        else {
            $(".comment-form-author > label").css('display', 'none');
        }
    });
    
    $(".comment-reply-click").click( function () {
        $(this).parent().append($("#respond"));
        var parent_id = $.map(this.className.split(' '), function (val, i) {
			if (val.indexOf("comment_id-")>-1) {
				return val.slice("comment_id-".length, val.length);
			}
		});
        console.log(parent_id[0]);
        $('#comment_parent_id').val(parent_id[0]);
    })
});
