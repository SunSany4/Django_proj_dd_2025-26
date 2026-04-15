document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("albumForm");
    const priceInput = document.getElementById("{{ form.price.id_for_label }}");
    const yearInput = document.getElementById("{{ form.year.id_for_label }}");

    //  Validation func
    function validatePrice() {
        const feedback = document.getElementById("{{ form.price.id_for_label }}-feedback");
        const value = priceInput.value.trim();
        if (value === '') {
            priceInput.classList.remove('is-valid', 'is-invalid');
            feedback.style.display = 'none'
            return
        }
        const price = parseFloat(value);

        if (isNaN(price)) {
            priceInput.classList.add('is-invalid');
            priceInput.classList.remove('is-valid');
            feedback.textContent = 'Пожалуйста, введите число';
            feedback.className = 'validation-feedback invalid-feedback';
            feedback.style.display = 'block';
        } else if (price <= 0) {
            priceInput.classList.add('is-invalid');
            priceInput.classList.remove('is-valid');
            feedback.textContent = 'Цена должна быть больше нуля';
            feedback.className = 'validation-feedback invalid-feedback';
            feedback.style.display = 'block';
        } else {
            priceInput.classList.add('is-valid');
            priceInput.classList.remove('is-invalid');
            feedback.textContent = '✓ Корректная цена';
            feedback.className = 'validation-feedback valid-feedback';
            feedback.style.display = 'block';
        }


    }

    function validateYear() {
        const feedback = document.getElementById("{{ form.year.id_for_label }}-feedback");
        const value = priceInput.value.trim();
        const currentYear = new Date().getFullYear();
        if (value === '') {
            priceInput.classList.remove('is-valid', 'is-invalid');
            feedback.style.display = 'none'
            return
        }

        const year = parseInt(value);
        if (isNaN(year)) {
            priceInput.classList.add('is-invalid');
            priceInput.classList.remove('is-valid');
            feedback.textContent = 'Пожалуйста, введите год';
            feedback.className = 'validation-feedback invalid-feedback';
            feedback.style.display = 'block';
        } else if (year <= 1900 || year > currentYear) {
            priceInput.classList.add('is-invalid');
            priceInput.classList.remove('is-valid');
            feedback.textContent = 'Год должен быть между 1900 и ${currentYear}';
            feedback.className = 'validation-feedback invalid-feedback';
            feedback.style.display = 'block';
        } else {
            priceInput.classList.add('is-valid');
            priceInput.classList.remove('is-invalid');
            feedback.textContent = '✓ Корректный год';
            feedback.className = 'validation-feedback valid-feedback';
            feedback.style.display = 'block';
        }

    }
    if (priceInput) {
        priceInput.addEventListener('input', validatePrice);
        priceInput.addEventListener('blur', validatePrice);
    }
    if (yearInput) {
        yearInput.addEventListener('input', validateYear);
        yearInput.addEventListener('blur', validateYear);
    }
    // Валидация всей формы перед отправкой
    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (priceInput) {
            validatePrice();
            if (priceInput.classList.contains('is-invalid')) {
                isValid = false;
            }
        }

        if (yearInput && yearInput.value.trim() !== '') {
            validateYear();
            if (yearInput.classList.contains('is-invalid')) {
                isValid = false;
            }
        }

        if (!isValid) {
            event.preventDefault();
            alert('Пожалуйста, исправьте ошибки в форме');
        }
    });
});