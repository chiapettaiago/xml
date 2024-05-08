document.getElementById('btnSwitch').addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);

});

// Verifica se há um tema armazenado no armazenamento local
const storedTheme = localStorage.getItem('theme');
if (storedTheme) {
    document.documentElement.setAttribute('data-bs-theme', storedTheme);
}
