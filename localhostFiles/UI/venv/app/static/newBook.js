var endpoint = "NotSet";
var username = "NotSet";
var password = "NotSet";
var noCoverImage = "NotSet";
var userId = "NotSet";
var openBooksEndpoint = "https://openlibrary.org/api/books?bibkeys";

function setAjaxDetails(endpointParam, usernameParam, passwordParam, noCoverImageParam, userIdParam)
{
  endpoint = endpointParam;
  username = usernameParam;
  password = passwordParam;
  noCoverImage = noCoverImageParam;
  userId = userIdParam;
}

function outputBookCardToSearchResults(book, searchResults, i)
{
  coverImageURI = book.coverImageURI == null ? noCoverImage : book.coverImageURI;
  description = book.description == null || book.description == "" ? "Not available" : book.description;
  publishedDate = book.publishedDate == null || book.publishedDate == "" ? "Not available" : book.publishedDate;
  searchResults.append(
    `<div class="card">
      <div class="card-header">
      <a class="card-title" data-toggle="collapse" href="#collapse` + i + `" id="title">
        ` + book.title + `
      </a>
    </div>
    <div class="card-body collapse" id="collapse` + i + `" data-parent="#accordion">
      <div class="cardImageContainer">
        <img src="` + coverImageURI + `" alt="Image of book cover" id="coverImage">
      </div>
      <h6 class="card-subtitle mb-2 text-muted">Author:</h6>
      <p class="card-text" id="author">` + book.author + `</p>
      <h6 class="card-subtitle mb-2 text-muted">ISBN:</h6>
      <p class="card-text" id="ISBN">` + book.ISBN + `</p>
      <h6 class="card-subtitle mb-2 text-muted">Description:</h6>
      <p class="card-text" id="description">` + description + `</p>
      <h6 class="card-subtitle mb-2 text-muted">Published Date:</h6>
      <p class="card-text" id="publishDate">` + publishedDate + `</p>
      <button value="` + book.id + `" class="btn btn-primary addBookButton">Add to my library</button>
    </div>
  </div>`
  );
}

function computeList(returnedBooks, ISBNOrTitle, searchResults)
{
  //if books are returned by the search then make sure no duplicates exist in the list
  if (returnedBooks.length > 0)
  {
    idList = []
    returnedBooks = returnedBooks.filter((item) => {
      if (idList.includes(item.id))
      {
        return false;
      }
      else
      {
        idList.push(item.id);
        return true;
      }
    });
    
    for (i = 0; i < returnedBooks.length; ++i)
    {
      book = returnedBooks[i];
      outputBookCardToSearchResults(book, searchResults, i);
    }
  }
  else
  {
    //book not stored in database so make call to the openbooks API to retrieve the book details and store it in the database before presenting book to the user
    $.ajax({
      //specify the endpoint of the request
      url: openBooksEndpoint + "=ISBN:" + ISBNOrTitle + "&jscmd=data&format=json",
      type: "GET",
      dataType: "json",
      success: function(response) {
        console.log(JSON.stringify(response));
        if (!jQuery.isEmptyObject(response))
        {
          bookDetails = response["ISBN:" + ISBNOrTitle];
          //if openbooks call returned a book
          dataToCreateNewBook = 
          {
            "ISBN": ISBNOrTitle,
            "title": bookDetails.title,
            "author": bookDetails.authors[0].name,
            "description": "",
            "coverImageURI": bookDetails.cover.large,
            "publishedDate": bookDetails.publish_date
          };
          //need to make another call to openbooks to get the description
          $.ajax({
            url: openBooksEndpoint + "=ISBN:" + ISBNOrTitle + "&jscmd=details&format=json",
            type: "GET",
            dataType: "json",
            success: function(response) {
              bookDetails = response["ISBN:" + ISBNOrTitle].details;
              dataToCreateNewBook.description = bookDetails.description;
            },
            complete: function(response) {
              //add new book to own database
              $.ajax({
                url: endpoint + "Books",
                type: "POST",
                data: JSON.stringify(dataToCreateNewBook),
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                headers: {
                  "Authorization": "Basic " + btoa(username + ":" + password)
                },
                success: function(response) {
                  book = response;
                  outputBookCardToSearchResults(book, searchResults, 0);
                },
                error: function(response) {
                  console.log(response.responseJSON.error);
                  searchResults.text("When attempting to add newly found book to database - ERROR: " + response.responseJSON.error);
                  searchResults.addClass("error");
                }
              });
            }
          });
        }
        else
        {
          //no books exist with that ISBN
          searchResults.text("No books found - try inputting the books ISBN instead of its title");
          searchResults.addClass("error");
        }
      } 
    });
  }
}

$(document).ready(function() {
  var searchButton = $("#ISBNSearchButton");
  var searchField = $("#ISBNField");
  var searchResults = $("#accordion");
  searchButton.on("click", function() {
    searchResults.removeClass("error");
    searchResults.html("");
    var returnedBooks = [];
    ISBNOrTitle = searchField.val();
    if (ISBNOrTitle.length == 0)
      ISBNOrTitle = "!!";
    
      ISBNOrTitle = encodeURIComponent(ISBNOrTitle);
    
    //search by ISBN
    $.ajax({
      //specify the endpoint of the request
      url: endpoint + "Books?ISBN=" + ISBNOrTitle,
      type: "GET",
      dataType: "json",
      headers: {
        "Authorization": "Basic " + btoa(username + ":" + password)
      },
      success: function(response) {
        returnedBooks.push.apply(returnedBooks, response);
      },
      error: function(response) {
        console.log(response.responseJSON.error);
        searchResults.text("ERROR: " + response.responseJSON.error);
        searchResults.addClass("error");
      },
      complete: function(response) {
        //search by title
        $.ajax({
          //specify the endpoint of the request
          url: endpoint + "Books?title=" + ISBNOrTitle,
          type: "GET",
          dataType: "json",
          headers: {
            "Authorization": "Basic " + btoa(username + ":" + password)
          },
          success: function(response) {
            returnedBooks.push.apply(returnedBooks, response);
          },
          error: function(response) {
            console.log(response.responseJSON.error);
            searchResults.text("ERROR: " + response.responseJSON.error);
            searchResults.addClass("error");
          },
          complete: function(response) {
            computeList(returnedBooks, ISBNOrTitle, searchResults);
          }
        });
      }
    });
  });

  //when button to add book to library is pressed
  searchResults.on("click", ".addBookButton",function() {
    var buttonClicked = $(this);
    var bookId = buttonClicked.val();
    //post new item to database
    $.ajax({
      url: endpoint + "UserReadBooks",
      type: "POST",
      data: JSON.stringify({"userId": userId, "bookId": bookId, "favourite": false}),
      contentType: "application/json; charset=utf-8",
      headers: {
        "Authorization": "Basic " + btoa(username + ":" + password)
      },
      success: function(response) {
        buttonClicked.parent().append(`<p class="card-text success" id="feedback">Book has been added to your library!</p>`)
        buttonClicked.prop("disabled", true);
      },
      error: function(response) {
        console.log(response.responseJSON.error);
        buttonClicked.parent().append(`<p class="card-text error" id="feedback">ERROR: ` + response.responseJSON.error + `</p>`)
        buttonClicked.prop("disabled", true);
      }
    });
  });

  //make search button click when enter key is pressed in field
  document.getElementById("ISBNField").addEventListener("keyup", function(event) {
    if (event.keyCode === 13)
    {
      //trigger click of search button
      document.getElementById("ISBNSearchButton").click();
    }
  });
});