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

  $("#books").on("click", ".thoughtsButton", function() {
    var buttonClicked = $(this);
    var cardBody = buttonClicked.prev();
    var thoughts = $("#thoughts" + buttonClicked.val());
    var currentThoughts = thoughts.text() == "No thoughts - add some now" ? "" : thoughts.text();
    thoughts.remove();
    buttonClicked.remove();
    cardBody.append(
      `<div class="form-group">
        <textarea class="form-control" rows="5" value="` + currentThoughts + `" id="thoughtsInput` + buttonClicked.val() + `"></textarea>
      </div>
      <button value="` + buttonClicked.val() + `" class="btn btn-primary changeThoughtsButton">Change thoughts</button>`
    );
  });

  $("#books").on("click", ".changeThoughtsButton", function() {
    var buttonClicked = $(this);
    var inputBox = $("#thoughtsInput" + buttonClicked.val());
    var newThoughts = inputBox.val();
    $.ajax({
      url: endpoint + "UserReadBooks/" + buttonClicked.val(),
      type: "PUT",
      data: JSON.stringify({"thoughts": newThoughts}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      headers: {
        "Authorization": "Basic " + btoa(username + ":" + password)
      },
      success: function(response) {
        var card = inputBox.parent().parent().parent();
        inputBox.parent().remove();
        inputBox.remove();
        buttonClicked.remove();
        card.html(`
          <div class="card-body">
            <h5 class="card-title">Your thoughts:</h5>
            <p class="card-text" id="thoughts`+ buttonClicked.val() + `">` + newThoughts + `</p>
          </div>
          <button value="` + buttonClicked.val() + `" class="btn btn-primary thoughtsButton">Change your thoughts</button>
        `);
      },
      error: function(response) {
        console.log(response.error);
        buttonClicked.parent().append(`<p class="card-text error" id="feedback">ERROR: ` + response.responseJSON.error + `</p>`)
        buttonClicked.prop("disabled", true);
      }
    });
  });
});