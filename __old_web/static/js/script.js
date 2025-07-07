document.addEventListener("DOMContentLoaded", function () {
    // Ativa o clique em qualquer linha da tabela
    document.querySelectorAll(".device-table tbody tr").forEach(row => {
        const hostnameCell = row.querySelector("td[data-hostname]");
        if (!hostnameCell) return;

        row.addEventListener("click", () => {
            const hostname = hostnameCell.getAttribute("data-hostname");
            showDeviceModal(hostname);
        });
    });
});

function showDeviceModal(hostname) {
    stopCountdown(); // interrompe contador automático

    fetch(`/device/${hostname}`)
        .then(res => res.text())
        .then(html => {
            document.getElementById("deviceModalDetails").innerHTML = html;
        });

    fetch(`/history/${hostname}`)
        .then(res => res.text())
        .then(html => {
            document.getElementById("deviceModalHistory").innerHTML = html;
            document.getElementById("deviceModal").style.display = "block";
        });
}

function closeDeviceModal() {
    document.getElementById("deviceModal").style.display = "none";
    window.location.reload(); // ou startCountdown();
}

window.onclick = function (event) {
    const modal = document.getElementById("deviceModal");
    if (event.target === modal) {
        closeDeviceModal();
    }
}