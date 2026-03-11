// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const dropdowns = document.querySelectorAll(".dropdown");

    dropdowns.forEach(dropdown => {
        const toggleBtn = dropdown.querySelector(".dropdown-toggle");

        toggleBtn.addEventListener("click", () => {
            // Close other dropdowns before opening this one
            dropdowns.forEach(d => {
                if (d !== dropdown) {
                    d.classList.remove("active");
                }
            });

            // Toggle current dropdown
            dropdown.classList.toggle("active");
        });
    });
});



