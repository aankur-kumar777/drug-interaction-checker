/**
 * API Utility Module
 * Handles all API communication with the backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class DrugInteractionAPI {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async checkInteractions(drugs, patientFactors = {}) {
        try {
            const response = await fetch(`${this.baseURL}/check-interactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drugs: drugs,
                    patient_factors: patientFactors
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error checking interactions:', error);
            throw error;
        }
    }

    async searchDrugs(query, limit = 10) {
        try {
            const response = await fetch(
                `${this.baseURL}/search?q=${encodeURIComponent(query)}&limit=${limit}`
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error searching drugs:', error);
            throw error;
        }
    }

    async getDrugInfo(drugName) {
        try {
            const response = await fetch(
                `${this.baseURL}/drug/${encodeURIComponent(drugName)}`
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting drug info:', error);
            throw error;
        }
    }

    async getAlternatives(drugName, contextDrugs = []) {
        try {
            const queryParams = contextDrugs.map(d => `context=${encodeURIComponent(d)}`).join('&');
            const url = `${this.baseURL}/alternatives/${encodeURIComponent(drugName)}${queryParams ? '?' + queryParams : ''}`;
            
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting alternatives:', error);
            throw error;
        }
    }

    async visualizeInteractions(drugs) {
        try {
            const response = await fetch(`${this.baseURL}/visualize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ drugs: drugs })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error visualizing interactions:', error);
            throw error;
        }
    }

    async getInteractionSeverity(drug1, drug2) {
        try {
            const response = await fetch(
                `${this.baseURL}/severity/${encodeURIComponent(drug1)}/${encodeURIComponent(drug2)}`
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting severity:', error);
            throw error;
        }
    }
}

// Export for use in main app
window.DrugInteractionAPI = DrugInteractionAPI;
