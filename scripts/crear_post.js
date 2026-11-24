fetch("/posts/new", {
    method: "POST",
    credentials: "same-origin",
    headers: {
        "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
        title: "<Escribe texto de título>",
        body: "<Body de ejemplo>"
    })
})
.then(response => {
    console.log("Estado HTTP:", response.status);
})
.catch(error => console.error(error));
