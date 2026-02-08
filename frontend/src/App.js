import React, { useState } from 'react';
import './App.css';
import DrugSearch from './components/DrugSearch';
import InteractionResults from './components/InteractionResults';
import Header from './components/Header';
import { checkInteractions } from './services/api';

function App() {
  const [selectedDrugs, setSelectedDrugs] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAddDrug = (drug) => {
    if (!selectedDrugs.includes(drug)) {
      setSelectedDrugs([...selectedDrugs, drug]);
      setResults(null); // Clear previous results
    }
  };

  const handleRemoveDrug = (drug) => {
    setSelectedDrugs(selectedDrugs.filter(d => d !== drug));
    setResults(null);
  };

  const handleCheckInteractions = async () => {
    if (selectedDrugs.length < 2) {
      setError('Please select at least 2 medications');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await checkInteractions(selectedDrugs);
      setResults(data);
    } catch (err) {
      setError(err.message || 'Failed to check interactions');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedDrugs([]);
    setResults(null);
    setError(null);
  };

  return (
    <div className="App">
      <Header />
      
      <main className="container">
        <div className="main-content">
          {/* Drug Selection Section */}
          <section className="search-section">
            <h2>Select Medications</h2>
            <p className="subtitle">
              Search and add medications to check for potential interactions
            </p>
            
            <DrugSearch 
              onAddDrug={handleAddDrug}
              selectedDrugs={selectedDrugs}
            />

            {/* Selected Drugs */}
            {selectedDrugs.length > 0 && (
              <div className="selected-drugs">
                <h3>Selected Medications ({selectedDrugs.length})</h3>
                <div className="drug-chips">
                  {selectedDrugs.map(drug => (
                    <div key={drug} className="drug-chip">
                      <span>{drug}</span>
                      <button 
                        className="remove-btn"
                        onClick={() => handleRemoveDrug(drug)}
                        aria-label={`Remove ${drug}`}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>

                <div className="action-buttons">
                  <button 
                    className="btn btn-primary"
                    onClick={handleCheckInteractions}
                    disabled={loading || selectedDrugs.length < 2}
                  >
                    {loading ? 'Analyzing...' : 'Check Interactions'}
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={handleClear}
                  >
                    Clear All
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="error-message">
                <strong>Error:</strong> {error}
              </div>
            )}
          </section>

          {/* Results Section */}
          {results && (
            <InteractionResults 
              results={results}
              selectedDrugs={selectedDrugs}
            />
          )}

          {/* Empty State */}
          {!results && selectedDrugs.length === 0 && (
            <div className="empty-state">
              <div className="empty-state-icon">💊</div>
              <h3>No medications selected</h3>
              <p>Search and add medications above to check for potential interactions</p>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>
          <strong>Disclaimer:</strong> This tool is for educational and research purposes only. 
          It is NOT a substitute for professional medical advice, diagnosis, or treatment. 
          Always consult qualified healthcare providers for medical decisions.
        </p>
      </footer>
    </div>
  );
}

export default App;
