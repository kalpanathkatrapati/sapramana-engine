// Small interactive behaviors for the South Indian chart component
document.addEventListener('DOMContentLoaded', function(){
  const cells = document.querySelectorAll('.sc-cell');
  cells.forEach(cell => {
    cell.addEventListener('click', () => cell.classList.toggle('sc-expanded'));
    cell.addEventListener('keydown', (e) => { if(e.key === 'Enter') cell.classList.toggle('sc-expanded'); });
  });
});
