import YourComponent from '../components/chatComponent';  // Import YourComponent

// Define the home page component
export default function Home() {
  return (
    <div>
      <h1>Hello, this is the home page.</h1>
      <YourComponent />  {/* Use YourComponent here */}
    </div>
  );
}
