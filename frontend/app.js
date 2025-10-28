// Elements Initialization
const form = document.getElementById('businessForm');
const loadingState = document.getElementById('loadingState');
const formSection = document.getElementsByClassName('form-section');
const btn = document.getElementsByClassName('btn-analyze')

for (let section of formSection) {
  section.style.display = "none";
}

function displayForm() {
  for (let section of formSection) {
    section.style.display = "inline";
  }
}

setTimeout(displayForm, 5500);

// JWhen form submit
// Form submit handler
form.addEventListener('submit', async function(e) {
    e.preventDefault(); // Page reload nahi hoga
    
    // Get form data
    const companyName = document.getElementById('companyName').value;
    const industry = document.getElementById('industry').value;
    const csvFile = document.getElementById('csvFile').files[0];
    
    // Validation
    if (!companyName || !industry || !csvFile) {
        alert('⚠️ Please fill all fields!');
        return;
    }
    
    // Show loading state
    form.style.display = 'none';
    loadingState.style.display = 'block';
    
    // ========== SAVE DATA TO localStorage ==========
    const formData = {
        companyName: companyName,
        industry: industry,
        fileName: csvFile.name,
        analysisDate: new Date().toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })
    };
    
    // Save to localStorage
    localStorage.setItem('businessData', JSON.stringify(formData));
    console.log('✅ Data saved:', formData);
    
    // Simulate processing (2 seconds)
    setTimeout(function() {
        // Redirect to dashboard
        window.location.href = 'dashboard.html';
    }, 2000);
    
    // TODO: Later, when Himanshu's backend ready:
    // const uploadData = new FormData();
    // uploadData.append('company', companyName);
    // uploadData.append('industry', industry);
    // uploadData.append('file', csvFile);
    // 
    // const response = await fetch('http://localhost:5000/analyze', {
    //     method: 'POST',
    //     body: uploadData
    // });
    // const result = await response.json();
    // localStorage.setItem('analysisResults', JSON.stringify(result));
});

console.log('✅ JavaScript loaded successfully!');
