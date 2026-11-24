document.title = "HACKED BY H4CKNET";

document.body.style.backgroundColor = "darkred";

const mensaje = document.createElement("h1");

mensaje.textContent = "HACKED BY H4CKNET";

mensaje.style.cssText = `
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2147483647;
    background: black;
    color: white;
    padding: 30px;
    font-size: 40px;
    border: 3px solid red;
`;

document.body.appendChild(mensaje);
