likePost = document.getElementById('like');

// Like post function; This function increments the like count on
// a post
likePost.addEventListener("click", function (event){
    event.preventDefault(); 
    console.log("in increase upvote");
    console.log(window.location.href);
    index = window.location.href.split("/");
    console.log(index);
    post_id = JSON.stringify(index[index.length-1]);
    console.log(post_id);
    fetch('/forum_item/like', {
        method: 'PUT',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: post_id 
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        window.location.reload();
    })
    .catch(error => {
        console.error("Error:", error);
    });
});


// Submit comment function: This function adds comments to a post. A new
// item is added to the database
document.querySelector("#comment_form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    let inputted_comment = document.getElementById("inputted_comment");
    let content = inputted_comment.value.trim();
    inputted_comment.value = "";

    if(content === ""){
        return;
    }
    body = JSON.stringify({"content": content});
    console.log("\n\n\n")
    console.log(commenturl)
    console.log("\n\n\n")
    fetch(commenturl, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: body
    })
    .then(response => response.json()) // Adjust based on expected response
    .then(data => {
        window.location.reload();
        console.log("Success:", data);
    })
    .catch(error => {
        console.log(response);
        console.error("Error:", error);
    });
});


function varPass(v) {
    return v
}
