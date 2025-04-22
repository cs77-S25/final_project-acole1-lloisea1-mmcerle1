// btn = document.getElementById('comment_btn');
// btn.addEventListener("click", handleMessage);

// function handleMessage(){
//     const inputField = document.getElementById("inputted_comment");
//     const message = inputField.value.trim();
//     if(message === ""){
//         return;
//     }
//     else{
//         const comments = document.getElementById("comments")
//         const userComment = document.createElement("div");
//         userComment.className = "comment";
//         userComment.innerText = message;
//         comments.appendChild(userComment);
//     }
// }


document.querySelector("#comment_form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    let content = document.getElementById("inputted_comment").value.trim();
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
        // console.log("Success:", data);
        // comment = data["comment"];

        // // if (relevant === "false") {window.location.href="/notrelevanterror";}

        // const comments = document.getElementById("comments")
        // const userComment = document.createElement("div");
        // userComment.className = "comment";
        // userComment.innerText = comment[""];
        // comments.appendChild(userComment);
    })
    .catch(error => {
        console.error("Error:", error);
    });
});


function varPass(v) {
    return v
}