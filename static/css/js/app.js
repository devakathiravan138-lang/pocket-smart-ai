document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const button = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (button) {
                button.disabled = true;
                button.innerHTML = "⏳ Generating Recommendations...";
            }

            let loader = document.createElement("div");

            loader.id = "ai-loader";

            loader.innerHTML = `
                <div class="loader-spinner"></div>
                <div>🤖 Generating AI Recommendations...</div>
                <small>Please wait...</small>
            `;

            form.parentNode.insertBefore(
                loader,
                form.nextSibling
            );
        });

    });

});