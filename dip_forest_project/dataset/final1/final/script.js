document.getElementById('registerForm').onsubmit = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    await fetch('/register', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: { 'Content-Type': 'application/json' }
    });
    alert('Registered!');
};

document.getElementById('progressForm').onsubmit = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const res = await fetch('/progress', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    document.getElementById('suggestion').innerText = data.suggestion;
};
