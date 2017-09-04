$(document).on('click',function(){
	$('.collapse').collapse('hide');
})

$(".search-form").on('click',function(e) {
    e.stopPropagation();
    return false;
});