search = document.getElementById('search-btn');
search.addEventListener("click", function (event){
    event.preventDefault(); 
    console.log("in search");
    topic = document.querySelector('select').value;
    console.log(topic);
    keyword = document.querySelector('.search-box').value;
    console.log(keyword);
    const url = new URL(window.location.href);
    url.searchParams.set("t", topic);
    url.searchParams.set("k", keyword);

    window.location.href = url;
});
