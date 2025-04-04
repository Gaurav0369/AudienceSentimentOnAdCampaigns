
document.addEventListener('DOMContentLoaded', () => {
  const textInput = document.getElementById('textInput');
  const analyzeButton = document.getElementById('analyzeButton');
  const resultsDiv = document.getElementById('results');

  analyzeButton.addEventListener('click', async () => {
      const tweetText = textInput.value.trim();

      if (!tweetText) {
          resultsDiv.innerHTML = '<p class="error">Please enter some text to analyze.</p>';
          return;
      }

      // Show loading state
      resultsDiv.innerHTML = '<p>Analyzing...</p>';
      analyzeButton.disabled = true; // Disable button during request

      try {
          const response = await fetch('/analyze', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ tweet: tweetText }),
          });

          const data = await response.json();

          if (!response.ok) {
              // Handle HTTP errors (like 400, 500) or backend-specific errors
              const errorMessage = data.error || `HTTP error ${response.status}`;
              const errorDetails = data.details ? `<br><small>${data.details}</small>` : '';
              resultsDiv.innerHTML = `<p class="error">Analysis failed: ${errorMessage}${errorDetails}</p>`;
          } else {
              // Process and display successful results
              displayResults(data);
          }
      } catch (error) {
          // Handle network errors or issues parsing JSON
          console.error('Error during fetch:', error);
          resultsDiv.innerHTML = `<p class="error">An error occurred while contacting the server. Please check the console.</p>`;
      } finally {
           analyzeButton.disabled = false; // Re-enable button
      }
  });

  function displayResults(sentimentData) {
      resultsDiv.innerHTML = ''; // Clear previous results or loading message

      // Sort results for consistent order (optional, e.g., by score descending)
      const sortedLabels = Object.keys(sentimentData).sort((a, b) => sentimentData[b] - sentimentData[a]);

      sortedLabels.forEach(label => {
          const score = sentimentData[label];
          const resultElement = document.createElement('p');
          resultElement.innerHTML = `
              <span class="label">${label}:</span>
              <span class="score">${score.toFixed(4)}</span>
          `; // Format score to 4 decimal places
          resultsDiv.appendChild(resultElement);
      });
  }
});