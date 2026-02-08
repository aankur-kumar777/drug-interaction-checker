/**
 * Drug Interaction Checker - Main Application
 */

// Initialize API client
const api = new DrugInteractionAPI();

// State management
let selectedDrugs = [];
let currentResults = null;

// DOM Elements
const drugSearch = document.getElementById('drug-search');
const drugSuggestions = document.getElementById('drug-suggestions');
const addDrugBtn = document.getElementById('add-drug-btn');
const selectedDrugsContainer = document.getElementById('selected-drugs');
const checkBtn = document.getElementById('check-btn');
const clearBtn = document.getElementById('clear-btn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');

// Event Listeners
drugSearch.addEventListener('input', handleDrugSearch);
drugSearch.addEventListener('keypress', handleKeyPress);
addDrugBtn.addEventListener('click', addDrug);
checkBtn.addEventListener('click', checkInteractions);
clearBtn.addEventListener('click', clearAll);

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!drugSearch.contains(e.target) && !drugSuggestions.contains(e.target)) {
        drugSuggestions.classList.remove('active');
    }
});

/**
 * Handle drug search input
 */
async function handleDrugSearch(e) {
    const query = e.target.value.trim();
    
    if (query.length < 2) {
        drugSuggestions.classList.remove('active');
        return;
    }
    
    try {
        const response = await api.searchDrugs(query);
        
        if (response.status === 'success' && response.data.results.length > 0) {
            displaySuggestions(response.data.results);
        } else {
            drugSuggestions.classList.remove('active');
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

/**
 * Display drug suggestions
 */
function displaySuggestions(drugs) {
    drugSuggestions.innerHTML = '';
    
    drugs.forEach(drug => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <div class="suggestion-name">${capitalizeFirst(drug.name)}</div>
            <div class="suggestion-class">${drug.class} - ${drug.description}</div>
        `;
        item.addEventListener('click', () => selectDrug(drug.name));
        drugSuggestions.appendChild(item);
    });
    
    drugSuggestions.classList.add('active');
}

/**
 * Handle enter key press
 */
function handleKeyPress(e) {
    if (e.key === 'Enter') {
        addDrug();
    }
}

/**
 * Select a drug from suggestions
 */
function selectDrug(drugName) {
    drugSearch.value = drugName;
    drugSuggestions.classList.remove('active');
    addDrug();
}

/**
 * Add a drug to the selection
 */
function addDrug() {
    const drugName = drugSearch.value.trim().toLowerCase();
    
    if (!drugName) {
        alert('Please enter a drug name');
        return;
    }
    
    if (selectedDrugs.includes(drugName)) {
        alert('This drug is already added');
        return;
    }
    
    selectedDrugs.push(drugName);
    drugSearch.value = '';
    drugSuggestions.classList.remove('active');
    
    updateSelectedDrugs();
    updateCheckButton();
}

/**
 * Update selected drugs display
 */
function updateSelectedDrugs() {
    selectedDrugsContainer.innerHTML = '';
    
    selectedDrugs.forEach(drug => {
        const tag = document.createElement('div');
        tag.className = 'drug-tag';
        tag.innerHTML = `
            <span>${capitalizeFirst(drug)}</span>
            <i class="fas fa-times" onclick="removeDrug('${drug}')"></i>
        `;
        selectedDrugsContainer.appendChild(tag);
    });
}

/**
 * Remove a drug from selection
 */
function removeDrug(drugName) {
    selectedDrugs = selectedDrugs.filter(d => d !== drugName);
    updateSelectedDrugs();
    updateCheckButton();
}

/**
 * Update check button state
 */
function updateCheckButton() {
    checkBtn.disabled = selectedDrugs.length < 2;
}

/**
 * Check interactions
 */
async function checkInteractions() {
    if (selectedDrugs.length < 2) {
        return;
    }
    
    // Show loading
    loading.style.display = 'block';
    resultsSection.style.display = 'none';
    
    try {
        const response = await api.checkInteractions(selectedDrugs);
        
        if (response.status === 'success') {
            currentResults = response.data;
            displayResults(response.data);
            
            // Load visualization
            loadVisualization();
        } else {
            alert('Error: ' + (response.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error checking interactions:', error);
        alert('Failed to check interactions. Please ensure the backend server is running.');
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Display results
 */
function displayResults(data) {
    // Overall risk
    displayOverallRisk(data.overall_risk, data.interactions);
    
    // Interactions
    displayInteractions(data.interactions);
    
    // Recommendations
    displayRecommendations(data.recommendations);
    
    // Alternatives
    if (data.safer_alternatives && data.safer_alternatives.length > 0) {
        displayAlternatives(data.safer_alternatives);
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Display overall risk assessment
 */
function displayOverallRisk(riskLevel, interactions) {
    const riskLevelDiv = document.getElementById('risk-level');
    const riskSummary = document.getElementById('risk-summary');
    
    riskLevelDiv.className = `risk-badge ${riskLevel}`;
    riskLevelDiv.textContent = riskLevel.toUpperCase() + ' RISK';
    
    const interactionCount = interactions.length;
    const severeDrugs = interactions.filter(i => 
        i.severity === 'major' || i.severity === 'contraindicated'
    ).length;
    
    let summaryText = `Found ${interactionCount} interaction(s) between ${selectedDrugs.length} drugs.`;
    if (severeDrugs > 0) {
        summaryText += ` ${severeDrugs} require immediate attention.`;
    }
    
    riskSummary.innerHTML = `<p>${summaryText}</p>`;
}

/**
 * Display interactions
 */
function displayInteractions(interactions) {
    const container = document.getElementById('interactions-container');
    container.innerHTML = '';
    
    if (interactions.length === 0) {
        container.innerHTML = '<p>No significant interactions detected.</p>';
        return;
    }
    
    interactions.forEach(interaction => {
        const card = document.createElement('div');
        card.className = `interaction-card ${interaction.severity}`;
        
        card.innerHTML = `
            <div class="interaction-header">
                <div class="interaction-drugs">
                    ${interaction.drug_pair.map(d => capitalizeFirst(d)).join(' ⚡ ')}
                </div>
                <span class="severity-badge ${interaction.severity}">
                    ${interaction.severity}
                </span>
            </div>
            <div class="interaction-details">
                <p><strong>Description:</strong> ${interaction.description}</p>
                <p><strong>Mechanism:</strong> ${interaction.mechanism}</p>
                ${interaction.clinical_effects ? `<p><strong>Clinical Effects:</strong> ${interaction.clinical_effects}</p>` : ''}
                ${interaction.risk_score ? `<p><strong>Risk Score:</strong> ${(interaction.risk_score * 100).toFixed(1)}%</p>` : ''}
                ${interaction.evidence_level ? `<p><strong>Evidence Level:</strong> ${interaction.evidence_level}</p>` : ''}
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p>No specific recommendations at this time.</p>';
        return;
    }
    
    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        
        // Determine icon based on content
        let icon = 'fa-info-circle';
        if (rec.includes('❌')) icon = 'fa-ban';
        else if (rec.includes('⚠️')) icon = 'fa-exclamation-triangle';
        else if (rec.includes('⚡')) icon = 'fa-bolt';
        else if (rec.includes('💡')) icon = 'fa-lightbulb';
        else if (rec.includes('✅')) icon = 'fa-check-circle';
        else if (rec.includes('👴')) icon = 'fa-user';
        
        item.innerHTML = `
            <i class="fas ${icon}"></i>
            <div>${rec}</div>
        `;
        
        container.appendChild(item);
    });
}

/**
 * Display safer alternatives
 */
function displayAlternatives(alternatives) {
    const section = document.getElementById('alternatives-section');
    const container = document.getElementById('alternatives-container');
    
    container.innerHTML = '';
    
    alternatives.forEach(alt => {
        const group = document.createElement('div');
        group.className = 'alternative-group';
        
        group.innerHTML = `
            <h4>Instead of ${capitalizeFirst(alt.replace)}:</h4>
            <div class="alternatives-list" id="alt-${alt.replace}"></div>
        `;
        
        container.appendChild(group);
        
        const list = document.getElementById(`alt-${alt.replace}`);
        alt.with.forEach(option => {
            const item = document.createElement('div');
            item.className = 'alternative-item';
            item.innerHTML = `
                <div class="alternative-name">${capitalizeFirst(option.name)}</div>
                <div class="alternative-reason">${option.reason}</div>
            `;
            list.appendChild(item);
        });
    });
    
    section.style.display = 'block';
}

/**
 * Load and display interaction visualization
 */
async function loadVisualization() {
    try {
        const response = await api.visualizeInteractions(selectedDrugs);
        
        if (response.status === 'success') {
            visualizeGraph(response.data);
        }
    } catch (error) {
        console.error('Visualization error:', error);
    }
}

/**
 * Visualize interaction graph using D3.js
 */
function visualizeGraph(graphData) {
    const container = document.getElementById('graph-container');
    container.innerHTML = '';
    
    const width = container.clientWidth || 800;
    const height = 400;
    
    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create force simulation
    const simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.edges)
            .id(d => d.id)
            .distance(150))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Draw edges
    const link = svg.append('g')
        .selectAll('line')
        .data(graphData.edges)
        .enter()
        .append('line')
        .attr('stroke', d => d.color)
        .attr('stroke-width', d => d.width)
        .attr('stroke-opacity', 0.6);
    
    // Draw nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(graphData.nodes)
        .enter()
        .append('circle')
        .attr('r', d => d.size)
        .attr('fill', d => d.color)
        .call(drag(simulation));
    
    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(graphData.nodes)
        .enter()
        .append('text')
        .text(d => capitalizeFirst(d.label))
        .attr('font-size', 12)
        .attr('dx', 25)
        .attr('dy', 4);
    
    // Update positions on tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Drag functionality
    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
}

/**
 * Clear all selections
 */
function clearAll() {
    selectedDrugs = [];
    currentResults = null;
    drugSearch.value = '';
    
    updateSelectedDrugs();
    updateCheckButton();
    
    resultsSection.style.display = 'none';
    drugSuggestions.classList.remove('active');
}

/**
 * Utility: Capitalize first letter
 */
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize
console.log('Drug Interaction Checker initialized');
console.log('Make sure the backend server is running on http://localhost:5000');
