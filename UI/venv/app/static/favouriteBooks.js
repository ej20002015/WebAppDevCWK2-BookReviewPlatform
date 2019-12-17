var endpoint = "NotSet";
var username = "NotSet";
var password = "NotSet";
var userId = "NotSet";

function setAjaxDetails(endpointParam, usernameParam, passwordParam, userIdParam)
{
  endpoint = endpointParam;
  username = usernameParam;
  password = passwordParam;
  userId = userIdParam;
}

$(document).ready(function() {
  //when favourite button is clicked then remove it from the library
  $("#books").on("click", ".favouriteButton",function() {
    var buttonClicked = $(this);
    //set the book as un favourited
    $.ajax({
      url: endpoint + "UserReadBooks/" + buttonClicked.val(),
      type: "PUT",
      data: JSON.stringify({"favourite": false}),
      contentType: "application/json; charset=utf-8",
      headers: {
        "Authorization": "Basic " + btoa(username + ":" + password)
      },
      success: function(response) {
        var modal = buttonClicked.parent().parent().parent().parent();
        var card = modal.prev();
        modal.modal("toggle");
        card.css({opacity: 1.0, visibility: "visible"}).animate({opacity: 0.0});
      },
      error: function(response) {
        console.log(response.responseJSON.error);
        buttonClicked.parent().append(`<p class="card-text error" id="feedback">ERROR: ` + response.responseJSON.error + `</p>`)
        buttonClicked.prop("disabled", true);
      }
    });
  });
});