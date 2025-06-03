document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/resumes/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("resumes");
            data.resumes.forEach(resume => {
                const el = document.createElement('div');
                el.className = 'resume-card';
                el.innerHTML = `
                    <div class="resume-title">${resume.title}</div>
                    <div>Может откликнуться: ${resume.can_apply ? "Да" : "Нет"}</div>
                `;
                container.appendChild(el);
            });
        });

    document.getElementById("apply-all").addEventListener("click", () => {
        fetch('/api/apply-all/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            alert("Успешно откликнулись на все доступные вакансии!");
        })
        .catch(() => {
            alert("Произошла ошибка при отклике.");
        });
    });
});
