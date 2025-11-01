const button = document.getElementById('getStartedBtn');

function showGetStartedButton() {
  setTimeout(() => {
    button.classList.add('visible');
  }, 3000);
}

function handleGetStartedClick() {
  button.addEventListener('click', () => {
    console.log('Get Started clicked!');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  showGetStartedButton();
});

button.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Redirect to analytics page
    window.location.href = 'survey.html';
});

/************************  Survey JS *********************** */

const form = document.getElementById('surveyForm');
  const inputs = form.querySelectorAll('input, select, textarea');

  // Radio and checkbox selection animation
  document.querySelectorAll('.radio-option').forEach(option => {
      option.addEventListener('click', function() {
          const radio = this.querySelector('input[type="radio"]');
          const group = radio.name;
          document.querySelectorAll(`input[name="${group}"]`).forEach(r => {
              r.closest('.radio-option').classList.remove('selected');
          });
          this.classList.add('selected');
          radio.checked = true;
      });
  });

  document.querySelectorAll('.checkbox-option').forEach(option => {
      option.addEventListener('click', function(e) {
          if (e.target.tagName !== 'INPUT') {
              const checkbox = this.querySelector('input[type="checkbox"]');
              checkbox.checked = !checkbox.checked;
          }
          this.classList.toggle('selected', this.querySelector('input[type="checkbox"]').checked);
      });
  });

  // Form submission
  form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Redirect to analytics page
      window.location.href = 'analytics.html';
  });