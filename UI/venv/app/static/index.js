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
  //when button to add book to library is pressed
  $("#books").on("click", ".favouriteButton",function() {
    var buttonClicked = $(this);
    if (buttonClicked.data("favourite") == "0")
    {
      //set the book as favourited
      $.ajax({
        url: endpoint + "UserReadBooks/" + buttonClicked.val(),
        type: "PUT",
        data: JSON.stringify({"favourite": true}),
        contentType: "application/json; charset=utf-8",
        headers: {
          "Authorization": "Basic " + btoa(username + ":" + password)
        },
        success: function(response) {
          buttonClicked.text("Remove from favourites")
          buttonClicked.removeClass("btn-primary");
          buttonClicked.addClass("btn-warning");
          buttonClicked.data("favourite", "1"); 
        },
        error: function(response) {
          console.log(response.responseJSON.error);
          buttonClicked.parent().append(`<p class="card-text error" id="feedback">ERROR: ` + response.responseJSON.error + `</p>`)
          buttonClicked.prop("disabled", true);
        }
      });
    }
    else
    {
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
          buttonClicked.text("Add to favourites")
          buttonClicked.removeClass("btn-warning");
          buttonClicked.addClass("btn-primary");
          buttonClicked.data("favourite", "0"); 
        },
        error: function(response) {
          console.log(response.responseJSON.error);
          buttonClicked.parent().append(`<p class="card-text error" id="feedback">ERROR: ` + response.responseJSON.error + `</p>`)
          buttonClicked.prop("disabled", true);
        }
      });
    }
  });
});