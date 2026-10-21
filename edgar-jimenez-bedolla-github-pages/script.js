'use strict';
const copyButton = document.getElementById('copy-email');
const copyStatus = document.getElementById('copy-status');
const messages = {
  en: ['Copied to clipboard', 'Please select and copy the address above.'],
  fr: ['Adresse copiée', 'Veuillez sélectionner et copier l’adresse ci-dessus.'],
  es: ['Correo copiado', 'Seleccione y copie el correo de arriba.']
}[document.documentElement.lang] || ['Copied to clipboard', 'Please select and copy the address above.'];
let clearStatus;
copyButton.addEventListener('click', async () => {
  window.clearTimeout(clearStatus);
  try {
    await navigator.clipboard.writeText('edgar.jimenez-bedolla@dauphine.eu');
    copyStatus.textContent = messages[0];
  } catch {
    copyStatus.textContent = messages[1];
  }
  clearStatus = window.setTimeout(() => { copyStatus.textContent = ''; }, 5000);
});

// Keep the current section when following a language link.
document.querySelectorAll('.language-switch a').forEach(link => {
  link.addEventListener('click', () => { link.hash = window.location.hash; });
});
