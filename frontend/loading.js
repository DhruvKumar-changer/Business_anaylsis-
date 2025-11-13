    console.log('🎬 Loading page started');
    
    // Get data
    const businessData = JSON.parse(sessionStorage.getItem('businessData'));
    if (!businessData) {
        alert('No data found!');
        window.location.href = '/Index/index.html';
    }

    // Simple animation
    setTimeout(() => document.getElementById('step1').classList.add('completed'), 500);
    setTimeout(() => document.getElementById('step2').classList.add('completed'), 1000);
    setTimeout(() => document.getElementById('step3').classList.add('completed'), 1500);
    setTimeout(() => document.getElementById('step4').classList.add('completed'), 2000);

    // Fetch data function
    async function fetchData() {
        console.log('📡 Fetching additional data...');
        
        // Recommendations
        try {
            const res = await fetch('http://localhost:5000/recommendations', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({kpis: businessData.kpis, profile: businessData.profile})
            });
            if (res.ok) {
                const data = await res.json();
                businessData.recommendations = data.recommendations;
                console.log('✅ Recommendations loaded');
            } else {
                console.log('❌ Recommendations failed:', await res.text());
            }
        } catch (e) {
            console.log('❌ Recommendations error:', e);
        }

        // Charts
        try {
            const res = await fetch('http://localhost:5000/charts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    filename: businessData.filename,
                    chart_types: ['revenue_trend', 'product_comparison', 'expense_breakdown', 'forecast']
                })
            });
            if (res.ok) {
                const data = await res.json();
                businessData.charts = data.charts;
                console.log('✅ Charts loaded');
            } else {
                console.log('❌ Charts failed:', await res.text());
            }
        } catch (e) {
            console.log('❌ Charts error:', e);
        }
        // Predictions (ADD IF MISSING)
    try {
        const res = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: businessData.filename})
        });
        if (res.ok) {
            const data = await res.json();
            businessData.predictions = data;
            console.log('✅ Predictions loaded');
        }
    } catch (e) {
        console.log('❌ Predictions error:', e);
    }

        // Save and redirect
        sessionStorage.setItem('businessData', JSON.stringify(businessData));
        console.log('💾 Data saved, redirecting...');
        
        window.location.href = '/Dashboard/dashboard.html';
    }

// Start after 3 seconds (ONLY ONCE)
setTimeout(fetchData, 3000);