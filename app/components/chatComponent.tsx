import { useState } from 'react';
import axios from 'axios';

const YourComponent = () => {
  const [question, setQuestion] = useState('');  // State to hold the user's question
  const [response, setResponse] = useState(null); // State to hold the model's response

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Send a POST request to the backend API route
      const apiResponse = await axios.post('/api/invokeSageMaker', {
        question: question,
      });
      // Display the API response
      setResponse(apiResponse.data);
    } catch (error) {
      console.error("API call failed:", error);
    }
  };

  return (
    <div>
      <h2>Ask the Llama 2 Model a Question</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={question} 
          onChange={(e) => setQuestion(e.target.value)} 
        />
        <button type="submit">Ask</button>
      </form>
      {response && <div>Model Response: {response}</div>}
    </div>
  );
};

export default YourComponent;
