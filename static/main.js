$(function() {
	$("#addPeople").click(function(e) {
		e.preventDefault();
		$("#addPeopleli").before('<li class="col-sm-2"> <input type="text" class="form-control" name="people_name"> <button class="close deletePeople" type="button" >×</button></li>');
	});

	$(document).on('click', '.deletePeople', function() {
		$(this).parent().remove();
	});

	$(document).on('click', '.deleteNews', function() {
		$(this).prev().remove();
		$(this).prev().remove();
		$(this).remove();
	});

	$(document).on('click', '#addNews', function(e) {
		e.preventDefault();
		$('#addNews').before('<input type="text" class="form-control" name="news_title" placeholder="News Title"><input type="text" class="form-control" name="news_description" placeholder="News descripiton"><button class="close deleteNews" type="button" >×</button>');
	});

	$(document).on('click', '.deletePublication', function() {
		$(this).prev().remove();
		$(this).remove();
	});

	$(document).on('click', '#addPublication', function(e) {
		e.preventDefault();
		$('#addPublication').before('<input type="text" class="form-control" name="publication_description" placeholder="Publication descripiton"><button class="close deletePublication" type="button" >×</button>');
	});
});