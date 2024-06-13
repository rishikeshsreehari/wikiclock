async function fetchQuote() {
    try {
        const response = await fetch('data/06_17_AM.json');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();

        const quoteContainer = document.getElementById('quote');
        quoteContainer.innerHTML = `
            ${data.excerpt_pre} 
            <span class="highlight">${data.excerpt_time}</span> 
            ${data.excerpt_post}`;

        const sourceContainer = document.getElementById('source');
        sourceContainer.innerHTML = `~ <a href="${data.link}" target="_blank">${data.title}</a>`;
    } catch (error) {
        console.error('Failed to fetch the JSON file:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchQuote();
});
