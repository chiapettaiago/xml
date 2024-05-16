 // Verificar se há dados do formulário armazenados na sessionStorage
 const formData = sessionStorage.getItem('form_data');
 if (formData) {
     // Preencher os campos do formulário com os valores armazenados
     const formValues = JSON.parse(formData);
     Object.keys(formValues).forEach(key => {
         const field = document.getElementById(key);
         if (field) {
             field.value = formValues[key];
         }
     });
 }

 // Armazenar valores do formulário na sessionStorage antes de sair da página
 window.addEventListener('beforeunload', () => {
     const form = document.getElementById('meuFormulario');
     const formData = new FormData(form);
     const formValues = {};
     for (const [key, value] of formData.entries()) {
         formValues[key] = value;
     }
     sessionStorage.setItem('form_data', JSON.stringify(formValues));
 });